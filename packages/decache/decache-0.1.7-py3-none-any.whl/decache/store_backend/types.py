#!/usr/bin/env python3


class NumpyBlobReference:
    """
    A placeholder object for a large NumPy array stored separately.
    """

    def __init__(self, blob_hash, dtype, shape, order):
        self.blob_hash = blob_hash
        self.dtype = dtype
        self.shape = shape
        self.order = order

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"hash={self.blob_hash[:7]}..., "
            f"shape={self.shape}, dtype={self.dtype})"
        )
