// sf_veritas/_sffastnetworkrequest.c
// ULTRA-FAST OUTBOUND NETWORK REQUEST TELEMETRY
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
#include <unistd.h>   // dup/close
#ifdef __x86_64__
#include <immintrin.h> // _mm_pause
#endif

// ===================== Thread-local guard flag ====================
// CRITICAL: Prevents _sfteepreload.c from capturing our telemetry traffic
__attribute__((visibility("default")))
__thread int g_in_telemetry_send = 0;

// ============================= Tunables =============================
#ifndef SFF_RING_CAP
#define SFF_RING_CAP 262144  // power-of-two; raise if you see drops
#endif

// Trim payloads to protect producer latency
#ifndef SFF_MAX_REQ_BODY
#define SFF_MAX_REQ_BODY 8192
#endif
#ifndef SFF_MAX_RESP_BODY
#define SFF_MAX_RESP_BODY 0   // 0 = don't capture response body in this path
#endif
#ifndef SFF_MAX_HEADER_VALUE
#define SFF_MAX_HEADER_VALUE 4096
#endif

#ifndef SFF_MAX_INFLIGHT
#define SFF_MAX_INFLIGHT 32   // concurrent in-flight posts
#endif
#ifndef SFF_POLL_TIMEOUT_MS
#define SFF_POLL_TIMEOUT_MS 10
#endif

// ============================= Types ==============================
// NEW: Simplified message type - just stores the ready-to-send HTTP body (like _sffastlog.c!)
typedef struct {
    char  *body;   // malloc'd HTTP JSON body (READY TO SEND)
    size_t len;
} sfnr_msg_t;

// ======================= Global Module State ======================
static sfnr_msg_t    *g_ring = NULL;
static size_t         g_cap  = 0;
static _Atomic size_t g_head = 0; // consumer index
static _Atomic size_t g_tail = 0; // producer index

// push lock (very short); we signal the cond only on empty->nonempty transition
static atomic_flag g_push_lock = ATOMIC_FLAG_INIT;

// wake/sleep
static pthread_mutex_t g_cv_mtx = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t  g_cv     = PTHREAD_COND_INITIALIZER;
static _Atomic int     g_running = 0;

// Thread pool for parallel sending (configurable via SF_FASTNETWORKREQUEST_SENDER_THREADS)
#define MAX_SENDER_THREADS 16
static pthread_t g_sender_threads[MAX_SENDER_THREADS];
static int g_num_sender_threads = 0;
static int g_configured_sender_threads = 1;  // Default: 1 thread

// curl state (per-thread)
__thread CURL *g_telem_curl = NULL;
static struct curl_slist *g_hdrs = NULL;

// config (owned strings)
static char *g_url = NULL;
static char *g_query_escaped = NULL; // escaped GraphQL "query"
static char *g_api_key = NULL;
static char *g_service_uuid = NULL;
static char *g_library = NULL;
static char *g_version = NULL;
static int   g_http2 = 1;

// JSON prefix: {"query":"<q>","variables":{"apiKey":"...","serviceUuid":"...","library":"...","version":"...
static char *g_json_prefix = NULL;
static const char *JSON_SUFFIX = "}}";

// ContextVar for trace_id (borrowed reference - don't decref!)
static PyObject *g_trace_id_ctx = NULL;

// Ultra-fast UUID generation (atomic counter + process ID)
static _Atomic uint64_t g_uuid_counter = 0;
static uint32_t g_process_id = 0;

// ============================ Helpers =============================
static inline uint64_t now_ms(void) {
#if defined(CLOCK_REALTIME_COARSE)
    struct timespec ts; clock_gettime(CLOCK_REALTIME_COARSE, &ts);
    return ((uint64_t)ts.tv_sec) * 1000ULL + (uint64_t)(ts.tv_nsec / 1000000ULL);
#else
    struct timeval tv; gettimeofday(&tv, NULL);
    return ((uint64_t)tv.tv_sec) * 1000ULL + (uint64_t)(tv.tv_usec / 1000ULL);
#endif
}

