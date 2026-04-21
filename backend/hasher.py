import hashlib
import concurrent.futures
import os

def calculate_sha256(chunk_data):
    """Calculate SHA-256 for a single chunk of data."""
    sha256_hash = hashlib.sha256()
    sha256_hash.update(chunk_data)
    return sha256_hash.hexdigest()

class ParallelHasher:
    def __init__(self, max_workers=None):
        self.executor = concurrent.futures.ProcessPoolExecutor(max_workers=max_workers)

    async def hash_chunks(self, chunks_list):
        """Asynchronously hash a list of chunks using a process pool."""
        loop = os.get_event_loop()
        futures = [loop.run_in_executor(self.executor, calculate_sha256, chunk) for chunk in chunks_list]
        return await concurrent.futures.gather(*futures)

    def shutdown(self):
        self.executor.shutdown()
