// sf_veritas/_sfservice.c
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
#ifndef SFS_RING_CAP
#define SFS_RING_CAP 256  // Smaller capacity for lower-load service operations
#endif

typedef struct {
    char  *body;   // malloc'd HTTP JSON body
    size_t len;
} sfs_msg_t;

static sfs_msg_t *g_ring = NULL;
static size_t     g_cap  = 0;
static _Atomic size_t g_head = 0; // consumer
static _Atomic size_t g_tail = 0; // producer

// tiny spinlock to make push MPMC-safe enough for Python producers
static atomic_flag g_push_lock = ATOMIC_FLAG_INIT;

// wake/sleep
static pthread_mutex_t g_cv_mtx = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t  g_cv     = PTHREAD_COND_INITIALIZER;
static _Atomic int     g_running = 0;

// Thread pool for parallel sending (configurable via SF_SERVICE_SENDER_THREADS)
#define MAX_SENDER_THREADS 16
static pthread_t g_sender_threads[MAX_SENDER_THREADS];
static int g_num_sender_threads = 0;
static int g_configured_sender_threads = 1;  // Default: 1 thread

// curl state (per-thread handles + shared headers)
__thread CURL *g_telem_curl = NULL;
static struct curl_slist *g_hdrs = NULL;

// config (owned strings)
static char *g_url = NULL;

static char *g_api_key = NULL;
static char *g_service_uuid = NULL;
static char *g_library = NULL;
static char *g_version = NULL;
static int   g_http2 = 0;

// --- SERVICE IDENTIFIER channel state ---
static char *g_service_identifier_query_escaped = NULL;
static char *g_json_prefix_service_identifier = NULL;

// --- DOMAINS channel state ---
static char *g_domains_query_escaped = NULL;
static char *g_json_prefix_domains = NULL;

// --- UPDATE SERVICE DETAILS channel state ---
static char *g_update_service_query_escaped = NULL;
static char *g_json_prefix_update_service = NULL;

// --- COLLECT METADATA channel state ---
static char *g_collect_metadata_query_escaped = NULL;
static char *g_json_prefix_collect_metadata = NULL;

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

