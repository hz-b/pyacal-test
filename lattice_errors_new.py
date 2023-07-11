#!/usr/bin/env python-sirius

import numpy as _np
import matplotlib.pyplot as _plt
import time as _time
import copy as _copy

import pyaccel as _pyaccel
import pymodels as _pymodels
from apsuite.orbcorr import OrbitCorr, CorrParams
from apsuite.optics_analysis import TuneCorr, OpticsCorr, CouplingCorr
from apsuite.commisslib.measure_bba import BBAParams
from mathphys.functions import save_pickle, load_pickle


class ConfigErrors:

    def __init__(self):
        self._fam_names = []
        self._sigma_x = 0
        self._sigma_y = 0
        self._sigma_roll = 0
        self._sigma_pitch = 0
        self._sigma_yaw = 0
        self._sigmas = dict()
        self._um = 1e-6
        self._mrad = 1e-3
        self._percent = 1e-2

    @property
    def error_types(self):
        return self._error_types

    @property
    def fam_names(self):
        return self._fam_names

    @fam_names.setter
    def fam_names(self, value):
        self._fam_names = value

    @property
    def sigma_x(self):
        return self._sigma_x

    @sigma_x.setter
    def sigma_x(self, value):
        self._sigma_x = value * self._um

    @property
    def sigma_y(self):
        return self._sigma_y

    @sigma_y.setter
    def sigma_y(self, value):
        self._sigma_y = value * self._um

    @property
    def sigma_roll(self):
        return self._sigma_roll

    @sigma_roll.setter
    def sigma_roll(self, value):
        self._sigma_roll = value * self._mrad

    @property
    def sigma_pitch(self):
        return self._sigma_pitch

    @sigma_pitch.setter
    def sigma_pitch(self, value):
        self._sigma_pitch = value * self._mrad

    @property
    def sigma_yaw(self):
        return self._sigma_yaw

    @sigma_yaw.setter
    def sigma_yaw(self, value):
        self._sigma_yaw = value * self._mrad

    @property
    def sigmas(self):
        return self._sigmas

    @sigmas.setter
    def sigmas(self, value):
        self._sigmas = value


class MultipolesErrors(ConfigErrors):

    def __init__(self):
        super().__init__()
        self._sigma_excit = 0
        self._r0 = 12e-3
        self._multipoles_dict = None
        self._normal_multipoles_order = []
        self._skew_multipoles_order = []
        self._sigma_multipoles_n = []
        self._sigma_multipoles_s = []

    @property
    def sigma_excit(self):
        return self._sigma_excit

    @sigma_excit.setter
    def sigma_excit(self, value):
        self._sigma_excit = value * self._percent

    @property
    def r0(self):
        return self._r0

    @r0.setter
    def r0(self, value):
        self._r0 = value

    @property
    def normal_multipoles_order(self):
        return self._normal_multipoles_order

    @normal_multipoles_order.setter
    def normal_multipoles_order(self, value):
        self._normal_multipoles_order = value

    @property
    def skew_multipoles_order(self):
        return self._skew_multipoles_order

    @skew_multipoles_order.setter
    def skew_multipoles_order(self, value):
        self._skew_multipoles_order = value

    @property
    def sigma_multipoles_n(self):
        return self._sigma_multipoles_n

    @sigma_multipoles_n.setter
    def sigma_multipoles_n(self, value):
        self._sigma_multipoles_n = value

    @property
    def sigma_multipoles_s(self):
        return self._sigma_multipoles_s

    @sigma_multipoles_s.setter
    def sigma_multipoles_s(self, value):
        self._sigma_multipoles_s = value

    @property
    def multipoles_dict(self):
        return self._multipoles_dict

    @multipoles_dict.setter
    def multipoles_dict(self, value):
        self._multipoles_dict = value

    def create_multipoles_dict(self):
        n_multipoles_order_dict = dict()
        s_multipoles_order_dict = dict()
        for i, order in enumerate(self.normal_multipoles_order):
            n_multipoles_order_dict[order] = self.sigma_multipoles_n[i]
        for i, order in enumerate(self.skew_multipoles_order):
            s_multipoles_order_dict[order] = self.sigma_multipoles_s[i]
        self.multipoles_dict = dict()
        self.multipoles_dict['normal'] = n_multipoles_order_dict
        self.multipoles_dict['skew'] = n_multipoles_order_dict
        self.multipoles_dict['r0'] = self._r0


