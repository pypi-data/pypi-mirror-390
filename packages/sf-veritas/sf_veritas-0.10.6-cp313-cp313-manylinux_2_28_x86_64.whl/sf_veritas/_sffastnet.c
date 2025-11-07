// sf_veritas/_sffastnet.c
// Ultra-fast network request capture with request/response data
// Key optimization: Use g_in_telemetry_send flag (not HTTP headers)

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <pthread.h>
#include <curl/curl.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>

// ===================== Thread-local guard flag ====================
// CRITICAL: Prevents _sfteepreload.c from capturing our telemetry traffic
__attribute__((visibility("default")))
__thread int g_in_telemetry_send = 0;

// ---------- Ring buffer ----------
#ifndef SFN_RING_CAP
#define SFN_RING_CAP 65536  // power-of-two recommended
#endif

typedef struct {
    char  *body;   // malloc'd HTTP JSON body
    size_t len;
} sfn_msg_t;

static sfn_msg_t *g_ring = NULL;
static size_t     g_cap  = 0;
static _Atomic size_t g_head = 0; // consumer
static _Atomic size_t g_tail = 0; // producer

// tiny spinlock to make push MPMC-safe enough for Python producers
static atomic_flag g_push_lock = ATOMIC_FLAG_INIT;


// wake/sleep
static pthread_mutex_t g_cv_mtx = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t  g_cv     = PTHREAD_COND_INITIALIZER;
static _Atomic int     g_running = 0;

// Thread pool for parallel sending (configurable via SF_FASTNET_SENDER_THREADS)
#define MAX_SENDER_THREADS 16
static pthread_t g_sender_threads[MAX_SENDER_THREADS];
static int g_num_sender_threads = 0;
static int g_configured_sender_threads = 1;  // Default: 1 thread

// Debug flag (set from SF_DEBUG environment variable)
static int SF_DEBUG = 0;

// curl state (per-thread handles + shared headers)
__thread CURL *g_telem_curl = NULL;
static struct curl_slist *g_hdrs = NULL;

// config (owned strings)
static char *g_url = NULL;
static char *g_query_escaped = NULL;
static char *g_api_key = NULL;
static int   g_http2 = 0;

// prebuilt JSON prefix for NETWORK REQUEST:
// {"query":"<escaped_query>","variables":{"data":{"apiKey":"..."
static char *g_json_prefix = NULL;

static const char *JSON_SUFFIX = "}}}";

// ---------- helpers ----------
static inline uint64_t now_ms(void) {
#if defined(CLOCK_REALTIME_COARSE)
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME_COARSE, &ts);
    return ((uint64_t)ts.tv_sec) * 1000ULL + (uint64_t)(ts.tv_nsec / 1000000ULL);
#else
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return ((uint64_t)tv.tv_sec) * 1000ULL + (uint64_t)(tv.tv_usec / 1000ULL);
#endif
}

static char *str_dup(const char *s) {
    size_t n = strlen(s);
    char *p = (char*)malloc(n + 1);
    if (!p) return NULL;
    memcpy(p, s, n);
    p[n] = 0;
    return p;
}

// Fast path: check if string needs escaping at all
static inline int needs_escape(const char *s, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        unsigned char c = (unsigned char)s[i];
        if (c == '\\' || c == '"' || c < 0x20) return 1;
    }
    return 0;
}

// escape for generic JSON string fields
static char *json_escape(const char *s) {
    if (!s) return str_dup("");

    size_t inlen = strlen(s);

    // Fast path: if no escaping needed, just duplicate
    if (!needs_escape(s, inlen)) {
        return str_dup(s);
    }

    // Slow path: need to escape
    const unsigned char *in = (const unsigned char*)s;
    size_t extra = 0;
    for (const unsigned char *p = in; *p; ++p) {
        switch (*p) {
            case '\\': case '"': extra++; break;
            default:
                if (*p < 0x20) extra += 5; // \u00XX
        }
    }

    char *out = (char*)malloc(inlen + extra + 1);
    if (!out) return NULL;

    char *o = out;
    for (const unsigned char *p = in; *p; ++p) {
        switch (*p) {
            case '\\': *o++='\\'; *o++='\\'; break;
            case '"':  *o++='\\'; *o++='"';  break;
            default:
                if (*p < 0x20) {
                    static const char hex[] = "0123456789abcdef";
                    *o++='\\'; *o++='u'; *o++='0'; *o++='0';
                    *o++=hex[(*p)>>4]; *o++=hex[(*p)&0xF];
                } else {
                    *o++ = (char)*p;
                }
        }
    }
    *o = 0;
    return out;
}

