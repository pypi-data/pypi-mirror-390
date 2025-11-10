# decache


A custom store backend for `joblib` that de-duplicates large NumPy arrays to save significant disk space in scientific computing and machine learning workflows.

## The Problem

`joblib.Memory` is an invaluable tool for caching the results of expensive function calls. It works by serializing the function's inputs and outputs, storing the output in a file system cache. When the function is called again with the same inputs, the output is retrieved from the cache, avoiding re-computation.

However, the standard caching mechanism operates at the *function call level*. If two different function calls (or calls to different functions) happen to return the exact same large NumPy array, `joblib` will save this array to disk **twice**, once for each cache entry.

In data-intensive fields, it's common for various preprocessing or simulation steps to produce identical, multi-gigabyte arrays. This redundancy can lead to massive consumption of disk space, especially in long-running projects with extensive caching.

## The Solution: Content-Addressable Storage

This project introduces the `ContentAddressableStoreBackend` (CAS), a drop-in replacement backend for `joblib.Memory` that solves this problem through content-addressable storage.

Instead of storing everything in a single file per function call, it intelligently separates large NumPy arrays and stores them based on the **hash of their content**.

### How It Works

1.  **Interception**: The backend intercepts the output of a cached function before it's saved to disk.
2.  **Traversal & Identification**: It recursively scans the output for NumPy arrays that exceed a configurable size threshold (e.g., 16 MB).
3.  **Hashing & De-duplication**: For each large array, it computes a unique hash of its data. The array is then saved to a central `blobs` directory, using its hash as the filename. If a file with that name already exists, it means the exact same array has been seen before, and no new data is written.
4.  **Replacement**: In the original function output, the large array is replaced with a small, lightweight placeholder object. This placeholder contains the array's hash and metadata (like its shape and data type).
5.  **Reconstruction**: When a result is loaded from the cache, the backend reverses the process. It loads the structure containing placeholders, and for each placeholder, it reads the corresponding array from the `blobs` directory to seamlessly reconstruct the original object.

The result is that any given large array is **only ever stored once on disk**, regardless of how many times it appears in your cache.

## Features

-   **Automatic De-duplication**: Drastically reduces disk space usage when caching functions that return identical large NumPy arrays.
-   **Transparent Integration**: Works as a drop-in backend for `joblib.Memory` with no changes needed to your existing cached functions.
-   **Configurable Threshold**: You can easily define what constitutes a "large" array via `backend_options`.
-   **Handles Nested Structures**: Correctly processes large arrays nested within lists, tuples, and dictionaries.

## Installation

``` bash
pip install decache
```

## Usage

Using the backend is straightforward. First, you must register it with `joblib`, and then you can instantiate `joblib.Memory` with the new backend.

Here is a complete example demonstrating the de-duplication feature:

```python
import joblib
import numpy as np
import shutil
from pathlib import Path

# 1. Import and register the custom backend
from decache.store_backend import register_cas_store_backend
register_cas_store_backend()

# 2. Define the cache directory and create the Memory object
#    Specify 'cas' as the backend and configure the threshold.
CACHE_DIR = "/tmp/decache"
memory = joblib.Memory(
    location=CACHE_DIR,
    backend="cas",
    backend_options={'large_array_threshold': 1 * 1024 * 1024},  # 1 MB
    verbose=10
)

# This array is large (~8 MB) and its content is identical every time.
IDENTICAL_LARGE_ARRAY = np.arange(1024 * 1024, dtype=np.float64)

@memory.cache
def process_data_source_a(source_id):
    """A cached function that returns a large, constant array."""
    print(f"Executing process_data_source_a for source '{source_id}'...")
    return IDENTICAL_LARGE_ARRAY.copy()

@memory.cache
def process_data_source_b(config_dict):
    """A completely different cached function that returns the same large array."""
    print(f"Executing process_data_source_b for config '{config_dict}'...")
    return IDENTICAL_LARGE_ARRAY.copy()

if __name__ == '__main__':
    # Call the first function. It will run and store the result.
    # A single blob for IDENTICAL_LARGE_ARRAY will be created.
    result_a = process_data_source_a("source1")

    # Call the second function. Its input is different, so it will also run.
    # However, since its output array is identical, it will *reuse* the existing blob.
    result_b = process_data_source_b({'user': 'test', 'version': 2})

    print("\n--- Cache Inspection ---")

    blobs_dir = Path(CACHE_DIR) / "joblib" / "blobs"
    blob_count = len(list(blobs_dir.iterdir()))
    print(f"Number of blobs stored: {blob_count}")

    # Although two functions were cached, only one blob file was created.
    assert blob_count == 1

    # Clean up
    # shutil.rmtree(CACHE_DIR)
```

## Running Tests

The backend comes with a comprehensive test suite using `pytest`. To run the tests, first install the dependencies:

```bash
pip install pytest 
```

Then, from the root of the project, simply run:

```bash
pytest
```

## Limitations and Future Work

-   **Garbage Collection**: This implementation does not automatically clean up "orphaned" blobs. If cache entries are cleared (e.g., via `memory.clear()`), the corresponding files in the `blobs` directory are not removed. A separate garbage collection script could be implemented to scan all cache entries and remove any unreferenced blobs.

## License

This project is licensed under the MIT License.
