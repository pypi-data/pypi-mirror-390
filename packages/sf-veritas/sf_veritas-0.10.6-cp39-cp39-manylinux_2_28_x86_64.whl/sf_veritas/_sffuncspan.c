// sf_veritas/_sffuncspan.c
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <frameobject.h>
#include <pthread.h>
#include <curl/curl.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>

// ---------- Thread-local guard flag to prevent recursive telemetry capture ----------
__attribute__((visibility("default")))
__thread int g_in_telemetry_send = 0;

// ---------- External Config System Integration ----------
// Config structure matches _sffuncspan_config.c
typedef struct {
    uint8_t include_arguments;
    uint8_t include_return_value;
    uint8_t autocapture_all_children;
    uint8_t _padding;
    float sample_rate;
    uint32_t arg_limit_mb;
    uint32_t return_limit_mb;
    uint64_t hash;
} sf_funcspan_config_t;

// Python module reference for config system
static PyObject *g_config_module = NULL;
static PyObject *g_config_get_func = NULL;

// Default config to use if config system is not available
static sf_funcspan_config_t g_fallback_config = {
    .include_arguments = 1,
    .include_return_value = 1,
    .autocapture_all_children = 1,
    ._padding = 0,
    .sample_rate = 1.0f,
    .arg_limit_mb = 1,
    .return_limit_mb = 1,
    .hash = 0
};

// Initialize config system integration (called once at init)
static void init_config_system(void) {
    // Try to import _sffuncspan_config module
    g_config_module = PyImport_ImportModule("sf_veritas._sffuncspan_config");
    if (g_config_module) {
        // Get the 'get' function
        g_config_get_func = PyObject_GetAttrString(g_config_module, "get");
        if (!g_config_get_func || !PyCallable_Check(g_config_get_func)) {
            Py_XDECREF(g_config_get_func);
            g_config_get_func = NULL;
            Py_DECREF(g_config_module);
            g_config_module = NULL;
            fprintf(stderr, "[_sffuncspan] WARNING: Config module imported but 'get' function not found\n");
        } else {
            fprintf(stderr, "[_sffuncspan] Config system initialized successfully\n");
        }
    } else {
        PyErr_Clear();  // Config module not available, use defaults
        fprintf(stderr, "[_sffuncspan] WARNING: Config module not available, using defaults\n");
    }
}

// Thread-local recursion guard to prevent calling Python from within config lookup
static _Thread_local int g_in_config_lookup = 0;

// Thread-local recursion guard to prevent profiling the profiler itself
static _Thread_local int g_in_profiler = 0;

// Debug counter (only log first few lookups)
static _Atomic int g_debug_lookup_count = 0;

// Simple cache for config lookups (to avoid calling Python during argument capture)
#define CONFIG_CACHE_SIZE 256
typedef struct {
    uint64_t hash;  // Hash of file_path:func_name
    sf_funcspan_config_t config;
} config_cache_entry_t;

static config_cache_entry_t g_config_cache[CONFIG_CACHE_SIZE];
static pthread_mutex_t g_config_cache_mutex = PTHREAD_MUTEX_INITIALIZER;

// Simple string hash function
static inline uint64_t simple_hash(const char *str1, const char *str2) {
    uint64_t hash = 5381;
    const unsigned char *s = (const unsigned char *)str1;
    while (*s) {
        hash = ((hash << 5) + hash) + *s++;
    }
    s = (const unsigned char *)str2;
    while (*s) {
        hash = ((hash << 5) + hash) + *s++;
    }
    return hash;
}

// Get config for a function by calling Python config system (with cache)
static inline sf_funcspan_config_t get_function_config(const char *file_path, const char *func_name) {
    uint64_t func_hash, file_hash;
    uint32_t func_cache_idx, file_cache_idx;
    int count;
    PyObject *args = NULL;
    PyObject *result = NULL;
    PyObject *val = NULL;
    sf_funcspan_config_t config;

    // First, check cache for function-specific config (exact match)
    func_hash = simple_hash(file_path, func_name);
    func_cache_idx = func_hash % CONFIG_CACHE_SIZE;

    // Check cache first (no lock for read - this is a simple cache, not perfect but fast)
    if (g_config_cache[func_cache_idx].hash == func_hash) {
        count = atomic_fetch_add(&g_debug_lookup_count, 1);
        if (count < 5) {
            fprintf(stderr, "[_sffuncspan] CACHE HIT (func): %s::%s -> args=%d ret=%d\n",
                    func_name, file_path,
                    g_config_cache[func_cache_idx].config.include_arguments,
                    g_config_cache[func_cache_idx].config.include_return_value);
        }
        return g_config_cache[func_cache_idx].config;
    }

    // Second, check cache for file-level config (using "<MODULE>" as function name)
    file_hash = simple_hash(file_path, "<MODULE>");
    file_cache_idx = file_hash % CONFIG_CACHE_SIZE;

    if (g_config_cache[file_cache_idx].hash == file_hash) {
        count = atomic_fetch_add(&g_debug_lookup_count, 1);
        if (count < 5) {
            fprintf(stderr, "[_sffuncspan] CACHE HIT (file): %s::%s -> args=%d ret=%d\n",
                    func_name, file_path,
                    g_config_cache[file_cache_idx].config.include_arguments,
                    g_config_cache[file_cache_idx].config.include_return_value);
        }
        return g_config_cache[file_cache_idx].config;
    }

    // CACHE MISS - try config module (includes HTTP header overrides!)
    if (g_config_get_func && !g_in_config_lookup) {
        // Prevent recursion
        g_in_config_lookup = 1;

        args = Py_BuildValue("(ss)", file_path, func_name);
        if (args) {
            result = PyObject_CallObject(g_config_get_func, args);
            Py_DECREF(args);

            if (result && PyDict_Check(result)) {
                config = g_fallback_config;

                val = PyDict_GetItemString(result, "include_arguments");
                if (val && PyBool_Check(val)) config.include_arguments = (val == Py_True) ? 1 : 0;

                val = PyDict_GetItemString(result, "include_return_value");
                if (val && PyBool_Check(val)) config.include_return_value = (val == Py_True) ? 1 : 0;

                val = PyDict_GetItemString(result, "autocapture_all_children");
                if (val && PyBool_Check(val)) config.autocapture_all_children = (val == Py_True) ? 1 : 0;

                val = PyDict_GetItemString(result, "arg_limit_mb");
                if (val && PyLong_Check(val)) config.arg_limit_mb = (uint32_t)PyLong_AsLong(val);

                val = PyDict_GetItemString(result, "return_limit_mb");
                if (val && PyLong_Check(val)) config.return_limit_mb = (uint32_t)PyLong_AsLong(val);

                val = PyDict_GetItemString(result, "sample_rate");
                if (val && PyFloat_Check(val)) config.sample_rate = (float)PyFloat_AsDouble(val);

                // DON'T cache configs from _sffuncspan_config.get() because they include
                // thread-local HTTP header overrides that change per-request.
                // Only cache configs that were pre-populated via cache_config().

                Py_DECREF(result);
                g_in_config_lookup = 0;
                return config;
            }

            Py_XDECREF(result);
            if (PyErr_Occurred()) PyErr_Clear();
        }
        g_in_config_lookup = 0;
    }

    // Fallback to defaults
    count = atomic_fetch_add(&g_debug_lookup_count, 1);
    if (count < 5) {
        fprintf(stderr, "[_sffuncspan] CACHE MISS: %s::%s - using fallback config\n", func_name, file_path);
    }
    return g_fallback_config;
}

// Compatibility for Python 3.8
#if PY_VERSION_HEX < 0x03090000  // Python < 3.9
static inline PyCodeObject* PyFrame_GetCode(PyFrameObject *frame) {
    PyCodeObject *code = frame->f_code;
    Py_INCREF(code);
    return code;
}
#endif

// ---------- Ring buffer ----------
#ifndef SFFS_RING_CAP
#define SFFS_RING_CAP 524288  // 512K slots for high-throughput (was 64K)
#endif

typedef struct {
    char  *body;   // malloc'd HTTP JSON body
    size_t len;
} sffs_msg_t;

static sffs_msg_t *g_ring = NULL;
static size_t     g_cap  = 0;
static _Atomic size_t g_head = 0; // consumer
static _Atomic size_t g_tail = 0; // producer

// tiny spinlock to make push MPMC-safe enough for Python producers
static atomic_flag g_push_lock = ATOMIC_FLAG_INIT;

// wake/sleep
static pthread_mutex_t g_cv_mtx = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t  g_cv     = PTHREAD_COND_INITIALIZER;
static _Atomic int     g_running = 0;

// Thread pool for concurrent senders (configurable via SF_FUNCSPAN_SENDER_THREADS)
#define MAX_SENDER_THREADS 16
static pthread_t g_sender_threads[MAX_SENDER_THREADS];
static int g_num_sender_threads = 0;

// curl state - per-thread handles for concurrent HTTP requests
__thread CURL *g_telem_curl = NULL;
static struct curl_slist *g_hdrs = NULL;

// config (owned strings)
static char *g_url = NULL;
static char *g_func_span_query_escaped = NULL;
static char *g_json_prefix_func_span = NULL;
static char *g_api_key = NULL;
static char *g_service_uuid = NULL;
static char *g_library = NULL;
static char *g_version = NULL;
static int   g_http2 = 0;

// Function span configuration
static size_t g_variable_capture_size_limit_bytes = 1048576; // 1MB default
static PyObject *g_capture_from_installed_libraries = NULL;  // list of strings or NULL