// Build SERVICE IDENTIFIER body
static int build_body_service_identifier(
    const char *service_identifier, size_t service_identifier_len,
    const char *service_version, size_t service_version_len,
    const char *service_additional_metadata, size_t service_additional_metadata_len,
    const char *git_sha, size_t git_sha_len,
    const char *infrastructure_type, size_t infrastructure_type_len,
    const char *infrastructure_details, size_t infrastructure_details_len,
    const char *setup_interceptors_file_path, size_t setup_interceptors_file_path_len,
    int setup_interceptors_line_number,
    char **out_body, size_t *out_len
){
    // Escape all string fields
    char *si_tmp = (char*)malloc(service_identifier_len + 1);
    if (!si_tmp) return 0;
    memcpy(si_tmp, service_identifier ? service_identifier : "", service_identifier_len);
    si_tmp[service_identifier_len] = 0;

    char *sv_tmp = (char*)malloc(service_version_len + 1);
    if (!sv_tmp) { free(si_tmp); return 0; }
    memcpy(sv_tmp, service_version ? service_version : "", service_version_len);
    sv_tmp[service_version_len] = 0;

    char *sam_tmp = (char*)malloc(service_additional_metadata_len + 3);  // +3 for "{}" and null
    if (!sam_tmp) { free(si_tmp); free(sv_tmp); return 0; }
    if (service_additional_metadata && service_additional_metadata_len > 0) {
        memcpy(sam_tmp, service_additional_metadata, service_additional_metadata_len);
        sam_tmp[service_additional_metadata_len] = 0;
    } else {
        strcpy(sam_tmp, "{}");
    }

    char *gs_tmp = (char*)malloc(git_sha_len + 1);
    if (!gs_tmp) { free(si_tmp); free(sv_tmp); free(sam_tmp); return 0; }
    memcpy(gs_tmp, git_sha ? git_sha : "", git_sha_len);
    gs_tmp[git_sha_len] = 0;

    char *it_tmp = (char*)malloc(infrastructure_type_len + 1);
    if (!it_tmp) { free(si_tmp); free(sv_tmp); free(sam_tmp); free(gs_tmp); return 0; }
    memcpy(it_tmp, infrastructure_type ? infrastructure_type : "", infrastructure_type_len);
    it_tmp[infrastructure_type_len] = 0;

    char *id_tmp = (char*)malloc(infrastructure_details_len + 3);  // +3 for "{}" and null
    if (!id_tmp) { free(si_tmp); free(sv_tmp); free(sam_tmp); free(gs_tmp); free(it_tmp); return 0; }
    if (infrastructure_details && infrastructure_details_len > 0) {
        memcpy(id_tmp, infrastructure_details, infrastructure_details_len);
        id_tmp[infrastructure_details_len] = 0;
    } else {
        strcpy(id_tmp, "{}");
    }

    char *sifp_tmp = (char*)malloc(setup_interceptors_file_path_len + 1);
    if (!sifp_tmp) { free(si_tmp); free(sv_tmp); free(sam_tmp); free(gs_tmp); free(it_tmp); free(id_tmp); return 0; }
    memcpy(sifp_tmp, setup_interceptors_file_path ? setup_interceptors_file_path : "", setup_interceptors_file_path_len);
    sifp_tmp[setup_interceptors_file_path_len] = 0;

    char *si_esc = json_escape(si_tmp);
    char *sv_esc = json_escape(sv_tmp);
    // DON'T escape serviceAdditionalMetadata - it's already JSON
    // DON'T escape infrastructureDetails - it's already JSON
    char *sam_esc = sam_tmp;  // Use raw JSON string
    char *gs_esc = json_escape(gs_tmp);
    char *it_esc = json_escape(it_tmp);
    char *id_esc = id_tmp;  // Use raw JSON string
    char *sifp_esc = json_escape(sifp_tmp);

    // Note: sam_tmp and id_tmp are now used directly (not escaped), so don't free them yet
    free(si_tmp); free(sv_tmp); free(gs_tmp); free(it_tmp); free(sifp_tmp);

    if (!si_esc || !sv_esc || !sam_esc || !gs_esc || !it_esc || !id_esc || !sifp_esc) {
        free(si_esc); free(sv_esc); free(sam_tmp); free(gs_esc); free(it_esc); free(id_tmp); free(sifp_esc);
        return 0;
    }

    uint64_t tms = now_ms();
    const char *k_si = ",\"serviceIdentifier\":\"";
    const char *k_sv = "\",\"serviceVersion\":\"";
    const char *k_sam = "\",\"serviceAdditionalMetadata\":";  // No quotes - raw JSON
    const char *k_gs = ",\"gitSha\":\"";
    const char *k_it = "\",\"infrastructureType\":\"";
    const char *k_id = "\",\"infrastructureDetails\":";  // No quotes - raw JSON
    const char *k_sifp = ",\"setupInterceptorsFilePath\":\"";
    const char *k_siln = "\",\"setupInterceptorsLineNumber\":";
    const char *k_ts = ",\"timestampMs\":\"";

    char ts_buf[32];
    int ts_len = snprintf(ts_buf, sizeof(ts_buf), "%llu", (unsigned long long)tms);
    char ln_buf[32];
    int ln_len = snprintf(ln_buf, sizeof(ln_buf), "%d", setup_interceptors_line_number);

    if (!g_json_prefix_service_identifier) {
        free(si_esc); free(sv_esc); free(sam_esc); free(gs_esc); free(it_esc); free(id_esc); free(sifp_esc);
        return 0;
    }

    size_t len = strlen(g_json_prefix_service_identifier)
               + strlen(k_si) + strlen(si_esc)
               + strlen(k_sv) + strlen(sv_esc)
               + strlen(k_sam) + strlen(sam_esc)
               + strlen(k_gs) + strlen(gs_esc)
               + strlen(k_it) + strlen(it_esc)
               + strlen(k_id) + strlen(id_esc)
               + strlen(k_sifp) + strlen(sifp_esc)
               + strlen(k_siln) + (size_t)ln_len
               + strlen(k_ts) + (size_t)ts_len + 1  // +1 for closing quote
               + strlen(JSON_SUFFIX);

    char *body = (char*)malloc(len + 1);
    if (!body) {
        free(si_esc); free(sv_esc);
        free(sam_esc);  // sam_esc points to sam_tmp
        free(gs_esc); free(it_esc);
        free(id_esc);  // id_esc points to id_tmp
        free(sifp_esc);
        return 0;
    }

    char *o = body;
    o += sprintf(o, "%s", g_json_prefix_service_identifier);
    o += sprintf(o, "%s%s", k_si, si_esc);
    o += sprintf(o, "%s%s", k_sv, sv_esc);
    o += sprintf(o, "%s%s", k_sam, sam_esc);
    o += sprintf(o, "%s%s", k_gs, gs_esc);
    o += sprintf(o, "%s%s", k_it, it_esc);
    o += sprintf(o, "%s%s", k_id, id_esc);
    o += sprintf(o, "%s%s", k_sifp, sifp_esc);
    o += sprintf(o, "%s%s", k_siln, ln_buf);
    o += sprintf(o, "%s%s\"", k_ts, ts_buf);
    o += sprintf(o, "%s", JSON_SUFFIX);
    *o = '\0';

    *out_body = body;
    *out_len  = (size_t)(o - body);

    // Free escaped strings (sam_esc/id_esc point to original sam_tmp/id_tmp buffers)
    free(si_esc); free(sv_esc);
    free(sam_esc);  // Frees sam_tmp
    free(gs_esc); free(it_esc);
    free(id_esc);  // Frees id_tmp
    free(sifp_esc);
    return 1;
}