static char *str_dup(const char *s) {
    if (!s) return NULL;
    size_t n = strlen(s);
    char *p = (char*)malloc(n + 1);
    if (!p) return NULL;
    memcpy(p, s, n); p[n] = 0;
    return p;
}

// Ultra-fast UUID generation (< 5ns) - atomic counter based, NOT cryptographically random
// Format: 8 hex chars (pid) + 16 hex chars (timestamp_ms) + 8 hex chars (counter)
// Example: "12ab34cd-0000018d12345678-00000001"
static inline void fast_uuid(char *buf) {
    uint64_t counter = atomic_fetch_add_explicit(&g_uuid_counter, 1, memory_order_relaxed);
    uint64_t ts = now_ms();

    // Format: PPPPPPPP-TTTTTTTTTTTTTTTT-CCCCCCCC (32 chars + 2 dashes = 34 chars + null)
    static const char hex[] = "0123456789abcdef";
    char *p = buf;

    // Process ID (8 hex chars)
    uint32_t pid = g_process_id;
    for (int i = 7; i >= 0; i--) {
        p[i] = hex[pid & 0xF];
        pid >>= 4;
    }
    p += 8;
    *p++ = '-';

    // Timestamp (16 hex chars)
    for (int i = 15; i >= 0; i--) {
        p[i] = hex[ts & 0xF];
        ts >>= 4;
    }
    p += 16;
    *p++ = '-';

    // Counter (8 hex chars)
    for (int i = 7; i >= 0; i--) {
        p[i] = hex[counter & 0xF];
        counter >>= 4;
    }
    p += 8;
    *p = '\0';
}

// Extract parent request ID from trace_id string
// trace_id format: "NONSESSION_APPLOGS-v3/api_key/uuid"
// Returns pointer to the UUID part (after last '/'), or NULL if not found
static inline const char *extract_parent_request_id(const char *trace_id) {
    if (!trace_id) return NULL;
    const char *last_slash = strrchr(trace_id, '/');
    return last_slash ? (last_slash + 1) : NULL;
}

// --- JSON escaping that writes into a growing buffer (no per-field mallocs) ---
typedef struct {
    char *buf; size_t len; size_t cap;
} sb_t;

static int sb_grow(sb_t *sb, size_t need) {
    if (sb->len + need <= sb->cap) return 1;
    size_t ncap = sb->cap ? sb->cap : 1024;
    while (ncap < sb->len + need) ncap <<= 1;
    char *nb = (char*)realloc(sb->buf, ncap);
    if (!nb) return 0;
    sb->buf = nb; sb->cap = ncap; return 1;
}

static int sb_putc(sb_t *sb, char c) {
    if (!sb_grow(sb, 1)) return 0;
    sb->buf[sb->len++] = c; return 1;
}
static int sb_puts(sb_t *sb, const char *s, size_t n) {
    if (!sb_grow(sb, n)) return 0;
    memcpy(sb->buf + sb->len, s, n); sb->len += n; return 1;
}

static int sb_put_escaped_json_string(sb_t *sb, const char *s) {
    // write a JSON string with quotes and escapes
    if (!sb_putc(sb, '"')) return 0;
    for (const unsigned char *p = (const unsigned char*)s; *p; ++p) {
        unsigned char c = *p;
        if (c == '"' || c == '\\') {
            if (!sb_grow(sb, 2)) return 0;
            sb->buf[sb->len++]='\\'; sb->buf[sb->len++]=c;
        } else if (c < 0x20) {
            // \u00XX
            if (!sb_grow(sb, 6)) return 0;
            static const char hex[]="0123456789abcdef";
            sb->buf[sb->len++]='\\'; sb->buf[sb->len++]='u';
            sb->buf[sb->len++]='0';  sb->buf[sb->len++]='0';
            sb->buf[sb->len++]=hex[c>>4];
            sb->buf[sb->len++]=hex[c&0xF];
        } else {
            if (!sb_putc(sb,(char)c)) return 0;
        }
    }
    return sb_putc(sb, '"');
}

