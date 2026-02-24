import logging
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from app.config import get_settings

_client: AsyncIOMotorClient | None = None
_db = None
_logger = logging.getLogger("uvicorn.error")

async def init_db() -> None:
    global _client, _db
    settings = get_settings()
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGODB_URI)
    _db = _client[settings.MONGODB_DB]
    try:
        await _db.command("ping")
        _logger.info("MongoDB connected: %s", settings.MONGODB_DB)
    except Exception as exc:
        _logger.exception("MongoDB connection failed")
        raise RuntimeError(f"MongoDB connection failed: {exc}") from exc
    await _db["leads"].create_index("created_at")
    await _db["leads"].create_index("company_name")
    await _db["leads"].create_index("company_domain")

def get_db():
    if _db is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _db

def get_leads_collection():
    return get_db()["leads"]

def serialize_lead(doc: dict) -> dict:
    if not doc:
        return doc
    if "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc

def to_object_id(lead_id: str) -> ObjectId:
    return ObjectId(lead_id)

async def close_db() -> None:
    global _client
    if _client is not None:
        _client.close()