// Sampling configuration for ultra-low overhead
static _Atomic uint64_t g_sample_counter = 0;
static uint64_t g_sample_rate = 1;  // 1 = capture all, 100 = capture 1/100, 10000 = capture 1/10000
static int g_enable_sampling = 0;  // 0 = disabled (capture all by default), 1 = enabled

// Master kill switch from SF_ENABLE_FUNCTION_SPANS env var (default: TRUE)
// When disabled, profiler hooks run but skip ALL expensive work (config, capture, transmission)
// NOTHING can override this (not headers, not decorators, nothing)
static int g_enable_function_spans = 1;  // Default: enabled

// Debug flag from environment (set in py_init)
static int SF_DEBUG = 0;

// Serialization configuration
static int g_parse_json_strings = 1;  // 1 = auto-parse JSON strings, 0 = keep as strings

// Capture control - granular configuration
static int g_capture_arguments = 1;  // 1 = capture arguments, 0 = skip
static int g_capture_return_value = 1;  // 1 = capture return value, 0 = skip
static size_t g_arg_limit_bytes = 1048576;  // 1MB default for arguments
static size_t g_return_limit_bytes = 1048576;  // 1MB default for return values

// Django view function filtering
static int g_include_django_view_functions = 0;  // 0 = skip Django view functions (default), 1 = include them

// Installed packages filtering - controlled by SF_FUNCSPAN_CAPTURE_INSTALLED_PACKAGES
static int g_capture_installed_packages = 0;  // 0 = skip site-packages/stdlib (default), 1 = capture them

// SF Veritas self-capture - controlled by SF_FUNCSPAN_CAPTURE_SF_VERITAS
static int g_capture_sf_veritas = 0;  // 0 = skip sf_veritas (default), 1 = capture our own telemetry code

// Performance monitoring
static _Atomic uint64_t g_spans_recorded = 0;
static _Atomic uint64_t g_spans_sampled_out = 0;
static _Atomic uint64_t g_spans_dropped = 0;

static const char *JSON_SUFFIX = "}}";

// Span ID management - thread-local storage for span stack
static pthread_key_t g_span_stack_key;
static pthread_once_t g_span_stack_key_once = PTHREAD_ONCE_INIT;

// Span ID counter
static _Atomic uint64_t g_span_id_counter = 0;

// Span stack entry
typedef struct span_entry {
    char *span_id;
    struct span_entry *next;
} span_entry_t;

// ---------- Helpers for epoch nanoseconds ----------
static inline uint64_t now_epoch_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return ((uint64_t)ts.tv_sec) * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

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

// ---------- Span stack management ----------
static void init_span_stack_key(void) {
    pthread_key_create(&g_span_stack_key, NULL);
}

static span_entry_t* get_span_stack(void) {
    pthread_once(&g_span_stack_key_once, init_span_stack_key);
    return (span_entry_t*)pthread_getspecific(g_span_stack_key);
}

static void set_span_stack(span_entry_t *stack) {
    pthread_once(&g_span_stack_key_once, init_span_stack_key);
    pthread_setspecific(g_span_stack_key, stack);
}

static char* generate_span_id(void) {
    uint64_t id = atomic_fetch_add(&g_span_id_counter, 1);
    char *span_id = (char*)malloc(32);
    if (!span_id) return NULL;
    snprintf(span_id, 32, "span-%llu", (unsigned long long)id);
    return span_id;
}

static void push_span(const char *span_id) {
    span_entry_t *entry = (span_entry_t*)malloc(sizeof(span_entry_t));
    if (!entry) return;
    entry->span_id = str_dup(span_id);
    entry->next = get_span_stack();
    set_span_stack(entry);
}

static char* pop_span(void) {
    span_entry_t *stack = get_span_stack();
    if (!stack) return NULL;
    char *span_id = stack->span_id;
    span_entry_t *next = stack->next;
    free(stack);
    set_span_stack(next);
    return span_id;
}

static char* peek_parent_span_id(void) {
    span_entry_t *stack = get_span_stack();
    if (!stack) return NULL;
    return stack->span_id ? str_dup(stack->span_id) : NULL;
}

// ---------- Build function span body ----------
static int build_body_func_span(
    const char *session_id,
    const char *span_id,
    const char *parent_span_id,
    const char *file_path,
    int line_number,
    int column_number,
    const char *function_name,
    const char *arguments_json,
    const char *return_value_json,
    uint64_t start_time_ns,
    uint64_t duration_ns,
    char **out_body,
    size_t *out_len
) {
    // Escape all string fields
    char *sid_esc = json_escape(session_id ? session_id : "");
    char *spanid_esc = json_escape(span_id ? span_id : "");
    char *pspanid_esc = parent_span_id ? json_escape(parent_span_id) : NULL;
    char *file_esc = json_escape(file_path ? file_path : "");
    char *func_esc = json_escape(function_name ? function_name : "");
    char *args_esc = json_escape(arguments_json ? arguments_json : "{}");
    char *ret_esc = return_value_json ? json_escape(return_value_json) : NULL;

    if (!sid_esc || !spanid_esc || !file_esc || !func_esc || !args_esc) {
        free(sid_esc); free(spanid_esc); free(pspanid_esc); free(file_esc);
        free(func_esc); free(args_esc); free(ret_esc);
        return 0;
    }

    uint64_t tms = now_ms();
    const char *k_sid = ",\"sessionId\":\"";
    const char *k_spanid = ",\"spanId\":\"";
    const char *k_pspanid = ",\"parentSpanId\":\"";
    const char *k_pspanid_null = ",\"parentSpanId\":null";
    const char *k_file = ",\"filePath\":\"";
    const char *k_line = ",\"lineNumber\":";
    const char *k_col = ",\"columnNumber\":";
    const char *k_func = ",\"functionName\":\"";
    const char *k_args = ",\"arguments\":\"";
    const char *k_ret = ",\"returnValue\":\"";
    const char *k_ret_null = ",\"returnValue\":null";
    const char *k_start = ",\"startTimeNs\":";
    const char *k_dur = ",\"durationNs\":";
    const char *k_ts = ",\"timestampMs\":\"";

    char ts_buf[32], line_buf[16], col_buf[16], start_buf[32], dur_buf[32];
    snprintf(ts_buf, sizeof(ts_buf), "%llu", (unsigned long long)tms);
    snprintf(line_buf, sizeof(line_buf), "%d", line_number);
    snprintf(col_buf, sizeof(col_buf), "%d", column_number);
    snprintf(start_buf, sizeof(start_buf), "%llu", (unsigned long long)start_time_ns);
    snprintf(dur_buf, sizeof(dur_buf), "%llu", (unsigned long long)duration_ns);

    if (!g_json_prefix_func_span) {
        free(sid_esc); free(spanid_esc); free(pspanid_esc); free(file_esc);
        free(func_esc); free(args_esc); free(ret_esc);
        return 0;
    }

    size_t len = strlen(g_json_prefix_func_span)
               + strlen(k_sid) + strlen(sid_esc)
               + strlen(k_spanid) + strlen(spanid_esc)
               + (pspanid_esc ? (strlen(k_pspanid) + strlen(pspanid_esc)) : strlen(k_pspanid_null))
               + strlen(k_file) + strlen(file_esc)
               + strlen(k_line) + strlen(line_buf)
               + strlen(k_col) + strlen(col_buf)
               + strlen(k_func) + strlen(func_esc)
               + strlen(k_args) + strlen(args_esc)
               + (ret_esc ? (strlen(k_ret) + strlen(ret_esc)) : strlen(k_ret_null))
               + strlen(k_start) + strlen(start_buf)
               + strlen(k_dur) + strlen(dur_buf)
               + strlen(k_ts) + strlen(ts_buf) + 1  // +1 for closing quote
               + strlen(JSON_SUFFIX) + 10;

    char *body = (char*)malloc(len);
    if (!body) {
        free(sid_esc); free(spanid_esc); free(pspanid_esc); free(file_esc);
        free(func_esc); free(args_esc); free(ret_esc);
        return 0;
    }

    char *o = body;
    o += sprintf(o, "%s", g_json_prefix_func_span);
    o += sprintf(o, "%s%s\"", k_sid, sid_esc);
    o += sprintf(o, "%s%s\"", k_spanid, spanid_esc);
    if (pspanid_esc) {
        o += sprintf(o, "%s%s\"", k_pspanid, pspanid_esc);
    } else {
        o += sprintf(o, "%s", k_pspanid_null);
    }
    o += sprintf(o, "%s%s\"", k_file, file_esc);
    o += sprintf(o, "%s%s", k_line, line_buf);
    o += sprintf(o, "%s%s", k_col, col_buf);
    o += sprintf(o, "%s%s\"", k_func, func_esc);
    o += sprintf(o, "%s%s\"", k_args, args_esc);
    if (ret_esc) {
        o += sprintf(o, "%s%s\"", k_ret, ret_esc);
    } else {
        o += sprintf(o, "%s", k_ret_null);
    }
    o += sprintf(o, "%s%s", k_start, start_buf);
    o += sprintf(o, "%s%s", k_dur, dur_buf);
    o += sprintf(o, "%s%s\"", k_ts, ts_buf);
    o += sprintf(o, "%s", JSON_SUFFIX);
    *o = '\0';

    *out_body = body;
    *out_len = (size_t)(o - body);

    free(sid_esc); free(spanid_esc); free(pspanid_esc); free(file_esc);
    free(func_esc); free(args_esc); free(ret_esc);
    return 1;
}

