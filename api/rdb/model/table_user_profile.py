# add new table classes here

import logging

from api.rdb.model.db import TextField
from api.rdb.model.db import Timestamped
from api.rdb.model.db import UUIDField

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# noinspection PyPep8Naming
class User_profile(Timestamped):
    # Foreign Key column example (email id)
    username = TextField(index=True)

    # phone number who'll receive an SMS message in e.I64 format. https://www.twilio.com/docs/glossary/what-e164

    given_name = TextField(null=True)

    family_name = TextField(null=True)

    avatar = UUIDField(default='00000000-0000-0000-0000-000000000000')

    address_line1 = TextField(null=True)

    address_line2 = TextField(null=True)

    city = TextField(null=True)

    state_or_province = TextField(null=True)

    postal_code = TextField(null=True)

    country_code = TextField(null=True)