// escape for the GraphQL "query" string (handle \n, \r, \t too)
static char *json_escape_query(const char *s) {
    const unsigned char *in = (const unsigned char*)s;
    size_t extra = 0;
    for (const unsigned char *p = in; *p; ++p) {
        switch (*p) {
            case '\\': case '"': case '\n': case '\r': case '\t': extra++; break;
            default: break;
        }
    }
    size_t inlen = strlen(s);
    char *out = (char*)malloc(inlen + extra + 1);
    if (!out) return NULL;
    char *o = out;
    for (const unsigned char *p = in; *p; ++p) {
        switch (*p) {
            case '\\': *o++='\\'; *o++='\\'; break;
            case '"':  *o++='\\'; *o++='"';  break;
            case '\n': *o++='\\'; *o++='n';  break;
            case '\r': *o++='\\'; *o++='r';  break;
            case '\t': *o++='\\'; *o++='t';  break;
            default: *o++=(char)*p;
        }
    }
    *o=0;
    return out;
}

// Extract "query|mutation operationName (fieldName)" from GraphQL request body
// Returns malloc'd string or NULL if not GraphQL or parse error
// Fast path: 2ns for non-GraphQL (just memcmp check)
// Slow path: 15-18ns for GraphQL (parse ~200 chars)
// Format: "query operationName (fieldName)" or "mutation operationName (fieldName)"
// Handles both direct GraphQL and JSON-wrapped: {"query": "mutation ..."}
static char *extract_graphql_name(const char *body, size_t len) {
    if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] START len=%zu, first 100 chars: %.100s\n", len, body);

    if (len < 6) {
        if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] FAIL: len < 6\n");
        return NULL;
    }

    const char *p = body;
    const char *end = body + len;
    const char *operation_type = NULL;
    size_t operation_type_len = 0;

    // Skip leading whitespace (handles "  mutation ..." or "\n\tquery ...")
    while (p < end && (*p == ' ' || *p == '\t' || *p == '\n' || *p == '\r')) p++;

    if (p >= end) {
        if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] FAIL: only whitespace\n");
        return NULL;
    }

    // Calculate remaining length after skipping whitespace
    size_t remaining = end - p;
    if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] After whitespace skip, remaining=%zu, first char='%c'\n", remaining, *p);

    // Check if it's JSON-wrapped GraphQL: {"query": "mutation ..."}
    // Fast check: starts with '{'
    if (remaining > 10 && *p == '{') {
        if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] Detected JSON format (starts with '{')\n");

        // Look for "query": or "query" : (with optional whitespace)
        const char *query_key = p + 1;

        // Skip whitespace after '{'
        while (query_key < end && (*query_key == ' ' || *query_key == '\t' || *query_key == '\n' || *query_key == '\r')) query_key++;

        if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] After '{', next chars: %.20s\n", query_key);

        // Check for "query" (with quotes)
        if ((end - query_key) > 10 && memcmp(query_key, "\"query\"", 7) == 0) {
            if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] Found \"query\" key\n");
            query_key += 7;

            // Skip whitespace
            while (query_key < end && (*query_key == ' ' || *query_key == '\t' || *query_key == '\n' || *query_key == '\r')) query_key++;

            // Expect ':'
            if (query_key < end && *query_key == ':') {
                if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] Found ':' after query key\n");
                query_key++;

                // Skip whitespace
                while (query_key < end && (*query_key == ' ' || *query_key == '\t' || *query_key == '\n' || *query_key == '\r')) query_key++;

                // Expect '"' (start of query string value)
                if (query_key < end && *query_key == '"') {
                    if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] Found opening quote for query value\n");
                    query_key++;

                    // Now query_key points to the GraphQL query string
                    // Update p and end to parse this substring
                    p = query_key;

                    // Find the closing quote (handle escaped quotes \")
                    const char *query_end = p;
                    while (query_end < end) {
                        if (*query_end == '"' && (query_end == p || *(query_end - 1) != '\\')) {
                            break;
                        }
                        query_end++;
                    }

                    if (query_end >= end) {
                        if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] FAIL: No closing quote for query value\n");
                        return NULL;
                    }

                    end = query_end;  // Limit parsing to within the query field
                    remaining = end - p;
                    if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] Extracted query value, first 100 chars: %.100s\n", p);
                } else {
                    if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] Expected opening quote but got: %c\n", query_key < end ? *query_key : '?');
                }
            } else {
                if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] Expected ':' but got: %c\n", query_key < end ? *query_key : '?');
            }
        } else {
            if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] Did not find \"query\" key, next chars: %.20s\n", query_key);
        }
    }

    // Skip any leading whitespace in the query string itself (handles escaped whitespace too)
    while (p < end && (*p == ' ' || *p == '\t' || *p == '\\' || *p == 'n' || *p == 't' || *p == 'r')) {
        if (*p == '\\' && p + 1 < end && (*(p + 1) == 'n' || *(p + 1) == 't' || *(p + 1) == 'r')) {
            p += 2;  // Skip \n, \t, or \r
        } else if (*p == ' ' || *p == '\t') {
            p++;
        } else {
            break;
        }
    }

    if (p >= end) {
        if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] FAIL: only whitespace after escaped whitespace skip\n");
        return NULL;
    }
    remaining = end - p;
    if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] Ready to match operation type, remaining=%zu, first 20 chars: %.20s\n", remaining, p);

    // Fast-path check for "mutation " or "query "
    if (remaining >= 9 && memcmp(p, "mutation ", 9) == 0) {
        if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] Matched 'mutation '\n");
        operation_type = "mutation";
        operation_type_len = 8;
        p += 9;
    } else if (remaining >= 6 && memcmp(p, "query ", 6) == 0) {
        if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] Matched 'query '\n");
        operation_type = "query";
        operation_type_len = 5;
        p += 6;
    } else if (remaining >= 9 && memcmp(p, "mutation{", 9) == 0) {
        if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] Matched 'mutation{' (anonymous)\n");
        // Anonymous mutation: "mutation{field}"
        operation_type = "mutation";
        operation_type_len = 8;
        p += 8;  // p now at '{'
    } else if (remaining >= 6 && memcmp(p, "query{", 6) == 0) {
        if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] Matched 'query{' (anonymous)\n");
        // Anonymous query: "query{field}"
        operation_type = "query";
        operation_type_len = 5;
        p += 5;  // p now at '{'
    } else {
        if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] FAIL: No operation type match, first 30 chars: %.30s\n", p);
        return NULL;  // Not a GraphQL operation
    }

    // Skip whitespace
    while (p < end && (*p == ' ' || *p == '\t' || *p == '\n' || *p == '\r')) p++;

    // Extract operation name (optional - may be anonymous)
    const char *op_name_start = p;
    const char *op_name_end = p;

    if (p < end && *p != '{' && *p != '(') {
        // We have an operation name
        while (p < end && *p != '(' && *p != '{' && *p != ' ' && *p != '\t' && *p != '\n' && *p != '\r') {
            p++;
        }
        op_name_end = p;
    }

    size_t op_name_len = op_name_end - op_name_start;

    // Skip whitespace
    while (p < end && (*p == ' ' || *p == '\t' || *p == '\n' || *p == '\r')) p++;

    // Skip parameter list if present: ($param1: Type, ...)
    // Use balanced parenthesis matching to handle nested types: ($x: Type($nested))
    if (p < end && *p == '(') {
        int depth = 1;
        p++;
        while (p < end && depth > 0) {
            if (*p == '(') depth++;
            else if (*p == ')') depth--;
            p++;
        }
        if (depth != 0) return NULL;  // Mismatched parens - parse error
    }

    // Skip whitespace
    while (p < end && (*p == ' ' || *p == '\t' || *p == '\n' || *p == '\r')) p++;

    // Expect '{'
    if (p >= end || *p != '{') return NULL;  // Parse error
    p++;  // Skip '{'

    // Skip whitespace inside selection set
    while (p < end && (*p == ' ' || *p == '\t' || *p == '\n' || *p == '\r')) p++;

    // Extract first field name (until '(' or '{' or whitespace)
    const char *field_start = p;
    while (p < end && *p != '(' && *p != '{' && *p != ' ' && *p != '\t' && *p != '\n' && *p != '\r') {
        p++;
    }
    const char *field_end = p;

    size_t field_len = field_end - field_start;
    if (field_len == 0) return NULL;  // No field name - parse error

    // Build result: "operation_type operationName (fieldName)"
    // Format examples:
    //   "query GetUser (user)"
    //   "mutation CollectFunctionSpan (collectFunctionSpan)"
    //   "mutation (createPost)"  (anonymous)

    // Calculate result length
    size_t result_len = operation_type_len + 1;  // "mutation "
    if (op_name_len > 0) {
        result_len += op_name_len + 1;  // "operationName "
    }
    result_len += 1 + field_len + 1;  // "(fieldName)"

    char *result = (char*)malloc(result_len + 1);
    if (!result) return NULL;

    // Build result string
    char *o = result;
    memcpy(o, operation_type, operation_type_len);
    o += operation_type_len;
    *o++ = ' ';

    if (op_name_len > 0) {
        memcpy(o, op_name_start, op_name_len);
        o += op_name_len;
        *o++ = ' ';
    }

    *o++ = '(';
    memcpy(o, field_start, field_len);
    o += field_len;
    *o++ = ')';
    *o = '\0';

    if (SF_DEBUG) fprintf(stderr, "[DEBUG extract_graphql_name] SUCCESS: result='%s'\n", result);
    return result;
}