// Build DOMAINS body (takes array of domain strings)
static int build_body_domains(
    const char **domains, size_t domain_count,
    char **out_body, size_t *out_len
){
    if (!g_json_prefix_domains) return 0;

    // Escape each domain and build JSON array
    char **escaped_domains = (char**)calloc(domain_count, sizeof(char*));
    if (!escaped_domains) return 0;

    size_t total_domains_len = 0;
    for (size_t i = 0; i < domain_count; i++) {
        escaped_domains[i] = json_escape(domains[i] ? domains[i] : "");
        if (!escaped_domains[i]) {
            for (size_t j = 0; j < i; j++) free(escaped_domains[j]);
            free(escaped_domains);
            return 0;
        }
        total_domains_len += strlen(escaped_domains[i]) + 3; // quotes + comma
    }

    uint64_t tms = now_ms();
    const char *k_domains = ",\"domains\":[";
    const char *k_ts = "],\"timestampMs\":\"";
    char ts_buf[32];
    int ts_len = snprintf(ts_buf, sizeof(ts_buf), "%llu", (unsigned long long)tms);

    size_t len = strlen(g_json_prefix_domains)
               + strlen(k_domains) + total_domains_len
               + strlen(k_ts) + (size_t)ts_len + 1  // +1 for closing quote
               + strlen(JSON_SUFFIX);

    char *body = (char*)malloc(len + 1);
    if (!body) {
        for (size_t i = 0; i < domain_count; i++) free(escaped_domains[i]);
        free(escaped_domains);
        return 0;
    }

    char *o = body;
    o += sprintf(o, "%s", g_json_prefix_domains);
    o += sprintf(o, "%s", k_domains);

    for (size_t i = 0; i < domain_count; i++) {
        if (i > 0) *o++ = ',';
        o += sprintf(o, "\"%s\"", escaped_domains[i]);
    }

    o += sprintf(o, "%s%s\"", k_ts, ts_buf);
    o += sprintf(o, "%s", JSON_SUFFIX);
    *o = '\0';

    *out_body = body;
    *out_len  = (size_t)(o - body);

    for (size_t i = 0; i < domain_count; i++) free(escaped_domains[i]);
    free(escaped_domains);
    return 1;
}

// Build UPDATE SERVICE DETAILS body (similar to domains)
static int build_body_update_service(
    const char **domains, size_t domain_count,
    char **out_body, size_t *out_len
){
    if (!g_json_prefix_update_service) return 0;

    // Escape each domain and build JSON array
    char **escaped_domains = (char**)calloc(domain_count, sizeof(char*));
    if (!escaped_domains) return 0;

    size_t total_domains_len = 0;
    for (size_t i = 0; i < domain_count; i++) {
        escaped_domains[i] = json_escape(domains[i] ? domains[i] : "");
        if (!escaped_domains[i]) {
            for (size_t j = 0; j < i; j++) free(escaped_domains[j]);
            free(escaped_domains);
            return 0;
        }
        total_domains_len += strlen(escaped_domains[i]) + 3; // quotes + comma
    }

    uint64_t tms = now_ms();
    const char *k_domains = ",\"domains\":[";
    const char *k_ts = "],\"timestampMs\":\"";
    char ts_buf[32];
    int ts_len = snprintf(ts_buf, sizeof(ts_buf), "%llu", (unsigned long long)tms);

    size_t len = strlen(g_json_prefix_update_service)
               + strlen(k_domains) + total_domains_len
               + strlen(k_ts) + (size_t)ts_len + 1  // +1 for closing quote
               + strlen(JSON_SUFFIX);

    char *body = (char*)malloc(len + 1);
    if (!body) {
        for (size_t i = 0; i < domain_count; i++) free(escaped_domains[i]);
        free(escaped_domains);
        return 0;
    }

    char *o = body;
    o += sprintf(o, "%s", g_json_prefix_update_service);
    o += sprintf(o, "%s", k_domains);

    for (size_t i = 0; i < domain_count; i++) {
        if (i > 0) *o++ = ',';
        o += sprintf(o, "\"%s\"", escaped_domains[i]);
    }

    o += sprintf(o, "%s%s\"", k_ts, ts_buf);
    o += sprintf(o, "%s", JSON_SUFFIX);
    *o = '\0';

    *out_body = body;
    *out_len  = (size_t)(o - body);

    for (size_t i = 0; i < domain_count; i++) free(escaped_domains[i]);
    free(escaped_domains);
    return 1;
}

