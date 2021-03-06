# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (C) 2015-2016 GEM Foundation
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

import time
import os.path
import operator
import logging
import functools
import collections

import numpy

from openquake.baselib import hdf5
from openquake.baselib.python3compat import encode
from openquake.baselib.general import AccumDict, group_array
from openquake.hazardlib.calc.filters import \
    filter_sites_by_distance_to_rupture
from openquake.hazardlib.calc.hazard_curve import (
    array_of_curves, ProbabilityMap)
from openquake.hazardlib import geo
from openquake.hazardlib.gsim.base import ContextMaker
from openquake.commonlib import readinput, parallel, calc
from openquake.commonlib.util import max_rel_diff_index, Rupture
from openquake.risklib.riskinput import create
from openquake.calculators import base
from openquake.calculators.classical import ClassicalCalculator, PSHACalculator

# ######################## rupture calculator ############################ #

U16 = numpy.uint16
U32 = numpy.uint32
F32 = numpy.float32
POEMAP = 1

event_dt = numpy.dtype([('eid', U32), ('ses', U32), ('occ', U32),
                        ('sample', U32)])


def get_geom(surface, is_from_fault_source, is_multi_surface):
    """
    The following fields can be interpreted different ways,
    depending on the value of `is_from_fault_source`. If
    `is_from_fault_source` is True, each of these fields should
    contain a 2D numpy array (all of the same shape). Each triple
    of (lon, lat, depth) for a given index represents the node of
    a rectangular mesh. If `is_from_fault_source` is False, each
    of these fields should contain a sequence (tuple, list, or
    numpy array, for example) of 4 values. In order, the triples
    of (lon, lat, depth) represent top left, top right, bottom
    left, and bottom right corners of the the rupture's planar
    surface. Update: There is now a third case. If the rupture
    originated from a characteristic fault source with a
    multi-planar-surface geometry, `lons`, `lats`, and `depths`
    will contain one or more sets of 4 points, similar to how
    planar surface geometry is stored (see above).

    :param rupture: an instance of :class:`openquake.hazardlib.source.rupture.BaseProbabilisticRupture`
    :param is_from_fault_source: a boolean
    :param is_multi_surface: a boolean
    """
    if is_from_fault_source:
        # for simple and complex fault sources,
        # rupture surface geometry is represented by a mesh
        surf_mesh = surface.get_mesh()
        lons = surf_mesh.lons
        lats = surf_mesh.lats
        depths = surf_mesh.depths
    else:
        if is_multi_surface:
            # `list` of
            # openquake.hazardlib.geo.surface.planar.PlanarSurface
            # objects:
            surfaces = surface.surfaces

            # lons, lats, and depths are arrays with len == 4*N,
            # where N is the number of surfaces in the
            # multisurface for each `corner_*`, the ordering is:
            #   - top left
            #   - top right
            #   - bottom left
            #   - bottom right
            lons = numpy.concatenate([x.corner_lons for x in surfaces])
            lats = numpy.concatenate([x.corner_lats for x in surfaces])
            depths = numpy.concatenate([x.corner_depths for x in surfaces])
        else:
            # For area or point source,
            # rupture geometry is represented by a planar surface,
            # defined by 3D corner points
            lons = numpy.zeros((4))
            lats = numpy.zeros((4))
            depths = numpy.zeros((4))

            # NOTE: It is important to maintain the order of these
            # corner points. TODO: check the ordering
            for i, corner in enumerate((surface.top_left,
                                        surface.top_right,
                                        surface.bottom_left,
                                        surface.bottom_right)):
                lons[i] = corner.longitude
                lats[i] = corner.latitude
                depths[i] = corner.depth
    return lons, lats, depths