// ---------- Sampling ----------
static inline int should_sample(void) {
    if (!g_enable_sampling) {
        return 1;  // Sampling disabled, capture all
    }

    // Fast path: atomic increment and modulo check
    uint64_t counter = atomic_fetch_add(&g_sample_counter, 1);
    if (counter % g_sample_rate == 0) {
        return 1;  // This one gets sampled
    }

    atomic_fetch_add(&g_spans_sampled_out, 1);
    return 0;  // Skip this one
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
        atomic_fetch_add(&g_spans_dropped, 1);  // Track dropped spans
        return 0; // full (drop)
    }
    size_t idx = t % g_cap;
    g_ring[idx].body = body;
    g_ring[idx].len  = len;
    atomic_store_explicit(&g_tail, t + 1, memory_order_release);
    atomic_flag_clear_explicit(&g_push_lock, memory_order_release);

    atomic_fetch_add(&g_spans_recorded, 1);  // Track recorded spans

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

// ---------- pthread cleanup handler for sender threads ----------
static void sender_cleanup(void *arg) {
    (void)arg;
    if (g_telem_curl) {
        curl_easy_cleanup(g_telem_curl);
        g_telem_curl = NULL;
    }
}

// ---------- sender thread ----------
static void *sender_main(void *arg) {
    (void)arg;

    // CRITICAL: Set thread-local guard flag to prevent recursive capture
    g_in_telemetry_send = 1;

    // Initialize per-thread curl handle
    g_telem_curl = curl_easy_init();
    if (!g_telem_curl) return NULL;

    // Configure per-thread curl handle
    curl_easy_setopt(g_telem_curl, CURLOPT_URL, g_url);
    curl_easy_setopt(g_telem_curl, CURLOPT_TCP_KEEPALIVE, 1L);
    curl_easy_setopt(g_telem_curl, CURLOPT_TCP_NODELAY, 1L);  // NEW: Disable Nagle for immediate sends
    curl_easy_setopt(g_telem_curl, CURLOPT_HTTPHEADER, g_hdrs);
#ifdef CURL_HTTP_VERSION_2TLS
    if (g_http2) {
        curl_easy_setopt(g_telem_curl, CURLOPT_HTTP_VERSION, CURL_HTTP_VERSION_2TLS);
    }
#endif
    curl_easy_setopt(g_telem_curl, CURLOPT_WRITEFUNCTION, _sink_write);
    curl_easy_setopt(g_telem_curl, CURLOPT_HEADERFUNCTION, _sink_header);

    // Register cleanup handler
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
            curl_easy_setopt(g_telem_curl, CURLOPT_POSTFIELDS, body);
            curl_easy_setopt(g_telem_curl, CURLOPT_POSTFIELDSIZE, (long)len);
            (void)curl_easy_perform(g_telem_curl); // fire-and-forget
            free(body);
            if (!atomic_load(&g_running)) break;
        }
    }

    pthread_cleanup_pop(1);
    return NULL;
}

// Forward declaration of serialization function (defined later)
static char* serialize_python_object_to_json(PyObject *value, size_t max_size);

// ---------- Ultra-fast C profiler hook ----------
// Thread-local storage for call stack (minimal overhead)
typedef struct call_frame {
    uint64_t start_ns;
    char *span_id;
    char *function_name;  // OWNED (str_dup'd from PyUnicode_AsUTF8), must free
    char *file_path;      // OWNED (str_dup'd from PyUnicode_AsUTF8), must free
    int line_number;
    char *arguments_json; // Owned, must free if not NULL
    PyFrameObject *frame; // Borrowed reference for argument capture
    sf_funcspan_config_t config;  // Config looked up during CALL, reused during RETURN
    struct call_frame *parent;
} call_frame_t;

static pthread_key_t g_call_stack_key;
static pthread_once_t g_call_stack_key_once = PTHREAD_ONCE_INIT;

static void init_call_stack_key(void) {
    pthread_key_create(&g_call_stack_key, NULL);
}

static call_frame_t* get_call_stack(void) {
    pthread_once(&g_call_stack_key_once, init_call_stack_key);
    return (call_frame_t*)pthread_getspecific(g_call_stack_key);
}

static void set_call_stack(call_frame_t *stack) {
    pthread_once(&g_call_stack_key_once, init_call_stack_key);
    pthread_setspecific(g_call_stack_key, stack);
}

// Debug counter for argument capture
static _Atomic int g_debug_arg_capture_count = 0;

// Capture function arguments from a frame (ultra-fast C implementation)
static char* capture_arguments_from_frame(PyFrameObject *frame) {
    int debug_count = atomic_fetch_add(&g_debug_arg_capture_count, 1);
    int should_debug = (debug_count < 5);

    if (!frame) {
        if (should_debug) fprintf(stderr, "[_sffuncspan] capture_args: frame is NULL\n");
        return str_dup("{}");
    }

    PyCodeObject *code = PyFrame_GetCode(frame);
    if (!code) {
        if (should_debug) fprintf(stderr, "[_sffuncspan] capture_args: code is NULL\n");
        return str_dup("{}");
    }

    // Get argument count
    int arg_count = code->co_argcount + code->co_kwonlyargcount;
    if (should_debug) {
        fprintf(stderr, "[_sffuncspan] capture_args: arg_count=%d\n", arg_count);
    }

    if (arg_count == 0) {
        Py_DECREF(code);
        if (should_debug) fprintf(stderr, "[_sffuncspan] capture_args: arg_count is 0, returning {}\n");
        return str_dup("{}");
    }

    // Build arguments dict as JSON
    size_t buf_size = 4096;
    char *buf = (char*)malloc(buf_size);
    if (!buf) {
        Py_DECREF(code);
        return str_dup("{}");
    }

    size_t pos = 0;
    buf[pos++] = '{';
    int added = 0;

    // Get frame locals - CRITICAL: must call PyFrame_FastToLocals first to populate the dict!
#if PY_VERSION_HEX >= 0x030B0000  // Python 3.11+
    PyObject *locals = PyFrame_GetLocals(frame);
#else
    // For Python < 3.11, we must explicitly populate f_locals from the fast locals array
    PyFrame_FastToLocals(frame);
    PyObject *locals = frame->f_locals;
    Py_XINCREF(locals);
#endif
    if (!locals) {
        Py_DECREF(code);
        free(buf);
        if (should_debug) fprintf(stderr, "[_sffuncspan] capture_args: locals is NULL\n");
        return str_dup("{}");
    }

    if (should_debug) {
        Py_ssize_t dict_size = PyDict_Check(locals) ? PyDict_Size(locals) : -1;
        fprintf(stderr, "[_sffuncspan] capture_args: locals dict size=%zd\n", dict_size);
    }

    // Get variable names
#if PY_VERSION_HEX >= 0x030B0000  // Python 3.11+
    PyObject *co_varnames = PyCode_GetVarnames(code);
#else
    PyObject *co_varnames = code->co_varnames;
    Py_XINCREF(co_varnames);
#endif
    if (!co_varnames) {
        Py_DECREF(locals);
        Py_DECREF(code);
        free(buf);
        return str_dup("{}");
    }

    // Iterate through argument names
    for (int i = 0; i < arg_count && i < PyTuple_Size(co_varnames); i++) {
        PyObject *var_name_obj = PyTuple_GetItem(co_varnames, i);
        if (!var_name_obj) continue;

        const char *var_name = PyUnicode_AsUTF8(var_name_obj);
        if (!var_name) continue;

        // Get value from locals
        PyObject *value = PyDict_GetItemString(locals, var_name);
        if (!value) continue;

        // Serialize value
        char *value_json = serialize_python_object_to_json(value, g_arg_limit_bytes / (arg_count > 0 ? arg_count : 1));
        if (!value_json) continue;

        // Escape variable name
        char *var_name_esc = json_escape(var_name);
        if (!var_name_esc) {
            free(value_json);
            continue;
        }

        // Check buffer space
        size_t needed = strlen(var_name_esc) + strlen(value_json) + 10;
        if (pos + needed >= buf_size - 10) {
            free(var_name_esc);
            free(value_json);
            break;
        }

        // Add to JSON
        if (added > 0) buf[pos++] = ',';
        buf[pos++] = '"';
        size_t name_len = strlen(var_name_esc);
        memcpy(buf + pos, var_name_esc, name_len);
        pos += name_len;
        buf[pos++] = '"';
        buf[pos++] = ':';
        size_t val_len = strlen(value_json);
        memcpy(buf + pos, value_json, val_len);
        pos += val_len;

        free(var_name_esc);
        free(value_json);
        added++;
    }

    buf[pos++] = '}';
    buf[pos] = '\0';

    Py_DECREF(co_varnames);
    Py_DECREF(locals);
    Py_DECREF(code);

    return buf;
}

// Debug counter for profiler callbacks
static _Atomic int g_profiler_call_count = 0;

// Debug counter for accepted functions
static _Atomic int g_debug_accepted_count = 0;

// Profiler ready flag - set to 1 after PyEval_SetProfile() completes successfully
// This prevents profiling during profiler installation (when Python may call our
// profiler for frames already on the stack, including sf_veritas initialization code)
static _Atomic int g_profiler_ready = 0;

// Interceptors ready flag - set to 1 after setup_interceptors() completes
// This prevents profiling during interceptor initialization (which can cause crashes)
static _Atomic int g_interceptors_ready = 0;

