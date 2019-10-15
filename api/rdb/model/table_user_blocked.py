import logging

from .db import (Timestamped, ForeignKeyField)
from .table_user_profile import User_profile

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class User_blocked(Timestamped):
    # username that wants sender blocked
    recipient_username = ForeignKeyField(User_profile, index=True, on_delete="CASCADE")

    # username of the sender
    blocked_username = ForeignKeyField(User_profile, index=True, on_delete="CASCADE")
