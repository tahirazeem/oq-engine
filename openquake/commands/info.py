# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (C) 2014-2016 GEM Foundation
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

from __future__ import print_function
import os
import logging
import operator
from openquake.baselib.general import groupby
from openquake.baselib.performance import Monitor
from openquake.commonlib import (
    sap, nrml, readinput, reportwriter, datastore, views)
from openquake.commonlib.parallel import get_pickled_sizes
from openquake.commonlib.export import export
from openquake.calculators import base
from openquake.hazardlib import gsim


def print_csm_info(fname):
    """
    Parse the composite source model without instantiating the sources and
    prints information about its composition and the full logic tree
    """
    oqparam = readinput.get_oqparam(fname)
    csm = readinput.get_composite_source_model(oqparam, in_memory=False)
    print(csm.info)
    print('See https://github.com/gem/oq-risklib/blob/master/doc/'
          'effective-realizations.rst for an explanation')
    rlzs_assoc = csm.info.get_rlzs_assoc()
    print(rlzs_assoc)
    tot, pairs = get_pickled_sizes(rlzs_assoc)
    print(views.rst_table(pairs, ['attribute', 'nbytes']))


def do_build_reports(directory):
    """
    Walk the directory and builds pre-calculation reports for all the
    job.ini files found.
    """
    for cwd, dirs, files in os.walk(directory):
        for f in files:
            if f in ('job.ini', 'job_h.ini', 'job_haz.ini', 'job_hazard.ini'):
                job_ini = os.path.join(cwd, f)
                print(job_ini)
                reportwriter.build_report(job_ini, cwd)


# the documentation about how to use this feature can be found
# in the file effective-realizations.rst
@sap.Script
def info(calculators, gsims, views, exports, build_reports, report,
         input_file=''):
    """
    Give information. You can pass the name of an available calculator,
    a job.ini file, or a zip archive with the input files.
    """
    logging.basicConfig(level=logging.INFO)
    if calculators:
        for calc in sorted(base.calculators):
            print(calc)
    if gsims:
        for gs in gsim.get_available_gsims():
            print(gs)
    if views:
        for name in sorted(datastore.view):
            print(name)
    if exports:
        dic = groupby(export, operator.itemgetter(0),
                      lambda group: [r[1] for r in group])
        n = 0
        for exporter, formats in dic.items():
            print(exporter, formats)
            n += len(formats)
        print('There are %d exporters defined.' % n)
    if build_reports:
        do_build_reports(input_file or '.')
    if input_file.endswith('.xml'):
        print(nrml.read(input_file).to_str())
    elif input_file.endswith(('.ini', '.zip')):
        with Monitor('info', measuremem=True) as mon:
            if report:
                print('Generated', reportwriter.build_report(input_file))
            else:
                print_csm_info(input_file)
        if mon.duration > 1:
            print(mon)
    elif input_file:
        print("No info for '%s'" % input_file)

info.flg('calculators', 'list available calculators')
info.flg('gsims', 'list available GSIMs')
info.flg('views', 'list available views')
info.flg('exports', 'list available exports')
info.flg('build_reports', 'build reports in rst format')
info.flg('report', 'build a report in rst format')
info.arg('input_file', 'job.ini file or zip archive')
