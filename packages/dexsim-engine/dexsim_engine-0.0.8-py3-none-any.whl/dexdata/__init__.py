# ----------------------------------------------------------------------------
# Copyright (c) 2021-2023 DexForce Technology Co., Ltd.
#
# All rights reserved.
# ----------------------------------------------------------------------------
import os
from dexdata.version import version


__version__ = version

DEXDATA_BASE_PATH = os.path.join(os.path.expanduser("~"), "dexdata")
