from __future__ import annotations

from base64 import b64decode
from collections.abc import Mapping, Sequence
from typing import Any, Dict, Iterable, Tuple

import numpy as np

from ekgtools.parser.base import BaseParser
from ekgtools.utils.eli import xli_decode


class ELIXMLParser(BaseParser):

    def __init__(self, config: dict, waveform_type: str, scale_method: str | None):
        if waveform_type != 'full':
            raise ValueError("ELI parser currently supports only full waveforms")
        super().__init__(config=config, waveform_type=waveform_type, scale_method=scale_method)
        self.text_data: Dict[str, Any] = {}
        self.data: Dict[str, Any] = {}

    @staticmethod
    def _to_python_scalar(x: Any) -> Any:
        """Convert numpy scalars etc. to plain Python types for safer serialization."""
        if isinstance(x, np.generic):
            return x.item()
        return x

    def _flatten_dictionary(
        self,
        obj: Any,
        parent_key: str = "",
        separator: str = "/",
        index_style: str = "slash",
        exclude: Iterable[str] = (),
    ) -> Dict[str, Any]:
        """Flatten nested dict/list structure into a simple key/value mapping."""
        items: list[Tuple[str, Any]] = []
        exclude_set = set(exclude)

        def make_key(base: str, child: str) -> str:
            return f"{base}{separator}{child}" if base else child

        def make_index_key(base: str, idx: int) -> str:
            if not base:
                return str(idx) if index_style == "slash" else f"[{idx}]"
            if index_style == "slash":
                return f"{base}{separator}{idx}"
            return f"{base}[{idx}]"

        def _flatten(current: Any, path: str) -> None:
            if path and path in exclude_set:
                return

            if isinstance(current, Mapping):
                for key, value in current.items():
                    new_key = make_key(path, str(key))
                    _flatten(value, new_key)
                return

            if isinstance(current, Sequence) and not isinstance(current, (str, bytes, bytearray)):
                for index, value in enumerate(current):
                    new_key = make_index_key(path, index)
                    _flatten(value, new_key)
                return

            try:
                items.append((path if path else "", self._to_python_scalar(current)))
            except Exception:
                items.append((path if path else "", str(current)))

        _flatten(obj, parent_key)
        return {k if k != "" else parent_key: v for k, v in items if k or parent_key}

    def parse_waveforms(self) -> None:
        xml_dict = getattr(self, 'xml_dict', None)
        if not xml_dict:
            raise ValueError("xml_dict is not loaded. Set xml_dict before calling parse().")

        try:
            waveform_block = xml_dict['EliEcg']['Ecg']['Waveform']
        except KeyError as exc:
            raise KeyError("Waveform section missing in ELI XML") from exc

        self.sampling_rate = int(waveform_block['@RhyRate'])
        resolution_uv = float(waveform_block['@RhyResolution'])
        leads = waveform_block['Lead']
        if not isinstance(leads, list):
            leads = [leads]

        self.lead = {}
        for lead_entry in leads:
            lead_name = lead_entry.get('@Name')
            rhythm = lead_entry.get('Rhythm', {})
            waveform_text = rhythm.get('#text')
            if not lead_name or waveform_text is None:
                continue

            waveform_bytes = b64decode(waveform_text)
            decoded = xli_decode(waveform_bytes, labels=[])
            if not decoded:
                continue

            signal = np.asarray(decoded[0], dtype=np.float32)
            scaled = signal * (resolution_uv / 1000.0)  # convert µV to mV
            self.lead[lead_name] = scaled

        if not self.lead:
            raise ValueError("No leads decoded from ELI waveform")

    def parse_metadata(self) -> None:
        flat = self._flatten_dictionary(self.xml_dict)
        self.data = flat
        self.flatdct = flat

        patient = self.xml_dict.get('EliEcg', {}).get('Patient', {})
        age = patient.get('Age') or flat.get('EliEcg/Patient/Age', 'unknown')
        gender = patient.get('Sex') or flat.get('EliEcg/Patient/Sex', 'unknown')
        self.text_data = {
            'age': str(age) if age is not None else 'unknown',
            'gender': str(gender) if gender is not None else 'unknown',
        }

    def parse(self) -> None:
        self.parse_waveforms()
        self.get_standard_derived_leads()

        sampling_rate = getattr(self, 'sampling_rate', 500)
        self.filter(sampling_rate=sampling_rate)
        self.resample()

        if self.scale_method is not None:
            scaler = self.get_scaling_method(self.scale_method)
            if scaler is not None:
                scaler()

        self.get_float_array()
        self.parse_metadata()

    def parse_fast(self) -> None:
        self.parse_waveforms()
        self.get_standard_derived_leads()

        sampling_rate = getattr(self, 'sampling_rate', 500)
        self.filter(sampling_rate=sampling_rate)
        self.resample()

        if self.scale_method is not None:
            scaler = self.get_scaling_method(self.scale_method)
            if scaler is not None:
                scaler()

        self.get_float_array()
