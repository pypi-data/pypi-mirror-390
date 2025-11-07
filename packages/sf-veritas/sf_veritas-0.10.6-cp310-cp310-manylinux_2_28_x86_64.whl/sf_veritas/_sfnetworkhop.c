// sf_veritas/_sfnetworkhop.c
// Ultra-fast network hop capture with non-blocking producers, no drops,
// and an HTTP/2 multiplexed libcurl-multi sender.

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

#ifndef SFN_RING_CAP
#define SFN_RING_CAP 65536  // power-of-two recommended
#endif

#ifndef SFN_ENDPOINT_CAP
#define SFN_ENDPOINT_CAP 2048
#endif

#ifndef SFN_MAX_INFLIGHT
#define SFN_MAX_INFLIGHT 128   // number of concurrent requests over H2
#endif

// ---------- Message (three types: fast work, work with bodies, ready body) ----------
typedef enum {
    SFN_MSG_WORK,         // raw work item (needs JSON building)
    SFN_MSG_WORK_BODIES,  // work item with request/response bodies
    SFN_MSG_BODY          // pre-built body (legacy path)
} sfn_msg_type;

typedef struct {
    sfn_msg_type type;
    union {
        struct {  // type == SFN_MSG_WORK
            char *session_id;    // malloced copy
            size_t session_len;
            int endpoint_id;
        } work;
        struct {  // type == SFN_MSG_WORK_BODIES
            char *session_id;    // malloced copy
            size_t session_len;
            int endpoint_id;
            char *route;         // malloced JSON-escaped string or NULL (overrides registered route)
            size_t route_len;
            char *query_params;  // malloced JSON-escaped string or NULL
            size_t query_params_len;
            char *req_headers;   // malloced JSON-escaped string or NULL
            size_t req_headers_len;
            char *req_body;      // malloced JSON-escaped string or NULL
            size_t req_body_len;
            char *resp_headers;  // malloced JSON-escaped string or NULL
            size_t resp_headers_len;
            char *resp_body;     // malloced JSON-escaped string or NULL
            size_t resp_body_len;
        } work_bodies;
        struct {  // type == SFN_MSG_BODY
            char *body;
            size_t len;
        } body;
    } data;
} sfn_msg_t;

// ---------- Ring buffer (bounded, cache-friendly) ----------
static sfn_msg_t *g_ring = NULL;
static size_t     g_cap  = 0;
static _Atomic size_t g_head = 0; // consumer index
static _Atomic size_t g_tail = 0; // producer index

// REMOVED: spinlock for MPMC push (replaced with lock-free CAS below)

// ---------- Overflow (unbounded, no-drop) ----------
typedef struct sfn_node_t {
    sfn_msg_t msg;
    struct sfn_node_t *next;
} sfn_node_t;

static _Atomic(sfn_node_t*) g_overflow_head = NULL;

// ---------- wake/sleep ----------
static pthread_mutex_t g_cv_mtx = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t  g_cv     = PTHREAD_COND_INITIALIZER;
static _Atomic int     g_running = 0;

// Thread pool for concurrent senders (configurable via SF_NETWORKHOP_SENDER_THREADS)
#define MAX_SENDER_THREADS 16
static pthread_t g_sender_threads[MAX_SENDER_THREADS];
static int g_num_sender_threads = 0;

// ---------- libcurl state ----------
__thread CURLM *g_multi = NULL;     // per-thread multi interface (HTTP/2 multiplexing)
static CURL  *g_share_template = NULL; // template to clone options from
static struct curl_slist *g_hdrs = NULL;
static _Atomic int g_inflight = 0;

// simple easy-handle pool (LIFO)
typedef struct pool_node_t { CURL *easy; struct pool_node_t *next; } pool_node_t;
static pool_node_t *g_easy_pool = NULL;
static pthread_mutex_t g_pool_mtx = PTHREAD_MUTEX_INITIALIZER;

// ---------- config ----------
static char *g_url = NULL;
static char *g_query_escaped = NULL;
static char *g_api_key = NULL;
static char *g_service_uuid = NULL;
static int   g_http2 = 0;

// JSON prefix/suffix
static char *g_json_prefix = NULL;
static size_t g_json_prefix_len = 0;
static const char *JSON_SUFFIX = "}}";

// ---------- Endpoint registry ----------
typedef struct {
    char  *suffix;      // pre-escaped invariant suffix (ends with ,\"timestampMs\":\")
    size_t suffix_len;
    int    in_use;
} endpoint_entry;

static endpoint_entry g_endpoints[SFN_ENDPOINT_CAP];
static _Atomic int g_endpoint_count = 0;

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

