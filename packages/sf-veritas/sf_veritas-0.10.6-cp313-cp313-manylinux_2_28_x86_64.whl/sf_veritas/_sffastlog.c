// sf_veritas/_sffastlog.c
// NOTE: Previously used g_in_telemetry_send from _sfteepreload.c
// Now uses X-Sf3-IsTelemetryMessage header for detection (no external symbol needed)

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

// ---------- Thread-local guard flag ----------
// CRITICAL: Prevents _sfteepreload.c from capturing our telemetry traffic
// Set to 1 in sender threads, provides ~5ns overhead vs 50-100ns for header parsing
__attribute__((visibility("default")))
__thread int g_in_telemetry_send = 0;

// ---------- Ring buffer ----------
#ifndef SFF_RING_CAP
#define SFF_RING_CAP 65536  // power-of-two recommended
#endif

typedef struct {
    char  *body;   // malloc'd HTTP JSON body
    size_t len;
} sff_msg_t;

static sff_msg_t *g_ring = NULL;
static size_t     g_cap  = 0;
static _Atomic size_t g_head = 0; // consumer
static _Atomic size_t g_tail = 0; // producer

// tiny spinlock to make push MPMC-safe enough for Python producers
static atomic_flag g_push_lock = ATOMIC_FLAG_INIT;

// wake/sleep
static pthread_mutex_t g_cv_mtx = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t  g_cv     = PTHREAD_COND_INITIALIZER;
static _Atomic int     g_running = 0;

// Thread pool for parallel sending (configurable via SF_LOG_SENDER_THREADS)
#define MAX_SENDER_THREADS 16
static pthread_t g_sender_threads[MAX_SENDER_THREADS];
static int g_num_sender_threads = 0;
static int g_configured_sender_threads = 1;  // Default: 1 thread

// curl state (per-thread)
__thread CURL *g_telem_curl = NULL;
static struct curl_slist *g_hdrs = NULL;

// config (owned strings)
static char *g_url = NULL;

static char *g_query_escaped = NULL;           // logs mutation (escaped)
static char *g_api_key = NULL;
static char *g_service_uuid = NULL;
static char *g_library = NULL;
static char *g_version = NULL;
static int   g_http2 = 0;

// prebuilt JSON prefix for LOGS:
// {"query":"<escaped_query>","variables":{"apiKey":"...","serviceUuid":"...","library":"...","version":"..."
static char *g_json_prefix = NULL;

// --- PRINT channel state ---
static char *g_print_query_escaped = NULL;     // prints mutation (escaped)
static char *g_json_prefix_print = NULL;       // same prefix style for print

// --- EXCEPTION channel state ---
static char *g_exception_query_escaped = NULL;  // exception mutation (escaped)
static char *g_json_prefix_exception = NULL;    // same prefix style for exception

static const char *JSON_SUFFIX = "}}";

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

