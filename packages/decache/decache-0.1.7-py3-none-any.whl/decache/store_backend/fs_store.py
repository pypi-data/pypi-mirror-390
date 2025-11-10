#!/usr/bin/env python3

import os
from joblib._store_backends import FileSystemStoreBackend
from joblib import hash as joblib_hash
from joblib import numpy_pickle
from joblib import register_store_backend
import numpy as np

from .types import NumpyBlobReference


class ContentAddressableStoreBackend(FileSystemStoreBackend):
    """
    A store backend that supports content-addressable storage for large NumPy arrays.
    """

    def __init__(self, *args, **kwargs):
        # We can accept a custom threshold for what constitutes a large array.
        self.large_array_threshold = kwargs.pop(
            "large_array_threshold", 16 * 1024 * 1024
        )
        super().__init__(*args, **kwargs)
        self.blob_store_path = None

    def configure(self, location, verbose=0, backend_options=dict()):
        if backend_options is None:
            backend_options = {}
        # Allow overriding the threshold during configuration.
        self.large_array_threshold = backend_options.get(
            "large_array_threshold", self.large_array_threshold
        )
        super().configure(location, verbose=verbose, backend_options=backend_options)
        # Create a subdirectory for blobs in the main cache location.
        self.blob_store_path = os.path.join(self.location, "blobs")
        if not os.path.exists(self.blob_store_path):
            os.makedirs(self.blob_store_path, exist_ok=True)

    def _replace_large_arrays(self, item):
        """
        Recursively traverse the item and replace large NumPy arrays
        with NumpyBlobReference.
        """
        if isinstance(item, np.ndarray) and item.nbytes > self.large_array_threshold:
            # 1. Compute the hash of the array content.
            array_hash = joblib_hash(item)
            blob_filename = os.path.join(self.blob_store_path, array_hash)
            # 2. If the blob doesn't exist, dump it.
            if not self._item_exists(blob_filename):

                def write_func(to_write, dest_filename):
                    numpy_pickle.dump(to_write, dest_filename)

                self._concurrency_safe_write(item, blob_filename, write_func)
            # 3. Create and return the placeholder.
            order = "F" if np.isfortran(item) else "C"
            return NumpyBlobReference(
                blob_hash=array_hash, dtype=item.dtype, shape=item.shape, order=order
            )

        # Recursively handle common data structures
        if isinstance(item, list):
            return [self._replace_large_arrays(sub_item) for sub_item in item]
        if isinstance(item, tuple):
            # Note that tuples are immutable, so a new one has to be created.
            return tuple(self._replace_large_arrays(sub_item) for sub_item in item)
        if isinstance(item, dict):
            return {
                key: self._replace_large_arrays(value) for key, value in item.items()
            }

        return item

    def _reconstruct_large_arrays(self, item):
        """
        Recursively traverse the item and reconstruct NumPy arrays from
        NumpyBlobReference.
        """
        if isinstance(item, NumpyBlobReference):
            # 1. Locate the blob file.
            blob_filename = os.path.join(self.blob_store_path, item.blob_hash)
            if not self._item_exists(blob_filename):
                raise FileNotFoundError(
                    f"Blob file not found for hash: {item.blob_hash}"
                )

            # 2. Load the array from the blob file.
            # We should respect the mmap_mode if it's set.
            mmap_mode = self.mmap_mode if hasattr(self, "mmap_mode") else None
            array = numpy_pickle.load(blob_filename, mmap_mode=mmap_mode)

            # (Optional but recommended) Verify that the loaded array matches
            # the metadata.
            assert array.shape == item.shape
            assert array.dtype == item.dtype

            return array

        if isinstance(item, list):
            return [self._reconstruct_large_arrays(sub_item) for sub_item in item]
        if isinstance(item, tuple):
            return tuple(self._reconstruct_large_arrays(sub_item) for sub_item in item)
        if isinstance(item, dict):
            return {
                key: self._reconstruct_large_arrays(value)
                for key, value in item.items()
            }

        return item

    def dump_item(self, call_id, item, verbose=1):
        """
        Before dumping, replace large arrays in the item with references.
        """
        # 1. Transform the item.
        processed_item = self._replace_large_arrays(item)

        # 2. Copy the original dumping logic from the parent class
        #    by directly invoking the implementation from StoreBackendMixin.
        try:
            item_path = os.path.join(self.location, *call_id)
            if not self._item_exists(item_path):
                self.create_location(item_path)
            filename = os.path.join(item_path, "output.pkl")
            if verbose > 10:
                print(f"Persisting metadata in {item_path}")

            def write_func(to_write, dest_filename):
                with self._open_item(dest_filename, "wb") as f:
                    numpy_pickle.dump(to_write, f, compress=self.compress)

            self._concurrency_safe_write(processed_item, filename, write_func)

        except Exception as e:
            import warnings
            from joblib.memory import CacheWarning

            warnings.warn(
                "Unable to cache to disk. Possibly a race condition in the "
                f"creation of the directory. Exception: {e}.",
                CacheWarning,
            )

    def load_item(self, call_id, verbose=1, timestamp=None, metadata=None):
        """
        After loading the item, reconstruct large arrays from their references.
        """

        full_path = os.path.join(self.location, *call_id)
        filename = os.path.join(full_path, "output.pkl")
        if not self._item_exists(filename):
            raise KeyError(f"Non-existing item: {filename}")

        mmap_mode = self.mmap_mode if hasattr(self, "mmap_mode") else None

        if mmap_mode is None:
            with self._open_item(filename, "rb") as f:
                processed_item = numpy_pickle.load(f)
        else:
            processed_item = numpy_pickle.load(filename, mmap_mode=mmap_mode)

        reconstructed_item = self._reconstruct_large_arrays(processed_item)

        return reconstructed_item


def register_cas_store_backend():
    """Register the S3 store backend for joblib memory caching."""
    register_store_backend("cas", ContentAddressableStoreBackend)