static int sb_put_uint(sb_t *sb, uint64_t v) {
    // max 20 digits
    char tmp[32]; int n = 0;
    if (v == 0) { return sb_putc(sb, '0'); }
    while (v) { tmp[n++] = (char)('0' + (v % 10)); v /= 10; }
    if (!sb_grow(sb, (size_t)n)) return 0;
    for (int i=n-1;i>=0;--i) sb->buf[sb->len++]=tmp[i];
    return 1;
}

static int sb_put_int(sb_t *sb, int v) {
    if (v < 0) { if (!sb_putc(sb,'-')) return 0; return sb_put_uint(sb, (uint64_t)(-(int64_t)v)); }
    return sb_put_uint(sb, (uint64_t)v);
}

// =========================== Ring Buffer ==========================
static inline size_t ring_count(void) {
    size_t h = atomic_load_explicit(&g_head, memory_order_acquire);
    size_t t = atomic_load_explicit(&g_tail, memory_order_acquire);
    return t - h;
}
static inline int ring_empty(void) { return ring_count() == 0; }

// NEW: Simplified ring push - stores ready-to-send body (like _sffastlog.c!)
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

// ========================= CURL Callbacks =========================
static size_t _sink_write(char *ptr, size_t size, size_t nmemb, void *userdata) {
    (void)ptr; (void)userdata; return size * nmemb;
}
static size_t _sink_header(char *ptr, size_t size, size_t nmemb, void *userdata) {
    (void)ptr; (void)userdata; return size * nmemb;
}