class DipolesErrors(MultipolesErrors):

    def __init__(self):
        super().__init__()
        self._sigma_kdip = 0
        self._set_default_dipole_config()

    @property
    def sigma_kdip(self):
        return self._sigma_kdip

    @sigma_kdip.setter
    def sigma_kdip(self, value):
        self._sigma_kdip = value * self._percent

    def _set_default_dipole_config(self):
        self.fam_names = ['B1', 'B2', 'BC']
        self.sigma_x = 40
        self.sigma_y = 40
        self.sigma_roll = 0.30
        self.sigma_pitch = 0
        self.sigma_yaw = 0
        self.sigma_excit = 0.05
        self.sigma_kdip = 0.10
        self.sigma_multipoles_n = _np.ones(4)*1.5e-4
        self.sigma_multipoles_s = _np.ones(4)*0.5e-4
        self.normal_multipoles_order = [3, 4, 5, 6]
        self.skew_multipoles_order = [3, 4, 5, 6]
        self.create_multipoles_dict()

        sigmas = dict()
        sigmas['posx'] = self.sigma_x
        sigmas['posy'] = self.sigma_y
        sigmas['roll'] = self.sigma_roll
        sigmas['pitch'] = self.sigma_pitch
        sigmas['yaw'] = self.sigma_yaw
        sigmas['excit'] = self.sigma_excit
        sigmas['kdip'] = self.sigma_kdip
        sigmas['multipoles'] = self.multipoles_dict
        self.sigmas = sigmas


class QuadsErrors(MultipolesErrors):

    def __init__(self):
        super().__init__()
        self._set_default_quad_config()

    def _set_default_quad_config(self):
        self.fam_names = ['QFA', 'QDA', 'Q1', 'Q2', 'Q3', 'Q4', 'QDB1',
                          'QFB',  'QDB2', 'QDP1', 'QFP', 'QDP2']
        self.sigma_x = 40
        self.sigma_y = 40
        self.sigma_roll = 0.30
        self.sigma_pitch = 0
        self.sigma_yaw = 0
        self.sigma_excit = 0.05
        self.sigma_multipoles_n = _np.ones(4)*1.5e-4
        self.sigma_multipoles_s = _np.ones(4)*0.5e-4
        self.normal_multipoles_order = [3, 4, 5, 6]
        self.skew_multipoles_order = [3, 4, 5, 6]
        self.create_multipoles_dict()

        sigmas = dict()
        sigmas['posx'] = self.sigma_x
        sigmas['posy'] = self.sigma_y
        sigmas['roll'] = self.sigma_roll
        sigmas['pitch'] = self.sigma_pitch
        sigmas['yaw'] = self.sigma_yaw
        sigmas['excit'] = self.sigma_excit
        sigmas['multipoles'] = self.multipoles_dict
        self.sigmas = sigmas


class QuadsSkewErrors(MultipolesErrors):

    def __init__(self):
        super().__init__()
        self._set_default_quad_config()

    def _set_default_quad_config(self):
        self.fam_names = ['QS']
        self.sigma_x = 0
        self.sigma_y = 0
        self.sigma_roll = 0
        self.sigma_pitch = 0
        self.sigma_yaw = 0
        self.sigma_excit = 0.05
        self.sigma_multipoles_n = _np.ones(4)*1.5e-4
        self.sigma_multipoles_s = _np.ones(4)*0.5e-4
        self.normal_multipoles_order = [3, 4, 5, 6]
        self.skew_multipoles_order = [3, 4, 5, 6]
        self.create_multipoles_dict()

        sigmas = dict()
        sigmas['posx'] = self.sigma_x
        sigmas['posy'] = self.sigma_y
        sigmas['roll'] = self.sigma_roll
        sigmas['pitch'] = self.sigma_pitch
        sigmas['yaw'] = self.sigma_yaw
        sigmas['excit'] = self.sigma_excit
        sigmas['multipoles'] = self.multipoles_dict
        self.sigmas = sigmas


class SextsErrors(MultipolesErrors):

    def __init__(self):
        super().__init__()
        self._set_default_sext_config()

    def _set_default_sext_config(self):
        self.fam_names = ['SFA0', 'SDA0', 'SDA1', 'SFA1', 'SDA2', 'SDA3',
                          'SFA2', 'SFB2', 'SDB3', 'SDB2', 'SFB1', 'SDB1',
                          'SDB0', 'SFB0', 'SFP2', 'SDP3', 'SDP2', 'SFP1',
                          'SDP1', 'SDP0', 'SFP0']
        self.sigma_x = 40
        self.sigma_y = 40
        self.sigma_roll = 0.17
        self.sigma_pitch = 0
        self.sigma_yaw = 0
        self.sigma_excit = 0.05
        self.sigma_multipoles_n = _np.ones(4)*1.5e-4
        self.sigma_multipoles_s = _np.ones(4)*0.5e-4
        self.normal_multipoles_order = [4, 5, 6, 7]
        self.skew_multipoles_order = [4, 5, 6, 7]
        self.create_multipoles_dict()

        sigmas = dict()
        sigmas['posx'] = self.sigma_x
        sigmas['posy'] = self.sigma_y
        sigmas['roll'] = self.sigma_roll
        sigmas['pitch'] = self.sigma_pitch
        sigmas['yaw'] = self.sigma_yaw
        sigmas['excit'] = self.sigma_excit
        sigmas['multipoles'] = self.multipoles_dict
        self.sigmas = sigmas