// escape for generic JSON string fields
static char *json_escape(const char *s) {
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

// generic prefix builder for a given escaped query
static int build_prefix_for_query(const char *query_escaped, char **out_prefix) {
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

// Build LOG body with level
static int build_body_log(
    const char *session_id,
    const char *level,
    const char *contents,
    int preactive,
    char **out_body,
    size_t *out_len
) {
    char *sid_esc = json_escape(session_id ? session_id : "");
    char *lvl_esc = json_escape(level ? level : "UNKNOWN");
    char *msg_esc = json_escape(contents ? contents : "");
    if (!sid_esc || !lvl_esc || !msg_esc) {
        free(sid_esc); free(lvl_esc); free(msg_esc);
        return 0;
    }

    uint64_t tms = now_ms();
    const char *k_sid = ",\"sessionId\":\"";
    const char *k_lvl = "\",\"level\":\"";
    const char *k_cts = "\",\"contents\":\"";
    const char *k_ts  = "\",\"timestampMs\":\"";
    const char *k_pre = ",\"reentrancyGuardPreactive\":";
    char ts_buf[32];
    int ts_len = snprintf(ts_buf, sizeof(ts_buf), "%llu", (unsigned long long)tms);
    const char *pre_str = preactive ? "true" : "false";

    size_t len = strlen(g_json_prefix)
               + strlen(k_sid) + strlen(sid_esc)
               + strlen(k_lvl) + strlen(lvl_esc)
               + strlen(k_cts) + strlen(msg_esc)
               + strlen(k_ts)  + (size_t)ts_len + 1  // +1 for closing quote
               + strlen(k_pre) + strlen(pre_str)
               + strlen(JSON_SUFFIX);

    char *body = (char*)malloc(len + 1);
    if (!body) { free(sid_esc); free(lvl_esc); free(msg_esc); return 0; }

    char *o = body;
    o += sprintf(o, "%s", g_json_prefix);
    o += sprintf(o, "%s%s", k_sid, sid_esc);
    o += sprintf(o, "%s%s", k_lvl, lvl_esc);
    o += sprintf(o, "%s%s", k_cts, msg_esc);
    o += sprintf(o, "%s%s\"", k_ts, ts_buf);
    o += sprintf(o, "%s%s", k_pre, pre_str);
    o += sprintf(o, "%s", JSON_SUFFIX);
    *o = '\0';

    *out_body = body;
    *out_len  = (size_t)(o - body);

    free(sid_esc); free(lvl_esc); free(msg_esc);
    return 1;
}

// Build PRINT body (no level), using g_json_prefix_print
static int build_body_print(
    const char *session_id, size_t session_len,
    const char *contents,  size_t contents_len,
    int preactive,
    char **out_body, size_t *out_len
){
    // Escape session_id & contents
    // (We have lengths available but json_escape takes NUL-terminated; copy into temp with NUL)
    char *sid_tmp = (char*)malloc(session_len + 1);
    if (!sid_tmp) return 0;
    memcpy(sid_tmp, session_id ? session_id : "", session_len);
    sid_tmp[session_len] = 0;

    char *cts_tmp = (char*)malloc(contents_len + 1);
    if (!cts_tmp) { free(sid_tmp); return 0; }
    memcpy(cts_tmp, contents ? contents : "", contents_len);
    cts_tmp[contents_len] = 0;

    char *sid_esc = json_escape(sid_tmp);
    char *msg_esc = json_escape(cts_tmp);
    free(sid_tmp); free(cts_tmp);
    if (!sid_esc || !msg_esc) {
        free(sid_esc); free(msg_esc);
        return 0;
    }

    uint64_t tms = now_ms();
    const char *k_sid = ",\"sessionId\":\"";
    const char *k_cts = "\",\"contents\":\"";
    const char *k_ts  = "\",\"timestampMs\":\"";
    const char *k_pre = ",\"reentrancyGuardPreactive\":";
    char ts_buf[32];
    int ts_len = snprintf(ts_buf, sizeof(ts_buf), "%llu", (unsigned long long)tms);
    const char *pre_str = preactive ? "true" : "false";

    if (!g_json_prefix_print) { free(sid_esc); free(msg_esc); return 0; }

    size_t len = strlen(g_json_prefix_print)
               + strlen(k_sid) + strlen(sid_esc)
               + strlen(k_cts) + strlen(msg_esc)
               + strlen(k_ts)  + (size_t)ts_len + 1  // +1 for closing quote
               + strlen(k_pre) + strlen(pre_str)
               + strlen(JSON_SUFFIX);

    char *body = (char*)malloc(len + 1);
    if (!body) { free(sid_esc); free(msg_esc); return 0; }

    char *o = body;
    o += sprintf(o, "%s", g_json_prefix_print);
    o += sprintf(o, "%s%s", k_sid, sid_esc);
    o += sprintf(o, "%s%s", k_cts, msg_esc);
    o += sprintf(o, "%s%s\"", k_ts, ts_buf);
    o += sprintf(o, "%s%s", k_pre, pre_str);
    o += sprintf(o, "%s", JSON_SUFFIX);
    *o = '\0';

    *out_body = body;
    *out_len  = (size_t)(o - body);

    free(sid_esc); free(msg_esc);
    return 1;
}

// Build EXCEPTION body
static int build_body_exception(
    const char *session_id, size_t session_len,
    const char *exception_message, size_t exception_len,
    const char *trace_json, size_t trace_len,
    int was_caught,
    int is_from_local_service,
    char **out_body, size_t *out_len
){
    // Escape session_id, exception_message & trace_json
    char *sid_tmp = (char*)malloc(session_len + 1);
    if (!sid_tmp) return 0;
    memcpy(sid_tmp, session_id ? session_id : "", session_len);
    sid_tmp[session_len] = 0;

    char *exc_tmp = (char*)malloc(exception_len + 1);
    if (!exc_tmp) { free(sid_tmp); return 0; }
    memcpy(exc_tmp, exception_message ? exception_message : "", exception_len);
    exc_tmp[exception_len] = 0;

    char *trace_tmp = (char*)malloc(trace_len + 1);
    if (!trace_tmp) { free(sid_tmp); free(exc_tmp); return 0; }
    memcpy(trace_tmp, trace_json ? trace_json : "", trace_len);
    trace_tmp[trace_len] = 0;

    char *sid_esc = json_escape(sid_tmp);
    char *exc_esc = json_escape(exc_tmp);
    char *trace_esc = json_escape(trace_tmp);
    free(sid_tmp); free(exc_tmp); free(trace_tmp);

    if (!sid_esc || !exc_esc || !trace_esc) {
        free(sid_esc); free(exc_esc); free(trace_esc);
        return 0;
    }

    uint64_t tms = now_ms();
    const char *k_sid = ",\"sessionId\":\"";
    const char *k_exc = "\",\"exceptionMessage\":\"";
    const char *k_trace = "\",\"traceJson\":\"";
    const char *k_caught = "\",\"wasCaught\":";
    const char *k_local = ",\"isFromLocalService\":";
    const char *k_ts  = ",\"timestampMs\":\"";
    const char *k_pre = ",\"reentrancyGuardPreactive\":";

    char ts_buf[32];
    int ts_len = snprintf(ts_buf, sizeof(ts_buf), "%llu", (unsigned long long)tms);
    const char *caught_str = was_caught ? "true" : "false";
    const char *local_str = is_from_local_service ? "true" : "false";

    if (!g_json_prefix_exception) { free(sid_esc); free(exc_esc); free(trace_esc); return 0; }

    size_t len = strlen(g_json_prefix_exception)
               + strlen(k_sid) + strlen(sid_esc)
               + strlen(k_exc) + strlen(exc_esc)
               + strlen(k_trace) + strlen(trace_esc)
               + strlen(k_caught) + strlen(caught_str)
               + strlen(k_local) + strlen(local_str)
               + strlen(k_ts)  + (size_t)ts_len + 1  // +1 for closing quote
               + strlen(k_pre) + 5  // "false"
               + strlen(JSON_SUFFIX);

    char *body = (char*)malloc(len + 1);
    if (!body) { free(sid_esc); free(exc_esc); free(trace_esc); return 0; }

    char *o = body;
    o += sprintf(o, "%s", g_json_prefix_exception);
    o += sprintf(o, "%s%s", k_sid, sid_esc);
    o += sprintf(o, "%s%s", k_exc, exc_esc);
    o += sprintf(o, "%s%s", k_trace, trace_esc);
    o += sprintf(o, "%s%s", k_caught, caught_str);
    o += sprintf(o, "%s%s", k_local, local_str);
    o += sprintf(o, "%s%s\"", k_ts, ts_buf);
    o += sprintf(o, "%sfalse", k_pre);  // reentrancyGuardPreactive always false for exceptions
    o += sprintf(o, "%s", JSON_SUFFIX);
    *o = '\0';

    *out_body = body;
    *out_len  = (size_t)(o - body);

    free(sid_esc); free(exc_esc); free(trace_esc);
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

// ---------- pthread cleanup handler ----------
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

    while (1) {
        // Keep running until shutdown requested AND queue is fully drained
        if (ring_empty()) {
            // Queue is empty - check if we should exit
            if (!atomic_load(&g_running)) {
                // Shutting down and queue is empty - safe to exit
                break;
            }
            // Still running - wait for new items
            pthread_mutex_lock(&g_cv_mtx);
            if (ring_empty() && atomic_load(&g_running))
                pthread_cond_wait(&g_cv, &g_cv_mtx);
            pthread_mutex_unlock(&g_cv_mtx);
            continue;
        }

        // Drain ALL items from queue (don't check g_running mid-drain)
        char *body = NULL; size_t len = 0;
        while (ring_pop(&body, &len)) {
            if (!body) continue;

            // Use thread-local curl handle (each thread has its own persistent connection)
            curl_easy_setopt(g_telem_curl, CURLOPT_POSTFIELDS, body);
            curl_easy_setopt(g_telem_curl, CURLOPT_POSTFIELDSIZE, (long)len);
            (void)curl_easy_perform(g_telem_curl); // fire-and-forget

            free(body);
        }
    }

    pthread_cleanup_pop(1);  // Execute cleanup handler
    return NULL;
}

// ---------- Python API ----------
static PyObject *py_init(PyObject *self, PyObject *args, PyObject *kw) {
    const char *url, *query, *api_key, *service_uuid, *library, *version;
    int http2 = 0;
    static char *kwlist[] = {"url","query","api_key","service_uuid","library","version","http2", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kw, "ssssssi",
        kwlist, &url, &query, &api_key, &service_uuid, &library, &version, &http2)) {
        return NULL;  // Exception already set by PyArg_ParseTupleAndKeywords
    }
    if (g_running) Py_RETURN_TRUE;

    g_url = str_dup(url);
    g_query_escaped = json_escape_query(query);
    g_api_key = str_dup(api_key);
    g_service_uuid = str_dup(service_uuid);
    g_library = str_dup(library);
    g_version = str_dup(version);
    g_http2 = http2 ? 1 : 0;
    if (!g_url || !g_query_escaped || !g_api_key || !g_service_uuid || !g_library || !g_version) {
        Py_RETURN_FALSE;
    }
    if (!build_prefix_for_query(g_query_escaped, &g_json_prefix)) { Py_RETURN_FALSE; }

    g_cap = SFF_RING_CAP;
    g_ring = (sff_msg_t*)calloc(g_cap, sizeof(sff_msg_t));
    if (!g_ring) { Py_RETURN_FALSE; }

    // Parse SF_LOG_SENDER_THREADS environment variable
    const char *env_threads = getenv("SF_LOG_SENDER_THREADS");
    if (env_threads) {
        int t = atoi(env_threads);
        if (t > 0 && t <= MAX_SENDER_THREADS) {
            g_configured_sender_threads = t;
        }
    }

    curl_global_init(CURL_GLOBAL_DEFAULT);

    // Initialize shared curl headers (Content-Type only)
    // NOTE: Removed X-Sf3-IsTelemetryMessage header - now use g_in_telemetry_send flag
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

static PyObject *py_init_print(PyObject *self, PyObject *args, PyObject *kw) {
    const char *url, *query, *api_key, *service_uuid, *library, *version;
    int http2 = 1;
    static char *kwlist[] = {"url","query","api_key","service_uuid","library","version","http2",NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kw, "ssssssi", kwlist,
                                     &url, &query, &api_key, &service_uuid, &library, &version, &http2)) {
        return NULL;  // Exception already set by PyArg_ParseTupleAndKeywords
    }

    // If not initialized yet, call init() first with the log query (empty for now)
    if (!g_running) {
        // Build a dummy log query just to initialize the transport
        const char *dummy_log_query =
            "mutation CollectLogs("
            "$apiKey: String!, "
            "$serviceUuid: String!, "
            "$sessionId: String!, "
            "$level: String!, "
            "$contents: String!, "
            "$reentrancyGuardPreactive: Boolean!, "
            "$library: String!, "
            "$timestampMs: String!, "
            "$version: String!"
            ") { "
            "collectLogs("
            "apiKey: $apiKey, "
            "serviceUuid: $serviceUuid, "
            "sessionId: $sessionId, "
            "level: $level, "
            "contents: $contents, "
            "reentrancyGuardPreactive: $reentrancyGuardPreactive, "
            "library: $library, "
            "timestampMs: $timestampMs, "
            "version: $version"
            ") }";

        // Call py_init to set up the transport
        PyObject *init_args = Py_BuildValue("(ssssssi)", url, dummy_log_query, api_key, service_uuid, library, version, http2);
        if (!init_args) return NULL;

        PyObject *init_result = py_init(self, init_args, NULL);
        Py_DECREF(init_args);

        if (!init_result || init_result == Py_False) {
            Py_XDECREF(init_result);
            Py_RETURN_FALSE;
        }
        Py_DECREF(init_result);
    }

    // Now set up the print query + prefix
    if (g_print_query_escaped) { free(g_print_query_escaped); g_print_query_escaped = NULL; }
    if (g_json_prefix_print)   { free(g_json_prefix_print);   g_json_prefix_print   = NULL; }

    g_print_query_escaped = json_escape_query(query);
    if (!g_print_query_escaped) Py_RETURN_FALSE;
    if (!build_prefix_for_query(g_print_query_escaped, &g_json_prefix_print)) {
        Py_RETURN_FALSE;
    }
    Py_RETURN_TRUE;
}

static PyObject *py_init_exception(PyObject *self, PyObject *args, PyObject *kw) {
    const char *url, *query, *api_key, *service_uuid, *library, *version;
    int http2 = 1;
    static char *kwlist[] = {"url","query","api_key","service_uuid","library","version","http2",NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kw, "ssssssi", kwlist,
                                     &url, &query, &api_key, &service_uuid, &library, &version, &http2)) {
        return NULL;  // Exception already set by PyArg_ParseTupleAndKeywords
    }

    // If not initialized yet, call init() first with the log query
    if (!g_running) {
        // Build a dummy log query just to initialize the transport
        const char *dummy_log_query =
            "mutation CollectLogs("
            "$apiKey: String!, "
            "$serviceUuid: String!, "
            "$sessionId: String!, "
            "$level: String!, "
            "$contents: String!, "
            "$reentrancyGuardPreactive: Boolean!, "
            "$library: String!, "
            "$timestampMs: String!, "
            "$version: String!"
            ") { "
            "collectLogs("
            "apiKey: $apiKey, "
            "serviceUuid: $serviceUuid, "
            "sessionId: $sessionId, "
            "level: $level, "
            "contents: $contents, "
            "reentrancyGuardPreactive: $reentrancyGuardPreactive, "
            "library: $library, "
            "timestampMs: $timestampMs, "
            "version: $version"
            ") }";

        // Call py_init to set up the transport
        PyObject *init_args = Py_BuildValue("(ssssssi)", url, dummy_log_query, api_key, service_uuid, library, version, http2);
        if (!init_args) return NULL;

        PyObject *init_result = py_init(self, init_args, NULL);
        Py_DECREF(init_args);

        if (!init_result || init_result == Py_False) {
            Py_XDECREF(init_result);
            Py_RETURN_FALSE;
        }
        Py_DECREF(init_result);
    }

    // Now set up the exception query + prefix
    if (g_exception_query_escaped) { free(g_exception_query_escaped); g_exception_query_escaped = NULL; }
    if (g_json_prefix_exception)   { free(g_json_prefix_exception);   g_json_prefix_exception   = NULL; }

    g_exception_query_escaped = json_escape_query(query);
    if (!g_exception_query_escaped) Py_RETURN_FALSE;
    if (!build_prefix_for_query(g_exception_query_escaped, &g_json_prefix_exception)) {
        Py_RETURN_FALSE;
    }
    Py_RETURN_TRUE;
}

