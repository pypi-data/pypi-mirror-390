// sf_veritas/_sffuncspan_config.c
// Ultra-fast configuration system for function span capture (<5ns lookups)
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>

// ---------- Configuration Structure ----------
// 32 bytes, cache-line friendly
typedef struct {
    uint8_t include_arguments;
    uint8_t include_return_value;
    uint8_t autocapture_all_children;
    uint8_t _padding;
    float sample_rate;
    uint32_t arg_limit_mb;
    uint32_t return_limit_mb;
    uint64_t hash;  // Pre-computed for validation
} sf_funcspan_config_t;

// Thread-local storage for header overrides (highest priority)
typedef struct {
    sf_funcspan_config_t config;
    uint8_t has_override;
    uint8_t _padding[7];  // Align to 32 bytes
} sf_thread_config_t;

static _Thread_local sf_thread_config_t g_thread_config = {0};

// ---------- Hash Table for O(1) Lookups ----------
// Using power-of-2 capacity for fast modulo (bitwise AND)
typedef struct {
    sf_funcspan_config_t* entries;  // Dense array of configs
    uint64_t* keys;                 // File path hashes
    uint32_t* indices;              // Hash table -> entries index
    uint32_t capacity;              // Power of 2
    uint32_t size;                  // Number of entries
} sf_config_table_t;

// Global lookup tables (built at startup)
static sf_config_table_t g_file_configs = {0};
static sf_config_table_t g_func_configs = {0};
static sf_funcspan_config_t g_default_config = {
    .include_arguments = 1,
    .include_return_value = 1,
    .autocapture_all_children = 1,
    ._padding = 0,
    .sample_rate = 1.0f,
    .arg_limit_mb = 1,
    .return_limit_mb = 1,
    .hash = 0
};

// Lock for table modifications (only used at startup)
static pthread_mutex_t g_config_mutex = PTHREAD_MUTEX_INITIALIZER;

// ---------- Fast Hash Function (xxHash-like) ----------
// Simple, fast hash for string keys (~2ns)
static inline uint64_t fast_hash(const char *str, size_t len) {
    const uint64_t PRIME64_1 = 11400714785074694791ULL;
    const uint64_t PRIME64_2 = 14029467366897019727ULL;
    const uint64_t PRIME64_3 = 1609587929392839161ULL;
    const uint64_t PRIME64_4 = 9650029242287828579ULL;
    const uint64_t PRIME64_5 = 2870177450012600261ULL;

    uint64_t h = PRIME64_5 + len;
    const uint8_t *data = (const uint8_t*)str;

    // Process 8 bytes at a time
    while (len >= 8) {
        h ^= *(const uint64_t*)data * PRIME64_2;
        h = (h << 31) | (h >> 33);
        h *= PRIME64_1;
        data += 8;
        len -= 8;
    }

    // Process remaining bytes
    while (len--) {
        h ^= (*data++) * PRIME64_5;
        h = (h << 11) | (h >> 53);
        h *= PRIME64_1;
    }

    // Final mix
    h ^= h >> 33;
    h *= PRIME64_2;
    h ^= h >> 29;
    h *= PRIME64_3;
    h ^= h >> 32;

    return h;
}

// ---------- Config Table Operations ----------
static int table_init(sf_config_table_t *table, uint32_t initial_capacity) {
    // Round up to next power of 2
    uint32_t capacity = 16;
    while (capacity < initial_capacity) capacity <<= 1;

    table->entries = (sf_funcspan_config_t*)calloc(capacity, sizeof(sf_funcspan_config_t));
    table->keys = (uint64_t*)calloc(capacity, sizeof(uint64_t));
    table->indices = (uint32_t*)malloc(capacity * sizeof(uint32_t));

    if (!table->entries || !table->keys || !table->indices) {
        free(table->entries);
        free(table->keys);
        free(table->indices);
        return 0;
    }

    // Initialize indices to UINT32_MAX (empty marker)
    for (uint32_t i = 0; i < capacity; i++) {
        table->indices[i] = UINT32_MAX;
    }

    table->capacity = capacity;
    table->size = 0;
    return 1;
}

static void table_free(sf_config_table_t *table) {
    free(table->entries);
    free(table->keys);
    free(table->indices);
    memset(table, 0, sizeof(sf_config_table_t));
}

