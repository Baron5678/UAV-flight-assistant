from pymongo.asynchronous.database import AsyncDatabase

from uav_assistant.settings import MONGO_DATABASE


async def get_database() -> AsyncDatabase:
    return MONGO_DATABASE.database
