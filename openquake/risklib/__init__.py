# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (C) 2010-2016 GEM Foundation
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>.

import os
import sys
from openquake.risklib.scientific import (
    VulnerabilityFunction, DegenerateDistribution, classical)
from openquake.baselib.general import search_module, git_suffix

__all__ = ["VulnerabilityFunction", "DegenerateDistribution", "classical"]

# the version is managed by packager.sh with a sed
__version__ = '2.1.0'
__version__ += git_suffix(__file__)

path = search_module('openquake.commonlib.general')
if path:
    sys.exit('Found an obsolete version of commonlib; '
             'please remove %s and/or fix your PYTHONPATH'
             % os.path.dirname(path))