// Fast C profiler callback - this replaces the Python _profile_callback
static int c_profile_func(PyObject *obj, PyFrameObject *frame, int what, PyObject *arg) {
    (void)obj;
    (void)arg;

    // CRITICAL: Recursion guard - prevent profiling the profiler itself!
    // This prevents infinite recursion when capturing sf_veritas code or calling Python from C
    if (g_in_profiler) {
        return 0;
    }
    g_in_profiler = 1;

    // CRITICAL: Defensive NULL checks first!
    if (!frame) {
        g_in_profiler = 0;
        return 0;
    }
    if (!g_running) {
        g_in_profiler = 0;
        return 0;
    }

    // DEBUG: Log first few calls
    int call_count = atomic_fetch_add(&g_profiler_call_count, 1);
    if (call_count < 5) {
        fprintf(stderr, "[_sffuncspan] PROFILER CALLED #%d, what=%d\n", call_count, what);
        fflush(stderr);
    }

    // PROFILER READY CHECK: Skip all calls until profiler is fully initialized
    // This prevents profiling during PyEval_SetProfile() installation, when Python may
    // call our profiler for frames already on the stack (including sf_veritas code).
    if (!atomic_load(&g_profiler_ready)) {
        if (SF_DEBUG && call_count < 5) {
            fprintf(stderr, "[_sffuncspan] PROFILER_NOT_READY: Skipping call during initialization\n");
            fflush(stderr);
        }
        g_in_profiler = 0;
        return 0;
    }

    // INTERCEPTORS READY CHECK: Skip all calls until interceptors are fully set up
    // This prevents profiling during setup_interceptors(), which can cause crashes
    // when profiling code that's in an inconsistent state during initialization.
    if (!atomic_load(&g_interceptors_ready)) {
        if (SF_DEBUG && call_count < 5) {
            fprintf(stderr, "[_sffuncspan] INTERCEPTORS_NOT_READY: Skipping call during interceptor setup\n");
            fflush(stderr);
        }
        g_in_profiler = 0;
        return 0;
    }

    // Fast sampling check - exit immediately if not capturing
    if (g_enable_sampling && !should_sample()) {
        g_in_profiler = 0;
        return 0;
    }

    // MASTER KILL SWITCH: If SF_ENABLE_FUNCTION_SPANS=false, hard disable
    // Profiler hooks still run (lightweight), but skip ALL expensive work:
    // - No config lookup
    // - No argument/return serialization
    // - No libcurl transmission
    // NOTHING can override this (not headers, not decorators, nothing)
    if (!g_enable_function_spans) {
        g_in_profiler = 0;
        return 0;
    }

    if (call_count < 5) {
        fprintf(stderr, "[_sffuncspan] DEBUG: Getting code object\n");
        fflush(stderr);
    }

    PyCodeObject *code = PyFrame_GetCode(frame);
    if (!code) {
        g_in_profiler = 0;
        return 0;
    }

    if (call_count < 5) {
        fprintf(stderr, "[_sffuncspan] DEBUG: Got code object\n");
        fflush(stderr);
    }

    // DEFENSIVE: Check for NULL before calling PyUnicode_AsUTF8
    if (!code->co_filename || !code->co_name) {
        Py_DECREF(code);
        g_in_profiler = 0;
        return 0;
    }

    if (call_count < 5) {
        fprintf(stderr, "[_sffuncspan] DEBUG: About to call PyUnicode_AsUTF8\n");
        fflush(stderr);
    }

    const char *filename = PyUnicode_AsUTF8(code->co_filename);
    const char *funcname = PyUnicode_AsUTF8(code->co_name);

    if (call_count < 5) {
        fprintf(stderr, "[_sffuncspan] DEBUG: Got filename=%s, funcname=%s\n",
                filename ? filename : "NULL", funcname ? funcname : "NULL");
        fflush(stderr);
    }

    // Fast path: Skip if no filename/funcname
    if (!filename || !funcname) {
        Py_DECREF(code);
        g_in_profiler = 0;
        return 0;
    }

    if (call_count < 5) {
        fprintf(stderr, "[_sffuncspan] DEBUG: About to check dunder methods\n");
        fflush(stderr);
    }

    // Fast path: Skip dunder methods
    if (funcname[0] == '_' && funcname[1] == '_') {
        // if (SF_DEBUG) {
        //     fprintf(stderr, "[_sffuncspan] FILTERED: %s::%s - dunder method\n", filename, funcname);
        //     fflush(stderr);
        // }
        Py_DECREF(code);
        g_in_profiler = 0;
        return 0;
    }

    if (call_count < 5) {
        fprintf(stderr, "[_sffuncspan] DEBUG: About to check sf_veritas\n");
        fflush(stderr);
    }

    // CRITICAL: Check for sf_veritas code FIRST, before Python stdlib check!
    // sf_veritas files are often in paths like /lib/python3.9/site-packages/sf_veritas/
    // which would match the stdlib filter, so we must check this first.
    int is_sf_veritas = (strstr(filename, "sf_veritas") != NULL);

    if (call_count < 5) {
        fprintf(stderr, "[_sffuncspan] DEBUG: is_sf_veritas=%d\n", is_sf_veritas);
        fflush(stderr);
    }

    // If it's sf_veritas and we don't want to capture it, skip early
    if (is_sf_veritas && !g_capture_sf_veritas) {
        // if (SF_DEBUG) {
        //     fprintf(stderr, "[_sffuncspan] FILTERED: %s::%s - sf_veritas code (capture_sf_veritas=false)\n", filename, funcname);
        //     fflush(stderr);
        // }
        Py_DECREF(code);
        g_in_profiler = 0;
        return 0;
    }

    // Fast path: ALWAYS skip Python stdlib, frozen modules, bootstrap code
    // These are Python internals, never capture them
    // BUT: Skip this check if it's sf_veritas (already handled above)
    if (!is_sf_veritas) {
        if (strstr(filename, "/lib/python") ||
            strstr(filename, "\\lib\\python") ||
            strstr(filename, "<frozen") ||
            strstr(filename, "<string>") ||
            strstr(filename, "importlib") ||
            strstr(filename, "_bootstrap")) {
            // if (SF_DEBUG) {
            //     fprintf(stderr, "[_sffuncspan] FILTERED: %s::%s - Python stdlib/internals\n", filename, funcname);
            //     fflush(stderr);
            // }
            Py_DECREF(code);
            g_in_profiler = 0;
            return 0;
        }
    }

    // Conditionally skip installed packages (site-packages)
    // BUT: if it's sf_veritas and we want to capture it, don't skip (already handled above)
    if (!g_capture_installed_packages && !is_sf_veritas) {
        if (strstr(filename, "site-packages") ||
            strstr(filename, "dist-packages")) {
            // if (SF_DEBUG) {
            //     fprintf(stderr, "[_sffuncspan] FILTERED: %s::%s - site-packages (capture_installed_packages=false)\n", filename, funcname);
            //     fflush(stderr);
            // }
            Py_DECREF(code);
            g_in_profiler = 0;
            return 0;
        }
    }

    // Skip Django view functions unless explicitly enabled
    if (!g_include_django_view_functions) {
        // Check if this is a Django view function (filename ends with views.py or views/__init__.py)
        const char *views_py = strstr(filename, "views.py");
        const char *views_init = strstr(filename, "views/__init__.py");
        if (views_py || views_init) {
            // Make sure it's actually the end of the path (not just a substring)
            size_t flen = strlen(filename);
            if ((views_py && (views_py == filename + flen - 8)) ||  // ends with "views.py"
                (views_init && (views_init == filename + flen - 17))) {  // ends with "views/__init__.py"
                // if (SF_DEBUG) {
                //     fprintf(stderr, "[_sffuncspan] FILTERED: %s::%s - Django view function (include_django_view_functions=false)\n", filename, funcname);
                //     fflush(stderr);
                // }
                Py_DECREF(code);
                g_in_profiler = 0;
                return 0;
            }
        }
    }

    if (what == PyTrace_CALL) {
        // Look up config for this function
        sf_funcspan_config_t func_config = get_function_config(filename, funcname);

        // Debug: Log when a function is ACCEPTED (passed all filters)
        if (SF_DEBUG) {
            int accepted_count = atomic_fetch_add(&g_debug_accepted_count, 1);
            if (accepted_count < 10) {
                fprintf(stderr, "[_sffuncspan] ACCEPTED: %s::%s (event=CALL, capture_installed_packages=%d, capture_sf_veritas=%d)\n",
                        filename, funcname, g_capture_installed_packages, g_capture_sf_veritas);
                fflush(stderr);
            }
        }

        // Per-function sampling check (sample_rate is 0.0-1.0)
        if (func_config.sample_rate < 1.0f) {
            // Generate a random float between 0.0 and 1.0
            static _Atomic uint64_t g_per_func_sample_counter = 0;
            uint64_t sample_val = atomic_fetch_add(&g_per_func_sample_counter, 1);
            // Simple LCG for pseudo-random: multiply by large prime, modulo 2^32
            sample_val = (sample_val * 1103515245 + 12345) & 0x7FFFFFFF;
            float rand_val = (float)sample_val / (float)0x7FFFFFFF;

            if (rand_val >= func_config.sample_rate) {
                Py_DECREF(code);
                atomic_fetch_add(&g_spans_sampled_out, 1);
                g_in_profiler = 0;
                return 0;  // Skip this span
            }
        }

        // Push frame onto call stack (ultra-minimal allocation)
        call_frame_t *new_frame = (call_frame_t*)malloc(sizeof(call_frame_t));
        if (!new_frame) {
            Py_DECREF(code);
            g_in_profiler = 0;
            return 0;
        }

        new_frame->start_ns = now_epoch_ns();
        new_frame->span_id = generate_span_id();

        // CRITICAL: OWN the strings! PyUnicode_AsUTF8() returns borrowed pointers owned by the code object.
        // When we Py_DECREF(code), those pointers become invalid. Duplicate them now while code is alive.
        new_frame->function_name = funcname ? str_dup(funcname) : str_dup("<unknown>");
        new_frame->file_path = filename ? str_dup(filename) : str_dup("");

        // Check if str_dup failed (malloc failure)
        if (!new_frame->function_name || !new_frame->file_path) {
            if (new_frame->function_name) free(new_frame->function_name);
            if (new_frame->file_path) free(new_frame->file_path);
            if (new_frame->span_id) free(new_frame->span_id);
            free(new_frame);
            Py_DECREF(code);
            g_in_profiler = 0;
            return 0;
        }

        new_frame->line_number = PyFrame_GetLineNumber(frame);
        new_frame->frame = frame;  // Borrowed! (for argument capture on return)

        // Capture arguments NOW (on function entry) if enabled by THIS function's config
        if (func_config.include_arguments) {
            // Use per-function arg limit
            size_t arg_limit = func_config.arg_limit_mb * 1048576;
            // Temporarily set global for capture_arguments_from_frame to use
            size_t saved_limit = g_arg_limit_bytes;
            g_arg_limit_bytes = arg_limit;
            new_frame->arguments_json = capture_arguments_from_frame(frame);
            g_arg_limit_bytes = saved_limit;
        } else {
            new_frame->arguments_json = NULL;
        }

        // Store config in frame so PyTrace_RETURN uses same config (handles HTTP header overrides)
        new_frame->config = func_config;

        new_frame->parent = get_call_stack();
        set_call_stack(new_frame);

    } else if (what == PyTrace_RETURN || what == PyTrace_EXCEPTION) {
        // Pop frame and record span
        call_frame_t *current = get_call_stack();
        if (!current) {
            Py_DECREF(code);
            g_in_profiler = 0;
            return 0;
        }

        uint64_t end_ns = now_epoch_ns();
        uint64_t duration_ns = end_ns - current->start_ns;

        // Get session ID from thread-local (fast path: use cached TLS)
        // For now, use a simple thread ID as session (avoid Python call overhead)
        char session_buf[32];
        snprintf(session_buf, sizeof(session_buf), "thread-%lu", (unsigned long)pthread_self());

        // Get parent span ID
        const char *parent_span_id = current->parent ? current->parent->span_id : NULL;

        // Use config stored during PyTrace_CALL (ensures consistent config even if HTTP headers change)
        sf_funcspan_config_t func_config = current->config;

        // Capture return value if enabled by config and it's a normal return (not exception)
        char *return_value_json = NULL;
        if (func_config.include_return_value && what == PyTrace_RETURN && arg) {
            size_t return_limit = func_config.return_limit_mb * 1048576;
            return_value_json = serialize_python_object_to_json(arg, return_limit);
        }

        // Get arguments JSON (already captured on function entry, or NULL if disabled)
        const char *arguments_json = current->arguments_json ? current->arguments_json : "{}";

        // Build span body and push to ring - RELEASE GIL for both!
        // This is the KEY optimization from Opportunity #2
        char *body = NULL;
        size_t len = 0;
        int ok = 0;

        // OPPORTUNITY #2 OPTIMIZATION: Release GIL during JSON build + ring push
        Py_BEGIN_ALLOW_THREADS
        if (build_body_func_span(
                session_buf,
                current->span_id,
                parent_span_id,
                current->file_path,
                current->line_number,
                0, // column_number,
                current->function_name,
                arguments_json,
                return_value_json,
                current->start_ns,
                duration_ns,
                &body,
                &len)) {

            // Push to ring buffer (still GIL-free)
            ok = ring_push(body, len);
        }
        Py_END_ALLOW_THREADS

        if (!ok) {
            free(body);
        }

        // Pop from stack
        set_call_stack(current->parent);
        free(current->span_id);
        // CRITICAL: Free owned strings (we duplicated them on CALL to prevent UAF)
        if (current->function_name) free(current->function_name);
        if (current->file_path) free(current->file_path);
        if (current->arguments_json) free(current->arguments_json);
        if (return_value_json) free(return_value_json);
        free(current);
    }

    Py_DECREF(code);
    g_in_profiler = 0;
    return 0;
}

