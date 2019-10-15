import logging

from .db import (Timestamped, TextField, ForeignKeyField)
from .table_user_profile import User_profile

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class User_message(Timestamped):
    # name - on_delete cascade is for for testing as we never really delete users in production
    from_username = ForeignKeyField(User_profile, index=True, on_delete="CASCADE")

    # message text
    message = TextField()

    # emil of the recipient
    to_username = ForeignKeyField(User_profile, index=True, on_delete="CASCADE")

    # AWS SNS message sent id
    sns_message_id = TextField(null=True)