// Build prefix: {"query":"...","variables":{"data":{"apiKey":"..."
static int build_prefix(void) {
    const char *p1 = "{\"query\":\"";
    const char *p2 = "\",\"variables\":{\"data\":{";
    const char *k1 = "\"apiKey\":\"";

    size_t n = strlen(p1) + strlen(g_query_escaped) + strlen(p2)
             + strlen(k1) + strlen(g_api_key) + 5;

    char *prefix = (char*)malloc(n);
    if (!prefix) return 0;

    char *o = prefix;
    o += sprintf(o, "%s%s%s", p1, g_query_escaped, p2);
    o += sprintf(o, "%s%s\"", k1, g_api_key);
    *o = '\0';

    g_json_prefix = prefix;
    return 1;
}

// Build NETWORK REQUEST body with all fields including request/response data and headers
static int build_body_network_request(
    const char *request_id,
    const char *page_visit_id,
    const char *recording_session_id,
    const char *service_uuid,
    uint64_t timestamp_start,
    uint64_t timestamp_end,
    int response_code,
    int success,
    const char *error,
    const char *url,
    const char *method,
    const char *request_data,
    const char *response_data,
    const char *request_headers,
    const char *response_headers,
    const char *name,
    char **out_body,
    size_t *out_len
) {
    // Escape all fields including headers
    // Headers are JSON strings from Python that must be escaped to embed as string values
    char *req_id_esc = json_escape(request_id);
    char *pv_id_esc = json_escape(page_visit_id);
    char *rec_sid_esc = json_escape(recording_session_id);
    char *svc_uuid_esc = json_escape(service_uuid);
    char *err_esc = json_escape(error);
    char *url_esc = json_escape(url);
    char *method_esc = json_escape(method);
    char *req_data_esc = json_escape(request_data);
    char *resp_data_esc = json_escape(response_data);
    char *req_hdrs_esc = json_escape(request_headers);
    char *resp_hdrs_esc = json_escape(response_headers);
    char *name_esc = json_escape(name);

    if (!req_id_esc || !pv_id_esc || !rec_sid_esc || !svc_uuid_esc ||
        !err_esc || !url_esc || !method_esc || !req_data_esc || !resp_data_esc ||
        !req_hdrs_esc || !resp_hdrs_esc || !name_esc) {
        free(req_id_esc); free(pv_id_esc); free(rec_sid_esc); free(svc_uuid_esc);
        free(err_esc); free(url_esc); free(method_esc); free(req_data_esc); free(resp_data_esc);
        free(req_hdrs_esc); free(resp_hdrs_esc); free(name_esc);
        return 0;
    }

    // Build JSON fields
    const char *k_req_id = ",\"requestId\":\"";
    const char *k_pv_id = "\",\"pageVisitId\":\"";
    const char *k_rec_sid = "\",\"recordingSessionId\":\"";
    const char *k_svc_uuid = "\",\"serviceUuid\":\"";
    const char *k_ts_start = "\",\"timestampStart\":";
    const char *k_ts_end = ",\"timestampEnd\":";
    const char *k_resp_code = ",\"responseCode\":";
    const char *k_success = ",\"success\":";
    const char *k_error = ",\"error\":";
    const char *k_url = ",\"url\":\"";
    const char *k_method = "\",\"method\":\"";
    const char *k_req_data = "\",\"requestBody\":\"";
    const char *k_resp_data = "\",\"responseBody\":\"";
    const char *k_req_hdrs = "\",\"requestHeaders\":\"";
    const char *k_resp_hdrs = "\",\"responseHeaders\":\"";
    const char *k_name = "\",\"name\":";

    char ts_start_buf[32], ts_end_buf[32], resp_code_buf[16];
    snprintf(ts_start_buf, sizeof(ts_start_buf), "%llu", (unsigned long long)timestamp_start);
    snprintf(ts_end_buf, sizeof(ts_end_buf), "%llu", (unsigned long long)timestamp_end);
    snprintf(resp_code_buf, sizeof(resp_code_buf), "%d", response_code);
    const char *success_str = success ? "true" : "false";
    const char *error_str = error ? "\"" : "null";
    const char *error_end = error ? "\"" : "";

    if (!g_json_prefix) {
        free(req_id_esc); free(pv_id_esc); free(rec_sid_esc); free(svc_uuid_esc);
        free(err_esc); free(url_esc); free(method_esc); free(req_data_esc); free(resp_data_esc);
        free(req_hdrs_esc); free(resp_hdrs_esc); free(name_esc);
        return 0;
    }

    // Handle name field (could be NULL for non-GraphQL requests)
    const char *name_str = name ? "\"" : "null";
    const char *name_end = name ? "\"" : "";

    size_t len = strlen(g_json_prefix)
               + strlen(k_req_id) + strlen(req_id_esc)
               + strlen(k_pv_id) + strlen(pv_id_esc)
               + strlen(k_rec_sid) + strlen(rec_sid_esc)
               + strlen(k_svc_uuid) + strlen(svc_uuid_esc)
               + strlen(k_ts_start) + strlen(ts_start_buf)
               + strlen(k_ts_end) + strlen(ts_end_buf)
               + strlen(k_resp_code) + strlen(resp_code_buf)
               + strlen(k_success) + strlen(success_str)
               + strlen(k_error) + strlen(error_str) + strlen(err_esc) + strlen(error_end)
               + strlen(k_url) + strlen(url_esc)
               + strlen(k_method) + strlen(method_esc)
               + strlen(k_req_data) + strlen(req_data_esc)
               + strlen(k_resp_data) + strlen(resp_data_esc)
               + strlen(k_req_hdrs) + strlen(req_hdrs_esc)
               + strlen(k_resp_hdrs) + strlen(resp_hdrs_esc)
               + strlen(k_name) + strlen(name_str) + strlen(name_esc) + strlen(name_end)
               + strlen(JSON_SUFFIX) + 10;

    char *body = (char*)malloc(len + 1);
    if (!body) {
        free(req_id_esc); free(pv_id_esc); free(rec_sid_esc); free(svc_uuid_esc);
        free(err_esc); free(url_esc); free(method_esc); free(req_data_esc); free(resp_data_esc);
        free(req_hdrs_esc); free(resp_hdrs_esc); free(name_esc);
        return 0;
    }

    char *o = body;
    o += sprintf(o, "%s", g_json_prefix);
    o += sprintf(o, "%s%s", k_req_id, req_id_esc);
    o += sprintf(o, "%s%s", k_pv_id, pv_id_esc);
    o += sprintf(o, "%s%s", k_rec_sid, rec_sid_esc);
    o += sprintf(o, "%s%s", k_svc_uuid, svc_uuid_esc);
    o += sprintf(o, "%s%s", k_ts_start, ts_start_buf);
    o += sprintf(o, "%s%s", k_ts_end, ts_end_buf);
    o += sprintf(o, "%s%s", k_resp_code, resp_code_buf);
    o += sprintf(o, "%s%s", k_success, success_str);
    if (error) {
        o += sprintf(o, "%s\"%s\"", k_error, err_esc);
    } else {
        o += sprintf(o, "%snull", k_error);
    }
    o += sprintf(o, "%s%s", k_url, url_esc);
    o += sprintf(o, "%s%s", k_method, method_esc);
    o += sprintf(o, "%s%s", k_req_data, req_data_esc);
    o += sprintf(o, "%s%s", k_resp_data, resp_data_esc);
    o += sprintf(o, "%s%s", k_req_hdrs, req_hdrs_esc);
    o += sprintf(o, "%s%s", k_resp_hdrs, resp_hdrs_esc);
    // Add name field (handles both GraphQL and non-GraphQL)
    if (name) {
        o += sprintf(o, "%s\"%s\"", k_name, name_esc);
    } else {
        o += sprintf(o, "%snull", k_name);
    }
    o += sprintf(o, "%s", JSON_SUFFIX);
    *o = '\0';

    *out_body = body;
    *out_len  = (size_t)(o - body);

    free(req_id_esc); free(pv_id_esc); free(rec_sid_esc); free(svc_uuid_esc);
    free(err_esc); free(url_esc); free(method_esc); free(req_data_esc); free(resp_data_esc);
    free(req_hdrs_esc); free(resp_hdrs_esc); free(name_esc);
    return 1;
}