class EBRupture(object):
    """
    An event based rupture. It is a wrapper over a hazardlib rupture
    object, containing an array of site indices affected by the rupture,
    as well as the tags of the corresponding seismic events.
    """
    def __init__(self, rupture, indices, events, source_id, grp_id, serial):
        self.rupture = rupture
        self.indices = indices
        self.events = events
        self.source_id = source_id
        self.grp_id = grp_id
        self.serial = serial
        self.weight = len(indices) * len(events)  # changed in set_weight

    @property
    def etags(self):
        """
        An array of tags for the underlying seismic events
        """
        tags = []
        for (eid, ses, occ, sampleid) in self.events:
            tag = 'trt=%02d~ses=%04d~src=%s~rup=%d-%02d' % (
                self.grp_id, ses, self.source_id, self.serial, occ)
            if sampleid > 0:
                tag += '~sample=%d' % sampleid
            tags.append(encode(tag))
        return numpy.array(tags)

    @property
    def eids(self):
        """
        An array with the underlying event IDs
        """
        return self.events['eid']

    @property
    def multiplicity(self):
        """
        How many times the underlying rupture occurs.
        """
        return len(self.events)

    def set_weight(self, num_rlzs_by_grp_id, num_assets_by_site_id):
        """
        Set the weight attribute of each rupture with the formula
        weight = multiplicity * affected_sites * realizations

        :param num_rlzs_by_grp_id: dictionary, possibly empty
        :param num_assets_by_site_id: dictionary, possibly empty
        """
        num_assets = sum(num_assets_by_site_id.get(sid, 1)
                         for sid in self.indices)
        self.weight = (len(self.events) * num_assets *
                       num_rlzs_by_grp_id.get(self.grp_id, 1))

    def export(self, mesh):
        """
        Yield :class:`openquake.commonlib.util.Rupture` objects, with all the
        attributes set, suitable for export in XML format.
        """
        rupture = self.rupture
        for etag in self.etags:
            new = Rupture(etag, self.indices)
            new.mesh = mesh[self.indices]
            new.etag = etag
            new.rupture = new
            new.is_from_fault_source = iffs = isinstance(
                rupture.surface, (geo.ComplexFaultSurface,
                                  geo.SimpleFaultSurface))
            new.is_multi_surface = ims = isinstance(
                rupture.surface, geo.MultiSurface)
            new.lons, new.lats, new.depths = get_geom(
                rupture.surface, iffs, ims)
            new.surface = rupture.surface
            new.strike = rupture.surface.get_strike()
            new.dip = rupture.surface.get_dip()
            new.rake = rupture.rake
            new.hypocenter = rupture.hypocenter
            new.tectonic_region_type = rupture.tectonic_region_type
            new.magnitude = new.mag = rupture.mag
            new.top_left_corner = None if iffs or ims else (
                new.lons[0], new.lats[0], new.depths[0])
            new.top_right_corner = None if iffs or ims else (
                new.lons[1], new.lats[1], new.depths[1])
            new.bottom_left_corner = None if iffs or ims else (
                new.lons[2], new.lats[2], new.depths[2])
            new.bottom_right_corner = None if iffs or ims else (
                new.lons[3], new.lats[3], new.depths[3])
            yield new

    def __lt__(self, other):
        return self.serial < other.serial

    def __repr__(self):
        return '<%s #%d, grp_id=%d>' % (self.__class__.__name__,
                                        self.serial, self.grp_id)


@parallel.litetask
def compute_ruptures(sources, sitecol, siteidx, rlzs_assoc, monitor):
    """
    :param sources:
        List of commonlib.source.Source tuples
    :param sitecol:
        a :class:`openquake.hazardlib.site.SiteCollection` instance
    :param siteidx:
        always equal to 0
    :param rlzs_assoc:
        a :class:`openquake.commonlib.source.RlzsAssoc` instance
    :param monitor:
        monitor instance
    :returns:
        a dictionary src_group_id -> [Rupture instances]
    """
    assert siteidx == 0, (
        'siteidx can be nonzero only for the classical_tiling calculations: '
        'tiling with the EventBasedRuptureCalculator is an error')
    # NB: by construction each block is a non-empty list with
    # sources of the same src_group_id
    src_group_id = sources[0].src_group_id
    oq = monitor.oqparam
    trt = sources[0].tectonic_region_type
    max_dist = oq.maximum_distance[trt]
    cmaker = ContextMaker(rlzs_assoc.gsims_by_grp_id[src_group_id])
    params = sorted(cmaker.REQUIRES_RUPTURE_PARAMETERS)
    rup_data_dt = numpy.dtype(
        [('rupserial', U32), ('multiplicity', U16),
         ('numsites', U32), ('occurrence_rate', F32)] + [
            (param, F32) for param in params])
    eb_ruptures = []
    rup_data = []
    calc_times = []
    rup_mon = monitor('filtering ruptures', measuremem=False)
    num_samples = rlzs_assoc.samples[src_group_id]

    # Compute and save stochastic event sets
    for src in sources:
        t0 = time.time()
        s_sites = src.filter_sites_by_distance_to_source(max_dist, sitecol)
        if s_sites is None:
            continue
        rupture_filter = functools.partial(
            filter_sites_by_distance_to_rupture,
            integration_distance=max_dist, sites=s_sites)
        num_occ_by_rup = sample_ruptures(
            src, oq.ses_per_logic_tree_path, num_samples,
            rlzs_assoc.seed)
        # NB: the number of occurrences is very low, << 1, so it is
        # more efficient to filter only the ruptures that occur, i.e.
        # to call sample_ruptures *before* the filtering
        for ebr in build_eb_ruptures(
                src, num_occ_by_rup, rupture_filter, oq.random_seed, rup_mon):
            nsites = len(ebr.indices)
            try:
                rate = ebr.rupture.occurrence_rate
            except AttributeError:  # for nonparametric sources
                rate = numpy.nan
            rc = cmaker.make_rupture_context(ebr.rupture)
            ruptparams = tuple(getattr(rc, param) for param in params)
            rup_data.append((ebr.serial, len(ebr.etags), nsites, rate) +
                            ruptparams)
            eb_ruptures.append(ebr)
        dt = time.time() - t0
        calc_times.append((src.id, dt))
    res = AccumDict({src_group_id: eb_ruptures})
    res.calc_times = calc_times
    res.rup_data = numpy.array(rup_data, rup_data_dt)
    res.trt = trt
    return res


