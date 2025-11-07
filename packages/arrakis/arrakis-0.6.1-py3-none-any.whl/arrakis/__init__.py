# Copyright (c) 2022, California Institute of Technology and contributors
#
# You should have received a copy of the licensing terms for this
# software included in the file "LICENSE" located in the top-level
# directory of this package. If you did not, you can view a copy at
# https://git.ligo.org/ngdd/arrakis-python/-/raw/main/LICENSE

try:
    from ._version import version as __version__
except ModuleNotFoundError:
    import setuptools_scm

    __version__ = setuptools_scm.get_version(fallback_version="?.?.?")

from .api import count as count
from .api import describe as describe
from .api import fetch as fetch
from .api import find as find
from .api import stream as stream
from .block import Freq as Freq
from .block import SeriesBlock as SeriesBlock
from .block import Time as Time
from .channel import Channel as Channel
from .client import Client as Client
from .publish import Publisher as Publisher