static char *json_escape(const char *s) {
    const unsigned char *in = (const unsigned char*)s;
    size_t extra = 0;
    for (const unsigned char *p = in; *p; ++p) {
        switch (*p) {
            case '\\': case '"': case '\n': case '\r': case '\t': case '\b': case '\f':
                extra++; break;
            default:
                if (*p < 0x20) extra += 5; // \u00XX for other control chars
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
            case '\b': *o++='\\'; *o++='b';  break;
            case '\f': *o++='\\'; *o++='f';  break;
            default:
                if (*p < 0x20) {
                    // Unicode escape for rare control chars
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

static int build_prefix(void) {
    const char *p1 = "{\"query\":\"";
    const char *p2 = "\",\"variables\":{";
    const char *k1 = "\"apiKey\":\"";
    const char *k2 = "\",\"serviceUuid\":\"";

    size_t n = strlen(p1) + strlen(g_query_escaped) + strlen(p2)
             + strlen(k1) + strlen(g_api_key)
             + strlen(k2) + strlen(g_service_uuid) + 5;

    char *prefix = (char*)malloc(n);
    if (!prefix) return 0;

    char *o = prefix;
    o += sprintf(o, "%s%s%s", p1, g_query_escaped, p2);
    o += sprintf(o, "%s%s", k1, g_api_key);
    o += sprintf(o, "%s%s\"", k2, g_service_uuid);
    *o = '\0';

    g_json_prefix = prefix;
    g_json_prefix_len = (size_t)(o - prefix);
    return 1;
}

static size_t json_escape_inline(char *out, const char *in, size_t in_len) {
    char *o = out;
    for (size_t i = 0; i < in_len; ++i) {
        unsigned char c = (unsigned char)in[i];
        switch (c) {
            case '\\': *o++='\\'; *o++='\\'; break;
            case '"':  *o++='\\'; *o++='"';  break;
            default:
                if (c < 0x20) {
                    static const char hex[] = "0123456789abcdef";
                    *o++='\\'; *o++='u'; *o++='0'; *o++='0';
                    *o++=hex[c>>4]; *o++=hex[c&0xF];
                } else {
                    *o++ = (char)c;
                }
        }
    }
    return (size_t)(o - out);
}

static inline size_t max_escaped_size(size_t len) { return len * 6; }

// ---------- Endpoint registry ----------
static int make_endpoint_suffix(
    const char *line_e, const char *column_e,
    const char *name_e, const char *entrypoint_e, const char *route_e,
    char **out, size_t *out_len
) {
    const char *k1 = ",\"line\":\"";
    const char *k2 = "\",\"column\":\"";
    const char *k3 = "\",\"name\":\"";
    const char *k4 = "\",\"entrypoint\":\"";
    const char *k5 = "\",\"route\":\"";
    const char *k6 = "\",\"timestampMs\":\"";

    size_t n = strlen(k1)+strlen(line_e)
             + strlen(k2)+strlen(column_e)
             + strlen(k3)+strlen(name_e)
             + strlen(k4)+strlen(entrypoint_e)
             + strlen(k5)+strlen(route_e)
             + strlen(k6);

    char *buf = (char*)malloc(n + 1);
    if (!buf) return 0;
    char *o = buf;
    o += sprintf(o, "%s%s%s%s%s%s%s%s%s%s%s",
                 k1, line_e, k2, column_e, k3, name_e, k4, entrypoint_e, k5, route_e, k6);
    *o = 0;
    *out = buf;
    *out_len = (size_t)(o - buf);
    return 1;
}

static int register_endpoint_internal(
    const char *line, const char *column, const char *name, const char *entrypoint, const char *route
) {
    int idx = atomic_fetch_add_explicit(&g_endpoint_count, 1, memory_order_acq_rel);
    if (idx < 0 || idx >= SFN_ENDPOINT_CAP) return -1;

    char *line_e = json_escape(line);
    char *col_e  = json_escape(column);
    char *name_e = json_escape(name);
    char *ep_e   = json_escape(entrypoint);
    char *route_e = json_escape(route ? route : "");
    if (!line_e || !col_e || !name_e || !ep_e || !route_e) {
        free(line_e); free(col_e); free(name_e); free(ep_e); free(route_e);
        return -1;
    }
    char *suffix = NULL; size_t suffix_len = 0;
    if (!make_endpoint_suffix(line_e, col_e, name_e, ep_e, route_e, &suffix, &suffix_len)) {
        free(line_e); free(col_e); free(name_e); free(ep_e); free(route_e);
        return -1;
    }
    free(line_e); free(col_e); free(name_e); free(ep_e); free(route_e);

    g_endpoints[idx].suffix = suffix;
    g_endpoints[idx].suffix_len = suffix_len;
    g_endpoints[idx].in_use = 1;
    return idx;
}

// ---------- message helpers ----------
static inline void msg_free(sfn_msg_t *msg) {
    if (!msg) return;
    if (msg->type == SFN_MSG_WORK) {
        free(msg->data.work.session_id);
    } else if (msg->type == SFN_MSG_WORK_BODIES) {
        free(msg->data.work_bodies.session_id);
        free(msg->data.work_bodies.route);
        free(msg->data.work_bodies.query_params);
        free(msg->data.work_bodies.req_headers);
        free(msg->data.work_bodies.req_body);
        free(msg->data.work_bodies.resp_headers);
        free(msg->data.work_bodies.resp_body);
    } else if (msg->type == SFN_MSG_BODY) {
        free(msg->data.body.body);
    }
}

// ---------- overflow ops ----------
static inline void overflow_push(sfn_msg_t msg) {
    sfn_node_t *n = (sfn_node_t*)malloc(sizeof(sfn_node_t));
    if (!n) { msg_free(&msg); return; }
    n->msg = msg;
    sfn_node_t *old = atomic_load_explicit(&g_overflow_head, memory_order_relaxed);
    do { n->next = old; }
    while (!atomic_compare_exchange_weak_explicit(
        &g_overflow_head, &old, n, memory_order_release, memory_order_relaxed));

    pthread_mutex_lock(&g_cv_mtx);
    pthread_cond_signal(&g_cv);
    pthread_mutex_unlock(&g_cv_mtx);
}

static inline sfn_node_t* overflow_pop_all(void) {
    return atomic_exchange_explicit(&g_overflow_head, NULL, memory_order_acq_rel);
}

static inline void overflow_free_list(sfn_node_t* list) {
    while (list) {
        sfn_node_t* next = list->next;
        msg_free(&list->msg);
        free(list);
        list = next;
    }
}

// ---------- ring ops ----------
static inline size_t ring_count(void) {
    size_t h = atomic_load_explicit(&g_head, memory_order_acquire);
    size_t t = atomic_load_explicit(&g_tail, memory_order_acquire);
    return t - h;
}
static inline int ring_empty(void) { return ring_count() == 0; }

// PERFORMANCE: Lock-free CAS-based push (removes global contention point)
// Many producers can make forward progress concurrently without spinning
static int ring_try_push(sfn_msg_t msg) {
    for (;;) {
        size_t t = atomic_load_explicit(&g_tail, memory_order_relaxed);
        size_t h = atomic_load_explicit(&g_head, memory_order_acquire);

        if ((t - h) >= g_cap) {
            return 0; // full
        }

        // Try to claim slot t via CAS
        if (atomic_compare_exchange_weak_explicit(
                &g_tail, &t, t + 1, memory_order_acq_rel, memory_order_relaxed)) {

            int was_empty = (h == t);
            size_t idx = t % g_cap;
            g_ring[idx] = msg; // single writer for this idx (we own it after CAS succeeds)

            if (was_empty) {
                pthread_mutex_lock(&g_cv_mtx);
                pthread_cond_signal(&g_cv);
                pthread_mutex_unlock(&g_cv_mtx);
#if LIBCURL_VERSION_NUM >= 0x073E00  // 7.62.0+
                // Also wake the multi loop if it's sleeping (immediate response)
                if (g_multi) curl_multi_wakeup(g_multi);
#endif
            }
            return 1;
        }
        // else: lost race, retry
    }
}

static int ring_pop(sfn_msg_t *out_msg) {
    size_t h = atomic_load_explicit(&g_head, memory_order_relaxed);
    size_t t = atomic_load_explicit(&g_tail, memory_order_acquire);
    if (h == t) return 0;
    size_t idx = h % g_cap;
    *out_msg = g_ring[idx];
    // Clear for safety
    g_ring[idx].type = SFN_MSG_BODY;
    g_ring[idx].data.body.body = NULL;
    g_ring[idx].data.body.len = 0;
    atomic_store_explicit(&g_head, h + 1, memory_order_release);
    return 1;
}

// ---------- curl callbacks ----------
static size_t _sink_write(char *ptr, size_t size, size_t nmemb, void *userdata) {
    (void)ptr; (void)userdata; return size * nmemb;
}
static size_t _sink_header(char *ptr, size_t size, size_t nmemb, void *userdata) {
    (void)ptr; (void)userdata; return size * nmemb;
}

// ---------- easy-handle pool ----------
static CURL* pool_acquire_easy(void) {
    pthread_mutex_lock(&g_pool_mtx);
    pool_node_t *node = g_easy_pool;
    if (node) g_easy_pool = node->next;
    pthread_mutex_unlock(&g_pool_mtx);
    if (node) {
        CURL *e = node->easy;
        free(node);
        // PERFORMANCE: NO curl_easy_reset() - keep invariants intact!
        // This eliminates option reconfiguration churn (libcurl connection reuse becomes cheap)
        // Only per-message options (POSTFIELDS/SIZE/PRIVATE) are set in multi_add_message()
        return e;
    }
    // new handle
    CURL *e = curl_easy_init();
    if (!e) return NULL;
    curl_easy_setopt(e, CURLOPT_URL, g_url);
    curl_easy_setopt(e, CURLOPT_HTTPHEADER, g_hdrs);
    curl_easy_setopt(e, CURLOPT_WRITEFUNCTION, _sink_write);
    curl_easy_setopt(e, CURLOPT_HEADERFUNCTION, _sink_header);
#ifdef CURL_HTTP_VERSION_2TLS
    if (g_http2) curl_easy_setopt(e, CURLOPT_HTTP_VERSION, CURL_HTTP_VERSION_2TLS);
#endif
    curl_easy_setopt(e, CURLOPT_TCP_KEEPALIVE, 1L);
    curl_easy_setopt(e, CURLOPT_NOSIGNAL, 1L);
#ifdef TCP_NODELAY
    curl_easy_setopt(e, CURLOPT_TCP_NODELAY, 1L);
#endif
    return e;
}

static void pool_release_easy(CURL *e) {
    if (!e) return;
    pool_node_t *node = (pool_node_t*)malloc(sizeof(pool_node_t));
    if (!node) { curl_easy_cleanup(e); return; }
    node->easy = e;
    pthread_mutex_lock(&g_pool_mtx);
    node->next = g_easy_pool;
    g_easy_pool = node;
    pthread_mutex_unlock(&g_pool_mtx);
}

// ---------- JSON building (on background thread) ----------
static char* build_body_from_work(const char *session_id, size_t session_len, int endpoint_id, size_t *out_len) {
    if (endpoint_id < 0 || endpoint_id >= SFN_ENDPOINT_CAP) return NULL;
    if (!g_endpoints[endpoint_id].in_use) return NULL;

    // NOW get the timestamp (on background thread, not request path!)
    uint64_t tms = now_ms();
    char ts_buf[32];
    int ts_len = snprintf(ts_buf, sizeof(ts_buf), "%llu", (unsigned long long)tms);

    size_t sess_frag_max = 14 + max_escaped_size(session_len) + 1;
    size_t total_max = g_json_prefix_len + sess_frag_max
                     + g_endpoints[endpoint_id].suffix_len
                     + (size_t)ts_len + 2;

    char *body = (char*)malloc(total_max + 1);
    if (!body) return NULL;

    char *o = body;
    memcpy(o, g_json_prefix, g_json_prefix_len); o += g_json_prefix_len;
    memcpy(o, ",\"sessionId\":\"", 14); o += 14;
    o += json_escape_inline(o, session_id, session_len); *o++='"';
    memcpy(o, g_endpoints[endpoint_id].suffix, g_endpoints[endpoint_id].suffix_len);
    o += g_endpoints[endpoint_id].suffix_len;
    memcpy(o, ts_buf, (size_t)ts_len); o += ts_len;
    *o++ = '"'; memcpy(o, JSON_SUFFIX, 2); o += 2; *o = 0;

    *out_len = (size_t)(o - body);
    return body;
}

// Build JSON body with request/response headers and bodies (on background thread)
static char* build_body_from_work_with_bodies(
    const char *session_id, size_t session_len, int endpoint_id,
    const char *route, size_t route_len,
    const char *query_params, size_t query_params_len,
    const char *req_headers, size_t req_headers_len,
    const char *req_body, size_t req_body_len,
    const char *resp_headers, size_t resp_headers_len,
    const char *resp_body, size_t resp_body_len,
    size_t *out_len
) {
    if (endpoint_id < 0 || endpoint_id >= SFN_ENDPOINT_CAP) return NULL;
    if (!g_endpoints[endpoint_id].in_use) return NULL;

    // Get timestamp (on background thread)
    uint64_t tms = now_ms();
    char ts_buf[32];
    int ts_len = snprintf(ts_buf, sizeof(ts_buf), "%llu", (unsigned long long)tms);

    // Calculate max size (headers/bodies are already JSON-escaped)
    size_t sess_frag_max = 14 + max_escaped_size(session_len) + 1;
    size_t total_max = g_json_prefix_len + sess_frag_max
                     + g_endpoints[endpoint_id].suffix_len
                     + (size_t)ts_len;

    // Add space for route/query override fields (already escaped)
    if (route) total_max += 12 + route_len;  // ",\"route\":\""
    if (query_params) total_max += 18 + query_params_len;  // ",\"queryParams\":\""

    // Add space for request/response fields (already escaped, just need quotes and keys)
    if (req_headers) total_max += 20 + req_headers_len;  // ",\"requestHeaders\":\""
    if (req_body) total_max += 17 + req_body_len;        // ",\"requestBody\":\""
    if (resp_headers) total_max += 21 + resp_headers_len; // ",\"responseHeaders\":\""
    if (resp_body) total_max += 18 + resp_body_len;      // ",\"responseBody\":\""
    total_max += 10; // closing quotes and braces

    char *body = (char*)malloc(total_max + 1);
    if (!body) return NULL;

    char *o = body;
    memcpy(o, g_json_prefix, g_json_prefix_len); o += g_json_prefix_len;
    memcpy(o, ",\"sessionId\":\"", 14); o += 14;
    o += json_escape_inline(o, session_id, session_len); *o++='"';
    memcpy(o, g_endpoints[endpoint_id].suffix, g_endpoints[endpoint_id].suffix_len);
    o += g_endpoints[endpoint_id].suffix_len;
    memcpy(o, ts_buf, (size_t)ts_len); o += ts_len;
    *o++ = '"';

    // Add route override if present (already JSON-escaped) - this overrides the registered route in suffix
    if (route && route_len > 0) {
        memcpy(o, ",\"route\":\"", 10); o += 10;
        memcpy(o, route, route_len); o += route_len;
        *o++ = '"';
    }

    // Add query params if present (already JSON-escaped)
    if (query_params && query_params_len > 0) {
        memcpy(o, ",\"queryParams\":\"", 16); o += 16;
        memcpy(o, query_params, query_params_len); o += query_params_len;
        *o++ = '"';
    }

    // Add request/response fields if present (already JSON-escaped)
    if (req_headers && req_headers_len > 0) {
        memcpy(o, ",\"requestHeaders\":\"", 19); o += 19;
        memcpy(o, req_headers, req_headers_len); o += req_headers_len;
        *o++ = '"';
    }
    if (req_body && req_body_len > 0) {
        memcpy(o, ",\"requestBody\":\"", 16); o += 16;
        memcpy(o, req_body, req_body_len); o += req_body_len;
        *o++ = '"';
    }
    if (resp_headers && resp_headers_len > 0) {
        memcpy(o, ",\"responseHeaders\":\"", 20); o += 20;
        memcpy(o, resp_headers, resp_headers_len); o += resp_headers_len;
        *o++ = '"';
    }
    if (resp_body && resp_body_len > 0) {
        memcpy(o, ",\"responseBody\":\"", 17); o += 17;
        memcpy(o, resp_body, resp_body_len); o += resp_body_len;
        *o++ = '"';
    }

    memcpy(o, JSON_SUFFIX, 2); o += 2; *o = 0;

    *out_len = (size_t)(o - body);
    return body;
}

// ---------- multi helpers ----------
static void multi_add_message(char *body, size_t len) {
    CURL *e = pool_acquire_easy();
    if (!e) { free(body); return; }

    curl_easy_setopt(e, CURLOPT_POSTFIELDS, body);
    curl_easy_setopt(e, CURLOPT_POSTFIELDSIZE_LARGE, (curl_off_t)len);
    // keep pointer to free later
    curl_easy_setopt(e, CURLOPT_PRIVATE, body);

    CURLMcode mc = curl_multi_add_handle(g_multi, e);
    if (mc != CURLM_OK) {
        pool_release_easy(e);
        free(body);
        return;
    }
    atomic_fetch_add_explicit(&g_inflight, 1, memory_order_acq_rel);

#if LIBCURL_VERSION_NUM >= 0x073E00  // 7.62.0+
    // PERFORMANCE: Wake multi loop immediately (avoid 50ms sleep tail latency)
    curl_multi_wakeup(g_multi);
#endif
}

static void process_msg(sfn_msg_t *msg) {
    if (msg->type == SFN_MSG_WORK) {
        // Build JSON from work item (expensive work happens HERE, not in request path)
        size_t len = 0;
        char *body = build_body_from_work(
            msg->data.work.session_id,
            msg->data.work.session_len,
            msg->data.work.endpoint_id,
            &len
        );
        if (body) {
            multi_add_message(body, len);
        }
        free(msg->data.work.session_id); // done with session_id
    } else if (msg->type == SFN_MSG_WORK_BODIES) {
        // Build JSON with request/response bodies (expensive work on background thread)
        size_t len = 0;
        char *body = build_body_from_work_with_bodies(
            msg->data.work_bodies.session_id,
            msg->data.work_bodies.session_len,
            msg->data.work_bodies.endpoint_id,
            msg->data.work_bodies.route,
            msg->data.work_bodies.route_len,
            msg->data.work_bodies.query_params,
            msg->data.work_bodies.query_params_len,
            msg->data.work_bodies.req_headers,
            msg->data.work_bodies.req_headers_len,
            msg->data.work_bodies.req_body,
            msg->data.work_bodies.req_body_len,
            msg->data.work_bodies.resp_headers,
            msg->data.work_bodies.resp_headers_len,
            msg->data.work_bodies.resp_body,
            msg->data.work_bodies.resp_body_len,
            &len
        );
        if (body) {
            multi_add_message(body, len);
        }
        // Free all work_bodies fields
        free(msg->data.work_bodies.session_id);
        free(msg->data.work_bodies.route);
        free(msg->data.work_bodies.query_params);
        free(msg->data.work_bodies.req_headers);
        free(msg->data.work_bodies.req_body);
        free(msg->data.work_bodies.resp_headers);
        free(msg->data.work_bodies.resp_body);
    } else if (msg->type == SFN_MSG_BODY) {
        // Already built (legacy path)
        multi_add_message(msg->data.body.body, msg->data.body.len);
    }
}

static void multi_pump(void) {
    int running = 0;
    // Drive state machine
    curl_multi_perform(g_multi, &running);

    // Reap completions
    int msgs = 0;
    CURLMsg *msg;
    while ((msg = curl_multi_info_read(g_multi, &msgs))) {
        if (msg->msg == CURLMSG_DONE) {
            CURL *e = msg->easy_handle;
            char *body = NULL;
            curl_easy_getinfo(e, CURLINFO_PRIVATE, &body);
            curl_multi_remove_handle(g_multi, e);
            pool_release_easy(e);
            free(body);
            atomic_fetch_sub_explicit(&g_inflight, 1, memory_order_acq_rel);
        }
    }
}

// ---------- Network capture suppression ----------
// Define the telemetry guard to prevent recursive capture
// Each C extension is compiled separately, so we need our own thread-local copy
__thread int g_in_telemetry_send = 0;

// ---------- pthread cleanup handler for sender threads ----------
static void sender_cleanup(void *arg) {
    (void)arg;
    if (g_multi) {
        curl_multi_cleanup(g_multi);
        g_multi = NULL;
    }
}

// ---------- sender thread (multi + H2 multiplex) ----------
static void *sender_main(void *arg) {
    (void)arg;

    // CRITICAL: Set telemetry guard for this thread to prevent _sfteepreload.c from capturing our traffic
    // This sender thread only sends telemetry, so ALL its network traffic should be suppressed
    g_in_telemetry_send = 1;

    // Initialize per-thread curl_multi handle
    g_multi = curl_multi_init();
    if (!g_multi) return NULL;
#ifdef CURLPIPE_MULTIPLEX
    curl_multi_setopt(g_multi, CURLMOPT_PIPELINING, CURLPIPE_MULTIPLEX);
#endif
    curl_multi_setopt(g_multi, CURLMOPT_MAX_TOTAL_CONNECTIONS, 1L);
    curl_multi_setopt(g_multi, CURLMOPT_MAX_HOST_CONNECTIONS, 1L);

    // Register cleanup handler
    pthread_cleanup_push(sender_cleanup, NULL);

    while (atomic_load(&g_running)) {
        // Fill up inflight up to SFN_MAX_INFLIGHT
        while (atomic_load_explicit(&g_inflight, memory_order_acquire) < SFN_MAX_INFLIGHT) {
            sfn_msg_t msg;
            if (ring_pop(&msg)) {
                process_msg(&msg);
                continue;
            }
            // drain overflow into ring-ish order (reverse the LIFO)
            sfn_node_t *list = overflow_pop_all();
            if (list) {
                // reverse to approx FIFO
                sfn_node_t *rev = NULL;
                while (list) { sfn_node_t *n = list->next; list->next = rev; rev = list; list = n; }
                while (rev && atomic_load_explicit(&g_inflight, memory_order_acquire) < SFN_MAX_INFLIGHT) {
                    sfn_node_t *n = rev->next;
                    process_msg(&rev->msg);
                    free(rev);
                    rev = n;
                }
                // any leftover (shouldn't happen often) goes back to overflow
                while (rev) { sfn_node_t *n = rev->next; overflow_push(rev->msg); free(rev); rev = n; }
                continue;
            }
            break; // nothing to send
        }

        // Drive transfers & poll
        multi_pump();

        // Sleep a bit if idle; otherwise use multi_poll for efficient wake-up
        if (atomic_load_explicit(&g_inflight, memory_order_acquire) == 0 &&
            ring_empty() &&
            atomic_load_explicit(&g_overflow_head, memory_order_acquire) == NULL) {
            pthread_mutex_lock(&g_cv_mtx);
            if (atomic_load_explicit(&g_inflight, memory_order_acquire) == 0 &&
                ring_empty() &&
                atomic_load_explicit(&g_overflow_head, memory_order_acquire) == NULL &&
                atomic_load(&g_running)) {
                pthread_cond_wait(&g_cv, &g_cv_mtx);
            }
            pthread_mutex_unlock(&g_cv_mtx);
        } else {
            // PERFORMANCE: Short poll wait (5ms) - curl_multi_wakeup handles immediate nudges
            // This removes scheduler-scale latency without busy-spinning
            int numfds = 0;
#if LIBCURL_VERSION_NUM >= 0x074200  // curl >= 7.66.0
            curl_multi_poll(g_multi, NULL, 0, 5, &numfds);  // 5ms guard (was 50ms)
#else
            curl_multi_wait(g_multi, NULL, 0, 5, &numfds);
#endif
        }
    }
    // final drain
    while (atomic_load_explicit(&g_inflight, memory_order_acquire) > 0) {
        multi_pump();
        int nfds = 0;
#if LIBCURL_VERSION_NUM >= 0x074200  // curl >= 7.66.0
        curl_multi_poll(g_multi, NULL, 0, 10, &nfds);
#else
        curl_multi_wait(g_multi, NULL, 0, 10, &nfds);
#endif
    }

    pthread_cleanup_pop(1);
    return NULL;
}

// ---------- Python API ----------
static PyObject *py_init(PyObject *self, PyObject *args, PyObject *kw) {
    const char *url, *query, *api_key, *service_uuid;
    int http2 = 0;
    static char *kwlist[] = {"url","query","api_key","service_uuid","http2", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kw, "ssss|i",
        kwlist, &url, &query, &api_key, &service_uuid, &http2)) {
        Py_RETURN_FALSE;
    }
    if (g_running) Py_RETURN_TRUE;

    g_url = str_dup(url);
    g_query_escaped = json_escape_query(query);
    g_api_key = str_dup(api_key);
    g_service_uuid = str_dup(service_uuid);
    g_http2 = http2 ? 1 : 0;
    if (!g_url || !g_query_escaped || !g_api_key || !g_service_uuid) {
        Py_RETURN_FALSE;
    }
    if (!build_prefix()) { Py_RETURN_FALSE; }

    g_cap = SFN_RING_CAP;
    g_ring = (sfn_msg_t*)calloc(g_cap, sizeof(sfn_msg_t));
    if (!g_ring) { Py_RETURN_FALSE; }

    curl_global_init(CURL_GLOBAL_DEFAULT);

    // common headers (REMOVED: X-Sf3-IsTelemetryMessage - no longer needed with guard flag)
    g_hdrs = NULL;
    g_hdrs = curl_slist_append(g_hdrs, "Content-Type: application/json");
    g_hdrs = curl_slist_append(g_hdrs, "Expect:");  // PERFORMANCE: Disable 100-continue (avoids 200ms stalls)

    // NOTE: g_multi is now initialized per-thread in sender_main()
    // This allows multiple sender threads each with their own curl_multi instance

    // a template easy to copy options from (kept as reference; not added to multi)
    g_share_template = curl_easy_init();
    if (!g_share_template) { Py_RETURN_FALSE; }
    curl_easy_setopt(g_share_template, CURLOPT_URL, g_url);
    curl_easy_setopt(g_share_template, CURLOPT_HTTPHEADER, g_hdrs);
    curl_easy_setopt(g_share_template, CURLOPT_WRITEFUNCTION, _sink_write);
    curl_easy_setopt(g_share_template, CURLOPT_HEADERFUNCTION, _sink_header);
#ifdef CURL_HTTP_VERSION_2TLS
    if (g_http2) curl_easy_setopt(g_share_template, CURLOPT_HTTP_VERSION, CURL_HTTP_VERSION_2TLS);
#endif
    curl_easy_setopt(g_share_template, CURLOPT_TCP_KEEPALIVE, 1L);
    curl_easy_setopt(g_share_template, CURLOPT_NOSIGNAL, 1L);
#ifdef TCP_NODELAY
    curl_easy_setopt(g_share_template, CURLOPT_TCP_NODELAY, 1L);
#endif

    // Parse SF_NETWORKHOP_SENDER_THREADS environment variable (default: 2, max: 16)
    // NetworkHop expected to have decent volume, so default to 2 threads
    const char *num_threads_env = getenv("SF_NETWORKHOP_SENDER_THREADS");
    g_num_sender_threads = num_threads_env ? atoi(num_threads_env) : 2;
    if (g_num_sender_threads < 1) g_num_sender_threads = 1;
    if (g_num_sender_threads > MAX_SENDER_THREADS) g_num_sender_threads = MAX_SENDER_THREADS;

    atomic_store(&g_running, 1);

    // Start thread pool
    for (int i = 0; i < g_num_sender_threads; i++) {
        if (pthread_create(&g_sender_threads[i], NULL, sender_main, NULL) != 0) {
            atomic_store(&g_running, 0);
            // Join any threads that were already created
            for (int j = 0; j < i; j++) {
                pthread_join(g_sender_threads[j], NULL);
            }
            Py_RETURN_FALSE;
        }
    }

    Py_RETURN_TRUE;
}

static PyObject *py_register_endpoint(PyObject *self, PyObject *args, PyObject *kw) {
    const char *line, *column, *name, *entrypoint, *route = NULL;
    static char *kwlist[] = {"line","column","name","entrypoint","route", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kw, "ssss|z", kwlist,
                                     &line, &column, &name, &entrypoint, &route)) {
        return PyLong_FromLong(-1);
    }
    if (!g_running || g_json_prefix == NULL) {
        return PyLong_FromLong(-1);
    }
    int idx = register_endpoint_internal(line, column, name, entrypoint, route);
    return PyLong_FromLong(idx);
}

// generic (kept); producer path is GIL-free
static PyObject *py_networkhop(PyObject *self, PyObject *args, PyObject *kw) {
    const char *session_id, *line, *column, *name, *entrypoint;
    Py_ssize_t session_len = 0, line_len = 0, column_len = 0, name_len = 0, entrypoint_len = 0;
    static char *kwlist[] = {"session_id","line","column","name","entrypoint", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kw, "s#s#s#s#s#", kwlist,
                                     &session_id, &session_len,
                                     &line, &line_len,
                                     &column, &column_len,
                                     &name, &name_len,
                                     &entrypoint, &entrypoint_len)) {
        Py_RETURN_NONE;
    }
    if (!g_running || g_json_prefix == NULL) Py_RETURN_NONE;

    char *body = NULL; size_t len = 0;

    Py_BEGIN_ALLOW_THREADS
    // Build the full body
    {
        uint64_t tms = now_ms();
        char ts_buf[32];
        int ts_len = snprintf(ts_buf, sizeof(ts_buf), "%llu", (unsigned long long)tms);

        size_t sess_frag_max = 14 + max_escaped_size((size_t)session_len) + 1;
        size_t max_len = g_json_prefix_len + sess_frag_max + 200
                       + max_escaped_size((size_t)line_len)
                       + max_escaped_size((size_t)column_len)
                       + max_escaped_size((size_t)name_len)
                       + max_escaped_size((size_t)entrypoint_len)
                       + (size_t)ts_len + 2;

        body = (char*)malloc(max_len + 1);
        if (body) {
            char *o = body;
            memcpy(o, g_json_prefix, g_json_prefix_len); o += g_json_prefix_len;
            memcpy(o, ",\"sessionId\":\"", 14); o += 14;
            o += json_escape_inline(o, session_id, (size_t)session_len); *o++='"';

            memcpy(o, ",\"line\":\"", 10); o += 10; o += json_escape_inline(o, line, (size_t)line_len);
            memcpy(o, "\",\"column\":\"", 12); o += 12; o += json_escape_inline(o, column, (size_t)column_len);
            memcpy(o, "\",\"name\":\"", 10); o += 10; o += json_escape_inline(o, name, (size_t)name_len);
            memcpy(o, "\",\"entrypoint\":\"", 16); o += 16; o += json_escape_inline(o, entrypoint, (size_t)entrypoint_len);

            memcpy(o, "\",\"timestampMs\":\"", 17); o += 17;
            memcpy(o, ts_buf, (size_t)ts_len); o += ts_len;
            *o++ = '"'; memcpy(o, JSON_SUFFIX, 2); o += 2; *o = 0;

            len = (size_t)(o - body);

            sfn_msg_t msg = { .type = SFN_MSG_BODY, .data.body = { .body = body, .len = len } };
            if (!ring_try_push(msg)) overflow_push(msg);
        }
    }
    Py_END_ALLOW_THREADS

    Py_RETURN_NONE;
}

// ULTRA-FAST PATH: Zero-copy - just queue the pointer, background thread copies
// This achieves TRUE async: only atomic queue operation on hot path (~1µs)
static PyObject *py_networkhop_fast(PyObject *self, PyObject *args, PyObject *kw) {
    const char *session_id; Py_ssize_t session_len = 0; int endpoint_id = -1;
    static char *kwlist[] = {"session_id","endpoint_id", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kw, "s#i", kwlist,
                                     &session_id, &session_len, &endpoint_id)) {
        Py_RETURN_NONE;
    }
    if (!g_running || g_json_prefix == NULL) Py_RETURN_NONE;
    if (endpoint_id < 0 || endpoint_id >= SFN_ENDPOINT_CAP) Py_RETURN_NONE;
    if (!g_endpoints[endpoint_id].in_use) Py_RETURN_NONE;

    // CRITICAL OPTIMIZATION: Do the malloc+memcpy in a SINGLE atomic operation
    // to minimize time holding the GIL. This is faster than releasing GIL,
    // doing malloc, then reacquiring.
    size_t len = (size_t)session_len;
    char *sid_copy = (char*)malloc(len + 1);
    if (!sid_copy) Py_RETURN_NONE;

    memcpy(sid_copy, session_id, len);
    sid_copy[len] = 0;

    sfn_msg_t msg = {
        .type = SFN_MSG_WORK,
        .data.work = {
            .session_id = sid_copy,
            .session_len = len,
            .endpoint_id = endpoint_id
        }
    };

    // Release GIL for queue operation (this is the only blocking part)
    int pushed = 0;
    Py_BEGIN_ALLOW_THREADS
    pushed = ring_try_push(msg);
    if (!pushed) overflow_push(msg);
    Py_END_ALLOW_THREADS

    Py_RETURN_NONE;
}

