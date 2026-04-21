// We use SHA-256 for chunk integrity
self.onmessage = async (e) => {
    const { chunk, chunkId } = e.data;
    
    try {
        const hashBuffer = await crypto.subtle.digest('SHA-256', chunk);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        
        self.postMessage({ chunkId, hash: hashHex });
    } catch (error: any) {
        self.postMessage({ chunkId, error: error.message });
    }
};
