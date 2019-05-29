import logging

from .db import (BaseModel, CharField, DateTimeField)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DatabaseMigration(BaseModel):
    name = CharField(max_length=1000, unique=True)

    migrated_at = DateTimeField(null=True)

    migrated_at._sort_key = (2, 998)