// Build COLLECT METADATA body
static int build_body_collect_metadata(
    const char *session_id, size_t session_id_len,
    const char *user_id, size_t user_id_len,
    const char *traits_json, size_t traits_json_len,
    const char **excluded_fields, size_t excluded_fields_count,
    int override,
    char **out_body, size_t *out_len
){
    if (!g_json_prefix_collect_metadata) return 0;

    // Escape session_id, user_id, and traits_json
    char *sid_tmp = (char*)malloc(session_id_len + 1);
    if (!sid_tmp) return 0;
    memcpy(sid_tmp, session_id ? session_id : "", session_id_len);
    sid_tmp[session_id_len] = 0;

    char *uid_tmp = (char*)malloc(user_id_len + 1);
    if (!uid_tmp) { free(sid_tmp); return 0; }
    memcpy(uid_tmp, user_id ? user_id : "", user_id_len);
    uid_tmp[user_id_len] = 0;

    char *tj_tmp = (char*)malloc(traits_json_len + 1);
    if (!tj_tmp) { free(sid_tmp); free(uid_tmp); return 0; }
    memcpy(tj_tmp, traits_json ? traits_json : "", traits_json_len);
    tj_tmp[traits_json_len] = 0;

    char *sid_esc = json_escape(sid_tmp);
    char *uid_esc = json_escape(uid_tmp);
    char *tj_esc = json_escape(tj_tmp);
    free(sid_tmp); free(uid_tmp); free(tj_tmp);

    if (!sid_esc || !uid_esc || !tj_esc) {
        free(sid_esc); free(uid_esc); free(tj_esc);
        return 0;
    }

    // Escape excluded fields array
    char **escaped_fields = NULL;
    size_t total_fields_len = 0;
    if (excluded_fields_count > 0) {
        escaped_fields = (char**)calloc(excluded_fields_count, sizeof(char*));
        if (!escaped_fields) {
            free(sid_esc); free(uid_esc); free(tj_esc);
            return 0;
        }

        for (size_t i = 0; i < excluded_fields_count; i++) {
            escaped_fields[i] = json_escape(excluded_fields[i] ? excluded_fields[i] : "");
            if (!escaped_fields[i]) {
                for (size_t j = 0; j < i; j++) free(escaped_fields[j]);
                free(escaped_fields);
                free(sid_esc); free(uid_esc); free(tj_esc);
                return 0;
            }
            total_fields_len += strlen(escaped_fields[i]) + 3; // quotes + comma
        }
    }

    uint64_t tms = now_ms();
    const char *k_sid = ",\"sessionId\":\"";
    const char *k_uid = "\",\"userId\":\"";
    const char *k_tj = "\",\"traitsJson\":\"";
    const char *k_ef = "\",\"excludedFields\":[";
    const char *k_ov = "],\"override\":";
    const char *k_ts = ",\"timestampMs\":\"";

    char ts_buf[32];
    int ts_len = snprintf(ts_buf, sizeof(ts_buf), "%llu", (unsigned long long)tms);
    const char *override_str = override ? "true" : "false";

    size_t len = strlen(g_json_prefix_collect_metadata)
               + strlen(k_sid) + strlen(sid_esc)
               + strlen(k_uid) + strlen(uid_esc)
               + strlen(k_tj) + strlen(tj_esc)
               + strlen(k_ef) + total_fields_len
               + strlen(k_ov) + strlen(override_str)
               + strlen(k_ts) + (size_t)ts_len + 1  // +1 for closing quote
               + strlen(JSON_SUFFIX);

    char *body = (char*)malloc(len + 1);
    if (!body) {
        if (escaped_fields) {
            for (size_t i = 0; i < excluded_fields_count; i++) free(escaped_fields[i]);
            free(escaped_fields);
        }
        free(sid_esc); free(uid_esc); free(tj_esc);
        return 0;
    }

    char *o = body;
    o += sprintf(o, "%s", g_json_prefix_collect_metadata);
    o += sprintf(o, "%s%s", k_sid, sid_esc);
    o += sprintf(o, "%s%s", k_uid, uid_esc);
    o += sprintf(o, "%s%s", k_tj, tj_esc);
    o += sprintf(o, "%s", k_ef);

    if (excluded_fields_count > 0) {
        for (size_t i = 0; i < excluded_fields_count; i++) {
            if (i > 0) *o++ = ',';
            o += sprintf(o, "\"%s\"", escaped_fields[i]);
        }
    }

    o += sprintf(o, "%s%s", k_ov, override_str);
    o += sprintf(o, "%s%s\"", k_ts, ts_buf);
    o += sprintf(o, "%s", JSON_SUFFIX);
    *o = '\0';

    *out_body = body;
    *out_len  = (size_t)(o - body);

    if (escaped_fields) {
        for (size_t i = 0; i < excluded_fields_count; i++) free(escaped_fields[i]);
        free(escaped_fields);
    }
    free(sid_esc); free(uid_esc); free(tj_esc);
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
    const char *url, *query, *api_key, *service_uuid, *library, *version;
    int http2 = 0;
    static char *kwlist[] = {"url","query","api_key","service_uuid","library","version","http2", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kw, "ssssssi",
        kwlist, &url, &query, &api_key, &service_uuid, &library, &version, &http2)) {
        Py_RETURN_FALSE;
    }
    if (g_running) Py_RETURN_TRUE;

    g_url = str_dup(url);
    g_api_key = str_dup(api_key);
    g_service_uuid = str_dup(service_uuid);
    g_library = str_dup(library);
    g_version = str_dup(version);
    g_http2 = http2 ? 1 : 0;
    if (!g_url || !g_api_key || !g_service_uuid || !g_library || !g_version) {
        Py_RETURN_FALSE;
    }

    g_cap = SFS_RING_CAP;
    g_ring = (sfs_msg_t*)calloc(g_cap, sizeof(sfs_msg_t));
    if (!g_ring) { Py_RETURN_FALSE; }

    // Parse SF_SERVICE_SENDER_THREADS environment variable
    const char *env_threads = getenv("SF_SERVICE_SENDER_THREADS");
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

