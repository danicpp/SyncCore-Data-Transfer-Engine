from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import asyncio
import logging
from streamer import DataStreamServer
from db import init_db, DBHandler, AsyncSessionLocal, Transfer
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    await init_db()
    # Start TCP Streaming Server in background
    app.state.stream_server = DataStreamServer(db_handler=DBHandler)
    asyncio.create_task(app.state.stream_server.start())
    yield
    # Cleanup if needed

app = FastAPI(title="Data Transfer Engine", lifespan=lifespan)

class ManifestItem(BaseModel):
    path: str
    size: int
    hash: str

class StartTransferRequest(BaseModel):
    id: str
    name: str # The task name
    device_name: str # The device name (e.g., 'Pixel 7')
    manifest: list[ManifestItem]

@app.get("/")
async def root():
    return {"status": "online", "msg": "High-Performance Data Sync Engine Active"}

@app.post("/transfer/start")
async def start_transfer(req: StartTransferRequest):
    # Ensure destination folder exists
    base_dir = os.path.join("transfers", req.device_name)
    os.makedirs(base_dir, exist_ok=True)

    async with AsyncSessionLocal() as session:
        new_transfer = Transfer(
            id=req.id,
            name=req.name,
            total_size=sum(item.size for item in req.manifest),
            status="IN_PROGRESS"
        )
        session.add(new_transfer)
        await session.commit()
    
    return {"status": "started", "transfer_id": req.id, "base_dir": base_dir}

@app.get("/transfer/{transfer_id}/status")
async def get_status(transfer_id: str):
    async with AsyncSessionLocal() as session:
        transfer = await session.get(Transfer, transfer_id)
        if not transfer:
            raise HTTPException(status_code=404, detail="Transfer not found")
        
        return {
            "id": transfer.id,
            "status": transfer.status,
            "total_size": transfer.total_size,
            "created_at": transfer.created_at
        }

@app.post("/troubleshoot/adb")
async def troubleshoot_adb():
    # Placeholder for agent-led troubleshooting logic
    # In a real scenario, this would execute shell commands and parse output
    return {
        "check": "ADB Status",
        "result": "Not Found",
        "suggestion": "Ensure USB Debugging is enabled and adb.exe is in PATH."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