// ---------- ring ops ----------
static inline size_t ring_count(void) {
    size_t h = atomic_load_explicit(&g_head, memory_order_acquire);
    size_t t = atomic_load_explicit(&g_tail, memory_order_acquire);
    return t - h;
}
static inline int ring_empty(void) { return ring_count() == 0; }

static int ring_push(char *body, size_t len) {
    while (atomic_flag_test_and_set_explicit(&g_push_lock, memory_order_acquire)) {
        // brief spin
    }
    size_t t = atomic_load_explicit(&g_tail, memory_order_relaxed);
    size_t h = atomic_load_explicit(&g_head, memory_order_acquire);
    if ((t - h) >= g_cap) {
        atomic_flag_clear_explicit(&g_push_lock, memory_order_release);
        return 0; // full (drop)
    }
    size_t idx = t % g_cap;
    g_ring[idx].body = body;
    g_ring[idx].len  = len;
    atomic_store_explicit(&g_tail, t + 1, memory_order_release);
    atomic_flag_clear_explicit(&g_push_lock, memory_order_release);

    pthread_mutex_lock(&g_cv_mtx);
    pthread_cond_signal(&g_cv);
    pthread_mutex_unlock(&g_cv_mtx);
    return 1;
}

static int ring_pop(char **body, size_t *len) {
    size_t h = atomic_load_explicit(&g_head, memory_order_relaxed);
    size_t t = atomic_load_explicit(&g_tail, memory_order_acquire);
    if (h == t) return 0;
    size_t idx = h % g_cap;
    *body = g_ring[idx].body;
    *len  = g_ring[idx].len;
    g_ring[idx].body = NULL;
    g_ring[idx].len  = 0;
    atomic_store_explicit(&g_head, h + 1, memory_order_release);
    return 1;
}

