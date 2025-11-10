"""pyytorch-helper package

Expose the helper to download the dataset so callers (or setup hooks)
can call `pyytorch_helper.download_data()`.
"""

from .downloader import download_data

__all__ = ["download_data"]
