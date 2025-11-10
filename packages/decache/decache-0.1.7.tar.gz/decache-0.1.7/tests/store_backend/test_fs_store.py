# test_cas_backend.py
import pytest
import joblib
import numpy as np
from pathlib import Path

from decache.store_backend import register_cas_store_backend

pytestmark = [pytest.mark.doing]

# Register the custom backend before tests run
register_cas_store_backend()


class Counter:
    def __init__(self, n=0):
        self.count = n

    def call(self, n):
        self.count += n
        return self.count

    def call_once(self):
        return self.call(1)


# Pytest fixture to provide a temporary cache directory and a configured Memory object
@pytest.fixture
def memory_cas(tmp_path):
    """Provides a joblib.Memory instance with the CAS backend in a temp dir."""
    cache_dir = tmp_path / "joblib_cache"
    memory = joblib.Memory(
        location=cache_dir,
        backend="cas",
        backend_options={
            "large_array_threshold": 1024 * 1024
        },  # 1MB threshold for tests
        verbose=0,
    )
    yield memory
    # Teardown: clean up the cache directory
    # shutil.rmtree(cache_dir)


# --- Test Implementations ---


def test_large_array_splitting(memory_cas):
    """Tests that a large array is split into a blob."""

    counter = Counter()

    @memory_cas.cache
    def create_data(size):
        # Array size > 1MB threshold
        counter.call_once()
        return np.ones(size, dtype=np.uint8)

    # First call: executes the function
    original_result = create_data(2 * 1024 * 1024)

    # Second call: should hit the cache
    cached_result = create_data(2 * 1024 * 1024)

    # Assertions
    assert np.array_equal(original_result, cached_result)
    assert counter.count == 1

    # Check filesystem
    blobs_dir = Path(memory_cas.location) / "blobs"
    assert blobs_dir.exists()
    blob_files = list(blobs_dir.iterdir())
    assert len(blob_files) == 1

    # Check that hashed numpy array size is
    output_pkl = list(Path(memory_cas.location).glob("**/output.pkl"))[
        0
    ]  # get the first function cache dir
    assert (
        output_pkl.stat().st_size < 1024
    )  # Should be very small, just the reference object


def test_small_array_no_splitting(memory_cas):
    """Tests that a small array is stored inline."""

    counter = Counter()

    @memory_cas.cache
    def create_small_data(size):
        # Array size < 1MB threshold
        counter.call_once()
        return np.ones(size, dtype=np.uint8)

    create_small_data(512 * 1024)  # Call to populate cache
    create_small_data(512 * 1024)  # Call to hit cache

    assert counter.count == 1

    # Check filesystem: blobs dir should be empty
    blobs_dir = Path(memory_cas.location) / "blobs"
    assert not list(blobs_dir.iterdir())  # Should be empty


def test_data_deduplication(memory_cas):
    """Tests that identical large arrays are stored as a single blob."""
    # This array will be returned by two different function calls
    identical_large_array = np.arange(500_000, dtype=np.float64)  # ~4MB

    counter_a = Counter()
    counter_b = Counter()

    @memory_cas.cache
    def func_a(x):
        counter_a.call_once()
        return identical_large_array.copy()

    @memory_cas.cache
    def func_b(y, z):
        counter_b.call_once()
        return identical_large_array.copy()

    # Call both functions with different arguments
    res_a = func_a(1)
    res_b = func_b(2, 3)

    # Assertions
    assert counter_a.count == 1
    assert counter_b.count == 1
    assert np.array_equal(res_a, res_b)

    # Crucial check: two function caches, but only one blob
    blobs_dir = Path(memory_cas.location) / "blobs"
    assert len(list(blobs_dir.iterdir())) == 1


def test_complex_nested_structure(memory_cas):
    """Tests caching with a complex structure of large and small arrays."""

    counter = Counter()

    @memory_cas.cache
    def create_complex_data():
        counter.call_once()
        return {
            "large1": np.full((1024, 1024), 1, dtype=np.int32),  # 4MB
            "data": [
                np.full((1024, 1024), 2, dtype=np.int32),  # 4MB, different content
                "some_string",
                np.zeros(100),  # small array
            ],
        }

    original = create_complex_data()
    cached = create_complex_data()

    # Assertions
    assert counter.count == 1
    # Deep comparison
    assert original.keys() == cached.keys()
    assert np.array_equal(original["large1"], cached["large1"])
    assert np.array_equal(original["data"][0], cached["data"][0])
    assert original["data"][1] == cached["data"][1]
    assert np.array_equal(original["data"][2], cached["data"][2])

    # Check filesystem: two unique large arrays -> two blobs
    blobs_dir = Path(memory_cas.location) / "blobs"
    assert len(list(blobs_dir.iterdir())) == 2


def test_no_numpy_arrays(memory_cas):
    """Tests caching of objects without any numpy arrays."""

    counter = Counter()

    @memory_cas.cache
    def get_plain_data(a):
        counter.call_once()
        return {"a": a, "b": [1, 2, 3]}

    get_plain_data(1)
    get_plain_data(1)

    assert counter.count == 1
    blobs_dir = Path(memory_cas.location) / "blobs"
    assert not list(blobs_dir.iterdir())