// Resize table when load factor > 0.75
static int table_resize(sf_config_table_t *table) {
    uint32_t new_capacity = table->capacity * 2;
    uint32_t *new_indices = (uint32_t*)malloc(new_capacity * sizeof(uint32_t));

    if (!new_indices) return 0;

    // Initialize new indices
    for (uint32_t i = 0; i < new_capacity; i++) {
        new_indices[i] = UINT32_MAX;
    }

    // Rehash all entries
    for (uint32_t i = 0; i < table->size; i++) {
        uint64_t hash = table->keys[i];
        uint32_t slot = hash & (new_capacity - 1);

        // Linear probing
        while (new_indices[slot] != UINT32_MAX) {
            slot = (slot + 1) & (new_capacity - 1);
        }

        new_indices[slot] = i;
    }

    free(table->indices);
    table->indices = new_indices;
    table->capacity = new_capacity;
    return 1;
}

static int table_insert(sf_config_table_t *table, uint64_t hash, const sf_funcspan_config_t *config) {
    pthread_mutex_lock(&g_config_mutex);

    // Check if we need to resize
    if (table->size >= (table->capacity * 3) / 4) {
        if (!table_resize(table)) {
            pthread_mutex_unlock(&g_config_mutex);
            return 0;
        }
    }

    // Find slot using linear probing
    uint32_t slot = hash & (table->capacity - 1);
    while (table->indices[slot] != UINT32_MAX) {
        // Check if key already exists (update case)
        uint32_t idx = table->indices[slot];
        if (table->keys[idx] == hash) {
            // Update existing entry
            table->entries[idx] = *config;
            table->entries[idx].hash = hash;
            pthread_mutex_unlock(&g_config_mutex);
            return 1;
        }
        slot = (slot + 1) & (table->capacity - 1);
    }

    // Insert new entry
    uint32_t idx = table->size++;
    table->keys[idx] = hash;
    table->entries[idx] = *config;
    table->entries[idx].hash = hash;
    table->indices[slot] = idx;

    pthread_mutex_unlock(&g_config_mutex);
    return 1;
}

// ---------- Ultra-Fast Lookup (<5ns) ----------
static inline const sf_funcspan_config_t* config_lookup(const char *file_path, const char *func_name) {
    // 1. Check thread-local override first (highest priority, ~1ns)
    if (g_thread_config.has_override) {
        return &g_thread_config.config;
    }

    // 2. Build combined key for function-level lookup
    //    Format: "file_path:func_name"
    char key_buf[512];
    size_t file_len = strlen(file_path);
    size_t func_len = strlen(func_name);

    if (file_len + func_len + 2 < sizeof(key_buf)) {
        memcpy(key_buf, file_path, file_len);
        key_buf[file_len] = ':';
        memcpy(key_buf + file_len + 1, func_name, func_len);
        key_buf[file_len + 1 + func_len] = '\0';

        // 3. Compute hash (fast, ~2ns)
        uint64_t hash = fast_hash(key_buf, file_len + 1 + func_len);

        // 4. Prefetch cache line (parallel with hash)
        __builtin_prefetch(&g_func_configs.indices[hash & (g_func_configs.capacity - 1)]);

        // 5. Lookup in function table (~1ns)
        uint32_t slot = hash & (g_func_configs.capacity - 1);
        uint32_t idx = g_func_configs.indices[slot];

        if (idx != UINT32_MAX && g_func_configs.keys[idx] == hash) {
            return &g_func_configs.entries[idx];
        }
    }

    // 6. Fallback to file-level lookup
    uint64_t file_hash = fast_hash(file_path, file_len);
    __builtin_prefetch(&g_file_configs.indices[file_hash & (g_file_configs.capacity - 1)]);

    uint32_t slot = file_hash & (g_file_configs.capacity - 1);
    uint32_t idx = g_file_configs.indices[slot];

    if (idx != UINT32_MAX && g_file_configs.keys[idx] == file_hash) {
        return &g_file_configs.entries[idx];
    }

    // 7. Return default config
    return &g_default_config;
}