// ========================= JSON Escape (needed by builder) ===========
// escape for generic JSON string fields
static char *json_escape(const char *s) {
    if (!s) return str_dup("");
    const unsigned char *in = (const unsigned char*)s;
    size_t extra = 0;
    for (const unsigned char *p = in; *p; ++p) {
        switch (*p) {
            case '\\': case '"': extra++; break;
            default:
                if (*p < 0x20) extra += 5; // \u00XX
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

// ========================= JSON builder (PRODUCER THREAD - RELEASED GIL) ===========
// NEW: Build complete GraphQL body in producer thread (ZERO GIL contention!)
// This is the KEY OPTIMIZATION from _sffastlog.c (lines 189-233)
static int build_body_networkhop(
    const char *trace_id,
    const char *url,
    const char *method,
    int status,
    int ok,
    uint64_t ts_start,
    uint64_t ts_end,
    const char *req_body, size_t req_len,
    const char *resp_body, size_t resp_len,
    const char *req_hdrs_json,
    const char *resp_hdrs_json,
    char **out_body,
    size_t *out_len
) {
    // Build ,"event":{...} - inputs are safe pointers from Python
    sb_t sb = {0};
    if (!sb_puts(&sb, g_json_prefix, strlen(g_json_prefix))) goto fail;
    if (!sb_puts(&sb, ",\"event\":{", 10)) goto fail;
    if (!sb_puts(&sb, "\"traceId\":", 10)) goto fail;
    if (!sb_put_escaped_json_string(&sb, trace_id ? trace_id : "")) goto fail;
    if (!sb_puts(&sb, ",\"url\":", 8)) goto fail;
    if (!sb_put_escaped_json_string(&sb, url ? url : "")) goto fail;
    if (!sb_puts(&sb, ",\"method\":", 11)) goto fail;
    if (!sb_put_escaped_json_string(&sb, method ? method : "")) goto fail;
    if (!sb_puts(&sb, ",\"status\":", 11)) goto fail;
    if (!sb_put_int(&sb, status)) goto fail;
    if (!sb_puts(&sb, ",\"ok\":", 6)) goto fail;
    if (!sb_puts(&sb, ok ? "true" : "false", ok ? 4 : 5)) goto fail;
    if (!sb_puts(&sb, ",\"timestampStartMs\":", 21)) goto fail;
    if (!sb_put_uint(&sb, ts_start)) goto fail;
    if (!sb_puts(&sb, ",\"timestampEndMs\":", 19)) goto fail;
    if (!sb_put_uint(&sb, ts_end)) goto fail;

    // Headers (already JSON strings from Python orjson!)
    if (!sb_puts(&sb, ",\"requestHeaders\":", 19)) goto fail;
    if (req_hdrs_json && req_hdrs_json[0]) {
        if (!sb_puts(&sb, req_hdrs_json, strlen(req_hdrs_json))) goto fail;
    } else {
        if (!sb_puts(&sb, "{}", 2)) goto fail;
    }

    if (!sb_puts(&sb, ",\"responseHeaders\":", 20)) goto fail;
    if (resp_hdrs_json && resp_hdrs_json[0]) {
        if (!sb_puts(&sb, resp_hdrs_json, strlen(resp_hdrs_json))) goto fail;
    } else {
        if (!sb_puts(&sb, "{}", 2)) goto fail;
    }

    // Bodies (escaped)
    if (!sb_puts(&sb, ",\"requestBody\":", 15)) goto fail;
    if (req_body && req_len) {
        char *tmp = (char*)malloc(req_len + 1);
        if (tmp) {
            memcpy(tmp, req_body, req_len); tmp[req_len]=0;
            sb_put_escaped_json_string(&sb, tmp);
            free(tmp);
        } else {
            sb_put_escaped_json_string(&sb, "");
        }
    } else {
        if (!sb_put_escaped_json_string(&sb, "")) goto fail;
    }

#if SFF_MAX_RESP_BODY > 0
    if (!sb_puts(&sb, ",\"responseBody\":", 16)) goto fail;
    if (resp_body && resp_len) {
        char *tmp2 = (char*)malloc(resp_len + 1);
        if (tmp2) {
            memcpy(tmp2, resp_body, resp_len); tmp2[resp_len]=0;
            sb_put_escaped_json_string(&sb, tmp2);
            free(tmp2);
        } else {
            sb_put_escaped_json_string(&sb, "");
        }
    } else {
        if (!sb_put_escaped_json_string(&sb, "")) goto fail;
    }
#endif

    if (!sb_putc(&sb, '}')) goto fail; // close event
    if (!sb_puts(&sb, JSON_SUFFIX, strlen(JSON_SUFFIX))) goto fail;
    if (!sb_grow(&sb, 1)) goto fail;
    if (sb.buf) sb.buf[sb.len] = 0;

    *out_body = sb.buf;
    *out_len  = sb.len;
    return 1;

fail:
    free(sb.buf);
    return 0;
}

static int build_prefix_for_query(const char *query_escaped, char **out_prefix) {
    if (!query_escaped || !g_api_key || !g_service_uuid || !g_library || !g_version) return 0;

    const char *p1 = "{\"query\":\"";
    const char *p2 = "\",\"variables\":{";
    const char *k1 = "\"apiKey\":\"";
    const char *k2 = "\",\"serviceUuid\":\"";
    const char *k3 = "\",\"library\":\"";
    const char *k4 = "\",\"version\":\"";

    size_t n = strlen(p1) + strlen(query_escaped) + strlen(p2)
             + strlen(k1) + strlen(g_api_key)
             + strlen(k2) + strlen(g_service_uuid)
             + strlen(k3) + strlen(g_library)
             + strlen(k4) + strlen(g_version) + 5;

    char *prefix = (char*)malloc(n);
    if (!prefix) return 0;

    char *o = prefix;
    o += sprintf(o, "%s%s%s", p1, query_escaped, p2);
    o += sprintf(o, "%s%s", k1, g_api_key);
    o += sprintf(o, "%s%s", k2, g_service_uuid);
    o += sprintf(o, "%s%s", k3, g_library);
    o += sprintf(o, "%s%s\"", k4, g_version);
    *o = '\0';

    *out_prefix = prefix;
    return 1;
}

// escape for the GraphQL "query" string (handle \n, \r, \t too)
static char *json_escape_query(const char *s) {
    if (!s) return str_dup("");
    const unsigned char *in = (const unsigned char*)s;
    size_t extra = 0;
    for (const unsigned char *p = in; *p; ++p) {
        switch (*p) { case '\\': case '"': case '\n': case '\r': case '\t': extra++; break; default: break; }
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
    *o=0; return out;
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

// ========================= Sender Thread ==========================
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
    curl_easy_setopt(g_telem_curl, CURLOPT_NOSIGNAL, 1L);
#ifdef CURLOPT_TCP_FASTOPEN
    curl_easy_setopt(g_telem_curl, CURLOPT_TCP_FASTOPEN, 1L);
#endif
#ifdef CURL_HTTP_VERSION_2TLS
    if (g_http2) {
        curl_easy_setopt(g_telem_curl, CURLOPT_HTTP_VERSION, CURL_HTTP_VERSION_2TLS);
    }
#endif
    curl_easy_setopt(g_telem_curl, CURLOPT_HTTPHEADER, g_hdrs);
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

// ============================ Python API ==========================

// init_networkhop(url, query, api_key, service_uuid, library, version, http2=1)
static PyObject *py_init_networkhop(PyObject *self, PyObject *args, PyObject *kw) {
    const char *url, *query, *api_key, *service_uuid, *library, *version;
    int http2 = 1;
    static char *kwlist[] = {"url","query","api_key","service_uuid","library","version","http2",NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kw, "ssssssi", kwlist,
                                     &url, &query, &api_key, &service_uuid, &library, &version, &http2)) {
        return NULL;
    }
    if (g_running) {
        // refresh query/prefix only
        free(g_query_escaped); g_query_escaped = json_escape_query(query);
        free(g_json_prefix);   g_json_prefix   = NULL;
        if (!g_query_escaped || !build_prefix_for_query(g_query_escaped, &g_json_prefix)) Py_RETURN_FALSE;
        Py_RETURN_TRUE;
    }

    // copy config
    g_url = str_dup(url);
    g_query_escaped = json_escape_query(query);
    g_api_key = str_dup(api_key);
    g_service_uuid = str_dup(service_uuid);
    g_library = str_dup(library);
    g_version = str_dup(version);
    g_http2   = http2 ? 1 : 0;

    if (!g_url || !g_query_escaped || !g_api_key || !g_service_uuid || !g_library || !g_version) Py_RETURN_FALSE;
    if (!build_prefix_for_query(g_query_escaped, &g_json_prefix)) Py_RETURN_FALSE;

    // ring
    g_cap = SFF_RING_CAP;
    g_ring = (sfnr_msg_t*)calloc(g_cap, sizeof(sfnr_msg_t));
    if (!g_ring) Py_RETURN_FALSE;

    // Parse SF_FASTNETWORKREQUEST_SENDER_THREADS environment variable
    const char *env_threads = getenv("SF_FASTNETWORKREQUEST_SENDER_THREADS");
    if (env_threads) {
        int t = atoi(env_threads);
        if (t > 0 && t <= MAX_SENDER_THREADS) {
            g_configured_sender_threads = t;
        }
    }

    // curl (shared headers only - handles are per-thread)
    curl_global_init(CURL_GLOBAL_DEFAULT);
    g_hdrs = NULL;
    g_hdrs = curl_slist_append(g_hdrs, "Content-Type: application/json");

    // Start sender thread pool
    atomic_store(&g_running, 1);
    g_num_sender_threads = g_configured_sender_threads;
    for (int i = 0; i < g_num_sender_threads; i++) {
        if (pthread_create(&g_sender_threads[i], NULL, sender_main, NULL) != 0) {
            atomic_store(&g_running, 0);
            // Clean up already-started threads
            for (int j = 0; j < i; j++) {
                pthread_join(g_sender_threads[j], NULL);
            }
            Py_RETURN_FALSE;
        }
    }

    Py_RETURN_TRUE;
}

// networkhop(...) - ULTRA-FAST: Build JSON WITH GIL RELEASED (like _sffastlog.c!)
// This is THE KEY OPTIMIZATION: All JSON work happens WITHOUT GIL held
static PyObject *py_networkhop(PyObject *self, PyObject *args, PyObject *kw) {
    const char *trace_id, *url, *method;
    int status, ok;
    long long ts_start, ts_end;
    const char *req_body = NULL; Py_ssize_t req_len = 0;
    const char *resp_body = NULL; Py_ssize_t resp_len = 0;
    const char *req_hdrs_json = NULL;   // JSON string from Python orjson
    const char *resp_hdrs_json = NULL;  // JSON string from Python orjson

    static char *kwlist[] = {
        "trace_id","url","method","status","ok",
        "timestamp_start","timestamp_end",
        "request_body","response_body","request_headers_json","response_headers_json", NULL
    };

    if (!PyArg_ParseTupleAndKeywords(
            args, kw, "sssiiLL|y#y#ss", kwlist,
            &trace_id, &url, &method, &status, &ok,
            &ts_start, &ts_end,
            &req_body, &req_len, &resp_body, &resp_len, &req_hdrs_json, &resp_hdrs_json)) {
        Py_RETURN_NONE;
    }
    if (!g_running || !g_json_prefix) Py_RETURN_NONE;

    // CRITICAL: Copy ONLY the small inputs WITH GIL held (just pointers to Python strings)
    // We'll use them directly in build_body_networkhop() WITHOUT GIL
    // Python guarantees these strings stay alive during Py_BEGIN_ALLOW_THREADS

    // Build complete JSON body WITHOUT GIL HELD (like _sffastlog.c lines 604-610!)
    char *body = NULL;
    size_t len = 0;
    int ok_result = 0;

    Py_BEGIN_ALLOW_THREADS
    // Build JSON body (WITHOUT GIL - pure C string operations)
    if (build_body_networkhop(
            trace_id, url, method, status, ok,
            (uint64_t)ts_start, (uint64_t)ts_end,
            req_body, (size_t)req_len,
            resp_body, (size_t)resp_len,
            req_hdrs_json, resp_hdrs_json,
            &body, &len)) {
        // Push to ring buffer (WITHOUT GIL)
        ok_result = ring_push(body, len);
    }
    Py_END_ALLOW_THREADS

    if (!ok_result) { free(body); }  // drop on backpressure
    Py_RETURN_NONE;
}

// is_ready()
static PyObject *py_is_ready(PyObject *self, PyObject *args) {
    if (g_running && g_json_prefix) Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}

// shutdown()
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
    free(g_service_uuid); g_service_uuid = NULL;
    free(g_library); g_library = NULL;
    free(g_version); g_version = NULL;

    // Drain and free ring buffer
    if (g_ring) {
        char *b; size_t l;
        while (ring_pop(&b, &l)) free(b);
        free(g_ring); g_ring = NULL;
    }

    Py_RETURN_NONE;
}

// (kept for compatibility; just forwards to networkhop)
static PyObject *py_networkhop_async(PyObject *self, PyObject *args, PyObject *kw) {
    return py_networkhop(self, args, kw);
}

static PyMethodDef SFNReqMethods[] = {
    {"init_networkhop",  (PyCFunction)py_init_networkhop,  METH_VARARGS | METH_KEYWORDS, "Init transport and prefix for outbound network hops"},
    {"networkhop",       (PyCFunction)py_networkhop,       METH_VARARGS | METH_KEYWORDS, "Enqueue outbound network hop (non-blocking)"},
    {"networkhop_async", (PyCFunction)py_networkhop_async, METH_VARARGS | METH_KEYWORDS, "Alias of networkhop"},
    {"is_ready",         (PyCFunction)py_is_ready,         METH_NOARGS,                   "Return True if sender thread/transport is up"},
    {"shutdown",         (PyCFunction)py_shutdown,         METH_NOARGS,                   "Shutdown sender and free state"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef sfnreq_module = {
    PyModuleDef_HEAD_INIT,
    "_sffastnetworkrequest",
    "sf_veritas ultra-fast outbound network request telemetry (producer->ring->sender)",
    -1,
    SFNReqMethods
};

PyMODINIT_FUNC PyInit__sffastnetworkrequest(void) {
    return PyModule_Create(&sfnreq_module);
}