// ---------- curl sink callbacks ----------
static size_t _sink_write(char *ptr, size_t size, size_t nmemb, void *userdata) {
    (void)ptr; (void)userdata;
    return size * nmemb;
}
static size_t _sink_header(char *ptr, size_t size, size_t nmemb, void *userdata) {
    (void)ptr; (void)userdata;
    return size * nmemb;
}

// ========================= pthread cleanup handler ==========================
static void sender_cleanup(void *arg) {
    (void)arg;

    // Close thread-local curl handle
    if (g_telem_curl) {
        curl_easy_cleanup(g_telem_curl);
        g_telem_curl = NULL;
    }
}

// ---------- sender thread ----------
static void *sender_main(void *arg) {
    (void)arg;

    // CRITICAL: Set telemetry guard for this thread (prevents _sfteepreload.c capture)
    g_in_telemetry_send = 1;

    // Initialize thread-local curl handle
    g_telem_curl = curl_easy_init();
    if (!g_telem_curl) {
        return NULL;
    }

    // Configure curl handle (copy from global settings)
    curl_easy_setopt(g_telem_curl, CURLOPT_URL, g_url);
    curl_easy_setopt(g_telem_curl, CURLOPT_TCP_KEEPALIVE, 1L);
    curl_easy_setopt(g_telem_curl, CURLOPT_TCP_NODELAY, 1L);  // NEW: Eliminate Nagle delay
    curl_easy_setopt(g_telem_curl, CURLOPT_HTTPHEADER, g_hdrs);
#ifdef CURL_HTTP_VERSION_2TLS
    if (g_http2) {
        curl_easy_setopt(g_telem_curl, CURLOPT_HTTP_VERSION, CURL_HTTP_VERSION_2TLS);
    }
#endif
    curl_easy_setopt(g_telem_curl, CURLOPT_WRITEFUNCTION, _sink_write);
    curl_easy_setopt(g_telem_curl, CURLOPT_HEADERFUNCTION, _sink_header);

    // Register cleanup handler (executes on thread exit)
    pthread_cleanup_push(sender_cleanup, NULL);

    while (atomic_load(&g_running)) {
        if (ring_empty()) {
            pthread_mutex_lock(&g_cv_mtx);
            if (ring_empty() && atomic_load(&g_running))
                pthread_cond_wait(&g_cv, &g_cv_mtx);
            pthread_mutex_unlock(&g_cv_mtx);
            if (!atomic_load(&g_running)) break;
        }
        char *body = NULL; size_t len = 0;
        while (ring_pop(&body, &len)) {
            if (!body) continue;

            // Use thread-local curl handle (each thread has its own persistent connection)
            curl_easy_setopt(g_telem_curl, CURLOPT_POSTFIELDS, body);
            curl_easy_setopt(g_telem_curl, CURLOPT_POSTFIELDSIZE, (long)len);
            (void)curl_easy_perform(g_telem_curl); // fire-and-forget

            free(body);
            if (!atomic_load(&g_running)) break;
        }
    }

    pthread_cleanup_pop(1);  // Execute cleanup handler
    return NULL;
}

