import logging

__version__ = "1.6.4"
logger = logging.getLogger("pyemd")

from .CEEMDAN import CEEMDAN  # noqa
from .EEMD import EEMD  # noqa
from .EMD import EMD  # noqa
from .visualisation import Visualisation  # noqa