static PyObject *py_log(PyObject *self, PyObject *args, PyObject *kw) {
    const char *level, *contents, *session_id;
    int preactive = 0;
    static char *kwlist[] = {"level","contents","session_id","preactive", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kw, "sss|p", kwlist,
                                     &level, &contents, &session_id, &preactive)) {
        Py_RETURN_NONE;
    }
    if (!g_running) Py_RETURN_NONE;

    // OPTIMIZATION: Release GIL during JSON building + ring push
    char *body = NULL;
    size_t len = 0;
    int ok = 0;

    Py_BEGIN_ALLOW_THREADS
    // Build JSON body (WITHOUT GIL - pure C string operations)
    if (build_body_log(session_id, level, contents, preactive, &body, &len)) {
        // Push to ring buffer (WITHOUT GIL)
        ok = ring_push(body, len);
    }
    Py_END_ALLOW_THREADS

    if (!ok) { free(body); }
    Py_RETURN_NONE;
}

static PyObject *py_print(PyObject *self, PyObject *args, PyObject *kw) {
    const char *contents, *session_id;
    Py_ssize_t contents_len = 0, session_len = 0;
    int preactive = 0;
    static char *kwlist[] = {"contents","session_id","preactive", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kw, "s#s#|p", kwlist,
                                     &contents, &contents_len,
                                     &session_id, &session_len,
                                     &preactive)) {
        Py_RETURN_NONE;
    }
    if (!g_running || g_json_prefix_print == NULL) Py_RETURN_NONE;

    // OPTIMIZATION: Release GIL during JSON building + ring push
    char *body = NULL;
    size_t len = 0;
    int ok = 0;

    Py_BEGIN_ALLOW_THREADS
    // Build JSON body (WITHOUT GIL - pure C string operations)
    if (build_body_print(session_id, (size_t)session_len,
                         contents, (size_t)contents_len,
                         preactive, &body, &len)) {
        // Push to ring buffer (WITHOUT GIL)
        ok = ring_push(body, len);
    }
    Py_END_ALLOW_THREADS

    if (!ok) { free(body); }  // ring owns on success
    Py_RETURN_NONE;
}