def sample_ruptures(src, num_ses, num_samples, seed):
    """
    Sample the ruptures contained in the given source.

    :param src: a hazardlib source object
    :param num_ses: the number of Stochastic Event Sets to generate
    :param num_samples: how many samples for the given source
    :param seed: master seed from the job.ini file
    :returns: a dictionary of dictionaries rupture -> {ses_id: num_occurrences}
    """
    # the dictionary `num_occ_by_rup` contains a dictionary
    # ses_id -> num_occurrences for each occurring rupture
    num_occ_by_rup = collections.defaultdict(AccumDict)
    # generating ruptures for the given source
    for rup_no, rup in enumerate(src.iter_ruptures()):
        rup.seed = src.serial[rup_no] + seed
        numpy.random.seed(rup.seed)
        for sampleid in range(num_samples):
            for ses_idx in range(1, num_ses + 1):
                num_occurrences = rup.sample_number_of_occurrences()
                if num_occurrences:
                    num_occ_by_rup[rup] += {
                        (sampleid, ses_idx): num_occurrences}
        rup.rup_no = rup_no + 1
    return num_occ_by_rup


def build_eb_ruptures(
        src, num_occ_by_rup, rupture_filter, random_seed, rup_mon):
    """
    Filter the ruptures stored in the dictionary num_occ_by_rup and
    yield pairs (rupture, <list of associated EBRuptures>)
    """
    for rup in sorted(num_occ_by_rup, key=operator.attrgetter('rup_no')):
        with rup_mon:
            r_sites = rupture_filter(rup)
        if r_sites is None:
            # ignore ruptures which are far away
            del num_occ_by_rup[rup]  # save memory
            continue

        # creating EBRuptures
        serial = rup.seed - random_seed + 1
        events = []
        for (sampleid, ses_idx), num_occ in sorted(
                num_occ_by_rup[rup].items()):
            for occ_no in range(1, num_occ + 1):
                # NB: the 0 below is a placeholder; the right eid will be
                # set later, in EventBasedRuptureCalculator.post_execute
                events.append((0, ses_idx, occ_no, sampleid))
        if events:
            yield EBRupture(rup, r_sites.indices,
                            numpy.array(events, event_dt),
                            src.source_id, src.src_group_id, serial)