// ---------- Python API ----------
static PyObject *py_init(PyObject *self, PyObject *args, PyObject *kw) {
    const char *url, *query, *api_key, *service_uuid, *library, *version;
    int http2 = 0;
    static char *kwlist[] = {"url","query","api_key","service_uuid","library","version","http2", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kw, "ssssssi",
        kwlist, &url, &query, &api_key, &service_uuid, &library, &version, &http2)) {
        Py_RETURN_FALSE;
    }
    if (g_running) Py_RETURN_TRUE;

    g_url = str_dup(url);
    g_func_span_query_escaped = json_escape_query(query);
    g_api_key = str_dup(api_key);
    g_service_uuid = str_dup(service_uuid);
    g_library = str_dup(library);
    g_version = str_dup(version);
    g_http2 = http2 ? 1 : 0;
    if (!g_url || !g_func_span_query_escaped || !g_api_key || !g_service_uuid || !g_library || !g_version) {
        Py_RETURN_FALSE;
    }
    if (!build_prefix_for_query(g_func_span_query_escaped, &g_json_prefix_func_span)) {
        Py_RETURN_FALSE;
    }

    g_cap = SFFS_RING_CAP;
    g_ring = (sffs_msg_t*)calloc(g_cap, sizeof(sffs_msg_t));
    if (!g_ring) { Py_RETURN_FALSE; }

    curl_global_init(CURL_GLOBAL_DEFAULT);
    g_hdrs = NULL;
    g_hdrs = curl_slist_append(g_hdrs, "Content-Type: application/json");

    // Initialize config system integration
    init_config_system();

    // Initialize SF_DEBUG from environment
    const char *debug_env = getenv("SF_DEBUG");
    if (debug_env && (strcmp(debug_env, "1") == 0 || strcmp(debug_env, "true") == 0 || strcmp(debug_env, "True") == 0)) {
        SF_DEBUG = 1;
        fprintf(stderr, "[_sffuncspan] SF_DEBUG enabled\n");
        fflush(stderr);
    }

    // Parse SF_FUNCSPAN_SENDER_THREADS environment variable (default: 4, max: 16)
    // FuncSpan expected to have HIGH volume, so default to 4 threads
    const char *num_threads_env = getenv("SF_FUNCSPAN_SENDER_THREADS");
    g_num_sender_threads = num_threads_env ? atoi(num_threads_env) : 4;
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

static PyObject *py_configure(PyObject *self, PyObject *args, PyObject *kw) {
    PyObject *capture_from_installed_libraries = NULL;
    int variable_capture_size_limit_mb = 1;  // default 1MB (deprecated, use arg_limit/return_limit)
    float sample_rate = 1.0f;  // default 1.0 = capture all (probabilistic 0.0-1.0)
    int enable_sampling = 0;  // default disabled
    int parse_json_strings = 1;  // default enabled
    int capture_arguments = 1;  // default enabled
    int capture_return_value = 1;  // default enabled
    int arg_limit_mb = 1;  // default 1MB for arguments
    int return_limit_mb = 1;  // default 1MB for return values
    int include_django_view_functions = 0;  // default disabled

    static char *kwlist[] = {
        "variable_capture_size_limit_mb",
        "capture_from_installed_libraries",
        "sample_rate",
        "enable_sampling",
        "parse_json_strings",
        "capture_arguments",
        "capture_return_value",
        "arg_limit_mb",
        "return_limit_mb",
        "include_django_view_functions",
        NULL
    };

    if (!PyArg_ParseTupleAndKeywords(args, kw, "|iOfppppiip", kwlist,
                                     &variable_capture_size_limit_mb,
                                     &capture_from_installed_libraries,
                                     &sample_rate,
                                     &enable_sampling,
                                     &parse_json_strings,
                                     &capture_arguments,
                                     &capture_return_value,
                                     &arg_limit_mb,
                                     &return_limit_mb,
                                     &include_django_view_functions)) {
        Py_RETURN_NONE;
    }

    // Legacy: if variable_capture_size_limit_mb is set but not arg/return limits,
    // use it for both
    if (arg_limit_mb == 1 && return_limit_mb == 1 && variable_capture_size_limit_mb != 1) {
        arg_limit_mb = variable_capture_size_limit_mb;
        return_limit_mb = variable_capture_size_limit_mb;
    }

    g_variable_capture_size_limit_bytes = (size_t)variable_capture_size_limit_mb * 1048576;
    g_arg_limit_bytes = (size_t)arg_limit_mb * 1048576;
    g_return_limit_bytes = (size_t)return_limit_mb * 1048576;

    if (capture_from_installed_libraries && PyList_Check(capture_from_installed_libraries)) {
        Py_XDECREF(g_capture_from_installed_libraries);
        Py_INCREF(capture_from_installed_libraries);
        g_capture_from_installed_libraries = capture_from_installed_libraries;
    }

    // Configure sampling
    // sample_rate is now a float (0.0-1.0 probability)
    // Convert to old modulo format: 1.0=capture all(1), 0.5=capture 50%(2), 0.1=capture 10%(10), etc.
    if (sample_rate < 0.001f) sample_rate = 0.001f;  // Minimum 0.1% (1 in 1000)
    if (sample_rate > 1.0f) sample_rate = 1.0f;  // Maximum 100%
    g_sample_rate = (uint64_t)(1.0f / sample_rate);  // Convert probability to modulo divisor
    g_enable_sampling = enable_sampling;

    // Configure JSON parsing
    g_parse_json_strings = parse_json_strings;

    // Configure capture control
    g_capture_arguments = capture_arguments;
    g_capture_return_value = capture_return_value;

    // Configure Django view function filtering
    g_include_django_view_functions = include_django_view_functions;

    Py_RETURN_NONE;
}

