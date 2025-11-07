from collections.abc import MutableMapping

import numpy as np

from ekgtools.parser.base import BaseParser

class MUSEXMLParser(BaseParser):

    def __init__(self, config, waveform_type, scale_method):
        super().__init__(config=config, waveform_type=waveform_type, scale_method=scale_method)

    def _flatten_dictionary(self, dictionary, parent_key='', separator='/'):
        exclude = ['RestingECG/Diagnosis/DiagnosisStatement','RestingECG/OriginalDiagnosis/DiagnosisStatement']
        items = []
        for key, value in dictionary.items():
            new_key = parent_key + separator + key if parent_key else key
            if isinstance(value, MutableMapping) and new_key not in exclude:
                items.extend(self._flatten_dictionary(value, new_key, separator=separator).items())
            elif 'Waveform' in key:
                for dictionary in value:
                    for key, value in dictionary.items():
                        if 'LeadData' not in key:
                            items.append((new_key + separator + dictionary['WaveformType'] + separator + key, value))   
                        else:
                            for subdictionary in value:
                
                                for key, value in subdictionary.items():
                                    items.append((new_key + separator + dictionary['WaveformType'] + separator + 'Lead_' + subdictionary['LeadID'] + separator + key, value))   
            elif 'DiagnosisStatement' in key:
                output = []
                string = ''
                end_line_flag = False

                if type(value) != list:
                    value = [value]

                for item in value:
                    for key,value in item.items():
                        if key == 'StmtFlag' and 'ENDSLINE' in value:
                            end_line_flag = True
                        if key == 'StmtText':
                            string = string + ' ' + value
                    if end_line_flag:
                        output.append(string.strip())
                        string = ''
                        end_line_flag = False
                value = '; '.join(output)
                items.append((new_key, value))
            else:         
                try:
                    items.append((new_key, value))
                except:
                    items.append((new_key, str(value)))

        return dict(items)
    
    def parse_waveforms(self):
       
        if self.waveform_type == 'full':
            signal_type = 'Rhythm'
        elif self.waveform_type == 'rep':
            signal_type = 'Median'

        for key in self.data.keys():

            if f'RestingECG/Waveform/{signal_type}/Lead_' in key:
                lead_name = key.split(f'RestingECG/Waveform/{signal_type}/Lead_')[-1].split('/')[0]                             
                if 'WaveFormData' in key:
                    signal = self.decoder(self.data[key])
                    self.sig_arr_length = len(signal)
                    self.data[key] = signal
                    unit_conversion = {
                        'VOLTS':1000,
                        'MILLIVOLTS':1,
                        'MICROVOLTS':0.001
                    }.get(self.data[f'RestingECG/Waveform/{signal_type}/Lead_'+lead_name+'/LeadAmplitudeUnits'],1.0) #converts signal to milivolts (mV)
                    conversion_factor = float(self.data[f'RestingECG/Waveform/{signal_type}/Lead_'+lead_name+'/LeadAmplitudeUnitsPerBit']) * unit_conversion
                    waveform_data = np.multiply(np.array(signal),conversion_factor)
                    self.lead[lead_name] = waveform_data.astype(np.float16)      
        self.get_standard_derived_leads()

    def parse_metadata(self):
        output_dict = {}
        output_dict['age'] = self.data.get('RestingECG/PatientDemographics/PatientAge','np.nan')
        output_dict['gender'] = self.data.get('RestingECG/PatientDemographics/Gender','np.nan')
        dx_statements = self.data.get('RestingECG/OriginalDiagnosis/DiagnosisStatement','np.nan').split(';')
        dx_statements = [item for item in dx_statements if 'compared with' not in item and 'no longer' not in item and 'has replaced' not in item]
        dx_statements = [item.split('(cited')[0] for item in dx_statements]
        output_dict['dx_statements'] = dx_statements
        discrete = {'RestingECG/RestingECGMeasurements/VentricularRate':'Ventricular Rate',
                    'RestingECG/RestingECGMeasurements/AtrialRate':'Atrial Rate',
                    'RestingECG/RestingECGMeasurements/PRInterval':'PR Interval',
                    'RestingECG/RestingECGMeasurements/QRSDuration':'QRS Duration',
                    'RestingECG/RestingECGMeasurements/QTInterval':'QT Interval',
                    'RestingECG/RestingECGMeasurements/PAxis':'P Axis',
                    'RestingECG/RestingECGMeasurements/RAxis':'R Axis',
                    'RestingECG/RestingECGMeasurements/TAxis':'T Axis'}
        for item in discrete.keys():
            output_dict[f"{discrete.get(item,'')}"] = self.data.get(item,'np.nan')
        self.text_data = output_dict

    def parse_fast(self):
        self.lead = {}
        for dct in self.xml_dict['RestingECG']['Waveform'][-1]['LeadData']:
            waveform_data = self.decoder(dct['WaveFormData'])
            self.sig_arr_length = len(waveform_data)
            unit_conversion = {
                        'VOLTS':1000,
                        'MILLIVOLTS':1,
                        'MICROVOLTS':0.001
                    }.get(dct['LeadAmplitudeUnits'],1.0) #converts signal to milivolts (mV)
            conversion_factor = float(dct['LeadAmplitudeUnitsPerBit']) * unit_conversion
            waveform_data = np.multiply(np.array(waveform_data),conversion_factor)
            self.lead[dct['LeadID']] = waveform_data
        self.get_standard_derived_leads()
        sampling_rate = int(self.xml_dict['RestingECG']['Waveform'][-1]['SampleBase'])
        self.filter(sampling_rate=sampling_rate)
        if self.scale_method is not None:
            method = self.get_scaling_method(self.scale_method)
            method()
        self.get_float_array()

    def parse(self):
        self.data = self._flatten_dictionary(self.xml_dict)
        self.parse_waveforms()    
        if self.waveform_type == 'full':
            sampling_rate = int(self.data['RestingECG/Waveform/Rhythm/SampleBase'])
        elif self.waveform_type == 'rep':
            sampling_rate = int(self.data['RestingECG/Waveform/Median/SampleBase'])
        self.filter(sampling_rate=sampling_rate)
        if self.scale_method is not None:
            method = self.get_scaling_method(self.scale_method)
            method()
        self.get_float_array()
        self.parse_metadata()