// Helper: concatenate dict of header key-value pairs or list of bytes chunks (with GIL held)
// Returns malloced JSON-escaped string
static char* extract_and_escape_data(PyObject *obj, size_t *out_len) {
    if (!obj || obj == Py_None) {
        *out_len = 0;
        return NULL;
    }

    // Handle dict (headers) - format as JSON object string
    if (PyDict_Check(obj)) {
        // Build JSON object: {"key":"value","key2":"value2"}
        PyObject *items = PyDict_Items(obj);
        if (!items) { *out_len = 0; return NULL; }

        Py_ssize_t nitems = PyList_Size(items);
        if (nitems == 0) {
            Py_DECREF(items);
            *out_len = 0;
            return NULL;
        }

        // Build JSON object (will be double-escaped: once here, once when inserted into variables)
        // Estimate size: {"key":"value","key2":"value2"}
        size_t total = 2; // {}
        for (Py_ssize_t i = 0; i < nitems; i++) {
            PyObject *pair = PyList_GetItem(items, i);
            PyObject *key = PyTuple_GetItem(pair, 0);
            PyObject *val = PyTuple_GetItem(pair, 1);
            const char *key_str = PyUnicode_AsUTF8(key);
            const char *val_str = PyUnicode_AsUTF8(val);
            if (key_str && val_str) {
                // "key":"value", (worst case: double length for escaping)
                total += strlen(key_str) * 2 + strlen(val_str) * 2 + 6; // quotes, colon, comma
            }
        }

        char *result = (char*)malloc(total * 2 + 1); // *2 for extra safety
        if (!result) {
            Py_DECREF(items);
            *out_len = 0;
            return NULL;
        }

        char *o = result;
        *o++ = '{';
        int first = 1;
        for (Py_ssize_t i = 0; i < nitems; i++) {
            PyObject *pair = PyList_GetItem(items, i);
            PyObject *key = PyTuple_GetItem(pair, 0);
            PyObject *val = PyTuple_GetItem(pair, 1);

            // Convert key to string (keys are always strings in JSON)
            const char *key_str = NULL;
            PyObject *key_str_obj = NULL;
            if (PyUnicode_Check(key)) {
                key_str = PyUnicode_AsUTF8(key);
            } else {
                key_str_obj = PyObject_Str(key);
                if (key_str_obj) {
                    key_str = PyUnicode_AsUTF8(key_str_obj);
                }
            }

            if (!key_str) {
                Py_XDECREF(key_str_obj);
                if (PyErr_Occurred()) PyErr_Clear();
                continue;
            }

            if (!first) *o++ = ',';
            first = 0;

            // Escape key (always quoted)
            *o++ = '"';
            char *key_esc = json_escape(key_str);
            if (key_esc) {
                size_t klen = strlen(key_esc);
                memcpy(o, key_esc, klen);
                o += klen;
                free(key_esc);
            }
            *o++ = '"';
            *o++ = ':';

            // Handle value based on type (preserve JSON types)
            if (val == Py_None) {
                // null
                memcpy(o, "null", 4);
                o += 4;
            } else if (PyBool_Check(val)) {
                // true or false
                if (val == Py_True) {
                    memcpy(o, "true", 4);
                    o += 4;
                } else {
                    memcpy(o, "false", 5);
                    o += 5;
                }
            } else if (PyLong_Check(val)) {
                // integer (no quotes)
                long num = PyLong_AsLong(val);
                if (num == -1 && PyErr_Occurred()) {
                    PyErr_Clear();
                    memcpy(o, "null", 4);
                    o += 4;
                } else {
                    char buf[32];
                    int len = snprintf(buf, sizeof(buf), "%ld", num);
                    memcpy(o, buf, len);
                    o += len;
                }
            } else if (PyFloat_Check(val)) {
                // float (no quotes)
                double num = PyFloat_AsDouble(val);
                if (num == -1.0 && PyErr_Occurred()) {
                    PyErr_Clear();
                    memcpy(o, "null", 4);
                    o += 4;
                } else {
                    char buf[64];
                    int len = snprintf(buf, sizeof(buf), "%.17g", num);
                    memcpy(o, buf, len);
                    o += len;
                }
            } else {
                // String or other type - convert to string and quote
                const char *val_str = NULL;
                PyObject *val_str_obj = NULL;
                if (PyUnicode_Check(val)) {
                    val_str = PyUnicode_AsUTF8(val);
                } else {
                    val_str_obj = PyObject_Str(val);
                    if (val_str_obj) {
                        val_str = PyUnicode_AsUTF8(val_str_obj);
                    }
                }

                if (val_str) {
                    *o++ = '"';
                    char *val_esc = json_escape(val_str);
                    if (val_esc) {
                        size_t vlen = strlen(val_esc);
                        memcpy(o, val_esc, vlen);
                        o += vlen;
                        free(val_esc);
                    }
                    *o++ = '"';
                } else {
                    // Fallback to null if conversion failed
                    memcpy(o, "null", 4);
                    o += 4;
                }

                Py_XDECREF(val_str_obj);
            }

            // Clean up temporary key string object
            Py_XDECREF(key_str_obj);

            // Clear any exceptions that occurred during conversion
            if (PyErr_Occurred()) {
                PyErr_Clear();
            }
        }
        *o++ = '}';
        *o = '\0';
        Py_DECREF(items);

        *out_len = (size_t)(o - result);
        return result;
    }

    // Handle list of bytes (body chunks)
    if (PyList_Check(obj)) {
        Py_ssize_t nchunks = PyList_Size(obj);
        if (nchunks == 0) {
            *out_len = 0;
            return NULL;
        }

        // First pass: calculate total size
        size_t total = 0;
        for (Py_ssize_t i = 0; i < nchunks; i++) {
            PyObject *chunk = PyList_GetItem(obj, i);
            if (PyBytes_Check(chunk)) {
                total += (size_t)PyBytes_Size(chunk);
            }
        }

        if (total == 0) {
            *out_len = 0;
            return NULL;
        }

        // Allocate raw buffer
        char *raw = (char*)malloc(total + 1);
        if (!raw) {
            *out_len = 0;
            return NULL;
        }

        // Second pass: concatenate
        char *o = raw;
        for (Py_ssize_t i = 0; i < nchunks; i++) {
            PyObject *chunk = PyList_GetItem(obj, i);
            if (PyBytes_Check(chunk)) {
                char *data = PyBytes_AsString(chunk);
                if (!data) {
                    PyErr_Clear();  // Clear exception and skip this chunk
                    continue;
                }
                Py_ssize_t len = PyBytes_Size(chunk);
                memcpy(o, data, (size_t)len);
                o += len;
            }
        }
        *o = '\0';

        // JSON-escape
        char *escaped = json_escape(raw);
        free(raw);

        if (escaped) {
            *out_len = strlen(escaped);
            return escaped;
        }
        *out_len = 0;
        return NULL;
    }

    // Handle bytes
    if (PyBytes_Check(obj)) {
        char *data = PyBytes_AsString(obj);
        if (!data) {
            PyErr_Clear();  // Clear exception
            *out_len = 0;
            return NULL;
        }
        Py_ssize_t len = PyBytes_Size(obj);
        char *escaped = json_escape(data);
        if (escaped) {
            *out_len = strlen(escaped);
            return escaped;
        }
        *out_len = 0;
        return NULL;
    }

    // Handle string
    if (PyUnicode_Check(obj)) {
        const char *str = PyUnicode_AsUTF8(obj);
        if (str) {
            char *escaped = json_escape(str);
            if (escaped) {
                *out_len = strlen(escaped);
                return escaped;
            }
        } else {
            // Clear exception from PyUnicode_AsUTF8 (invalid UTF-8 string)
            PyErr_Clear();
        }
        *out_len = 0;
        return NULL;
    }

    *out_len = 0;
    return NULL;
}