static PyObject *py_init_service_identifier(PyObject *self, PyObject *args, PyObject *kw) {
    const char *url, *query, *api_key, *service_uuid, *library, *version;
    int http2 = 1;
    static char *kwlist[] = {"url","query","api_key","service_uuid","library","version","http2",NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kw, "ssssssi", kwlist,
                                     &url, &query, &api_key, &service_uuid, &library, &version, &http2)) {
        Py_RETURN_FALSE;
    }
    if (g_service_identifier_query_escaped) { free(g_service_identifier_query_escaped); g_service_identifier_query_escaped = NULL; }
    if (g_json_prefix_service_identifier)   { free(g_json_prefix_service_identifier);   g_json_prefix_service_identifier   = NULL; }

    g_service_identifier_query_escaped = json_escape_query(query);
    if (!g_service_identifier_query_escaped) Py_RETURN_FALSE;
    if (!build_prefix_for_query(g_service_identifier_query_escaped, &g_json_prefix_service_identifier)) {
        Py_RETURN_FALSE;
    }
    Py_RETURN_TRUE;
}

static PyObject *py_init_domains(PyObject *self, PyObject *args, PyObject *kw) {
    const char *url, *query, *api_key, *service_uuid, *library, *version;
    int http2 = 1;
    static char *kwlist[] = {"url","query","api_key","service_uuid","library","version","http2",NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kw, "ssssssi", kwlist,
                                     &url, &query, &api_key, &service_uuid, &library, &version, &http2)) {
        Py_RETURN_FALSE;
    }
    if (g_domains_query_escaped) { free(g_domains_query_escaped); g_domains_query_escaped = NULL; }
    if (g_json_prefix_domains)   { free(g_json_prefix_domains);   g_json_prefix_domains   = NULL; }

    g_domains_query_escaped = json_escape_query(query);
    if (!g_domains_query_escaped) Py_RETURN_FALSE;
    if (!build_prefix_for_query(g_domains_query_escaped, &g_json_prefix_domains)) {
        Py_RETURN_FALSE;
    }
    Py_RETURN_TRUE;
}

static PyObject *py_init_update_service(PyObject *self, PyObject *args, PyObject *kw) {
    const char *url, *query, *api_key, *service_uuid, *library, *version;
    int http2 = 1;
    static char *kwlist[] = {"url","query","api_key","service_uuid","library","version","http2",NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kw, "ssssssi", kwlist,
                                     &url, &query, &api_key, &service_uuid, &library, &version, &http2)) {
        Py_RETURN_FALSE;
    }
    if (g_update_service_query_escaped) { free(g_update_service_query_escaped); g_update_service_query_escaped = NULL; }
    if (g_json_prefix_update_service)   { free(g_json_prefix_update_service);   g_json_prefix_update_service   = NULL; }

    g_update_service_query_escaped = json_escape_query(query);
    if (!g_update_service_query_escaped) Py_RETURN_FALSE;
    if (!build_prefix_for_query(g_update_service_query_escaped, &g_json_prefix_update_service)) {
        Py_RETURN_FALSE;
    }
    Py_RETURN_TRUE;
}