// ---------- Fast C-based object serialization ----------
// Serialize any Python object to JSON string, with aggressive introspection
// Returns malloc'd JSON string, caller must free()
static char* serialize_python_object_to_json(PyObject *value, size_t max_size) {
    if (!value) {
        return str_dup("null");
    }

    // Fast path: Try direct JSON serialization for primitives
    if (PyUnicode_Check(value)) {
        const char *str = PyUnicode_AsUTF8(value);
        if (!str) return str_dup("null");

        // Try to parse as JSON if enabled and string looks like JSON
        if (g_parse_json_strings && str[0] && (str[0] == '{' || str[0] == '[')) {
            // Import json module and try to parse
            PyObject *json_module = PyImport_ImportModule("json");
            if (json_module) {
                PyObject *loads_func = PyObject_GetAttrString(json_module, "loads");
                if (loads_func && PyCallable_Check(loads_func)) {
                    PyObject *args = PyTuple_Pack(1, value);
                    if (args) {
                        PyObject *parsed = PyObject_CallObject(loads_func, args);
                        Py_DECREF(args);

                        if (parsed && !PyErr_Occurred()) {
                            // Successfully parsed! Recursively serialize the parsed object
                            char *parsed_json = serialize_python_object_to_json(parsed, max_size);
                            Py_DECREF(parsed);
                            Py_XDECREF(loads_func);
                            Py_DECREF(json_module);
                            return parsed_json;
                        }

                        // Failed to parse, clear error and continue with string
                        Py_XDECREF(parsed);
                        if (PyErr_Occurred()) PyErr_Clear();
                    }
                }
                Py_XDECREF(loads_func);
                Py_DECREF(json_module);
            }
            if (PyErr_Occurred()) PyErr_Clear();
        }

        // Regular string serialization (not JSON or parsing disabled)
        // Check if string length exceeds max_size
        size_t str_len = strlen(str);

        if (str_len > max_size) {
            // Truncate the string to max_size
            char *truncated_str = (char*)malloc(max_size + 20);  // Extra space for <<TRIMMED>>
            if (!truncated_str) return str_dup("null");

            // Copy up to max_size bytes
            memcpy(truncated_str, str, max_size);
            strcpy(truncated_str + max_size, "<<TRIMMED>>");

            char *escaped = json_escape(truncated_str);
            free(truncated_str);
            if (!escaped) return str_dup("null");

            size_t len = strlen(escaped) + 3; // quotes + null
            char *result = (char*)malloc(len);
            if (!result) { free(escaped); return str_dup("null"); }
            snprintf(result, len, "\"%s\"", escaped);
            free(escaped);
            return result;
        }

        // String is within size limit, serialize normally
        char *escaped = json_escape(str);
        if (!escaped) return str_dup("null");
        size_t len = strlen(escaped) + 3; // quotes + null
        char *result = (char*)malloc(len);
        if (!result) { free(escaped); return str_dup("null"); }
        snprintf(result, len, "\"%s\"", escaped);
        free(escaped);
        return result;
    }

    // Check bool BEFORE int (since bool is a subclass of int in Python)
    if (PyBool_Check(value)) {
        return str_dup(value == Py_True ? "true" : "false");
    }

    if (PyLong_Check(value)) {
        long long num = PyLong_AsLongLong(value);
        char *result = (char*)malloc(32);
        if (!result) return str_dup("null");
        snprintf(result, 32, "%lld", num);
        return result;
    }

    if (PyFloat_Check(value)) {
        double num = PyFloat_AsDouble(value);
        char *result = (char*)malloc(32);
        if (!result) return str_dup("null");
        snprintf(result, 32, "%.17g", num);
        return result;
    }

    if (value == Py_None) {
        return str_dup("null");
    }

    // Bytes - try to decode as UTF-8, fallback to repr
    if (PyBytes_Check(value)) {
        char *bytes_data = NULL;
        Py_ssize_t bytes_len = 0;

        if (PyBytes_AsStringAndSize(value, &bytes_data, &bytes_len) == 0 && bytes_data) {
            // Try to decode as UTF-8
            PyObject *decoded = PyUnicode_DecodeUTF8(bytes_data, bytes_len, "strict");
            if (decoded && PyUnicode_Check(decoded)) {
                // Successfully decoded to string - recursively serialize it
                // This will trigger JSON parsing if enabled and string contains JSON
                char *result = serialize_python_object_to_json(decoded, max_size);
                Py_DECREF(decoded);
                return result;
            }
            Py_XDECREF(decoded);
            if (PyErr_Occurred()) PyErr_Clear();
        }

        // Fallback: not UTF-8 or decode failed, use repr (b'...')
        PyObject *repr_obj = PyObject_Repr(value);
        if (repr_obj && PyUnicode_Check(repr_obj)) {
            const char *repr_str = PyUnicode_AsUTF8(repr_obj);
            if (repr_str) {
                char *escaped = json_escape(repr_str);
                Py_DECREF(repr_obj);
                if (!escaped) return str_dup("null");
                size_t len = strlen(escaped) + 3;
                char *result = (char*)malloc(len);
                if (!result) { free(escaped); return str_dup("null"); }
                snprintf(result, len, "\"%s\"", escaped);
                free(escaped);
                return result;
            }
        }
        Py_XDECREF(repr_obj);
        if (PyErr_Occurred()) PyErr_Clear();
    }

    // Tuples - serialize as JSON arrays
    if (PyTuple_Check(value)) {
        Py_ssize_t tuple_len = PyTuple_Size(value);
        if (tuple_len > 100) tuple_len = 100;

        size_t buf_size = 4096;
        char *buf = (char*)malloc(buf_size);
        if (!buf) return str_dup("null");
        size_t pos = 0;
        buf[pos++] = '[';

        for (Py_ssize_t i = 0; i < tuple_len; i++) {
            PyObject *item = PyTuple_GetItem(value, i);
            char *item_json = serialize_python_object_to_json(item, max_size / 10);
            size_t item_len = strlen(item_json);

            if (pos + item_len + 2 >= buf_size) {
                free(item_json);
                break;
            }

            if (i > 0) buf[pos++] = ',';
            memcpy(buf + pos, item_json, item_len);
            pos += item_len;
            free(item_json);
        }

        buf[pos++] = ']';
        buf[pos] = '\0';
        return buf;
    }

    // Lists
    if (PyList_Check(value)) {
        Py_ssize_t list_len = PyList_Size(value);
        if (list_len > 100) list_len = 100; // Limit list introspection

        size_t buf_size = 4096;
        char *buf = (char*)malloc(buf_size);
        if (!buf) return str_dup("null");
        size_t pos = 0;
        buf[pos++] = '[';

        for (Py_ssize_t i = 0; i < list_len; i++) {
            PyObject *item = PyList_GetItem(value, i);
            char *item_json = serialize_python_object_to_json(item, max_size / 10);
            size_t item_len = strlen(item_json);

            if (pos + item_len + 2 >= buf_size) {
                free(item_json);
                break; // truncate
            }

            if (i > 0) buf[pos++] = ',';
            memcpy(buf + pos, item_json, item_len);
            pos += item_len;
            free(item_json);
        }

        buf[pos++] = ']';
        buf[pos] = '\0';
        return buf;
    }

    // Dicts
    if (PyDict_Check(value)) {
        PyObject *key, *val;
        Py_ssize_t dict_pos = 0;
        int count = 0;

        size_t buf_size = 8192;
        char *buf = (char*)malloc(buf_size);
        if (!buf) return str_dup("null");
        size_t pos = 0;
        buf[pos++] = '{';

        while (PyDict_Next(value, &dict_pos, &key, &val) && count < 50) {
            const char *key_str = PyUnicode_Check(key) ? PyUnicode_AsUTF8(key) : NULL;
            if (!key_str) continue;

            // Skip private/dunder keys
            if (key_str[0] == '_') continue;

            char *key_escaped = json_escape(key_str);
            char *val_json = serialize_python_object_to_json(val, max_size / 10);

            size_t needed = strlen(key_escaped) + strlen(val_json) + 5;
            if (pos + needed >= buf_size) {
                free(key_escaped);
                free(val_json);
                break; // truncate
            }

            if (count > 0) buf[pos++] = ',';
            buf[pos++] = '"';
            size_t key_len = strlen(key_escaped);
            memcpy(buf + pos, key_escaped, key_len);
            pos += key_len;
            buf[pos++] = '"';
            buf[pos++] = ':';
            size_t val_len = strlen(val_json);
            memcpy(buf + pos, val_json, val_len);
            pos += val_len;

            free(key_escaped);
            free(val_json);
            count++;
        }

        buf[pos++] = '}';
        buf[pos] = '\0';
        return buf;
    }

    // Complex object introspection - build result dict
    PyObject *type_obj = PyObject_Type(value);
    if (!type_obj) {
        PyErr_Clear();
        return str_dup("null");
    }

    PyObject *type_name_obj = PyObject_GetAttrString(type_obj, "__name__");
    if (!type_name_obj) PyErr_Clear();

    PyObject *module_obj = PyObject_GetAttrString(type_obj, "__module__");
    if (!module_obj) PyErr_Clear();

    const char *type_name = type_name_obj && PyUnicode_Check(type_name_obj) ? PyUnicode_AsUTF8(type_name_obj) : "unknown";
    const char *module_name = module_obj && PyUnicode_Check(module_obj) ? PyUnicode_AsUTF8(module_obj) : "builtins";

    // Use a larger buffer to accommodate trimmed large attributes
    // max_size / 20 per attribute + overhead = could be 50KB+ per attribute
    // Allow room for ~10 attributes of max size
    size_t buf_size = (max_size / 2) > 16384 ? (max_size / 2) : 16384;
    if (buf_size > 1048576) buf_size = 1048576; // Cap at 1MB

    char *buf = (char*)malloc(buf_size);
    if (!buf) {
        Py_XDECREF(type_obj);
        Py_XDECREF(type_name_obj);
        Py_XDECREF(module_obj);
        return str_dup("null");
    }

    size_t pos = 0;
    buf[pos++] = '{';

    // Add _type field
    if (strcmp(module_name, "builtins") == 0) {
        pos += snprintf(buf + pos, buf_size - pos, "\"_type\":\"%s\"", type_name);
    } else {
        pos += snprintf(buf + pos, buf_size - pos, "\"_type\":\"%s.%s\"", module_name, type_name);
    }

    int added_attrs = 0;

    // Try __dict__ introspection
    PyObject *obj_dict = PyObject_GetAttrString(value, "__dict__");
    if (PyErr_Occurred()) PyErr_Clear();

    if (obj_dict && PyDict_Check(obj_dict)) {
        PyObject *key, *val;
        Py_ssize_t dict_pos = 0;
        int attr_count = 0;

        if (!added_attrs) {
            pos += snprintf(buf + pos, buf_size - pos, ",\"attributes\":{");
            added_attrs = 1;
        }

        while (PyDict_Next(obj_dict, &dict_pos, &key, &val) && attr_count < 30) {
            const char *key_str = PyUnicode_Check(key) ? PyUnicode_AsUTF8(key) : NULL;
            if (!key_str || key_str[0] == '_') continue; // Skip private

            // Skip callables (methods)
            if (PyCallable_Check(val)) continue;

            char *key_escaped = json_escape(key_str);
            char *val_json = serialize_python_object_to_json(val, max_size / 20);

            size_t needed = strlen(key_escaped) + strlen(val_json) + 5;
            if (pos + needed >= buf_size - 100) {
                free(key_escaped);
                free(val_json);
                break;
            }

            if (attr_count > 0) buf[pos++] = ',';
            pos += snprintf(buf + pos, buf_size - pos, "\"%s\":%s", key_escaped, val_json);

            free(key_escaped);
            free(val_json);
            attr_count++;
        }

        if (added_attrs) {
            buf[pos++] = '}';
        }
    }
    Py_XDECREF(obj_dict);
    if (PyErr_Occurred()) PyErr_Clear();

    // Try common data attributes
    const char *data_attrs[] = {"data", "value", "content", "body", "result", "message", "text", NULL};
    for (int i = 0; data_attrs[i]; i++) {
        PyObject *attr = PyObject_GetAttrString(value, data_attrs[i]);
        if (PyErr_Occurred()) PyErr_Clear();

        if (attr && !PyCallable_Check(attr)) {
            char *attr_json = serialize_python_object_to_json(attr, max_size / 20);
            size_t needed = strlen(data_attrs[i]) + strlen(attr_json) + 5;

            if (pos + needed < buf_size - 100) {
                pos += snprintf(buf + pos, buf_size - pos, ",\"%s\":%s", data_attrs[i], attr_json);
            }

            free(attr_json);
        }
        Py_XDECREF(attr);
    }
    if (PyErr_Occurred()) PyErr_Clear();

    // Note: We removed _repr from the root level for cleaner output
    // The attributes and common data fields provide enough context

    buf[pos++] = '}';
    buf[pos] = '\0';

    Py_XDECREF(type_obj);
    Py_XDECREF(type_name_obj);
    Py_XDECREF(module_obj);

    // Check size limit
    if (pos > max_size) {
        free(buf);
        char *truncated = (char*)malloc(256);
        snprintf(truncated, 256, "{\"_truncated\":true,\"_size\":%zu,\"_type\":\"%s.%s\"}",
                 pos, module_name, type_name);
        return truncated;
    }

    return buf;
}

