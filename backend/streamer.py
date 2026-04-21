import asyncio
import logging
import json
import os
from hasher import calculate_sha256

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHUNK_SIZE = 1024 * 1024 * 16  # 16MB Optimized for Wi-Fi 6

class DataStreamServer:
    def __init__(self, host='0.0.0.0', port=8888, db_handler=None):
        self.host = host
        self.port = port
        self.db_handler = db_handler # Placeholder for DB operations
        self.is_running = False

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        logger.info(f"Accepted connection from {addr}")

        try:
            while True:
                # 1. Read Header (JSON, fixed size 1024 bytes for simplicity or prefix size)
                header_size_data = await reader.read(4)
                if not header_size_data:
                    break
                
                header_size = int.from_bytes(header_size_data, 'big')
                header_data = await reader.readexactly(header_size)
                header = json.loads(header_data.decode())

                # Header example: {"type": "CHUNK", "id": 1, "size": 4096, "hash": "sha...", "offset": 0}
                data_type = header.get("type")
                
                if data_type == "MANIFEST":
                    logger.info("Received Manifest Map")
                    # Handle manifest storage
                    continue

                if data_type == "CHUNK":
                    chunk_id = header.get("id")
                    expected_size = header.get("size")
                    expected_hash = header.get("hash")
                    
                    # 2. Read Raw Data
                    data = await reader.readexactly(expected_size)
                    
                    # 3. Verify Hash (Atomic Check)
                    actual_hash = calculate_sha256(data)
                    if actual_hash == expected_hash:
                        logger.info(f"Chunk {chunk_id} verified successfully.")
                        # 4. Stream to Hot-Buffer (DB)
                        if self.db_handler:
                            await self.db_handler.save_chunk(chunk_id, data, actual_hash)
                        
                        # Send ACK
                        writer.write(b"ACK" + chunk_id.to_bytes(4, 'big'))
                        await writer.drain()
                    else:
                        logger.error(f"Hash mismatch for chunk {chunk_id}!")
                        writer.write(b"ERR" + chunk_id.to_bytes(4, 'big'))
                        await writer.drain()

        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            logger.info(f"Connection from {addr} closed")

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = server.sockets[0].getsockname()
        logger.info(f"Serving on {addr}")
        self.is_running = True
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    server = DataStreamServer()
    asyncio.run(server.start())