static PyObject *py_init_collect_metadata(PyObject *self, PyObject *args, PyObject *kw) {
    const char *url, *query, *api_key, *service_uuid, *library, *version;
    int http2 = 1;
    static char *kwlist[] = {"url","query","api_key","service_uuid","library","version","http2",NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kw, "ssssssi", kwlist,
                                     &url, &query, &api_key, &service_uuid, &library, &version, &http2)) {
        Py_RETURN_FALSE;
    }
    if (g_collect_metadata_query_escaped) { free(g_collect_metadata_query_escaped); g_collect_metadata_query_escaped = NULL; }
    if (g_json_prefix_collect_metadata)   { free(g_json_prefix_collect_metadata);   g_json_prefix_collect_metadata   = NULL; }

    g_collect_metadata_query_escaped = json_escape_query(query);
    if (!g_collect_metadata_query_escaped) Py_RETURN_FALSE;
    if (!build_prefix_for_query(g_collect_metadata_query_escaped, &g_json_prefix_collect_metadata)) {
        Py_RETURN_FALSE;
    }
    Py_RETURN_TRUE;
}

static PyObject *py_service_identifier(PyObject *self, PyObject *args, PyObject *kw) {
    const char *service_identifier, *service_version, *service_additional_metadata;
    const char *git_sha, *infrastructure_type, *infrastructure_details;
    const char *setup_interceptors_file_path;
    Py_ssize_t si_len = 0, sv_len = 0, sam_len = 0, gs_len = 0;
    Py_ssize_t it_len = 0, id_len = 0, sifp_len = 0;
    int setup_interceptors_line_number = 0;

    static char *kwlist[] = {
        "service_identifier", "service_version", "service_additional_metadata",
        "git_sha", "infrastructure_type", "infrastructure_details",
        "setup_interceptors_file_path", "setup_interceptors_line_number", NULL
    };

    if (!PyArg_ParseTupleAndKeywords(args, kw, "s#s#s#s#s#s#s#i", kwlist,
                                     &service_identifier, &si_len,
                                     &service_version, &sv_len,
                                     &service_additional_metadata, &sam_len,
                                     &git_sha, &gs_len,
                                     &infrastructure_type, &it_len,
                                     &infrastructure_details, &id_len,
                                     &setup_interceptors_file_path, &sifp_len,
                                     &setup_interceptors_line_number)) {
        Py_RETURN_NONE;
    }
    if (!g_running || g_json_prefix_service_identifier == NULL) Py_RETURN_NONE;

    // OPTIMIZATION: Release GIL during JSON building + ring push
    // All string arguments are already C strings from PyArg_ParseTupleAndKeywords,
    // so we can safely release GIL for the entire body building + transmission.
    // This extends GIL-free duration from ~100ns to ~500-2000ns (5-20x improvement).
    char *body = NULL;
    size_t len = 0;
    int ok = 0;

    Py_BEGIN_ALLOW_THREADS
    // Build JSON body (WITHOUT GIL - pure C string operations)
    if (build_body_service_identifier(
            service_identifier, (size_t)si_len,
            service_version, (size_t)sv_len,
            service_additional_metadata, (size_t)sam_len,
            git_sha, (size_t)gs_len,
            infrastructure_type, (size_t)it_len,
            infrastructure_details, (size_t)id_len,
            setup_interceptors_file_path, (size_t)sifp_len,
            setup_interceptors_line_number,
            &body, &len)) {
        // Push to ring buffer (WITHOUT GIL)
        ok = ring_push(body, len);
    }
    Py_END_ALLOW_THREADS

    if (!ok && body) free(body);
    Py_RETURN_NONE;
}

static PyObject *py_domains(PyObject *self, PyObject *args, PyObject *kw) {
    PyObject *domains_list = NULL;
    static char *kwlist[] = {"domains", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kw, "O", kwlist, &domains_list)) {
        Py_RETURN_NONE;
    }
    if (!g_running || g_json_prefix_domains == NULL) Py_RETURN_NONE;

    if (!PyList_Check(domains_list)) {
        PyErr_SetString(PyExc_TypeError, "domains must be a list");
        Py_RETURN_NONE;
    }

    Py_ssize_t domain_count = PyList_Size(domains_list);
    if (domain_count == 0) Py_RETURN_NONE;

    const char **domains = (const char**)malloc(sizeof(char*) * domain_count);
    if (!domains) Py_RETURN_NONE;

    for (Py_ssize_t i = 0; i < domain_count; i++) {
        PyObject *item = PyList_GetItem(domains_list, i);
        if (!PyUnicode_Check(item)) {
            free(domains);
            PyErr_SetString(PyExc_TypeError, "all domains must be strings");
            Py_RETURN_NONE;
        }
        domains[i] = PyUnicode_AsUTF8(item);
    }

    // OPTIMIZATION: Release GIL during JSON building + ring push
    // All string arguments are already C strings from PyArg_ParseTupleAndKeywords,
    // so we can safely release GIL for the entire body building + transmission.
    char *body = NULL;
    size_t len = 0;
    int ok = 0;

    Py_BEGIN_ALLOW_THREADS
    // Build JSON body (WITHOUT GIL - pure C string operations)
    if (build_body_domains(domains, (size_t)domain_count, &body, &len)) {
        // Push to ring buffer (WITHOUT GIL)
        ok = ring_push(body, len);
    }
    Py_END_ALLOW_THREADS

    free(domains);
    if (!ok && body) free(body);
    Py_RETURN_NONE;
}