static PyObject *py_exception(PyObject *self, PyObject *args, PyObject *kw) {
    const char *exception_message, *trace_json, *session_id;
    Py_ssize_t exception_len = 0, trace_len = 0, session_len = 0;
    int was_caught = 1;
    int is_from_local_service = 0;
    static char *kwlist[] = {"exception_message","trace_json","session_id","was_caught","is_from_local_service", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kw, "s#s#s#|pp", kwlist,
                                     &exception_message, &exception_len,
                                     &trace_json, &trace_len,
                                     &session_id, &session_len,
                                     &was_caught,
                                     &is_from_local_service)) {
        Py_RETURN_NONE;
    }
    if (!g_running || g_json_prefix_exception == NULL) Py_RETURN_NONE;

    // OPTIMIZATION: Release GIL during JSON building + ring push
    char *body = NULL;
    size_t len = 0;
    int ok = 0;

    Py_BEGIN_ALLOW_THREADS
    // Build JSON body (WITHOUT GIL - pure C string operations)
    if (build_body_exception(session_id, (size_t)session_len,
                             exception_message, (size_t)exception_len,
                             trace_json, (size_t)trace_len,
                             was_caught, is_from_local_service,
                             &body, &len)) {
        // Push to ring buffer (WITHOUT GIL)
        ok = ring_push(body, len);
    }
    Py_END_ALLOW_THREADS

    if (!ok) { free(body); }  // ring owns on success
    Py_RETURN_NONE;
}