static PyObject *py_serialize_value(PyObject *self, PyObject *args) {
    PyObject *value;
    size_t max_size = 1048576; // 1MB default

    if (!PyArg_ParseTuple(args, "O|n", &value, &max_size)) {
        Py_RETURN_NONE;
    }

    char *json_str = serialize_python_object_to_json(value, max_size);
    if (!json_str) {
        Py_RETURN_NONE;
    }

    PyObject *result = PyUnicode_FromString(json_str);
    free(json_str);
    return result;
}

static PyObject *py_record_span(PyObject *self, PyObject *args, PyObject *kw) {
    const char *session_id, *span_id, *parent_span_id = NULL;
    const char *file_path, *function_name, *arguments_json, *return_value_json = NULL;
    int line_number = 0, column_number = 0;
    unsigned long long start_time_ns = 0, duration_ns = 0;

    static char *kwlist[] = {
        "session_id", "span_id", "parent_span_id", "file_path", "line_number",
        "column_number", "function_name", "arguments_json", "return_value_json",
        "start_time_ns", "duration_ns", NULL
    };

    if (!PyArg_ParseTupleAndKeywords(args, kw, "sszsiissz|KK", kwlist,
                                     &session_id, &span_id, &parent_span_id,
                                     &file_path, &line_number, &column_number,
                                     &function_name, &arguments_json, &return_value_json,
                                     &start_time_ns, &duration_ns)) {
        Py_RETURN_NONE;
    }
    if (!g_running) Py_RETURN_NONE;

    // Fast sampling check - exit early if not sampling this span
    if (!should_sample()) {
        Py_RETURN_NONE;
    }

    // OPTIMIZATION: Release GIL during JSON building + ring push
    // All string arguments are already C strings from PyArg_ParseTupleAndKeywords,
    // so we can safely release GIL for the entire body building + transmission.
    // This extends GIL-free duration from ~100ns to ~500-2000ns (5-20x improvement).
    char *body = NULL;
    size_t len = 0;
    int ok = 0;

    Py_BEGIN_ALLOW_THREADS
    // Build JSON body (WITHOUT GIL - pure C string operations)
    if (build_body_func_span(
            session_id, span_id, parent_span_id,
            file_path, line_number, column_number,
            function_name, arguments_json, return_value_json,
            (uint64_t)start_time_ns, (uint64_t)duration_ns,
            &body, &len)) {
        // Push to ring buffer (WITHOUT GIL)
        ok = ring_push(body, len);
    }
    Py_END_ALLOW_THREADS

    if (!ok) { free(body); }
    Py_RETURN_NONE;
}

static PyObject *py_generate_span_id(PyObject *self, PyObject *args) {
    char *span_id = generate_span_id();
    if (!span_id) Py_RETURN_NONE;
    PyObject *result = PyUnicode_FromString(span_id);
    free(span_id);
    return result;
}

static PyObject *py_push_span(PyObject *self, PyObject *args) {
    const char *span_id;
    if (!PyArg_ParseTuple(args, "s", &span_id)) {
        Py_RETURN_NONE;
    }
    push_span(span_id);
    Py_RETURN_NONE;
}

static PyObject *py_pop_span(PyObject *self, PyObject *args) {
    char *span_id = pop_span();
    if (!span_id) Py_RETURN_NONE;
    PyObject *result = PyUnicode_FromString(span_id);
    free(span_id);
    return result;
}

static PyObject *py_peek_parent_span_id(PyObject *self, PyObject *args) {
    char *parent_span_id = peek_parent_span_id();
    if (!parent_span_id) Py_RETURN_NONE;
    PyObject *result = PyUnicode_FromString(parent_span_id);
    free(parent_span_id);
    return result;
}

static PyObject *py_get_epoch_ns(PyObject *self, PyObject *args) {
    uint64_t ns = now_epoch_ns();
    return PyLong_FromUnsignedLongLong(ns);
}

static PyObject *py_get_stats(PyObject *self, PyObject *args) {
    uint64_t recorded = atomic_load(&g_spans_recorded);
    uint64_t sampled_out = atomic_load(&g_spans_sampled_out);
    uint64_t dropped = atomic_load(&g_spans_dropped);
    size_t buffer_size = ring_count();

    PyObject *dict = PyDict_New();
    if (!dict) Py_RETURN_NONE;

    PyDict_SetItemString(dict, "spans_recorded", PyLong_FromUnsignedLongLong(recorded));
    PyDict_SetItemString(dict, "spans_sampled_out", PyLong_FromUnsignedLongLong(sampled_out));
    PyDict_SetItemString(dict, "spans_dropped", PyLong_FromUnsignedLongLong(dropped));
    PyDict_SetItemString(dict, "ring_buffer_used", PyLong_FromSize_t(buffer_size));
    PyDict_SetItemString(dict, "ring_buffer_capacity", PyLong_FromSize_t(g_cap));
    PyDict_SetItemString(dict, "sample_rate", PyLong_FromUnsignedLongLong(g_sample_rate));
    PyDict_SetItemString(dict, "sampling_enabled", PyBool_FromLong(g_enable_sampling));

    return dict;
}

