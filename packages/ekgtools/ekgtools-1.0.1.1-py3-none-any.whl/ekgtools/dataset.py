import os
import posixpath
import tempfile
import warnings
from io import BytesIO

import numpy as np
import pandas as pd
import scipy
import torch
import torch.nn.functional as F
from matplotlib import pyplot as plt
from torch.utils.data import Dataset
import torchvision.transforms as T
from PIL import Image

from ekgtools.config import config
from ekgtools.parser import ECGParser
from ekgtools.plot import plot, plot_one
from ekgtools.s3 import S3Setup


class ECGDataset(Dataset):
    
    def __init__(self, 
                 directory: str, 
                 df: pd.DataFrame, 
                 filename_column: str,
                 label_column: str, 
                 output_image: bool = False, 
                 metadata_fields: list = ['age','gender'],
                 add_meta: bool = False,
                 specify_leads: list = config['standard_12_leads'],
                 sig_arr_length: int = 5000,
                 scale_method: str = 'standard',
                 order: list = ['channels','length'],
                 fast: bool = True,
                 storage: str = 'local',
                 s3_setup: S3Setup | None = None,
                 cache_dir: str | None = None):
        """
         Args:
            directory: path to folder containing ECG XML files
            df: dataframe containing filenames, labels, and optional metadata
            filename_column: name of column in df with file names
            label_column: name of column in df with labels
            metadata_fields: optional list of metadata fields (e.g., ['age', 'gender'])
            specify_leads: list of leads to extract (e.g., ['I', 'II', 'V1'])
            sig_arr_length: target length to resample ECG signals
            bandpass_lower: lower frequency for bandpass filtering
            bandpass_higher: upper frequency for bandpass filtering
            median_filter_size: window size for median filter
            denoise_steps: list of denoising steps (default: ['bandpass', 'median'])
            num_class: Number of output classes (if None, inferred)
            add_meta: Whether to use metadata
            storage: 'local' or 's3' data source
            s3_setup: configuration helper when storage='s3'
            cache_dir: local cache root for S3 downloads
        """
        self.base_directory = directory

        before = len(df)
        self.df = df.dropna(subset=[label_column])
        after = len(self.df)
        if before - after:
            warnings.warn(f"Dropped {before - after} rows due to missing labels!")
        
        self.filename_column_idx = self.df.columns.get_loc(filename_column)
        self.label_column = label_column
        
        self.num_class = len(self.df[label_column].unique())

        self.add_meta = metadata_fields if add_meta else []
        for meta in metadata_fields:
            if meta not in ['age','gender']:
                raise NotImplementedError('Only age and gender can be added as metadata!')
        self.output_image = output_image
        self.order = order
        self.specify_leads = specify_leads
        self.sig_arr_length = sig_arr_length
        self.scale_method = scale_method
        self.fast = fast
        if self.fast and add_meta:
            raise ValueError('Fast parsing does not allow for metadata!')

        storage_mode = storage.lower()
        if storage_mode not in {'local', 's3'}:
            raise ValueError("storage must be either 'local' or 's3'")
        self.storage_mode = storage_mode

        if self.storage_mode == 'local':
            if directory != '':
                self.local_root = os.path.abspath(os.path.expanduser(directory))
            else:
                self.local_root = None
            self.cache_dir = None
            self.s3_setup = None
            self.s3_prefix = None
        else:
            if s3_setup is None:
                raise ValueError("s3_setup must be provided when storage='s3'")
            self.s3_setup = s3_setup
            prefix = directory.strip('/\\')
            prefix = posixpath.normpath(prefix) if prefix else ''
            self.s3_prefix = '' if prefix in {'.', ''} else prefix
            cache_root = cache_dir or os.path.join(tempfile.gettempdir(), 'ekgtools_cache')
            self.cache_dir = os.path.abspath(os.path.expanduser(cache_root))
            os.makedirs(self.cache_dir, exist_ok=True)
            self.local_root = None

    @staticmethod
    def create_1d_array(ecg_dict, 
                    sig_arr_length, 
                    specify_leads):
        leads = []
        for lead in specify_leads:
            if lead not in ecg_dict.keys():
                print(f"Lead {lead} missing — filling with zeros")
                signal = np.zeros(sig_arr_length)  # zero-filled array
            else:
                signal = ecg_dict[lead]
                if len(signal) != sig_arr_length:
                    signal = scipy.signal.resample(signal,sig_arr_length) #resample using Fourier method    
            leads.append(signal)
        output = np.array(leads)
        complete_leads = all(lead in ecg_dict for lead in specify_leads)
        return output, complete_leads, None

    def _build_s3_relative_key(self, filename: str) -> str:
        if self.storage_mode != 's3':
            raise RuntimeError("_build_s3_relative_key called while storage_mode is not 's3'")

        clean_name = str(filename).lstrip('/\\')
        clean_name = clean_name.replace('\\', '/')
        parts = []
        if self.s3_prefix:
            parts.append(self.s3_prefix)
        parts.append(clean_name)
        relative_key = posixpath.normpath(posixpath.join(*parts)) if parts else posixpath.normpath(clean_name)
        if relative_key.startswith('..'):
            raise ValueError(f"Filename '{filename}' resolves outside the configured S3 prefix")
        return '' if relative_key == '.' else relative_key

    def _download_s3_key(self, relative_key: str, ensure_companion: bool = True) -> str:
        if self.storage_mode != 's3':
            raise RuntimeError("_download_s3_key called while storage_mode is not 's3'")

        fs = self.s3_setup._get_fs()
        local_path = os.path.join(self.cache_dir, relative_key.replace('/', os.sep)) if relative_key else self.cache_dir
        if not relative_key:
            raise ValueError("Relative key must not be empty for S3 downloads")

        if not os.path.exists(local_path):
            directory = os.path.dirname(local_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            key_parts = []
            if self.s3_setup.prefix:
                key_parts.append(self.s3_setup.prefix.strip('/'))
            key_parts.append(relative_key)
            s3_key = posixpath.join(*key_parts) if key_parts else ''
            source = f"{self.s3_setup.bucket}/{s3_key}" if s3_key else self.s3_setup.bucket
            try:
                fs.get(source, local_path)
            except FileNotFoundError as exc:
                raise FileNotFoundError(f"S3 object not found: s3://{source}") from exc

        if ensure_companion:
            base, ext = os.path.splitext(relative_key)
            ext = ext.lower()
            if ext in {'.hea', '.dat'}:
                companion_key = base + ('.dat' if ext == '.hea' else '.hea')
                companion_local = os.path.join(self.cache_dir, companion_key.replace('/', os.sep))
                if not os.path.exists(companion_local):
                    self._download_s3_key(companion_key, ensure_companion=False)

        return local_path

    def _resolve_path(self, filename: str) -> str:
        if self.storage_mode == 'local':
            filename = os.path.expanduser(filename)
            if self.local_root:
                candidate = os.path.abspath(os.path.join(self.local_root, filename))
                if os.path.commonpath([self.local_root, candidate]) != self.local_root:
                    raise ValueError(f"Filename '{filename}' resolves outside the dataset directory")
                return candidate
            return os.path.abspath(filename)

        relative_key = self._build_s3_relative_key(filename)
        return self._download_s3_key(relative_key)

    def __len__(self):
        return len(self.df)
    
    def __getitem__(self, idx):
        filename = str(self.df.iloc[idx, self.filename_column_idx])
        path = self._resolve_path(filename)

        ep = None
        try:
            ep = ECGParser(path,fast=self.fast)
            ecg_dict = ep.lead
        except Exception as e:
            print(f"[ERROR] Failed to parse ECG file {path}: {e}")
            raise
        
        # Output
        if self.output_image:
            complete_leads = True
            if len(self.specify_leads) == 1:
                fig = plot_one(ep.lead[self.specify_leads[0]])
            elif len(self.specify_leads) == 12:
                fig = plot(ep.float_array, sample_rate=500, lead_index=self.specify_leads, columns=4)
            else:
                raise NotImplementedError('ECGDataset is only configured for 12 lead and single lead plots!')
            
            # Save plot to memory buffer
            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
            buf.seek(0)
            plt.close(fig)

            # Convert to image tensor
            img = Image.open(buf).convert('RGB')
            output = T.ToTensor()(img)  # shape: [3, H, W]
        else:
            # Lead derivation
            if "V3-V2" in self.specify_leads:
                output_v3, complete_v3, _ = self.create_1d_array(ecg_dict, self.sig_arr_length, ["V3"])
                output_v2, complete_v2, _ = self.create_1d_array(ecg_dict, self.sig_arr_length, ["V2"])
                output = output_v3 - output_v2
                complete_leads = complete_v3 and complete_v2
            elif "V4-V3" in self.specify_leads:
                output_v3, complete_v3, _ = self.create_1d_array(ecg_dict, self.sig_arr_length, ["V3"])
                output_v4, complete_v4, _ = self.create_1d_array(ecg_dict, self.sig_arr_length, ["V4"])
                output = output_v4 - output_v3
                complete_leads = complete_v3 and complete_v4
            else:
                output, complete_leads, _ = self.create_1d_array(ecg_dict, self.sig_arr_length, self.specify_leads)

            if output is None or output.size == 0:
                raise ValueError(f"[ERROR] Output is empty for file: {path}; ecg_dict: {ecg_dict}")
    
            if len(self.specify_leads) == 1:
                output = torch.tensor(output, dtype=torch.float32).unsqueeze(0)
            else:
                output = torch.tensor(output, dtype=torch.float32)
                if self.order == ['length','channels']:
                    output = output.permute(1, 0).contiguous()

        # Label
        label = self.df[self.label_column].iloc[idx]
        label = torch.tensor([label], dtype=torch.int64)
        if self.num_class > 1:
            label = F.one_hot(label, num_classes=self.num_class).squeeze().to(torch.float32)
        
        # Add Metadata and return
        if self.add_meta:
            age = ep.text_data.get('age',0)
            gender = ep.text_data.get('gender',0)
            age_onehot = self.bucketize_age_np(age).reshape(-1, 1)
            gender = np.array(gender).reshape(-1, 1)
            meta = np.concatenate([gender, age_onehot], axis=0).squeeze()
            meta = torch.tensor(meta, dtype=torch.float32)
            return output, meta, label, complete_leads
        else:
            return output, label, complete_leads

    def bucketize_age_np(self, age_array):
        """
        age_array: (B,) numpy array of float, age values
        return: (B, 6) one-hot encoded age buckets
        """
        # Define the cut：[40, 50, 60, 70, 80]
        buckets = np.digitize(age_array, bins=[40, 50, 60, 70, 80])  # returns 0~5
        one_hot = np.eye(6)[buckets]  # (B, 6) one-hot encoding
        return one_hot