// ---------- Python API ----------
static PyObject *py_init(PyObject *self, PyObject *args, PyObject *kw) {
    // Initialize SF_DEBUG from environment variable (once)
    static int initialized = 0;
    if (!initialized) {
        const char *debug_val = getenv("SF_DEBUG");
        SF_DEBUG = (debug_val && (strcmp(debug_val, "True") == 0 || strcmp(debug_val, "true") == 0 || strcmp(debug_val, "1") == 0)) ? 1 : 0;
        initialized = 1;
    }

    if (SF_DEBUG) fprintf(stderr, "[DEBUG py_init] CALLED!\n");
    fflush(stderr);

    const char *url, *query, *api_key;
    int http2 = 0;
    static char *kwlist[] = {"url","query","api_key","http2", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kw, "sss|i",
        kwlist, &url, &query, &api_key, &http2)) {
        if (SF_DEBUG) fprintf(stderr, "[DEBUG py_init] FAIL: arg parse error\n");
        fflush(stderr);
        Py_RETURN_FALSE;
    }
    if (g_running) {
        if (SF_DEBUG) fprintf(stderr, "[DEBUG py_init] Already running, returning True\n");
        fflush(stderr);
        Py_RETURN_TRUE;
    }

    g_url = str_dup(url);
    g_query_escaped = json_escape_query(query);
    g_api_key = str_dup(api_key);
    g_http2 = http2 ? 1 : 0;
    if (!g_url || !g_query_escaped || !g_api_key) {
        Py_RETURN_FALSE;
    }
    if (!build_prefix()) { Py_RETURN_FALSE; }

    g_cap = SFN_RING_CAP;
    g_ring = (sfn_msg_t*)calloc(g_cap, sizeof(sfn_msg_t));
    if (!g_ring) { Py_RETURN_FALSE; }

    // Parse SF_FASTNET_SENDER_THREADS environment variable
    const char *env_threads = getenv("SF_FASTNET_SENDER_THREADS");
    if (env_threads) {
        int t = atoi(env_threads);
        if (t > 0 && t <= MAX_SENDER_THREADS) {
            g_configured_sender_threads = t;
        }
    }

    // Initialize curl (shared headers only - handles are per-thread)
    curl_global_init(CURL_GLOBAL_DEFAULT);
    g_hdrs = NULL;
    g_hdrs = curl_slist_append(g_hdrs, "Content-Type: application/json");

    // Start sender thread pool
    atomic_store(&g_running, 1);
    g_num_sender_threads = g_configured_sender_threads;
    for (int i = 0; i < g_num_sender_threads; i++) {
        if (pthread_create(&g_sender_threads[i], NULL, sender_main, NULL) != 0) {
            if (SF_DEBUG) fprintf(stderr, "[DEBUG py_init] FAIL: pthread_create failed for thread %d\n", i);
            fflush(stderr);
            atomic_store(&g_running, 0);
            // Clean up already-started threads
            for (int j = 0; j < i; j++) {
                pthread_join(g_sender_threads[j], NULL);
            }
            Py_RETURN_FALSE;
        }
    }
    if (SF_DEBUG) fprintf(stderr, "[DEBUG py_init] SUCCESS: _sffastnet initialized with %d threads!\n", g_num_sender_threads);
    fflush(stderr);
    Py_RETURN_TRUE;
}

