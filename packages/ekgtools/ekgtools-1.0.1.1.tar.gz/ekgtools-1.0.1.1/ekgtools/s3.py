import threading
from typing import Optional, Any, Dict
import fsspec
import s3fs

class S3Setup:

    def __init__(self, bucket: str, prefix: str, endpoint_url: str, access_key_id: str, secret_key: str, region_name: str, use_ssl: bool = False) -> None:
        self.bucket = bucket 
        self.prefix = prefix          
        self.endpoint_url = endpoint_url
        self.access_key_id = access_key_id
        self.secret_access_key = secret_key
        self.region_name = region_name
        self.use_ssl: bool = False           # True if your endpoint is https
        self._local = threading.local() # Thread/worker-local filesystem so each DataLoader worker has its own client

    def local_path_to_s3_key(self, local_path: str, base_local="/path/to"):  
        """
        Map a local-style path to an S3 key under the configured prefix.
        Example:
        /path/to/ECG/2021/abc.xml  ->  ecg/ECG/2021/abc.xml
        """
        # Strip the common local base
        if local_path.startswith(base_local.rstrip("/")):
            rel = local_path[len(base_local.rstrip("/")):].lstrip("/")
        else:
            rel = local_path.lstrip("/")
        return f"{self.prefix}/{rel}"

    def _get_fs(self, cache_dir: Optional[str] = None):
        """
        Returns an fsspec filesystem for S3 (MinIO).
        If cache_dir is provided, wraps access through a simple local cache.
        """
        if getattr(self._local, "fs", None) is None or getattr(self._local, "cache_dir", None) != cache_dir:
            s3_kwargs: Dict[str, Any] = {
                "key":self.access_key_id,
                "secret": self.secret_access_key,
                "anon": False,
                "client_kwargs": {
                    "endpoint_url": self.endpoint_url,
                    "region_name": self.region_name,
                },
                # Avoid very small reads; tune as needed
                "config_kwargs": {"signature_version": "s3v4"},
            }
            base_fs = s3fs.S3FileSystem(**s3_kwargs)

            if cache_dir:
                # Use fsspec's "simplecache" to store whole objects locally after first read
                # You can also consider "filecache" if you want chunked caching.
                fs = fsspec.filesystem(
                    "simplecache",
                    target_protocol="s3",
                    target_options=s3_kwargs,
                    cache_storage=cache_dir,
                )
            else:
                fs = base_fs

            self._local.fs = fs
            self._local.cache_dir = cache_dir
        return self._local.fs