// ---------- Header Parsing ----------
// Parse header format: "include_arguments-include_return_value-arg_limit_mb-return_limit_mb-autocapture_all_children-sample_rate"
// Example: "1-1-1-1-1-1.0" or "0-0-2-2-1-0.5"
static int parse_header_override(const char *header, sf_funcspan_config_t *config) {
    if (!header || !config) return 0;

    // Parse using sscanf (fast enough for header parsing, ~100ns)
    int values[5];
    float sample_rate;

    int parsed = sscanf(header, "%d-%d-%d-%d-%d-%f",
                        &values[0], &values[1], &values[2],
                        &values[3], &values[4], &sample_rate);

    if (parsed != 6) return 0;  // Parse error

    // Validate values
    if (sample_rate < 0.0f || sample_rate > 1.0f) return 0;
    for (int i = 0; i < 5; i++) {
        if (values[i] < 0) return 0;
    }

    // Set config
    config->include_arguments = (uint8_t)values[0];
    config->include_return_value = (uint8_t)values[1];
    config->arg_limit_mb = (uint32_t)values[2];
    config->return_limit_mb = (uint32_t)values[3];
    config->autocapture_all_children = (uint8_t)values[4];
    config->sample_rate = sample_rate;
    config->_padding = 0;
    config->hash = 0;

    return 1;  // Success
}

// ---------- Python API ----------

static PyObject* py_init(PyObject *self, PyObject *args) {
    PyObject *config_dict;

    if (!PyArg_ParseTuple(args, "O", &config_dict)) {
        return NULL;
    }

    if (!PyDict_Check(config_dict)) {
        PyErr_SetString(PyExc_TypeError, "config must be a dictionary");
        return NULL;
    }

    // Initialize default config from dict
    PyObject *val;

    val = PyDict_GetItemString(config_dict, "include_arguments");
    if (val && PyBool_Check(val)) {
        g_default_config.include_arguments = (val == Py_True) ? 1 : 0;
    }

    val = PyDict_GetItemString(config_dict, "include_return_value");
    if (val && PyBool_Check(val)) {
        g_default_config.include_return_value = (val == Py_True) ? 1 : 0;
    }

    val = PyDict_GetItemString(config_dict, "autocapture_all_children");
    if (val && PyBool_Check(val)) {
        g_default_config.autocapture_all_children = (val == Py_True) ? 1 : 0;
    }

    val = PyDict_GetItemString(config_dict, "arg_limit_mb");
    if (val && PyLong_Check(val)) {
        g_default_config.arg_limit_mb = (uint32_t)PyLong_AsLong(val);
    }

    val = PyDict_GetItemString(config_dict, "return_limit_mb");
    if (val && PyLong_Check(val)) {
        g_default_config.return_limit_mb = (uint32_t)PyLong_AsLong(val);
    }

    val = PyDict_GetItemString(config_dict, "sample_rate");
    if (val && PyFloat_Check(val)) {
        g_default_config.sample_rate = (float)PyFloat_AsDouble(val);
    }

    // Initialize hash tables
    if (g_file_configs.capacity == 0) {
        if (!table_init(&g_file_configs, 1024)) {
            PyErr_SetString(PyExc_RuntimeError, "Failed to initialize file config table");
            return NULL;
        }
    }

    if (g_func_configs.capacity == 0) {
        if (!table_init(&g_func_configs, 4096)) {
            PyErr_SetString(PyExc_RuntimeError, "Failed to initialize function config table");
            return NULL;
        }
    }

    Py_RETURN_NONE;
}

