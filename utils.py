"""."""
from threading import Thread as _Thread, Event as _Event
import logging as _log

from mathphys.functions import save_pickle as _save_pickle, \
    load_pickle as _load_pickle


class DataBaseClass:
    """."""

    def __init__(self, params=None):
        """."""
        self.data = dict()
        self.params = params

    def save_data(self, fname, overwrite=False):
        """."""
        data = dict(data=self.data)
        _save_pickle(data, fname, overwrite=overwrite)

    def load_and_apply(self, fname):
        """."""
        data = self.load_data(fname)
        self.data = data['data']

    @staticmethod
    def load_data(fname):
        """."""
        return _load_pickle(fname)


class MeasBaseClass:
    """."""

    def __init__(self, params=None):
        """."""
        self.params = params
        self.data = dict()
        self.devices = dict()
        self.analysis = dict()
        self.pvs = dict()

    @property
    def connected(self):
        """."""
        conn = all([dev.connected for dev in self.devices.values()])
        conn &= all([pv.connected for pv in self.pvs.values()])
        return conn

    def wait_for_connection(self, timeout=None):
        """."""
        obs = list(self.devices.values()) + list(self.pvs.values())
        for dev in obs:
            if not dev.wait_for_connection(timeout=timeout):
                return False
        return True

    def save_data(self, fname, overwrite=False):
        """."""
        data = dict(params=self.params, data=self.data)
        _save_pickle(data, fname, overwrite=overwrite)

    def load_and_apply(self, fname):
        """."""
        data = self.load_data(fname)
        self.data = data['data']
        self.params = data['params']

    @staticmethod
    def load_data(fname):
        """."""
        return _load_pickle(fname)


class ThreadedMeasBaseClass(MeasBaseClass):
    """."""

    def __init__(self, params=None, target=None, isonline=True):
        """."""
        super().__init__(params=params)
        self.isonline = bool(isonline)
        self._target = target
        self._stopevt = _Event()
        self._finished = _Event()
        self._finished.set()
        self._thread = _Thread(target=self._run, daemon=True)

    def start(self):
        """."""
        if self.ismeasuring:
            _log.error('There is another measurement happening.')
            return
        self._stopevt.clear()
        self._finished.clear()
        self._thread = _Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """."""
        self._stopevt.set()

    @property
    def ismeasuring(self):
        """."""
        return self._finished.is_set()

    def wait_measurement(self, timeout=None):
        """Wait for measurement to finish."""
        return self._finished.wait(timeout=timeout)

    def _run(self):
        self._finished.clear()
        if self._target is not None:
            self._target()
        self._finished.set()