@base.calculators.add('event_based_rupture')
class EventBasedRuptureCalculator(PSHACalculator):
    """
    Event based PSHA calculator generating the ruptures only
    """
    core_task = compute_ruptures
    is_stochastic = True

    def init(self):
        """
        Set the random seed passed to the SourceManager and the
        minimum_intensity dictionary.
        """
        oq = self.oqparam
        self.random_seed = oq.random_seed
        self.rlzs_assoc = self.datastore['csm_info'].get_rlzs_assoc()
        self.min_iml = calc.fix_minimum_intensity(
            oq.minimum_intensity, oq.imtls)
        self.rup_data = {}

    def count_eff_ruptures(self, ruptures_by_grp_id, src_group):
        """
        Returns the number of ruptures sampled in the given src_group.

        :param ruptures_by_grp_id: a dictionary with key grp_id
        :param src_group: a SourceGroup instance
        """
        nr = sum(
            len(ruptures) for grp_id, ruptures in ruptures_by_grp_id.items()
            if src_group.id == grp_id)
        return nr

    def zerodict(self):
        """
        Initial accumulator, a dictionary (grp_id, gsim) -> curves
        """
        zd = AccumDict()
        zd.calc_times = []
        zd.eff_ruptures = AccumDict()
        return zd

    def agg_dicts(self, acc, ruptures_by_grp_id):
        """
        Aggregate dictionaries of hazard curves by updating the accumulator.

        :param acc: accumulator dictionary
        :param ruptures_by_grp_id: a nested dictionary grp_id -> ProbabilityMap
        """
        with self.monitor('aggregate curves', autoflush=True):
            if hasattr(ruptures_by_grp_id, 'calc_times'):
                acc.calc_times.extend(ruptures_by_grp_id.calc_times)
            if hasattr(ruptures_by_grp_id, 'eff_ruptures'):
                acc.eff_ruptures += ruptures_by_grp_id.eff_ruptures
            acc += ruptures_by_grp_id
            if len(ruptures_by_grp_id):
                trt = ruptures_by_grp_id.trt
                try:
                    dset = self.rup_data[trt]
                except KeyError:
                    dset = self.rup_data[trt] = self.datastore.create_dset(
                        'rup_data/' + trt, ruptures_by_grp_id.rup_data.dtype)
                dset.extend(ruptures_by_grp_id.rup_data)
        self.datastore.flush()
        return acc

    def post_execute(self, result):
        """
        Save the SES collection
        """
        with self.monitor('saving ruptures', autoflush=True):
            # ordering ruptures
            sescollection = []
            for grp_id in result:
                for ebr in result[grp_id]:
                    sescollection.append(ebr)
            sescollection.sort(key=operator.attrgetter('serial'))
            etags = numpy.concatenate([ebr.etags for ebr in sescollection])
            self.datastore['etags'] = etags
            nr = len(sescollection)
            logging.info('Saving SES collection with %d ruptures, %d events',
                         nr, len(etags))
            eid = 0
            for ebr in sescollection:
                eids = []
                for event in ebr.events:
                    event['eid'] = eid
                    eids.append(eid)
                    eid += 1
                self.datastore['sescollection/%s' % ebr.serial] = ebr
            self.datastore.set_nbytes('sescollection')

        for dset in self.rup_data.values():
            if len(dset.dset):
                numsites = dset.dset['numsites']
                multiplicity = dset.dset['multiplicity']
                spr = numpy.average(numsites, weights=multiplicity)
                mul = numpy.average(multiplicity, weights=numsites)
                self.datastore.set_attrs(dset.name, sites_per_rupture=spr,
                                         multiplicity=mul)
        if self.rup_data:
            self.datastore.set_nbytes('rup_data')


# ######################## GMF calculator ############################ #

@parallel.litetask
def compute_gmfs_and_curves(eb_ruptures, sitecol, imts, rlzs_assoc,
                            min_iml, monitor):
    """
    :param eb_ruptures:
        a list of blocks of EBRuptures of the same SESCollection
    :param sitecol:
        a :class:`openquake.hazardlib.site.SiteCollection` instance
    :param imts:
        a list of IMT string
    :param rlzs_assoc:
        a RlzsAssoc instance
    :param monitor:
        a Monitor instance
    :returns:
        a dictionary (rlzi, imt) -> [gmfarray, haz_curves]
   """
    oq = monitor.oqparam
    # NB: by construction each block is a non-empty list with
    # ruptures of the same src_group_id
    trunc_level = oq.truncation_level
    correl_model = readinput.get_correl_model(oq)
    gmfadict = create(
        calc.GmfColl, eb_ruptures, sitecol, imts, rlzs_assoc, trunc_level,
        correl_model, min_iml, monitor).by_rlzi()
    result = {rlzi: [gmfadict[rlzi], None]
              if oq.ground_motion_fields else [None, None]
              for rlzi in gmfadict}
    if oq.hazard_curves_from_gmfs:
        with monitor('bulding hazard curves', measuremem=False):
            duration = oq.investigation_time * oq.ses_per_logic_tree_path
            for rlzi in gmfadict:
                gmvs_by_sid = group_array(gmfadict[rlzi], 'sid')
                result[rlzi][POEMAP] = calc.gmvs_to_poe_map(
                    gmvs_by_sid, oq.imtls, oq.investigation_time, duration)
    return result


