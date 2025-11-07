# Copyright (c) 2022, California Institute of Technology and contributors
#
# You should have received a copy of the licensing terms for this
# software included in the file "LICENSE" located in the top-level
# directory of this package. If you did not, you can view a copy at
# https://git.ligo.org/ngdd/arrakis-python/-/raw/main/LICENSE

from datetime import timedelta

import numpy

DEFAULT_ARRAKIS_SERVER = "grpc://0.0.0.0:31206"

DEFAULT_MATCH = ".*"
DEFAULT_TIMEOUT = timedelta(seconds=2)
DEFAULT_QUEUE_TIMEOUT = timedelta(milliseconds=125)

MIN_SAMPLE_RATE = 0
MAX_SAMPLE_RATE = numpy.iinfo(numpy.uint32).max