static PyObject *py_shutdown(PyObject *self, PyObject *args) {
    if (!g_running) Py_RETURN_NONE;

    atomic_store(&g_running, 0);

    // Wake all sender threads (use broadcast for multiple threads)
    pthread_mutex_lock(&g_cv_mtx);
    pthread_cond_broadcast(&g_cv);
    pthread_mutex_unlock(&g_cv_mtx);

    // Join all sender threads (cleanup handlers execute automatically)
    for (int i = 0; i < g_num_sender_threads; i++) {
        if (g_sender_threads[i]) {
            pthread_join(g_sender_threads[i], NULL);
        }
    }

    // Clean up shared curl resources
    // NOTE: g_curl is now per-thread, cleaned by pthread_cleanup_push
    if (g_hdrs) {
        curl_slist_free_all(g_hdrs);
        g_hdrs = NULL;
    }
    curl_global_cleanup();

    // Free all allocated strings (NULL after free to prevent use-after-free)
    free(g_url);
    g_url = NULL;

    free(g_query_escaped);
    g_query_escaped = NULL;
    free(g_json_prefix);
    g_json_prefix = NULL;

    free(g_print_query_escaped);
    g_print_query_escaped = NULL;
    free(g_json_prefix_print);
    g_json_prefix_print = NULL;

    free(g_exception_query_escaped);
    g_exception_query_escaped = NULL;
    free(g_json_prefix_exception);
    g_json_prefix_exception = NULL;

    free(g_api_key);
    g_api_key = NULL;
    free(g_service_uuid);
    g_service_uuid = NULL;
    free(g_library);
    g_library = NULL;
    free(g_version);
    g_version = NULL;

    // Free ring buffer (drain remaining messages first)
    if (g_ring) {
        char *b;
        size_t l;
        while (ring_pop(&b, &l)) free(b);
        free(g_ring);
        g_ring = NULL;
    }

    Py_RETURN_NONE;
}