class GirderErrors(ConfigErrors):

    def __init__(self):
        super().__init__()
        self._set_default_girder_config()

    def _set_default_girder_config(self):
        self.fam_names = ['girder']
        self.sigma_x = 80
        self.sigma_y = 80
        self.sigma_roll = 0.30
        self.sigma_pitch = 0
        self.sigma_yaw = 0

        sigmas = dict()
        sigmas['posx'] = self.sigma_x
        sigmas['posy'] = self.sigma_y
        sigmas['roll'] = self.sigma_roll
        sigmas['pitch'] = self.sigma_pitch
        sigmas['yaw'] = self.sigma_yaw
        self.sigmas = sigmas


class BpmsErrors(ConfigErrors):

    def __init__(self):
        super().__init__()
        self._set_default_bpm_config()

    def _set_default_bpm_config(self):
        self.fam_names = ['BPM']
        self.sigma_x = 20
        self.sigma_y = 20
        self.sigma_roll = 0.30
        self.sigma_pitch = 0
        self.sigma_yaw = 0

        sigmas = dict()
        sigmas['posx'] = self.sigma_x
        sigmas['posy'] = self.sigma_y
        sigmas['roll'] = self.sigma_roll
        sigmas['pitch'] = self.sigma_pitch
        sigmas['yaw'] = self.sigma_yaw
        self.sigmas = sigmas