// Ultra-fast path - use s# format for zero-copy bytes access like _sffastlog
static PyObject *py_network_request(PyObject *self, PyObject *args) {
    if (SF_DEBUG) fprintf(stderr, "[DEBUG py_network_request] CALLED!\n");
    fflush(stderr);

    // Accept bytes objects with lengths for zero-copy access
    // Order: request_id, page_visit_id, recording_session_id, service_uuid,
    //        timestamp_start, timestamp_end, response_code, success,
    //        error, url, method, request_data, response_data,
    //        request_headers, response_headers

    if (!g_running || !g_json_prefix) {
        if (SF_DEBUG) fprintf(stderr, "[DEBUG py_network_request] EARLY RETURN: g_running=%d, g_json_prefix=%p\n", g_running, g_json_prefix);
        fflush(stderr);
        Py_RETURN_NONE;
    }

    const char *req_id, *pv_id, *rec_sid, *svc_uuid, *url, *method, *error;
    const char *req_data, *resp_data, *req_hdrs, *resp_hdrs;
    Py_ssize_t req_id_len, pv_id_len, rec_sid_len, svc_uuid_len, url_len, method_len;
    Py_ssize_t req_data_len = 0, resp_data_len = 0, req_hdrs_len = 0, resp_hdrs_len = 0;
    unsigned long long ts_start, ts_end;
    int resp_code, success;
    PyObject *o_error = NULL;

    // Use s# for bytes (zero-copy), y# also works for bytes objects
    // Parse as: str, str, str, str, int, int, int, bool, obj, str, str, bytes, bytes, bytes, bytes
    if (!PyArg_ParseTuple(args, "ssssKKipOssy#y#y#y#",
                          &req_id, &pv_id, &rec_sid, &svc_uuid,
                          &ts_start, &ts_end, &resp_code, &success,
                          &o_error, &url, &method,
                          &req_data, &req_data_len,
                          &resp_data, &resp_data_len,
                          &req_hdrs, &req_hdrs_len,
                          &resp_hdrs, &resp_hdrs_len)) {
        Py_RETURN_NONE;
    }

    error = (o_error != Py_None) ? PyUnicode_AsUTF8(o_error) : NULL;

    char *body = NULL;
    size_t len = 0;
    int ok = 0;

    // Create null-terminated strings from byte buffers for JSON building
    // Allocate on stack for small strings, heap for large
    char req_data_buf[65536];  // 64KB max
    char resp_data_buf[65536];
    char req_hdrs_buf[8192];   // 8KB max
    char resp_hdrs_buf[8192];

    // Copy and null-terminate (safe truncation)
    size_t req_data_copy = req_data_len > 65535 ? 65535 : req_data_len;
    size_t resp_data_copy = resp_data_len > 65535 ? 65535 : resp_data_len;
    size_t req_hdrs_copy = req_hdrs_len > 8191 ? 8191 : req_hdrs_len;
    size_t resp_hdrs_copy = resp_hdrs_len > 8191 ? 8191 : resp_hdrs_len;

    memcpy(req_data_buf, req_data, req_data_copy);
    req_data_buf[req_data_copy] = '\0';

    memcpy(resp_data_buf, resp_data, resp_data_copy);
    resp_data_buf[resp_data_copy] = '\0';

    memcpy(req_hdrs_buf, req_hdrs, req_hdrs_copy);
    req_hdrs_buf[req_hdrs_copy] = '\0';

    memcpy(resp_hdrs_buf, resp_hdrs, resp_hdrs_copy);
    resp_hdrs_buf[resp_hdrs_copy] = '\0';

    // Everything from here runs without GIL
    Py_BEGIN_ALLOW_THREADS
    // Extract GraphQL operation name from request body if present
    // Fast path: 2ns for non-GraphQL, 15-18ns for GraphQL
    if (SF_DEBUG) fprintf(stderr, "[DEBUG py_network_request] Calling extract_graphql_name with req_data_copy=%zu bytes\n", req_data_copy);
    char *graphql_name = extract_graphql_name(req_data_buf, req_data_copy);
    if (SF_DEBUG) fprintf(stderr, "[DEBUG py_network_request] extract_graphql_name returned: %s\n", graphql_name ? graphql_name : "NULL");

    if (build_body_network_request(
            req_id, pv_id, rec_sid, svc_uuid,
            ts_start, ts_end,
            resp_code, success, error,
            url, method,
            req_data_buf, resp_data_buf,
            req_hdrs_buf, resp_hdrs_buf,
            graphql_name,
            &body, &len)) {
        ok = ring_push(body, len);
    }

    // Free the malloc'd GraphQL name if extracted
    if (graphql_name) free(graphql_name);
    Py_END_ALLOW_THREADS

    if (!ok && body) free(body);
    Py_RETURN_NONE;
}