static PyObject *py_update_service(PyObject *self, PyObject *args, PyObject *kw) {
    PyObject *domains_list = NULL;
    static char *kwlist[] = {"domains", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kw, "O", kwlist, &domains_list)) {
        Py_RETURN_NONE;
    }
    if (!g_running || g_json_prefix_update_service == NULL) Py_RETURN_NONE;

    if (!PyList_Check(domains_list)) {
        PyErr_SetString(PyExc_TypeError, "domains must be a list");
        Py_RETURN_NONE;
    }

    Py_ssize_t domain_count = PyList_Size(domains_list);
    if (domain_count == 0) Py_RETURN_NONE;

    const char **domains = (const char**)malloc(sizeof(char*) * domain_count);
    if (!domains) Py_RETURN_NONE;

    for (Py_ssize_t i = 0; i < domain_count; i++) {
        PyObject *item = PyList_GetItem(domains_list, i);
        if (!PyUnicode_Check(item)) {
            free(domains);
            PyErr_SetString(PyExc_TypeError, "all domains must be strings");
            Py_RETURN_NONE;
        }
        domains[i] = PyUnicode_AsUTF8(item);
    }

    // OPTIMIZATION: Release GIL during JSON building + ring push
    // All string arguments are already C strings from PyArg_ParseTupleAndKeywords,
    // so we can safely release GIL for the entire body building + transmission.
    char *body = NULL;
    size_t len = 0;
    int ok = 0;

    Py_BEGIN_ALLOW_THREADS
    // Build JSON body (WITHOUT GIL - pure C string operations)
    if (build_body_update_service(domains, (size_t)domain_count, &body, &len)) {
        // Push to ring buffer (WITHOUT GIL)
        ok = ring_push(body, len);
    }
    Py_END_ALLOW_THREADS

    free(domains);
    if (!ok && body) free(body);
    Py_RETURN_NONE;
}

static PyObject *py_collect_metadata(PyObject *self, PyObject *args, PyObject *kw) {
    const char *session_id, *user_id, *traits_json;
    Py_ssize_t session_id_len = 0, user_id_len = 0, traits_json_len = 0;
    PyObject *excluded_fields_list = NULL;
    int override = 0;

    static char *kwlist[] = {"session_id", "user_id", "traits_json", "excluded_fields", "override", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kw, "s#s#s#O|p", kwlist,
                                     &session_id, &session_id_len,
                                     &user_id, &user_id_len,
                                     &traits_json, &traits_json_len,
                                     &excluded_fields_list,
                                     &override)) {
        Py_RETURN_NONE;
    }
    if (!g_running || g_json_prefix_collect_metadata == NULL) Py_RETURN_NONE;

    if (!PyList_Check(excluded_fields_list)) {
        PyErr_SetString(PyExc_TypeError, "excluded_fields must be a list");
        Py_RETURN_NONE;
    }

    Py_ssize_t excluded_fields_count = PyList_Size(excluded_fields_list);
    const char **excluded_fields = NULL;

    if (excluded_fields_count > 0) {
        excluded_fields = (const char**)malloc(sizeof(char*) * excluded_fields_count);
        if (!excluded_fields) Py_RETURN_NONE;

        for (Py_ssize_t i = 0; i < excluded_fields_count; i++) {
            PyObject *item = PyList_GetItem(excluded_fields_list, i);
            if (!PyUnicode_Check(item)) {
                free(excluded_fields);
                PyErr_SetString(PyExc_TypeError, "all excluded_fields must be strings");
                Py_RETURN_NONE;
            }
            excluded_fields[i] = PyUnicode_AsUTF8(item);
        }
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
    if (build_body_collect_metadata(
            session_id, (size_t)session_id_len,
            user_id, (size_t)user_id_len,
            traits_json, (size_t)traits_json_len,
            excluded_fields, (size_t)excluded_fields_count,
            override,
            &body, &len)) {
        // Push to ring buffer (WITHOUT GIL)
        ok = ring_push(body, len);
    }
    Py_END_ALLOW_THREADS

    if (excluded_fields) free(excluded_fields);
    if (!ok && body) free(body);
    Py_RETURN_NONE;
}

