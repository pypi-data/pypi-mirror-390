import base64
import binascii
import json

import numpy as np
import scipy
from scipy.signal import butter, sosfilt
from sklearn.preprocessing import MinMaxScaler
import wfdb

from ekgtools.config import resolve_config

class BaseParser:

    def __init__(self, config: dict | None = None, waveform_type: str = 'full', scale_method: str | None = 'standard'):
        cfg = resolve_config(config)
        self.xml_dict = {}
        self.data = {}
        self.lead = {}
        if waveform_type not in ['full','rep']:
            raise ValueError(f"waveform_type must be either 'full' or 'median', not {waveform_type}")
        self.waveform_type = waveform_type
        self.scaled_lead = {}
        self.bandpass_lower = cfg['bandpass_lower']
        self.bandpass_higher = cfg['bandpass_higher']
        self.sig_arr_length = cfg['sig_arr_length']
        self.median_filter_size = cfg['median_filter_size']
        self.default_8_leads = cfg['default_8_leads']
        self.standard_12_leads = cfg['standard_12_leads']
        self.scale_method = scale_method

    def butter_bandpass(self, lowcut, highcut, fs=500, order=5):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        return butter(order, [low, high], analog=False, btype='band', output='sos')

    def butter_bandpass_filter(self, signal, lowcut, highcut, fs=500, order=5):
        sos = self.butter_bandpass(lowcut, highcut, fs, order=order)
        return sosfilt(sos, signal)

    @staticmethod
    def decoder(input_data):
        try:
            decoded = base64.b64decode(input_data)
            if len(decoded) % 2 != 0:
                raise ValueError("Decoded data length is not aligned to 2 bytes.")
            signal = np.frombuffer(decoded, dtype='<i2')  # Little-endian int16
            return signal
        except (binascii.Error, ValueError) as e:
            raise RuntimeError(f"Decoding failed: {e}")

    def get_standard_derived_leads(self):
        # Generate III, aVL, avR, aVF
        self.lead['III'] = self.lead['II'] - self.lead['I']
        self.lead['aVL'] = (self.lead['I'] - self.lead['III'])/2
        self.lead['aVR'] = (self.lead['I'] + self.lead['II'])/2
        self.lead['aVF'] = (self.lead['II'] + self.lead['III'])/2

    def get_standard_scaled_leads(self):
        # Stack into (n_leads, n_samples)
        ecg_array = np.stack(list(self.lead.values()))  
        # Per-lead (row-wise) mean and std
        mean = ecg_array.mean(axis=1, keepdims=True)
        std = ecg_array.std(axis=1, keepdims=True)
        # Avoid division by zero if any lead is flat
        std[std == 0] = 1.0  
        scaled_ecg_array = (ecg_array - mean) / std
        # Map back into dict
        for idx, lead in enumerate(self.lead.keys()):
            self.scaled_lead[lead] = scaled_ecg_array[idx, :]

    def get_minmax_scaled_leads(self):
        ecg_array = np.stack(list(self.lead.values()))
        scaled_ecg_array = MinMaxScaler(feature_range=(-1,1)).fit_transform(ecg_array)
        for idx,lead in zip(range(scaled_ecg_array.shape[0]),list(self.lead.keys())):
            self.scaled_lead[lead] = scaled_ecg_array[idx,:]

    def get_scaling_method(self,method):
        return {
            'standard':self.get_standard_scaled_leads,
            'minmax':self.get_minmax_scaled_leads
        }.get(method, None)

    def filter(self,denoise_steps: list =['bandpass','median'], sampling_rate: int = 500):
            for lead in self.lead.keys():
                signal = self.lead[lead]
                if 'bandpass' in denoise_steps:
                    signal = self.butter_bandpass_filter(signal,
                                                        lowcut=self.bandpass_lower,
                                                        highcut=self.bandpass_higher,
                                                        fs=sampling_rate)
                if 'median_filter' in denoise_steps:
                    signal = scipy.ndimage.median_filter(signal, size=self.median_filter_size)
                self.lead[lead] = signal

    def resample(self):
        for lead in self.lead.keys():
            self.lead[lead] = scipy.signal.resample(self.lead[lead],self.sig_arr_length) #resample using Fourier method    

    def get_float_array(self):
        self.float_array = np.zeros(shape=(12,self.sig_arr_length))
        for idx,lead in enumerate(self.standard_12_leads):
            if self.scale_method is not None:
                self.float_array[idx,:] = self.scaled_lead[lead]
            else:
                self.float_array[idx,:] = self.lead[lead]
        
    def save_to_json(self,save_path:str):
        json.dumps(self.data,save_path)

    @staticmethod
    def export_ecg_to_wfdb(self, ecg_data: np.ndarray, metadata: dict, output_dir: str = "."):
        """
        Export ECG data and metadata to WFDB format.

        Parameters:
        - ecg_data: NumPy array of shape (n_samples, n_leads) or (n_leads, n_samples)
        - metadata: Dictionary with keys such as 'record_name', 'fs', 'units', 'sig_names'
        - output_dir: Folder to save the .dat and .hea files
        """
        # Ensure signal is (n_samples, n_channels)
        if ecg_data.shape[0] < ecg_data.shape[1]:
            ecg_data = ecg_data.T

        # Basic validation
        n_channels = ecg_data.shape[1]
        record_name = metadata.get("record_name", "ecg_record")
        fs = metadata.get("fs", 500)
        units = metadata.get("units", ["mV"] * n_channels)
        sig_names = metadata.get("sig_names", [f"ch{i+1}" for i in range(n_channels)])

        if len(units) != n_channels or len(sig_names) != n_channels:
            raise ValueError("Length of 'units' and 'sig_names' must match number of channels")

        # Format signals (ensure float32 for wfdb)
        ecg_data = ecg_data.astype(np.float32)

        # Patient-level comments
        comments = []
        for field in ["age", "sex", "diagnosis", "patient_id"]:
            if field in metadata:
                comments.append(f"{field}: {metadata[field]}")

        # Write record
        wfdb.wrsamp(
            record_name=record_name,
            fs=fs,
            units=units,
            sig_name=sig_names,
            p_signal=ecg_data,
            fmt=["16"] * n_channels,
            write_dir=output_dir,
            comments=comments
        )
        print(f"WFDB record '{record_name}' written to '{output_dir}'")