@base.calculators.add('event_based')
class EventBasedCalculator(ClassicalCalculator):
    """
    Event based PSHA calculator generating the ground motion fields and
    the hazard curves from the ruptures, depending on the configuration
    parameters.
    """
    pre_calculator = 'event_based_rupture'
    core_task = compute_gmfs_and_curves
    is_stochastic = True

    def pre_execute(self):
        """
        Read the precomputed ruptures (or compute them on the fly) and
        prepare some empty files in the export directory to store the gmfs
        (if any). If there were pre-existing files, they will be erased.
        """
        super(EventBasedCalculator, self).pre_execute()
        rlzs_by_tr_id = self.rlzs_assoc.get_rlzs_by_grp_id()
        num_rlzs = {t: len(rlzs) for t, rlzs in rlzs_by_tr_id.items()}
        self.sesruptures = []
        for serial in self.datastore['sescollection']:
            sr = self.datastore['sescollection/' + serial]
            sr.set_weight(num_rlzs, {})
            self.sesruptures.append(sr)
        self.sesruptures.sort(key=operator.attrgetter('serial'))
        if self.oqparam.ground_motion_fields:
            calc.check_overflow(self)
            for rlz in self.rlzs_assoc.realizations:
                self.datastore.create_dset(
                    'gmf_data/%04d' % rlz.ordinal, calc.gmv_dt)

    def combine_curves_and_save_gmfs(self, acc, res):
        """
        Combine the hazard curves (if any) and save the gmfs (if any)
        sequentially; notice that the gmfs may come from
        different tasks in any order.

        :param acc: an accumulator for the hazard curves
        :param res: a dictionary rlzi, imt -> [gmf_array, curves_by_imt]
        :returns: a new accumulator
        """
        sav_mon = self.monitor('saving gmfs')
        agg_mon = self.monitor('aggregating hcurves')
        for rlzi in res:
            gmfa, curves = res[rlzi]
            if gmfa is not None:
                with sav_mon:
                    hdf5.extend(self.datastore['gmf_data/%04d' % rlzi], gmfa)
            if curves is not None:  # aggregate hcurves
                with agg_mon:
                    self.agg_dicts(acc, {rlzi: curves})
        sav_mon.flush()
        agg_mon.flush()
        self.datastore.flush()
        return acc

    def execute(self):
        """
        Run in parallel `core_task(sources, sitecol, monitor)`, by
        parallelizing on the ruptures according to their weight and
        tectonic region type.
        """
        oq = self.oqparam
        if not oq.hazard_curves_from_gmfs and not oq.ground_motion_fields:
            return
        monitor = self.monitor(self.core_task.__name__)
        monitor.oqparam = oq
        min_iml = calc.fix_minimum_intensity(
            oq.minimum_intensity, oq.imtls)
        acc = parallel.apply_reduce(
            self.core_task.__func__,
            (self.sesruptures, self.sitecol, oq.imtls, self.rlzs_assoc,
             min_iml, monitor),
            concurrent_tasks=self.oqparam.concurrent_tasks,
            agg=self.combine_curves_and_save_gmfs,
            acc=ProbabilityMap(),
            key=operator.attrgetter('grp_id'),
            weight=operator.attrgetter('weight'))
        if oq.ground_motion_fields:
            self.datastore.set_nbytes('gmf_data')
        return acc

    def post_execute(self, result):
        """
        :param result:
            a dictionary (src_group_id, gsim) -> haz_curves or an empty
            dictionary if hazard_curves_from_gmfs is false
        """
        oq = self.oqparam
        if not oq.hazard_curves_from_gmfs and not oq.ground_motion_fields:
            return
        elif oq.hazard_curves_from_gmfs:
            rlzs = self.rlzs_assoc.realizations
            dic = {}
            for rlzi in result:
                dic[rlzs[rlzi]] = array_of_curves(
                    result[rlzi], len(self.sitecol), oq.imtls)
            self.save_curves(dic)
        if oq.compare_with_classical:  # compute classical curves
            export_dir = os.path.join(oq.export_dir, 'cl')
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            oq.export_dir = export_dir
            # one could also set oq.number_of_logic_tree_samples = 0
            self.cl = ClassicalCalculator(oq, self.monitor)
            # TODO: perhaps it is possible to avoid reprocessing the source
            # model, however usually this is quite fast and do not dominate
            # the computation
            self.cl.run()
            for imt in self.mean_curves.dtype.fields:
                rdiff, index = max_rel_diff_index(
                    self.cl.mean_curves[imt], self.mean_curves[imt])
                logging.warn('Relative difference with the classical '
                             'mean curves for IMT=%s: %d%% at site index %d',
                             imt, rdiff * 100, index)