// Ultra-fast body capture with GIL-released consolidation
static PyObject *py_networkhop_with_bodies(PyObject *self, PyObject *args, PyObject *kw) {
    const char *session_id; Py_ssize_t session_len = 0;
    int endpoint_id = -1;
    const char *raw_path = NULL;
    const char *raw_query_string = NULL; Py_ssize_t raw_query_len = 0;
    PyObject *req_headers_obj = NULL, *req_body_obj = NULL;
    PyObject *resp_headers_obj = NULL, *resp_body_obj = NULL;

    static char *kwlist[] = {"session_id", "endpoint_id", "raw_path", "raw_query_string",
                             "request_headers", "request_body",
                             "response_headers", "response_body", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kw, "s#i|zy#OOOO", kwlist,
                                     &session_id, &session_len, &endpoint_id,
                                     &raw_path,
                                     &raw_query_string, &raw_query_len,
                                     &req_headers_obj, &req_body_obj,
                                     &resp_headers_obj, &resp_body_obj)) {
        return NULL;  // PyArg_ParseTupleAndKeywords sets exception on failure
    }

    if (!g_running || g_json_prefix == NULL) Py_RETURN_NONE;
    if (endpoint_id < 0 || endpoint_id >= SFN_ENDPOINT_CAP) Py_RETURN_NONE;
    if (!g_endpoints[endpoint_id].in_use) Py_RETURN_NONE;

    // Copy session_id with GIL held (small, fast)
    size_t len = (size_t)session_len;
    char *sid_copy = (char*)malloc(len + 1);
    if (!sid_copy) Py_RETURN_NONE;
    memcpy(sid_copy, session_id, len);
    sid_copy[len] = 0;

    // JSON-escape raw_path if provided (it's a string)
    char *route_escaped = NULL;
    size_t route_len = 0;
    if (raw_path) {
        route_escaped = json_escape(raw_path);
        if (route_escaped) route_len = strlen(route_escaped);
    }

    // Decode and JSON-escape raw_query_string if provided (it's bytes)
    char *query_params_escaped = NULL;
    size_t query_params_len = 0;
    if (raw_query_string && raw_query_len > 0) {
        // Decode bytes to string (UTF-8)
        char *query_str = (char*)malloc((size_t)raw_query_len + 1);
        if (query_str) {
            memcpy(query_str, raw_query_string, (size_t)raw_query_len);
            query_str[raw_query_len] = 0;

            // JSON-escape it
            query_params_escaped = json_escape(query_str);
            if (query_params_escaped) query_params_len = strlen(query_params_escaped);

            free(query_str);
        }
    }

    // Extract and JSON-escape request/response data (with GIL held)
    size_t req_headers_len = 0, req_body_len = 0, resp_headers_len = 0, resp_body_len = 0;
    char *req_headers = extract_and_escape_data(req_headers_obj, &req_headers_len);
    char *req_body = extract_and_escape_data(req_body_obj, &req_body_len);
    char *resp_headers = extract_and_escape_data(resp_headers_obj, &resp_headers_len);
    char *resp_body = extract_and_escape_data(resp_body_obj, &resp_body_len);

    // Check if any Python exceptions occurred during extraction
    if (PyErr_Occurred()) {
        // Clean up allocated memory
        free(sid_copy);
        free(route_escaped);
        free(query_params_escaped);
        free(req_headers);
        free(req_body);
        free(resp_headers);
        free(resp_body);
        return NULL;  // Propagate the exception
    }

    // Build message (all data copied, GIL can be released for queue)
    sfn_msg_t msg = {
        .type = SFN_MSG_WORK_BODIES,
        .data.work_bodies = {
            .session_id = sid_copy,
            .session_len = len,
            .endpoint_id = endpoint_id,
            .route = route_escaped,
            .route_len = route_len,
            .query_params = query_params_escaped,
            .query_params_len = query_params_len,
            .req_headers = req_headers,
            .req_headers_len = req_headers_len,
            .req_body = req_body,
            .req_body_len = req_body_len,
            .resp_headers = resp_headers,
            .resp_headers_len = resp_headers_len,
            .resp_body = resp_body,
            .resp_body_len = resp_body_len
        }
    };

    // Release GIL for queue operation
    int pushed = 0;
    Py_BEGIN_ALLOW_THREADS
    pushed = ring_try_push(msg);
    if (!pushed) overflow_push(msg);
    Py_END_ALLOW_THREADS

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

    // NOTE: g_multi is now per-thread and cleaned by pthread_cleanup_push in sender_main()
    // No need to clean it here

    // cleanup pool
    pthread_mutex_lock(&g_pool_mtx);
    while (g_easy_pool) {
        pool_node_t *n = g_easy_pool; g_easy_pool = n->next;
        curl_easy_cleanup(n->easy);
        free(n);
    }
    pthread_mutex_unlock(&g_pool_mtx);

    if (g_share_template) { curl_easy_cleanup(g_share_template); g_share_template = NULL; }
    if (g_hdrs) { curl_slist_free_all(g_hdrs); g_hdrs = NULL; }

    curl_global_cleanup();

    free(g_url); g_url=NULL;
    free(g_query_escaped); g_query_escaped=NULL;
    free(g_json_prefix);   g_json_prefix=NULL;
    free(g_api_key); g_api_key=NULL;
    free(g_service_uuid); g_service_uuid=NULL;

    for (int i = 0; i < SFN_ENDPOINT_CAP; ++i) {
        if (g_endpoints[i].in_use) {
            free(g_endpoints[i].suffix);
            g_endpoints[i].suffix = NULL;
            g_endpoints[i].suffix_len = 0;
            g_endpoints[i].in_use = 0;
        }
    }
    atomic_store(&g_endpoint_count, 0);

    if (g_ring) {
        sfn_msg_t msg;
        while (ring_pop(&msg)) {
            msg_free(&msg);
        }
        free(g_ring); g_ring=NULL;
    }
    sfn_node_t *list = overflow_pop_all();
    while (list) {
        sfn_node_t *next = list->next;
        msg_free(&list->msg);
        free(list);
        list = next;
    }

    Py_RETURN_NONE;
}

