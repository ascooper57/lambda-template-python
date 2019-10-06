#  add new table classes here

# http://docs.peewee-orm.com/en/latest/peewee/models.html

from api.rdb.model.db import BooleanField
from api.rdb.model.db import DecimalField
from api.rdb.model.db import IntegerField
from api.rdb.model.db import TextField
from api.rdb.model.db import Timestamped


# noinspection PyPep8Naming
class Sample(Timestamped):
    # Index key column example
    index_key_example = IntegerField(index=True)

    # Integer column example
    integer_example = IntegerField(null=True)

    # Datetime column example
    datetime_example = TextField(null=True)

    # Text column example
    text_example = TextField(null=True)

    # Decimal number column example
    decimal_example = DecimalField(null=True)

    # Boolean column example
    boolean_example = BooleanField(null=True)