class ManageErrors():

    def __init__(self):
        self._machines_data = None
        self._ids = None
        self._nr_mach = 20
        self._seed = 140699
        self._cutoff = 1
        self._error_configs = []
        self._famdata = None
        self._fam_errors = None
        self._bba_idcs = None
        self._nominal_model = None
        self._models = []
        self.functions = {'posx': _pyaccel.lattice.add_error_misalignment_x,
                          'posy': _pyaccel.lattice.add_error_misalignment_y,
                          'roll': _pyaccel.lattice.add_error_rotation_roll,
                          'pitch': _pyaccel.lattice.add_error_rotation_pitch,
                          'yaw': _pyaccel.lattice.add_error_rotation_yaw,
                          'excit': _pyaccel.lattice.add_error_excitation_main,
                          'kdip': _pyaccel.lattice.add_error_excitation_kdip}
        self._orbcorr_params = CorrParams()
        self._orbcorr = None
        self._save_jacobians = False
        self._load_jacobians = True
        self._do_bba = True
        self._ramp_with_ids = False
        self._do_opt_corr = True
        self._corr_multipoles = True

        # debug tools
        self.apply_girder = True
        self.rescale_girder = 1

    @property
    def machines_data(self):
        return self._machines_data

    @machines_data.setter
    def machines_data(self, value):
        self._machines_data = value

    @property
    def ids(self):
        return self._ids

    @ids.setter
    def ids(self, value):
        self._ids = value

    @property
    def nr_mach(self):
        return self._nr_mach

    @nr_mach.setter
    def nr_mach(self, value):
        if isinstance(value, int):
            self._nr_mach = value
        else:
            raise ValueError('Number of machines must be an integer')

    @property
    def seed(self):
        return self._seed

    @seed.setter
    def seed(self, value):
        self._seed = value
        _np.random.seed(seed=self._seed)

    @property
    def error_configs(self):
        return self._error_configs

    @error_configs.setter
    def error_configs(self, value):
        self._error_configs = value

    @property
    def famdata(self):
        return self._famdata

    @famdata.setter
    def famdata(self, value):
        self._famdata = value

    @property
    def cutoff(self):
        return self._cutoff

    @cutoff.setter
    def cutoff(self, value):
        self._cutoff = value

    @property
    def fam_errors(self):
        return self._fam_errors

    @fam_errors.setter
    def fam_errors(self, value):
        self._fam_errors = value

    @property
    def bba_idcs(self):
        return self._bba_idcs

    @bba_idcs.setter
    def bba_idcs(self, value):
        self._bba_idcs = value

    @property
    def models(self):
        return self._models

    @models.setter
    def models(self, value):
        self._models = value

    @property
    def nominal_model(self):
        return self._nominal_model

    @nominal_model.setter
    def nominal_model(self, value):
        self._nominal_model = value

    @property
    def save_jacobians(self):
        return self._save_jacobians

    @save_jacobians.setter
    def save_jacobians(self, value):
        if type(value) != bool:
            raise ValueError('Save jacobian must be boolean type')
        else:
            self._save_jacobians = value

    @property
    def load_jacobians(self):
        return self._load_jacobians

    @load_jacobians.setter
    def load_jacobians(self, value):
        if type(value) != bool:
            raise ValueError('Load jacobian must be boolean type')
        else:
            self._load_jacobians = value

    @property
    def orbcorr(self):
        return self._orbcorr

    @orbcorr.setter
    def orbcorr(self, value):
        self._orbcorr = value

    @property
    def orbcorr_params(self):
        return self._orbcorr_params

    @orbcorr_params.setter
    def orbcorr_params(self, value):
        self._orbcorr_params = value

    @property
    def ramp_with_ids(self):
        return self._ramp_with_ids

    @ramp_with_ids.setter
    def ramp_with_ids(self, value):
        if type(value) != bool:
            raise ValueError('ramp_with_ids must be boolean type')
        else:
            self._ramp_with_ids = value

    @property
    def do_opt_corr(self):
        return self._do_opt_corr

    @do_opt_corr.setter
    def do_opt_corr(self, value):
        if type(value) != bool:
            raise ValueError('do_opt_corr must be boolean type')
        else:
            self._do_opt_corr = value

    @property
    def do_bba(self):
        return self._do_bba

    @do_bba.setter
    def do_bba(self, value):
        if type(value) != bool:
            raise ValueError('do_bba must be boolean type')
        else:
            self._do_bba = value

    @property
    def corr_multipoles(self):
        return self._corr_multipoles

    @corr_multipoles.setter
    def corr_multipoles(self, value):
        if type(value) != bool:
            raise ValueError('corr_multipoles must be boolean type')
        else:
            self._corr_multipoles = value

    def reset_seed(self):
        self.seed = int(_time.time_ns() % 1e6)
        print('New seed: ', self.seed)

    def _generate_normal_dist(self, sigma, dim, mean=0):
        dist = _np.random.normal(loc=mean, scale=sigma, size=dim)
        while _np.any(_np.abs(dist) > self.cutoff*sigma):
            idx = _np.argwhere(_np.abs(dist) > self.cutoff*sigma)
            for i in idx:
                mach = i[0]
                element = i[1]
                dist[mach][element] = _np.random.normal(
                    loc=mean, scale=sigma, size=1)
        return dist

    def generate_errors(self, save_errors=False):
        fam_errors = dict()
        for config in self.error_configs:
            for fam_name in config.fam_names:
                idcs = _np.array(self.famdata[fam_name]['index'],
                                 dtype="object")
                error_type_dict = dict()
                for error_type, sigma in config.sigmas.items():
                    if error_type == 'multipoles':
                        error = dict()
                        multipole_dict_n = dict()
                        multipole_dict_s = dict()
                        for order, mp_value in sigma['normal'].items():
                            error_ = self._generate_normal_dist(
                                        sigma=mp_value, dim=(2*self.nr_mach,
                                                             len(idcs)))
                            multipole_dict_n[order] = error_
                        for order, mp_value in sigma['skew'].items():
                            error_ = self._generate_normal_dist(
                                        sigma=mp_value, dim=(2*self.nr_mach,
                                                             len(idcs)))
                            multipole_dict_s[order] = error_
                        error['normal'] = multipole_dict_n
                        error['skew'] = multipole_dict_s
                        error['r0'] = sigma['r0']
                    else:
                        error = self._generate_normal_dist(
                            sigma=sigma, dim=(2*self.nr_mach, len(idcs)))
                    error_type_dict[error_type] = error
                error_type_dict['index'] = idcs
                fam_errors[fam_name] = error_type_dict
        self.fam_errors = fam_errors
        if save_errors:
            self._save_error_file()
        return fam_errors

    def _save_error_file(self, filename=None):
        if filename is None:
            filename = str(self.nr_mach) + '_errors_seed_' + str(
                self.seed)
        save_pickle(self.fam_errors, filename, overwrite=True)

    def load_error_file(self, filename):
        self.fam_errors = load_pickle(filename)
        fams = list(self.fam_errors.keys())
        nr_mach = len(self.fam_errors[fams[0]]['posx'])
        self.nr_mach = int(nr_mach/2)
        return self.fam_errors

    def _create_models(self):
        models_ = list()
        if self.ramp_with_ids:
            ids = self.ids
        else:
            ids = None
        for _ in range(2*self.nr_mach):
            model = _pymodels.si.create_accelerator(ids=ids)
            model.cavity_on = False
            model.radiation_on = 0
            model.vchamber_on = False
            models_.append(model)
        self.models = models_

    def _get_bba_idcs(self):
        quaddevnames = list(BBAParams.QUADNAMES)
        quads = [famname for famname in self.famdata.keys()
                 if famname[0] == 'Q' and famname[1] != 'N']
        quads_idcs = list()
        for quadfam in quads:
            for idx, devname in zip(self.famdata[quadfam]['index'],
                                    self.famdata[quadfam]['devnames']):
                if devname in quaddevnames:
                    quads_idcs.append(idx)
        bba_idcs = _np.array(quads_idcs).ravel()
        self.bba_idcs = _np.sort(bba_idcs)

    def _apply_errors(self, nr_steps, mach):

        print('Applying errors...', end='')
        for fam, family in self.fam_errors.items():
            if fam != 'girder':
                apply_flag = True
                rescale = 1
            elif fam == 'girder' and self.apply_girder:
                apply_flag = True
                rescale = self.rescale_girder
            else:
                apply_flag = False

            if apply_flag:
                inds = family['index']
                error_types = [err for err in family.keys() if err != 'index']
                for error_type in error_types:
                    if error_type != 'multipoles':
                        errors = family[error_type]
                        self.functions[error_type](
                            self.models[mach], inds,
                            rescale*errors[mach]/nr_steps)

        print('Done!')

    def _restore_error_step(self, nr_steps, mach):
        print('Restoring machine...', end='')
        for fam, family in self.fam_errors.items():
            if fam != 'girder':
                apply_flag = True
                rescale = -1
            elif fam == 'girder' and self.apply_girder:
                apply_flag = True
                rescale = -1*self.rescale_girder
            else:
                apply_flag = False

            if apply_flag:
                inds = family['index']
                error_types = [err for err in family.keys() if err != 'index']
                for error_type in error_types:
                    if error_type != 'multipoles':
                        errors = family[error_type]
                        self.functions[error_type](
                            self.models[mach], inds,
                            rescale*errors[mach]/nr_steps)

        print('Done!')

    def _apply_multipoles_errors(self, nr_steps, mach):
        error_type = 'multipoles'
        for fam, family in self.fam_errors.items():
            inds = family['index']
            if error_type in family.keys():
                main_monoms = {'B': 1, 'Q': 2, 'S': 3, 'QS': -2}
                mag_key = fam[0] if fam != 'QS' else fam
                main_monom = _np.ones(len(inds))*main_monoms[mag_key]
                r0 = family[error_type]['r0']
                polb_order = list(family[error_type]['normal'].keys())
                pola_order = list(family[error_type]['skew'].keys())
                Bn_norm = _np.zeros((len(inds), max(polb_order)+1))
                An_norm = _np.zeros((len(inds), max(pola_order)+1))
                for n in polb_order:
                    Bn_norm[:, n] =\
                        family[error_type]['normal'][n][mach]/nr_steps
                for n in pola_order:
                    An_norm[:, n] =\
                        family[error_type]['skew'][n][mach]/nr_steps
                _pyaccel.lattice.add_error_multipoles(
                    self.models[mach], inds, r0,
                    main_monom, Bn_norm, An_norm)

    def _get_girder_errors(self, nr_steps, step, idcs, mach):
        girder_errorx = list()
        girder_errory = list()
        for i, girder in enumerate(self.fam_errors['girder']['index']):
            for idx in girder:
                if _np.any(idcs == idx):
                    girder_errorx.append(
                        self.fam_errors['girder']['posx'][mach][i])
                    girder_errory.append(
                        self.fam_errors['girder']['posy'][mach][i])
        girder_errors_idcs = _np.array(girder_errorx + girder_errory).ravel()
        return step*girder_errors_idcs/nr_steps

    def _simulate_bba(self, nr_steps, step, mach):
        bpms = _np.array(self.famdata['BPM']['index']).ravel()
        orb0 = _np.zeros(2*len(bpms))
        orb0[:len(bpms)] += _pyaccel.lattice.get_error_misalignment_x(
                self.models[mach], self.bba_idcs).ravel()
        orb0[:len(bpms)] += _pyaccel.lattice.get_error_misalignment_x(
                self.models[mach], bpms).ravel()
        orb0[len(bpms):] += _pyaccel.lattice.get_error_misalignment_y(
                self.models[mach], self.bba_idcs).ravel()
        orb0[len(bpms):] += _pyaccel.lattice.get_error_misalignment_y(
                self.models[mach], bpms).ravel()

        if 'girder' in self.fam_errors.keys() and self.apply_girder:
            bpm_girder_errors = self.rescale_girder*self._get_girder_errors(
                nr_steps, step, bpms, mach)
            orb0 -= bpm_girder_errors

        return orb0

    def _config_orb_corr(self, jac=None):
        self.orbcorr = OrbitCorr(
                self.nominal_model, 'SI', '4d',
                params=self.orbcorr_params)
        if jac is not None:
            self.orbmat = jac
        else:
            self.orbmat = self.orbcorr.get_jacobian_matrix()
        return self.orbmat

    def _correct_orbit_once(self, orb0, mach):
        print('Correcting orbit...', end='')
        self.orbcorr.respm.model = self.models[mach]
        self.orbcorr_status = self.orbcorr.correct_orbit(
                jacobian_matrix=self.orbmat, goal_orbit=orb0)
        if self.orbcorr_status == 0:
            print('Could not achieve tolerance!\n')
        elif self.orbcorr_status == 2:
            print('Correction could not converge!\n')
        else:
            print('Done!\n')

        return self.orbcorr.get_orbit(), self.orbcorr.get_kicks()

    def _correct_orbit_iter(self, orb0, mach, nr_steps=1):
        orb_temp, kicks_temp = self._correct_orbit_once(orb0, mach)
        init_minsingval = _copy.copy(self.orbcorr_params.minsingval)
        i = 0
        while self.orbcorr_status == 2 and i < 50:
            self.orbcorr.set_kicks(self.kicks_)
            self._restore_error_step(nr_steps, mach)
            self.orbcorr_params.minsingval += 0.05
            if self.orbcorr_params.minsingval > 0.5:
                print('Correcting optics...')
                res = self._correct_optics(mach)
                res = True if res == 1 else False
                print('Optics correction tolerance achieved: ', res)
                print()
                self.orbcorr_params.minsingval = init_minsingval
            print('min singval: ', self.orbcorr_params.minsingval)
            orb_temp, kicks_temp = self._correct_orbit_once(
                orb0, mach)
            i += 1
        self.orbf_, self.kicks_ = orb_temp, kicks_temp
        self.orbcorr_params.minsingval = init_minsingval
        return self.orbf_, self.kicks_

    def _config_tune_corr(self, jac=None):
        self.tunecorr = TuneCorr(
                            self.nominal_model,
                            'SI', method='Proportional',
                            grouping='TwoKnobs')
        if jac is not None:
            self.tunemat = jac
        else:
            self.tunemat = self.tunecorr.calc_jacobian_matrix()
        self.goal_tunes = self.tunecorr.get_tunes()
        print('Nominal tunes: {:.4f} {:.4f}'.format(
            self.goal_tunes[0], self.goal_tunes[1]))
        return self.tunemat

    def _correct_tunes(self, mach):
        self.tunecorr.correct_parameters(
            model=self.models[mach],
            goal_parameters=self.goal_tunes,
            jacobian_matrix=self.tunemat)

    def _calc_coupling(self, mach):
        ed_tang, *_ = _pyaccel.optics.calc_edwards_teng(self.models[mach])
        min_tunesep, ratio =\
            _pyaccel.optics.estimate_coupling_parameters(ed_tang)

        return min_tunesep

    def _config_coupling_corr(self, jac=None):
        idcs = list()
        for idx, sub in zip(
                self.famdata['QS']['index'],
                self.famdata['QS']['subsection']):
            if 'C2' not in sub:
                idcs.append(idx)
        self.coup_corr = CouplingCorr(self.nominal_model, 'SI',
                                      skew_list=idcs)
        if jac is not None:
            self.coupmat = jac
        else:
            self.coupmat = self.coup_corr.calc_jacobian_matrix(
                model=self.nominal_model, weight_dispy=5)
        return self.coupmat

    def _correct_coupling(self, mach):
        self.coup_corr.model = self.models[mach]
        self.coup_corr.coupling_correction(
                    jacobian_matrix=self.coupmat,
                    tol=1e-8, weight_dispy=5)

    def _config_optics_corr(self, jac=None):
        self.opt_corr = OpticsCorr(self.nominal_model, 'SI')
        if jac is not None:
            self.optmat = jac
        else:
            self.optmat = self.opt_corr.calc_jacobian_matrix()
        return self.optmat

    def _correct_optics(self, mach):
        self.opt_corr.model = self.models[mach]
        return self.opt_corr.optics_corr_loco(goal_model=self.nominal_model,
                                              nr_max=10, nsv=150,
                                              jacobian_matrix=self.optmat)

    def _do_all_opt_corrections(self, mach):

        # Symmetrize optics
        print('Correcting optics...')
        for i in range(1):
            res = self._correct_optics(mach)
            # self._correct_orbit_once(orb0, mach)
        res = True if res == 1 else False
        print('Optics correction tolerance achieved: ', res)
        print()

        # Correct tunes
        print('Correcting tunes:')
        tunes = self.tunecorr.get_tunes(model=self.models[mach])
        print('Old tunes: {:.4f} {:.4f}'.format(tunes[0], tunes[1]))
        self._correct_tunes(mach)
        tunes = self.tunecorr.get_tunes(
                    model=self.models[mach])
        print('New tunes: {:.4f} {:.4f}'.format(
                        tunes[0], tunes[1]))
        print()

        # Correct coupling
        print('Correcting coupling:')
        mintune = self._calc_coupling(mach)
        print('Minimum tune separation before corr: {:.3f} %'.format(
                 100*mintune))
        self._correct_coupling(mach)
        mintune = self._calc_coupling(mach)
        print('Minimum tune separation after corr: {:.3f} %'.format(
                            100*mintune))
        print()

        ed_tang, *_ = _pyaccel.optics.calc_edwards_teng(self.models[mach])
        twiss, *_ = _pyaccel.optics.calc_twiss(self.models[mach])
        twiss0, *_ = _pyaccel.optics.calc_twiss(self.nominal_model)

        return twiss, ed_tang, twiss0

    def configure_corrections(self):
        orbmat, optmat, tunemat, coupmat = None, None, None, None
        if self.load_jacobians:
            respmats = load_pickle('respmats')
            orbmat = respmats['orbmat']
            optmat = respmats['optmat']
            tunemat = respmats['tunemat']
            coupmat = respmats['coupmat']

        # Config orbit correction
        print('Configuring orbit correction...')
        orbmat = self._config_orb_corr(orbmat)

        # Config optics correction
        print('Configuring optics correction...')
        optmat = self._config_optics_corr(optmat)

        # Config tune correction
        print('Configuring tune correction...')
        tunemat = self._config_tune_corr(tunemat)

        # Config coupling correction
        print('Configuring coupling correction...')
        coupmat = self._config_coupling_corr(coupmat)

        if self.save_jacobians:
            respmats = dict()
            respmats['orbmat'] = orbmat
            respmats['optmat'] = optmat
            respmats['tunemat'] = tunemat
            respmats['coupmat'] = coupmat
            save_pickle(respmats, 'respmats', overwrite=True)

    def save_machines(self, sulfix=None):
        filename = str(self.nr_mach) + '_machines_seed_' + str(self.seed)
        if self.ramp_with_ids:
            filename += '_'
            filename += self.ids[0].fam_name
        if sulfix is not None:
            filename += sulfix
        if not self.do_bba:
            filename += '_no_bba'
        if not self.apply_girder:
            filename += '_no_girder'

        save_pickle(self.machines_data, filename, overwrite=True)

    def load_machines(self):
        filename = str(self.nr_mach) + '_machines_seed_' + str(self.seed)
        data = load_pickle(filename)
        print('loading ' + filename)
        return data

    def generate_machines(self, nr_steps=10):
        # Get quadrupoles near BPMs indexes
        self._get_bba_idcs()

        # Create SI models
        self._create_models()

        data = dict()
        for mach in range(2*self.nr_mach):
            print('Machine ', mach)

            step_data = dict()
            for step in range(nr_steps):
                print('Step ', step+1)

                self._apply_errors(nr_steps, mach)

                # Save sextupoles values and set then to zero
                if step == 0:
                    index = self.famdata['SN']['index']
                    values = _pyaccel.lattice.get_attribute(
                        self.models[mach], 'SL', index)

                    zeros = _np.zeros(len(index))
                    _pyaccel.lattice.set_attribute(
                        self.models[mach], 'SL', index, zeros)

                # Orbit setted by BBA or setted to zero
                if self.do_bba:
                    orb0_ = self._simulate_bba(nr_steps, step+1, mach)
                else:
                    orb0_ = _np.zeros(2*len(self.bba_idcs))

                # Correct orbit
                orbf_, kicks_ = self._correct_orbit_iter(orb0_, mach, nr_steps)

                step_dict = dict()
                step_dict['orbcorr_status'] = self.orbcorr_status
                step_dict['ref_orb'] = orb0_
                step_dict['orbit'] = orbf_
                step_dict['corr_kicks'] = kicks_
                step_data['step_' + str(step + 1)] = step_dict

                _pyaccel.lattice.set_attribute(
                    self.models[mach], 'SL', index, (step + 1)*values/nr_steps)

            # Perform one last orbit correction after turning ON sextupoles
            orbf_, kicks_ = self._correct_orbit_iter(orb0_, mach, nr_steps)

            # Save last orbit corr data
            step_dict = dict()
            step_dict['orbcorr_status'] = self.orbcorr_status
            step_dict['ref_orb'] = orb0_
            step_dict['orbit'] = orbf_
            step_dict['corr_kicks'] = kicks_
            step_data['step_' + str(step + 2)] = step_dict

            # Do optics corrections:
            step_dict = step_data['step_' + str(step + 2)]
            if self.do_opt_corr:

                for i in range(1):
                    twiss, edtang, twiss0 = self._do_all_opt_corrections(
                        mach)

                orbf_, kicks_ = self._correct_orbit_once(orb0_, mach)

                dbetax = (twiss.betax - twiss0.betax)/twiss0.betax
                dbetay = (twiss.betay - twiss0.betay)/twiss0.betay
                step_dict['orbcorr_status'] = self.orbcorr_status
                step_dict['ref_orb'] = orb0_
                step_dict['orbit'] = orbf_
                step_dict['corr_kicks'] = kicks_
                step_dict['twiss'] = twiss
                step_dict['edtang'] = edtang
                step_dict['betabeatingx'] = dbetax
                step_dict['betabeatingy'] = dbetay
                step_data['step_final'] = step_dict

            # Apply multipoles errors
            self._apply_multipoles_errors(1, mach)
            if self.corr_multipoles:

                twiss, edtang, twiss0 = self._do_all_opt_corrections(
                        mach)
                dbetax = (twiss.betax - twiss0.betax)/twiss0.betax
                dbetay = (twiss.betay - twiss0.betay)/twiss0.betay
                step_dict['orbcorr_status'] = self.orbcorr_status
                step_dict['ref_orb'] = orb0_
                step_dict['orbit'] = orbf_
                step_dict['corr_kicks'] = kicks_
                step_dict['twiss'] = twiss
                step_dict['edtang'] = edtang
                step_dict['betabeatingx'] = dbetax
                step_dict['betabeatingy'] = dbetay
                step_data['step_final'] = step_dict

            model_dict = dict()
            model_dict['model'] = self.models[mach]
            model_dict['data'] = step_data
            data['orbcorr_params'] = self.orbcorr_params
            data[mach] = model_dict
            self.machines_data = data
            self.save_machines()
            if mach + 1 == self.nr_mach:
                break
        return data

    def insert_kickmap(self, model):
        kickmaps = _pymodels.si.lattice.create_id_kickmaps_dict(
            self.ids, energy=3e9)
        twiss, *_ = _pyaccel.optics.calc_twiss(model, indices='closed')
        print('Model without ID:')
        print('length : {:.4f} m'.format(model.length))
        print('tunex  : {:.6f}'.format(twiss.mux[-1]/2/_np.pi))
        print('tuney  : {:.6f}'.format(twiss.muy[-1]/2/_np.pi))
        print()

        for id_ in self.ids:
            idcs = _np.array(
                self.famdata[id_.fam_name]['index']).ravel()
            for i, idc in enumerate(idcs):
                model[idc] = kickmaps[id_.subsec][i]

        twiss, *_ = _pyaccel.optics.calc_twiss(model, indices='closed')
        print('Model with ID:')
        print('length : {:.4f} m'.format(model.length))
        print('tunex  : {:.6f}'.format(twiss.mux[-1]/2/_np.pi))
        print('tuney  : {:.6f}'.format(twiss.muy[-1]/2/_np.pi))
        print()
        return model

    def corr_ids(self):
        data_mach = self.load_machines()
        self.orbcorr_params = data_mach['orbcorr_params']
        # insert ID in each machine
        models = list()
        for mach in range(self.nr_mach):
            model_ = data_mach[mach]['model']
            model = self.insert_kickmap(model_)
            models.append(model)
        self.models = models

        data = dict()
        for mach in range(self.nr_mach):
            step_data = dict()

            # get ref_orb
            ref_orb = data_mach[mach]['data']['step_final']['ref_orb']

            # correct orbit
            orbf_, kicks_ = self._correct_orbit_once(ref_orb, mach=mach)

            # do all optics corretions
            for i in range(1):
                twiss, edtang, twiss0 = self._do_all_opt_corrections(
                    mach)

            dbetax = (twiss.betax - twiss0.betax)/twiss0.betax
            dbetay = (twiss.betay - twiss0.betay)/twiss0.betay
            step_dict = dict()
            step_dict['twiss'] = twiss
            step_dict['edtang'] = edtang
            step_dict['betabeatingx'] = dbetax
            step_dict['betabeatingy'] = dbetay
            step_dict['ref_orb'] = ref_orb
            step_dict['orbit'] = orbf_
            step_dict['corr_kicks'] = kicks_
            step_data['step_final'] = step_dict

            model_dict = dict()
            model_dict['model'] = self.models[mach]
            model_dict['data'] = step_data
            data[mach] = model_dict
        self.machines_data = data
        sulfix = '_' + self.ids[0].fam_name + '_symm'
        self.save_machines(sulfix=sulfix)