static PyMethodDef SFNetworkHopMethods[] = {
    {"init",                  (PyCFunction)py_init,                  METH_VARARGS | METH_KEYWORDS, "Init networkhop and start sender"},
    {"register_endpoint",     (PyCFunction)py_register_endpoint,     METH_VARARGS | METH_KEYWORDS, "Register endpoint invariants -> endpoint_id"},
    {"networkhop",            (PyCFunction)py_networkhop,            METH_VARARGS | METH_KEYWORDS, "Send network hop (generic)"},
    {"networkhop_fast",       (PyCFunction)py_networkhop_fast,       METH_VARARGS | METH_KEYWORDS, "Send network hop (fast, uses endpoint_id)"},
    {"networkhop_with_bodies",(PyCFunction)py_networkhop_with_bodies,METH_VARARGS | METH_KEYWORDS, "Send network hop with optional body chunks (GIL-released)"},
    {"shutdown",              (PyCFunction)py_shutdown,              METH_NOARGS,                   "Shutdown sender and free state"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef sfnetworkhopmodule = {
    PyModuleDef_HEAD_INIT,
    "_sfnetworkhop",
    "sf_veritas ultra-fast network hop capture",
    -1,
    SFNetworkHopMethods
};

PyMODINIT_FUNC PyInit__sfnetworkhop(void) {
    return PyModule_Create(&sfnetworkhopmodule);
}