// ---------- Module table (SINGLE definition) ----------
static PyMethodDef SFFastLogMethods[] = {
    {"init",            (PyCFunction)py_init,           METH_VARARGS | METH_KEYWORDS, "Init (logs) and start sender"},
    {"init_print",      (PyCFunction)py_init_print,     METH_VARARGS | METH_KEYWORDS, "Init (prints) query/prefix"},
    {"init_exception",  (PyCFunction)py_init_exception, METH_VARARGS | METH_KEYWORDS, "Init (exception) query/prefix"},
    {"log",             (PyCFunction)py_log,            METH_VARARGS | METH_KEYWORDS, "Send log"},
    {"print_",          (PyCFunction)py_print,          METH_VARARGS | METH_KEYWORDS, "Send print"},
    {"exception",       (PyCFunction)py_exception,      METH_VARARGS | METH_KEYWORDS, "Send exception"},
    {"shutdown",        (PyCFunction)py_shutdown,       METH_NOARGS,                   "Shutdown sender and free state"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef sffastlogmodule = {
    PyModuleDef_HEAD_INIT,
    "_sffastlog",
    "sf_veritas ultra-fast logging/printing",
    -1,
    SFFastLogMethods
};

PyMODINIT_FUNC PyInit__sffastlog(void) {
    return PyModule_Create(&sffastlogmodule);
}
