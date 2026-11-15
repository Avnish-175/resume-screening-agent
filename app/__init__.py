"""Resume Screening Agent package."""

# Compatibility shims for huggingface_hub / datasets with newer Python/package versions
try:
    import huggingface_hub.errors
    if not hasattr(huggingface_hub.errors, "BucketNotFoundError"):
        class BucketNotFoundError(Exception):
            """Fallback BucketNotFoundError shim."""
        huggingface_hub.errors.BucketNotFoundError = BucketNotFoundError
except Exception:
    pass

try:
    import huggingface_hub.hf_file_system
    if not hasattr(huggingface_hub.hf_file_system, "HfFileSystemResolvedBucketPath"):
        class HfFileSystemResolvedBucketPath:
            pass
        huggingface_hub.hf_file_system.HfFileSystemResolvedBucketPath = HfFileSystemResolvedBucketPath
    if not hasattr(huggingface_hub.hf_file_system, "HfFileSystemResolvedRepositoryPath"):
        class HfFileSystemResolvedRepositoryPath:
            pass
        huggingface_hub.hf_file_system.HfFileSystemResolvedRepositoryPath = HfFileSystemResolvedRepositoryPath
except Exception:
    pass

try:
    import huggingface_hub.utils
    if not hasattr(huggingface_hub.utils, "httpx"):
        try:
            import httpx2
            huggingface_hub.utils.httpx = httpx2
        except ImportError:
            pass
except Exception:
    pass
