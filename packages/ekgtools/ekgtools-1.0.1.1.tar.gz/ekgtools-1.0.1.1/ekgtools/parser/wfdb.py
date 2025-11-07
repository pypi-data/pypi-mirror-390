import os
from typing import Any, Dict, Iterable

import numpy as np
import wfdb

from ekgtools.parser.base import BaseParser


_UNIT_SCALE_TO_MV: Dict[str, float] = {
    'v': 1000.0,
    'mv': 1.0,
    'uv': 0.001,
    'µv': 0.001,
    'μv': 0.001,
    'nv': 1e-6,
}


class WFDBParser(BaseParser):
    """Parser for WFDB-formatted ECG records."""

    def __init__(self, config: dict, waveform_type: str = 'full', scale_method: str | None = 'standard'):
        super().__init__(config=config, waveform_type=waveform_type, scale_method=scale_method)
        self._raw_signal: np.ndarray | None = None
        self._fields: Dict[str, Any] = {}
        self.record_path: str | None = None
        self.text_data: Dict[str, Any] = {}
        self.data: Dict[str, Any] = {}

    @staticmethod
    def _strip_extension(path: str) -> str:
        base, ext = os.path.splitext(path)
        return base if ext.lower() in {'.hea', '.dat'} else path

    def load_record(self, path: str) -> None:
        """Load WFDB record from disk without performing any processing."""
        record_base = self._strip_extension(path)
        signal, fields = wfdb.rdsamp(record_base)
        self._raw_signal = signal
        self._fields = fields
        self.record_path = path

    def parse_waveforms(self) -> None:
        if self._raw_signal is None:
            raise ValueError("WFDB data not loaded. Call load_record() or parse(path) first.")

        self.lead = {}
        self.scaled_lead = {}

        sig_names: Iterable[str] = self._fields.get('sig_name') or []
        units: Iterable[str] = self._fields.get('units') or []

        # Fallback names/units if header information is incomplete
        if not sig_names:
            sig_names = [f'Lead_{idx}' for idx in range(self._raw_signal.shape[1])]
        if not units:
            units = ['mV'] * len(sig_names)

        signals = self._raw_signal.T.astype(np.float32)

        for idx, name in enumerate(sig_names):
            unit = units[idx] if idx < len(units) else 'mV'
            scale = _UNIT_SCALE_TO_MV.get(unit.lower(), 1.0)
            self.lead[name] = signals[idx] * scale

        if 'I' in self.lead and 'II' in self.lead:
            self.get_standard_derived_leads()

        # Ensure all standard leads exist to avoid downstream key errors
        if not self.lead:
            self.sig_arr_length = 0
            return

        first_lead = next(iter(self.lead.values()))
        self.sig_arr_length = first_lead.shape[0]
        for lead_name in self.standard_12_leads:
            if lead_name not in self.lead:
                self.lead[lead_name] = np.zeros(self.sig_arr_length, dtype=np.float32)

    def parse_metadata(self) -> None:
        if not self._fields:
            self.text_data = {}
            self.data = {}
            return

        metadata: Dict[str, Any] = {
            'record_name': self._fields.get('record_name'),
            'sampling_rate': self._fields.get('fs'),
            'signal_length': self._fields.get('sig_len'),
            'sig_names': list(self._fields.get('sig_name', [])),
            'comments': list(self._fields.get('comments', [])),
        }

        # Promote colon-delimited comment pairs into structured fields
        for comment in metadata['comments']:
            if ':' in comment:
                key, value = comment.split(':', 1)
                metadata[key.strip().lower()] = value.strip()

        self.text_data = metadata
        self.data = metadata

    def parse(self, path: str | None = None) -> None:
        if path is not None:
            self.load_record(path)

        if self._raw_signal is None:
            raise ValueError("No WFDB record loaded for parsing.")

        self.parse_waveforms()
        sampling_rate = int(self._fields.get('fs', 500))
        self.filter(sampling_rate=sampling_rate)

        if self.scale_method is not None:
            scaler = self.get_scaling_method(self.scale_method)
            if scaler is not None:
                scaler()

        self.get_float_array()
        self.parse_metadata()
