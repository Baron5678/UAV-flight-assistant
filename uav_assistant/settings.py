from typing import cast

from uav_assistant.infra.db.interfaces import Database
from uav_assistant.infra.db.mongo.mongo import MongoDatabase
from uav_assistant.infra.db.postgre.postgre import PostgresDatabase


DATABASES: tuple[Database, ...] = (
    PostgresDatabase(),
    MongoDatabase(),
)

POSTGRES_DATABASE = cast(PostgresDatabase, DATABASES[0])
MONGO_DATABASE = cast(MongoDatabase, DATABASES[1])
