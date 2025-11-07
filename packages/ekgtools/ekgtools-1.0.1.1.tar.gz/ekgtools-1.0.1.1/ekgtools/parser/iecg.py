from collections.abc import MutableMapping

import numpy as np
import pandas as pd

from ekgtools.parser.base import BaseParser
from ekgtools.utils.iecg import read_base64_encoding, xli_decode
from ekgtools.utils.iecg14bit import xli_decode_14bit

class IECGXMLParser(BaseParser):

    def __init__(self, config, waveform_type, scale_method):
        super().__init__(config=config, waveform_type=waveform_type, scale_method=scale_method)

    def _flatten_dictionary(self, dictionary, parent_key='', separator='/'):
        items = []
        exclude = []
        for key, value in dictionary.items():
            new_key = parent_key + separator + key if parent_key else key
            if isinstance(value, MutableMapping) and new_key not in exclude:
                items.extend(self._flatten_dictionary(value, new_key, separator=separator).items())
            else:         
                try:
                    items.append((new_key, value))
                except:
                    items.append((new_key, str(value)))
        return dict(items)

    def parse_waveforms(self):

        if self.waveform_type == 'full':
            
            if self.data['restingecgdata/waveforms/parsedwaveforms/@dataencoding'] != 'Base64':
                raise ValueError(f"Data Encoding: {self.data['restingecgdata/waveforms/parsedwaveforms/@dataencoding']} is not Base64!")
            if self.data['restingecgdata/waveforms/parsedwaveforms/@compression'] != 'XLI':
                raise ValueError(f"Compression Method: {self.data['restingecgdata/waveforms/parsedwaveforms/@compression']} is not XLI!")
            if self.data['restingecgdata/waveforms/parsedwaveforms/@numberofleads'] != '12':
                raise ValueError(f"Number of leads: {self.data['restingecgdata/waveforms/parsedwaveforms/@numberofleads']} is not 12!")

            leads = self.data['restingecgdata/waveforms/parsedwaveforms/@leadlabels'].split(' ')
            bytes = read_base64_encoding(self.data['restingecgdata/waveforms/parsedwaveforms/#text'])
            if int(self.data['restingecgdata/waveforms/parsedwaveforms/@bitspersample']) == 16:
                data = np.array(xli_decode(bytes,labels=[]))
            elif int(self.data['restingecgdata/waveforms/parsedwaveforms/@bitspersample']) == 14:
                data = np.array(xli_decode_14bit(bytes,labels=[]))
            else:
                raise ValueError(f"Invalid bits per sample: {self.data['restingecgdata/waveforms/parsedwaveforms/@bitspersample']}")
            
            #sampling_freq = int(self.data['restingecgdata/dataacquisition/signalcharacteristics/samplingrate'])
            #duration = int(self.data['restingecgdata/waveforms/parsedwaveforms/@durationperchannel'])
            #arr_length = int(duration * (sampling_freq / 1000)) - the last 1 second of Philips iECG recordings are not signal data
            for idx,lead in enumerate(leads):
                self.lead[lead] = data[idx,:self.sig_arr_length].astype(np.float16) 
                #Convert to correct units
                scale_factor =  int(self.data['restingecgdata/dataacquisition/signalcharacteristics/resolution'])
                scale_factor = scale_factor / 1000 #convert to milivolts
                offset = int(self.data['restingecgdata/dataacquisition/signalcharacteristics/signaloffset'])
                self.lead[lead] = np.subtract(self.lead[lead],offset)
                self.lead[lead] = np.multiply(self.lead[lead],scale_factor)

        elif self.waveform_type == 'median':
            if self.data['restingecgdata/waveforms/repbeats/@dataencoding'] != 'Base64':
                raise ValueError(f"Data Encoding: {self.data['restingecgdata/waveforms/repbeats/@dataencoding']} is not Base64!")
            
            for lead_data in self.data['restingecgdata/waveforms/repbeats/repbeat']:
                leadname = lead_data['@leadname']
                waveform_duration = int(lead_data['waveform']['@duration'])
                waveform_text = lead_data['waveform']['#text']
                bytes = read_base64_encoding(waveform_text)
                waveform = np.frombuffer(bytes, dtype=np.int16)[:waveform_duration]
                self.lead[leadname] = waveform

        self.get_standard_derived_leads()

    def parse_metadata(self):
        output_dict = {}
        ecg_date = pd.to_datetime(self.data.get('restingecgdata/dataacquisition/@date','2100-01-01'),format='%Y-%m-%d')
        dob = pd.to_datetime(self.data.get('restingecgdata/patient/generalpatientdata/age/dateofbirth','1900-01-01'),format='%Y-%m-%d')
        age = (ecg_date - dob) / np.timedelta64(52, 'W')
        output_dict['age'] = str(int(age)) if age < 120 else "unknown"

        output_dict['gender'] = self.data.get('restingecgdata/patient/generalpatientdata/sex','unknown')

        dx_statements = []
        try:
            source = self.data['restingecgdata/interpretations/interpretation/statement']
            if isinstance(source,list):
                for statement_dict in self.data['restingecgdata/interpretations/interpretation/statement']:
                    dx_statements += [statement_dict['leftstatement'] + '; ' + statement_dict['rightstatement']]
            else:
                raise ValueError("Single statement dictionary")
        except:
            left = self.data['restingecgdata/interpretations/interpretation/statement/leftstatement']
            right = self.data['restingecgdata/interpretations/interpretation/statement/rightstatement']
            dx_statements += [left + ';' + right]

        output_dict['dx_statements'] = dx_statements
        discrete = {'restingecgdata/interpretations/interpretation/globalmeasurements/heartrate/#text':'Ventricular Rate',
                    'restingecgdata/interpretations/interpretation/globalmeasurements/atrialrate/#text':'Atrial Rate',
                    'restingecgdata/interpretations/interpretation/globalmeasurements/print/#text':'PR Interval',
                    'restingecgdata/interpretations/interpretation/globalmeasurements/qrsdur/#text':'QRS Duration',
                    'restingecgdata/interpretations/interpretation/globalmeasurements/qtint/#text':'QT Interval',
                    'restingecgdata/interpretations/interpretation/globalmeasurements/pfrontaxis/#text':'P Axis',
                    'restingecgdata/interpretations/interpretation/globalmeasurements/qrsfrontaxis/#text':'R Axis',
                    'restingecgdata/interpretations/interpretation/globalmeasurements/thorizaxis/#text':'T Axis'}
        for item in discrete.keys():
            output_dict[f"{discrete.get(item,'')}"] = self.data.get(item,'unknown')
        self.text_data = output_dict
    
    def parse_fast(self):
        self.lead = {}
        dct = self.xml_dict['restingecgdata']['waveforms']['parsedwaveforms']
        
        leads = dct['@leadlabels'].split(' ')
        bytes = read_base64_encoding(dct['#text'])
        if int(dct['@bitspersample']) == 16:
            data = np.array(xli_decode(bytes,labels=[]))
        elif int(dct['@bitspersample']) == 14:
            data = np.array(xli_decode_14bit(bytes,labels=[]))
        else:
            raise ValueError(f"Invalid bits per sample: {dct['@bitspersample']}")

        for idx,lead in enumerate(leads):
            self.lead[lead] = data[idx,:self.sig_arr_length].astype(np.float16) 
            self.sig_arr_length = len(self.lead[lead])
            #Convert to correct units
            scale_factor =  int(self.xml_dict['restingecgdata']['dataacquisition']['signalcharacteristics']['resolution'])
            scale_factor = scale_factor / 1000 #convert to milivolts
            offset = int(self.xml_dict['restingecgdata']['dataacquisition']['signalcharacteristics']['signaloffset'])
            self.lead[lead] = np.subtract(self.lead[lead],offset)
            self.lead[lead] = np.multiply(self.lead[lead],scale_factor)
        self.get_standard_derived_leads()
        sampling_rate = int(self.xml_dict['restingecgdata']['dataacquisition']['signalcharacteristics']['samplingrate'])
        self.filter(sampling_rate=sampling_rate)
        if self.scale_method is not None:
            method = self.get_scaling_method(self.scale_method)
            method() 
        self.get_float_array()

    def parse(self):
        self.data = self._flatten_dictionary(self.xml_dict)
        self.parse_waveforms()
        if self.waveform_type == 'full':
            sampling_rate = int(self.data['restingecgdata/dataacquisition/signalcharacteristics/samplingrate'])
        elif self.waveform_type == 'rep':
            sampling_rate = int(self.data['restingecgdata/waveforms/repbeats/@dataencoding'])
        self.filter(sampling_rate=sampling_rate)
        if self.scale_method is not None:
            method = self.get_scaling_method(self.scale_method)
            method()
        self.get_float_array()
        self.parse_metadata()