static PyObject* py_add_file(PyObject *self, PyObject *args) {
    const char *file_path;
    PyObject *config_dict;

    if (!PyArg_ParseTuple(args, "sO", &file_path, &config_dict)) {
        return NULL;
    }

    if (!PyDict_Check(config_dict)) {
        PyErr_SetString(PyExc_TypeError, "config must be a dictionary");
        return NULL;
    }

    // Build config from dict
    sf_funcspan_config_t config = g_default_config;  // Start with defaults
    PyObject *val;

    val = PyDict_GetItemString(config_dict, "include_arguments");
    if (val && PyBool_Check(val)) {
        config.include_arguments = (val == Py_True) ? 1 : 0;
    }

    val = PyDict_GetItemString(config_dict, "include_return_value");
    if (val && PyBool_Check(val)) {
        config.include_return_value = (val == Py_True) ? 1 : 0;
    }

    val = PyDict_GetItemString(config_dict, "autocapture_all_children");
    if (val && PyBool_Check(val)) {
        config.autocapture_all_children = (val == Py_True) ? 1 : 0;
    }

    val = PyDict_GetItemString(config_dict, "arg_limit_mb");
    if (val && PyLong_Check(val)) {
        config.arg_limit_mb = (uint32_t)PyLong_AsLong(val);
    }

    val = PyDict_GetItemString(config_dict, "return_limit_mb");
    if (val && PyLong_Check(val)) {
        config.return_limit_mb = (uint32_t)PyLong_AsLong(val);
    }

    val = PyDict_GetItemString(config_dict, "sample_rate");
    if (val && PyFloat_Check(val)) {
        config.sample_rate = (float)PyFloat_AsDouble(val);
    }

    // Compute hash and insert
    uint64_t hash = fast_hash(file_path, strlen(file_path));

    if (!table_insert(&g_file_configs, hash, &config)) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to insert file config");
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject* py_add_function(PyObject *self, PyObject *args) {
    const char *file_path;
    const char *func_name;
    PyObject *config_dict;

    if (!PyArg_ParseTuple(args, "ssO", &file_path, &func_name, &config_dict)) {
        return NULL;
    }

    if (!PyDict_Check(config_dict)) {
        PyErr_SetString(PyExc_TypeError, "config must be a dictionary");
        return NULL;
    }

    // Build config from dict (same as add_file)
    sf_funcspan_config_t config = g_default_config;
    PyObject *val;

    val = PyDict_GetItemString(config_dict, "include_arguments");
    if (val && PyBool_Check(val)) {
        config.include_arguments = (val == Py_True) ? 1 : 0;
    }

    val = PyDict_GetItemString(config_dict, "include_return_value");
    if (val && PyBool_Check(val)) {
        config.include_return_value = (val == Py_True) ? 1 : 0;
    }

    val = PyDict_GetItemString(config_dict, "autocapture_all_children");
    if (val && PyBool_Check(val)) {
        config.autocapture_all_children = (val == Py_True) ? 1 : 0;
    }

    val = PyDict_GetItemString(config_dict, "arg_limit_mb");
    if (val && PyLong_Check(val)) {
        config.arg_limit_mb = (uint32_t)PyLong_AsLong(val);
    }

    val = PyDict_GetItemString(config_dict, "return_limit_mb");
    if (val && PyLong_Check(val)) {
        config.return_limit_mb = (uint32_t)PyLong_AsLong(val);
    }

    val = PyDict_GetItemString(config_dict, "sample_rate");
    if (val && PyFloat_Check(val)) {
        config.sample_rate = (float)PyFloat_AsDouble(val);
    }

    // Build combined key: "file_path:func_name"
    size_t file_len = strlen(file_path);
    size_t func_len = strlen(func_name);
    char *key = (char*)malloc(file_len + func_len + 2);

    if (!key) {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate key");
        return NULL;
    }

    memcpy(key, file_path, file_len);
    key[file_len] = ':';
    memcpy(key + file_len + 1, func_name, func_len);
    key[file_len + 1 + func_len] = '\0';

    uint64_t hash = fast_hash(key, file_len + 1 + func_len);
    free(key);

    if (!table_insert(&g_func_configs, hash, &config)) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to insert function config");
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject* py_set_thread_override(PyObject *self, PyObject *args) {
    const char *header;

    if (!PyArg_ParseTuple(args, "s", &header)) {
        return NULL;
    }

    sf_funcspan_config_t config;
    if (!parse_header_override(header, &config)) {
        PyErr_SetString(PyExc_ValueError, "Invalid header format. Expected: 'include_arguments-include_return_value-arg_limit_mb-return_limit_mb-autocapture_all_children-sample_rate'");
        return NULL;
    }

    g_thread_config.config = config;
    g_thread_config.has_override = 1;

    Py_RETURN_NONE;
}

static PyObject* py_clear_thread_override(PyObject *self, PyObject *args) {
    g_thread_config.has_override = 0;
    memset(&g_thread_config.config, 0, sizeof(sf_funcspan_config_t));
    Py_RETURN_NONE;
}

static PyObject* py_get_thread_override(PyObject *self, PyObject *args) {
    // Return current thread-local override as formatted string, or None if not set
    if (!g_thread_config.has_override) {
        Py_RETURN_NONE;
    }

    const sf_funcspan_config_t *config = &g_thread_config.config;

    // Format: "include_arguments-include_return_value-arg_limit_mb-return_limit_mb-autocapture_all_children-sample_rate"
    // Example: "1-1-1-1-1-1.0" or "0-0-2-2-1-0.5"
    char buffer[128];
    int written = snprintf(
        buffer,
        sizeof(buffer),
        "%d-%d-%u-%u-%d-%.2f",
        (int)config->include_arguments,
        (int)config->include_return_value,
        config->arg_limit_mb,
        config->return_limit_mb,
        (int)config->autocapture_all_children,
        config->sample_rate
    );

    if (written < 0 || written >= (int)sizeof(buffer)) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to format thread override string");
        return NULL;
    }

    return PyUnicode_FromString(buffer);
}

static PyObject* py_get(PyObject *self, PyObject *args) {
    const char *file_path;
    const char *func_name;

    if (!PyArg_ParseTuple(args, "ss", &file_path, &func_name)) {
        return NULL;
    }

    const sf_funcspan_config_t *config = config_lookup(file_path, func_name);

    // Return as dictionary
    PyObject *dict = PyDict_New();
    if (!dict) return NULL;

    PyDict_SetItemString(dict, "include_arguments", PyBool_FromLong(config->include_arguments));
    PyDict_SetItemString(dict, "include_return_value", PyBool_FromLong(config->include_return_value));
    PyDict_SetItemString(dict, "autocapture_all_children", PyBool_FromLong(config->autocapture_all_children));
    PyDict_SetItemString(dict, "arg_limit_mb", PyLong_FromLong(config->arg_limit_mb));
    PyDict_SetItemString(dict, "return_limit_mb", PyLong_FromLong(config->return_limit_mb));
    PyDict_SetItemString(dict, "sample_rate", PyFloat_FromDouble(config->sample_rate));

    return dict;
}

static PyObject* py_get_raw_pointer(PyObject *self, PyObject *args) {
    const char *file_path;
    const char *func_name;

    if (!PyArg_ParseTuple(args, "ss", &file_path, &func_name)) {
        return NULL;
    }

    const sf_funcspan_config_t *config = config_lookup(file_path, func_name);

    // Return pointer as PyCapsule (for C-level integration)
    return PyCapsule_New((void*)config, "sf_funcspan_config_ptr", NULL);
}

static PyObject* py_shutdown(PyObject *self, PyObject *args) {
    pthread_mutex_lock(&g_config_mutex);

    table_free(&g_file_configs);
    table_free(&g_func_configs);

    // Reset default config
    g_default_config.include_arguments = 1;
    g_default_config.include_return_value = 1;
    g_default_config.autocapture_all_children = 1;
    g_default_config.sample_rate = 1.0f;
    g_default_config.arg_limit_mb = 1;
    g_default_config.return_limit_mb = 1;

    pthread_mutex_unlock(&g_config_mutex);

    Py_RETURN_NONE;
}

// ---------- Module Definition ----------
static PyMethodDef ConfigMethods[] = {
    {"init", py_init, METH_VARARGS, "Initialize config system with default config"},
    {"add_file", py_add_file, METH_VARARGS, "Add file-level config"},
    {"add_function", py_add_function, METH_VARARGS, "Add function-level config"},
    {"set_thread_override", py_set_thread_override, METH_VARARGS, "Set thread-local override from header"},
    {"clear_thread_override", py_clear_thread_override, METH_NOARGS, "Clear thread-local override"},
    {"get_thread_override", py_get_thread_override, METH_NOARGS, "Get thread-local override as formatted string"},
    {"get", py_get, METH_VARARGS, "Get config for file:func (returns dict)"},
    {"get_raw_pointer", py_get_raw_pointer, METH_VARARGS, "Get raw config pointer (PyCapsule)"},
    {"shutdown", py_shutdown, METH_NOARGS, "Shutdown and free all tables"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef sffuncspanconfigmodule = {
    PyModuleDef_HEAD_INIT,
    "_sffuncspan_config",
    "Ultra-fast configuration system for function span capture (<5ns lookups)",
    -1,
    ConfigMethods
};

PyMODINIT_FUNC PyInit__sffuncspan_config(void) {
    return PyModule_Create(&sffuncspanconfigmodule);
}
