import os
import xmltodict

from ekgtools.config import resolve_config
from ekgtools.parser.eli import ELIXMLParser
from ekgtools.parser.iecg import IECGXMLParser
from ekgtools.parser.mimic import MIMICParser
from ekgtools.parser.muse import MUSEXMLParser
from ekgtools.parser.wfdb import WFDBParser

class ECGParser:

    def __init__(self, path, config: dict | None = None, config_overrides: dict | None = None, waveform_type: str = 'full', normalize: bool = False, scale_method: str | None = 'standard', fast: bool = True):
        effective_config = resolve_config(config, config_overrides)
        self.infer_filetype(path)
        if self.filetype == 'iecg':
            self.obj = IECGXMLParser(config=effective_config, waveform_type=waveform_type, scale_method=scale_method)
            with open(path, 'rb') as fd:
                self.obj.xml_dict = xmltodict.parse(fd.read().decode('utf8'))
                if fast:
                    self.obj.parse_fast()
                else:
                    self.obj.parse()
        elif self.filetype == 'muse':
            self.obj = MUSEXMLParser(config=effective_config, waveform_type=waveform_type, scale_method=scale_method)
            with open(path, 'rb') as fd:
                self.obj.xml_dict = xmltodict.parse(fd.read().decode('utf8')) 
                if fast:
                    self.obj.parse_fast()
                else:
                    self.obj.parse()
        elif self.filetype == 'eli':
            self.obj = ELIXMLParser(config=effective_config, waveform_type=waveform_type, scale_method=scale_method)
            with open(path, 'rb') as fd:
                self.obj.xml_dict = xmltodict.parse(fd.read().decode('utf8'))
            if fast:
                self.obj.parse_fast()
            else:
                self.obj.parse()
        elif self.filetype == 'mimic':
            self.obj = MIMICParser(config=effective_config, waveform_type=waveform_type, normalize=normalize)
            with open(path, 'r') as fd:
                self.obj.load_from_json(fd.read()) 
        elif self.filetype == 'wfdb':
            self.obj = WFDBParser(config=effective_config, waveform_type=waveform_type, scale_method=scale_method)
            self.obj.parse(path)
        else:
            raise ValueError(f"Unsupported ECG file type for path: {path}")

    def __getattr__(self, name):
        return getattr(self.obj, name)

    def __dir__(self):
        return list(set(dir(type(self)) + dir(self.obj)))

    def infer_filetype(self, path):
        _, ext = os.path.splitext(path)
        ext = ext.lower()

        if ext in {'.hea', '.dat'}:
            self.filetype = 'wfdb'
            return

        wfdb_base_exists = os.path.exists(f"{path}.hea") or os.path.exists(f"{path}.dat")
        if wfdb_base_exists:
            self.filetype = 'wfdb'
            return
        if ext == '.json':
            self.filetype = 'mimic'
            return

        if not os.path.exists(path):
            self.filetype = 'unknown'
            return

        with open(path, 'r', encoding='utf8', errors='ignore') as f:
            file_str = f.read()
            if 'MuseInfo' in file_str:
                self.filetype = 'muse'
            elif 'PhilipsECG' in file_str:
                self.filetype = 'iecg'
            elif 'EliEcg' in file_str:
                self.filetype = 'eli'
            else:
                self.filetype = 'unknown'