// Convenience wrapper: identify (calls collect_metadata)
static PyObject *py_identify(PyObject *self, PyObject *args, PyObject *kw) {
    const char *session_id, *user_id, *traits_json;
    Py_ssize_t session_id_len = 0, user_id_len = 0, traits_json_len = 0;
    PyObject *excluded_fields_list = NULL;
    int override = 0;

    static char *kwlist[] = {"session_id", "user_id", "traits_json", "excluded_fields", "override", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kw, "s#s#s#O|p", kwlist,
                                     &session_id, &session_id_len,
                                     &user_id, &user_id_len,
                                     &traits_json, &traits_json_len,
                                     &excluded_fields_list,
                                     &override)) {
        Py_RETURN_NONE;
    }

    // Just delegate to collect_metadata
    return py_collect_metadata(self, args, kw);
}

// Convenience wrapper: add_or_update_metadata (calls collect_metadata)
static PyObject *py_add_or_update_metadata(PyObject *self, PyObject *args, PyObject *kw) {
    const char *session_id, *user_id, *traits_json;
    Py_ssize_t session_id_len = 0, user_id_len = 0, traits_json_len = 0;
    PyObject *excluded_fields_list = NULL;
    int override = 0;

    static char *kwlist[] = {"session_id", "user_id", "traits_json", "excluded_fields", "override", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kw, "s#s#s#O|p", kwlist,
                                     &session_id, &session_id_len,
                                     &user_id, &user_id_len,
                                     &traits_json, &traits_json_len,
                                     &excluded_fields_list,
                                     &override)) {
        Py_RETURN_NONE;
    }

    // Just delegate to collect_metadata
    return py_collect_metadata(self, args, kw);
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

    free(g_service_identifier_query_escaped); g_service_identifier_query_escaped = NULL;
    free(g_json_prefix_service_identifier); g_json_prefix_service_identifier = NULL;

    free(g_domains_query_escaped); g_domains_query_escaped = NULL;
    free(g_json_prefix_domains); g_json_prefix_domains = NULL;

    free(g_update_service_query_escaped); g_update_service_query_escaped = NULL;
    free(g_json_prefix_update_service); g_json_prefix_update_service = NULL;

    free(g_collect_metadata_query_escaped); g_collect_metadata_query_escaped = NULL;
    free(g_json_prefix_collect_metadata); g_json_prefix_collect_metadata = NULL;

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

// ---------- Module table ----------
static PyMethodDef SFServiceMethods[] = {
    {"init",                    (PyCFunction)py_init,                   METH_VARARGS | METH_KEYWORDS, "Init and start sender"},
    {"init_service_identifier", (PyCFunction)py_init_service_identifier,METH_VARARGS | METH_KEYWORDS, "Init (service identifier) query/prefix"},
    {"init_domains",            (PyCFunction)py_init_domains,           METH_VARARGS | METH_KEYWORDS, "Init (domains) query/prefix"},
    {"init_update_service",     (PyCFunction)py_init_update_service,    METH_VARARGS | METH_KEYWORDS, "Init (update service) query/prefix"},
    {"init_collect_metadata",   (PyCFunction)py_init_collect_metadata,  METH_VARARGS | METH_KEYWORDS, "Init (collect metadata) query/prefix"},
    {"service_identifier",      (PyCFunction)py_service_identifier,     METH_VARARGS | METH_KEYWORDS, "Send service identifier"},
    {"domains",                 (PyCFunction)py_domains,                METH_VARARGS | METH_KEYWORDS, "Send domains"},
    {"update_service",          (PyCFunction)py_update_service,         METH_VARARGS | METH_KEYWORDS, "Send update service"},
    {"collect_metadata",        (PyCFunction)py_collect_metadata,       METH_VARARGS | METH_KEYWORDS, "Send collect metadata"},
    {"identify",                (PyCFunction)py_identify,               METH_VARARGS | METH_KEYWORDS, "Identify user (alias for collect_metadata)"},
    {"add_or_update_metadata",  (PyCFunction)py_add_or_update_metadata, METH_VARARGS | METH_KEYWORDS, "Add/update metadata (alias for collect_metadata)"},
    {"shutdown",                (PyCFunction)py_shutdown,               METH_NOARGS,                   "Shutdown sender and free state"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef sfservicemodule = {
    PyModuleDef_HEAD_INIT,
    "_sfservice",
    "sf_veritas ultra-fast service operations",
    -1,
    SFServiceMethods
};

PyMODINIT_FUNC PyInit__sfservice(void) {
    return PyModule_Create(&sfservicemodule);
}