static PyObject *py_reset_stats(PyObject *self, PyObject *args) {
    atomic_store(&g_spans_recorded, 0);
    atomic_store(&g_spans_sampled_out, 0);
    atomic_store(&g_spans_dropped, 0);
    atomic_store(&g_sample_counter, 0);
    Py_RETURN_NONE;
}

// Global flag to enable profiler for new threads
static _Atomic int g_profiler_enabled = 0;

// Thread start callback to enable profiler on new threads
static void thread_start_callback(PyThreadState *tstate) {
    if (atomic_load(&g_profiler_enabled)) {
        PyEval_SetProfile(c_profile_func, NULL);
    }
}

static PyObject *py_start_c_profiler(PyObject *self, PyObject *args) {
    if (!g_running) {
        PyErr_SetString(PyExc_RuntimeError, "Profiler not initialized - call init() first");
        return NULL;
    }

    // Check if profiler is already running - prevent double installation
    if (atomic_load(&g_profiler_ready)) {
        // fprintf(stderr, "[_sffuncspan] WARNING: Profiler already running, skipping duplicate start_c_profiler() call\n");
        // fflush(stderr);
        Py_RETURN_NONE;
    }

    fprintf(stderr, "[_sffuncspan] Installing C profiler...\n");
    fflush(stderr);

    // Enable profiler flag for new threads
    atomic_store(&g_profiler_enabled, 1);

    // Set the C-level profiler for current thread (ultra-fast!)
    PyEval_SetProfile(c_profile_func, NULL);

    // CRITICAL: Mark profiler as ready AFTER PyEval_SetProfile() completes
    // This ensures any profiler callbacks during installation will skip early
    atomic_store(&g_profiler_ready, 1);

    fprintf(stderr, "[_sffuncspan] C profiler installed successfully\n");
    fflush(stderr);

    // Note: For Python 3.12+, we'd use PyEval_SetProfileAllThreads
    // For earlier versions, we rely on threading.setprofile in Python wrapper

    Py_RETURN_NONE;
}

static PyObject *py_stop_c_profiler(PyObject *self, PyObject *args) {
    // Mark profiler as not ready
    atomic_store(&g_profiler_ready, 0);

    // Disable profiler flag for new threads
    atomic_store(&g_profiler_enabled, 0);

    // Remove the C-level profiler
    PyEval_SetProfile(NULL, NULL);

    Py_RETURN_NONE;
}

static PyObject *py_cache_config(PyObject *self, PyObject *args) {
    const char *file_path;
    const char *func_name;
    int include_arguments;
    int include_return_value;
    int autocapture_all_children;
    int arg_limit_mb;
    int return_limit_mb;
    float sample_rate;

    if (!PyArg_ParseTuple(args, "ssiiiiff",
                          &file_path, &func_name,
                          &include_arguments, &include_return_value,
                          &autocapture_all_children,
                          &arg_limit_mb, &return_limit_mb, &sample_rate)) {
        Py_RETURN_NONE;
    }

    // Build config
    sf_funcspan_config_t config;
    config.include_arguments = (uint8_t)include_arguments;
    config.include_return_value = (uint8_t)include_return_value;
    config.autocapture_all_children = (uint8_t)autocapture_all_children;
    config.arg_limit_mb = (uint32_t)arg_limit_mb;
    config.return_limit_mb = (uint32_t)return_limit_mb;
    config.sample_rate = sample_rate;

    // Compute hash and cache
    uint64_t hash = simple_hash(file_path, func_name);
    uint32_t cache_idx = hash % CONFIG_CACHE_SIZE;

    pthread_mutex_lock(&g_config_cache_mutex);
    g_config_cache[cache_idx].hash = hash;
    g_config_cache[cache_idx].config = config;
    pthread_mutex_unlock(&g_config_cache_mutex);

    Py_RETURN_NONE;
}

static PyObject *py_set_function_spans_enabled(PyObject *self, PyObject *args) {
    int enabled;
    if (!PyArg_ParseTuple(args, "p", &enabled)) {
        return NULL;
    }
    g_enable_function_spans = enabled;
    Py_RETURN_NONE;
}

static PyObject *py_set_capture_installed_packages(PyObject *self, PyObject *args) {
    int enabled;
    if (!PyArg_ParseTuple(args, "p", &enabled)) {
        return NULL;
    }
    g_capture_installed_packages = enabled;
    Py_RETURN_NONE;
}

static PyObject *py_set_capture_sf_veritas(PyObject *self, PyObject *args) {
    int enabled;
    if (!PyArg_ParseTuple(args, "p", &enabled)) {
        return NULL;
    }
    g_capture_sf_veritas = enabled;
    Py_RETURN_NONE;
}

static PyObject *py_set_interceptors_ready(PyObject *self, PyObject *args) {
    // Mark interceptors as fully initialized - profiling can now begin
    atomic_store(&g_interceptors_ready, 1);
    fprintf(stderr, "[_sffuncspan] Interceptors ready - profiling enabled\n");
    fflush(stderr);
    Py_RETURN_NONE;
}

static PyObject *py_shutdown(PyObject *self, PyObject *args) {
    if (!g_running) Py_RETURN_NONE;

    // Stop profiler first
    PyEval_SetProfile(NULL, NULL);

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

    free(g_url); g_url = NULL;
    free(g_func_span_query_escaped); g_func_span_query_escaped = NULL;
    free(g_json_prefix_func_span); g_json_prefix_func_span = NULL;
    free(g_api_key); g_api_key = NULL;
    free(g_service_uuid); g_service_uuid = NULL;
    free(g_library); g_library = NULL;
    free(g_version); g_version = NULL;

    Py_XDECREF(g_capture_from_installed_libraries);
    g_capture_from_installed_libraries = NULL;

    if (g_ring) {
        char *b; size_t l;
        while (ring_pop(&b, &l)) free(b);
        free(g_ring); g_ring = NULL;
    }
    Py_RETURN_NONE;
}

// ---------- Module table ----------
static PyMethodDef SFFuncSpanMethods[] = {
    {"init",                (PyCFunction)py_init,                METH_VARARGS | METH_KEYWORDS, "Init and start sender"},
    {"configure",           (PyCFunction)py_configure,           METH_VARARGS | METH_KEYWORDS, "Configure function span settings"},
    {"record_span",         (PyCFunction)py_record_span,         METH_VARARGS | METH_KEYWORDS, "Record a function span"},
    {"serialize_value",     (PyCFunction)py_serialize_value,     METH_VARARGS,                  "Serialize Python object to JSON (ultra-fast C)"},
    {"generate_span_id",    (PyCFunction)py_generate_span_id,    METH_NOARGS,                   "Generate a new span ID"},
    {"push_span",           (PyCFunction)py_push_span,           METH_VARARGS,                  "Push span ID onto stack"},
    {"pop_span",            (PyCFunction)py_pop_span,            METH_NOARGS,                   "Pop span ID from stack"},
    {"peek_parent_span_id", (PyCFunction)py_peek_parent_span_id, METH_NOARGS,                   "Peek parent span ID"},
    {"get_epoch_ns",        (PyCFunction)py_get_epoch_ns,        METH_NOARGS,                   "Get current epoch nanoseconds"},
    {"get_stats",           (PyCFunction)py_get_stats,           METH_NOARGS,                   "Get performance statistics"},
    {"reset_stats",         (PyCFunction)py_reset_stats,         METH_NOARGS,                   "Reset performance statistics"},
    {"start_c_profiler",    (PyCFunction)py_start_c_profiler,    METH_NOARGS,                   "Start ultra-fast C profiler (replaces sys.setprofile)"},
    {"stop_c_profiler",     (PyCFunction)py_stop_c_profiler,     METH_NOARGS,                   "Stop ultra-fast C profiler"},
    {"cache_config",        (PyCFunction)py_cache_config,        METH_VARARGS,                  "Cache config for a function (avoids Python calls in profiler)"},
    {"set_function_spans_enabled", (PyCFunction)py_set_function_spans_enabled, METH_VARARGS,    "Enable/disable function span capture and transmission (master kill switch)"},
    {"set_capture_installed_packages", (PyCFunction)py_set_capture_installed_packages, METH_VARARGS, "Enable/disable capturing spans from installed packages (site-packages, dist-packages)"},
    {"set_capture_sf_veritas", (PyCFunction)py_set_capture_sf_veritas, METH_VARARGS, "Enable/disable capturing spans from sf_veritas telemetry code itself"},
    {"set_interceptors_ready", (PyCFunction)py_set_interceptors_ready, METH_NOARGS, "Mark interceptors as ready - enables profiling (call after setup_interceptors completes)"},
    {"shutdown",            (PyCFunction)py_shutdown,            METH_NOARGS,                   "Shutdown sender and free state"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef sffuncspanmodule = {
    PyModuleDef_HEAD_INIT,
    "_sffuncspan",
    "sf_veritas ultra-fast function span collection",
    -1,
    SFFuncSpanMethods
};

PyMODINIT_FUNC PyInit__sffuncspan(void) {
    return PyModule_Create(&sffuncspanmodule);
}
