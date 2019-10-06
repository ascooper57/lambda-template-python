import logging

from playhouse.postgres_ext import HStoreField, TSVectorField

from .db import (ForeignKeyField, Timestamped, UUIDField, DateTimeField, DecimalField, IntegerField)
from .table_user_profile import User_profile

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Media(Timestamped):
    # S3 bucket where the  medias lives
    media_uuid = UUIDField(primary_key=True, index=True)

    # Subscription's username is the Subscription's ID
    username = ForeignKeyField(User_profile, on_delete="CASCADE", index=True)

    # comma separated list of tags
    tags = HStoreField(null=True, index=True)

    # description of what the media is about - full text search
    description = TSVectorField(null=True)

    # geocode info
    latitude = DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = DecimalField(max_digits=9, decimal_places=6, null=True)

    # time taken
    media_created = DateTimeField(null=True)

    # likes
    likes = IntegerField(default=0)
