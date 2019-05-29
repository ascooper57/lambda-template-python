import sys

from .config import init

# Must initialize the config module before proceeding
init(module=sys.modules[__package__])

# noinspection PyPep8
from .model import *