static PyObject *py_shutdown(PyObject *self, PyObject *args) {
    if (!g_running) Py_RETURN_NONE;

    atomic_store(&g_running, 0);

    // Wake ALL threads with broadcast (not signal)
    pthread_mutex_lock(&g_cv_mtx);
    pthread_cond_broadcast(&g_cv);
    pthread_mutex_unlock(&g_cv_mtx);

    // Join all sender threads in thread pool
    for (int i = 0; i < g_num_sender_threads; i++) {
        if (g_sender_threads[i]) {
            pthread_join(g_sender_threads[i], NULL);
            g_sender_threads[i] = 0;
        }
    }
    g_num_sender_threads = 0;

    // Cleanup curl (per-thread handles cleaned by pthread_cleanup_push)
    if (g_hdrs) { curl_slist_free_all(g_hdrs); g_hdrs = NULL; }
    curl_global_cleanup();

    // Free all config strings and NULL pointers
    free(g_url); g_url = NULL;
    free(g_query_escaped); g_query_escaped = NULL;
    free(g_json_prefix); g_json_prefix = NULL;
    free(g_api_key); g_api_key = NULL;

    // Drain and free ring buffer
    if (g_ring) {
        char *b; size_t l;
        while (ring_pop(&b, &l)) free(b);
        free(g_ring); g_ring = NULL;
    }

    Py_RETURN_NONE;
}

// ---------- Module table ----------
static PyMethodDef SFFastNetMethods[] = {
    {"init",            (PyCFunction)py_init,            METH_VARARGS | METH_KEYWORDS, "Init network request tracking and start sender"},
    {"network_request", py_network_request,              METH_VARARGS,                  "Send network request (fast positional-only)"},
    {"shutdown",        (PyCFunction)py_shutdown,        METH_NOARGS,                   "Shutdown sender and free state"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef sffastnetmodule = {
    PyModuleDef_HEAD_INIT,
    "_sffastnet",
    "sf_veritas ultra-fast network request tracking with request/response data",
    -1,
    SFFastNetMethods
};

PyMODINIT_FUNC PyInit__sffastnet(void) {
    return PyModule_Create(&sffastnetmodule);
}
