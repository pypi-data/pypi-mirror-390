from collections.abc import MutableMapping
import json
import os

import numpy as np
import pandas as pd
from scipy.signal import resample
import wfdb

from ekgtools.parser.base import BaseParser

class MIMICParser(BaseParser):
    """
    Parser for MIMIC-IV ECG data format based on data_process_v2.py and MimicivDataset class.
    
    This class handles ECG data from the MIMIC-IV database with enhanced functionality
    for local file processing, label filtering, and augmented reporting capabilities.
    It provides functionality equivalent to MUSEXMLParser but adapted for MIMIC-IV data structure.
    
    Attributes:
        data_path: Local path to MIMIC-IV dataset files
        background_info: Dictionary containing diagnostic label descriptions
        label_list: List of available diagnostic labels
        mlb: MultiLabelBinarizer for one-hot encoding
        data: Flattened dictionary containing parsed ECG data
        lead: Dictionary of ECG lead signals
        normalized_lead: Dictionary of normalized ECG lead signals  
        text_data: Dictionary containing patient demographics and measurements
    """

    def __init__(self, config: dict, waveform_type: str, normalize: bool,
                 data_path: str = "dataset/mimiciv/"):
        """
        Initialize MIMICParser with configuration parameters.
        
        Args:
            config: Configuration dictionary containing signal processing parameters
            waveform_type: Type of waveform to process ('full' or 'rep')  
            normalize: Whether to normalize the ECG signals
            data_path: Path to local MIMIC-IV dataset files
        """
        scale_method = 'standard' if normalize else None
        super().__init__(config=config, waveform_type=waveform_type, scale_method=scale_method)
        self.normalize = normalize
        self.data_path = data_path
        self.background_info = {}
        self.label_list = []
        self.mlb = None
        self.vis_root = '/home/user/dataSpace/mimic_iv_ecg/mimic-iv-ecg-diagnostic-electrocardiogram-matched-subset-1.0/'
        
    def load_label_mapping(self, augment_type: str = "mimiciv_label_map_report_gemini"):
        """
        Load background information and label mapping for diagnostic augmentation.
        
        Args:
            augment_type: Type of augmentation mapping to load
                         - "mimiciv_label_map_report_gemini": Gemini-generated descriptions
                         - "mimiciv_label_map_report": Standard descriptions
        """
        import pickle
        
        # Load background information for diagnostic descriptions
        background_path = os.path.join(self.data_path, f"{augment_type}.json")
        if os.path.exists(background_path):
            with open(background_path, "r") as f:
                self.background_info = json.load(f)
        
        # Load MultiLabelBinarizer for label encoding
        mlb_path = os.path.join(self.data_path, "mlb.pkl")
        if os.path.exists(mlb_path):
            with open(mlb_path, 'rb') as f:
                self.mlb = pickle.load(f)
                self.label_list = self.mlb.classes_
    
    def load_machine_measurements(self) -> pd.DataFrame:
        """
        Load machine measurements from local CSV file.
        
        Returns:
            pd.DataFrame: DataFrame containing combined ECG reports and metadata
        """
        machine_measurements_path = os.path.join(self.data_path, "machine_measurements.csv")
        df = pd.read_csv(machine_measurements_path)
        
        def combine_reports(row):
            reports = [str(elem) for elem in row if elem and str(elem) != 'nan']
            return ', '.join(reports)
        
        report_cols = [col for col in df.columns if 'report_' in col]
        df['report'] = df[report_cols].apply(combine_reports, axis=1)
        df['study_id'] = df['study_id'].astype(str)
        df['subject_id'] = df['subject_id'].astype(str)
        
        return df[['subject_id', "study_id", "report"]]
    
    def load_label_annotations(self) -> pd.DataFrame:
        """
        Load annotated labels from local JSON file.
        
        Returns:
            pd.DataFrame: DataFrame containing ECG labels and metadata
        """
        label_data_path = os.path.join(self.data_path, "mimiciv_ecg_label_annotated_11_9.json")
        label_data = pd.read_json(label_data_path)
        label_data['study_id'] = label_data['study_id'].astype(str)
        label_data['subject_id'] = label_data['subject_id'].astype(str)
        
        return label_data
    
    def filter_labels_by_frequency(self, label_data: pd.DataFrame, min_count: int = 2000) -> pd.DataFrame:
        """
        Filter diagnostic labels by minimum occurrence frequency.
        
        Args:
            label_data: DataFrame containing ECG labels
            min_count: Minimum occurrence count for label inclusion
            
        Returns:
            pd.DataFrame: DataFrame with filtered labels
        """
        # Count frequency of each diagnostic label
        label_set_count = {}
        for idx, item in label_data.iterrows():
            for label in item['labels']:
                if label not in label_set_count.keys():
                    label_set_count[label] = 1
                else:
                    label_set_count[label] += 1
        
        # Sort labels by frequency (most common first)
        label_set_count = {k: v for k, v in sorted(label_set_count.items(), 
                                                  key=lambda item: item[1], reverse=True)}
        
        # Keep only labels with ≥min_count occurrences
        sorted_filter_dict = {key: value / label_data.shape[0] 
                            for key, value in label_set_count.items() 
                            if value >= min_count}
        
        # Filter labels in each record
        label_data['filter_labels'] = label_data['labels'].apply(
            lambda x: [i for i in x if i in sorted_filter_dict.keys()]
        )
        
        # Remove records with no frequent labels
        label_data = label_data[label_data['filter_labels'].map(lambda d: len(d)) > 0]
        
        return label_data
    
    def load_ecg_waveform(self, path: str) -> np.ndarray:
        """
        Load ECG waveform data from WFDB format.
        
        Args:
            path: Path to ECG waveform file
            
        Returns:
            np.ndarray: ECG waveform data with shape (n_leads, n_samples)
        """
        import wfdb
        full_path = os.path.join(self.vis_root, path)
        ecg_signal = wfdb.rdsamp(full_path)
        ecg = ecg_signal[0].T  # Shape: (n_leads, n_samples)
        
        # Resample to reduce data size (divide by 5)
        ecg = resample(ecg, int(ecg.shape[1] / 5), axis=1)
        
        # Handle NaN values
        if np.any(np.isnan(ecg)):
            ecg = np.where(np.isnan(ecg), 0, ecg)
            
        return ecg.astype(np.float32)
    
    def parse_waveforms(self):
        """
        Extract and process ECG lead waveform data from MIMIC format.
        
        Loads waveform data using WFDB format and processes it into standard
        12-lead ECG format. Generates derived leads if standard leads are available.
        """
        if 'path' in self.data:
            # Load waveform from WFDB file
            try:
                waveform_data = self.load_ecg_waveform(self.data['path'])
                
                # Assume 12-lead ECG format
                lead_names = ['I', 'II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'aVR', 'aVL', 'aVF', 'III']
                
                for i, lead_name in enumerate(lead_names[:waveform_data.shape[0]]):
                    self.lead[lead_name] = waveform_data[i, :].astype(np.float16)
                
                # Generate derived leads if I and II are available
                if 'I' in self.lead and 'II' in self.lead:
                    self.get_standard_derived_leads()
                    
            except Exception as e:
                print(f"Warning: Could not load waveform data from {self.data['path']}: {e}")
    
    def generate_augmented_report(self, report: str, labels: list) -> str:
        """
        Generate augmented report with background diagnostic information.
        
        Args:
            report: Original ECG report text
            labels: List of diagnostic labels
            
        Returns:
            str: Augmented report with background information
        """
        if not report or str(report) == 'nan':
            report = ""
        
        background_list = []
        for label in labels:
            if label in self.background_info:
                background_list.append(self.background_info[label])
        
        if background_list:
            background_info = ". ".join(background_list)
            final_report = f" This ECG is: {report}\nBackground information: {background_info}"
        else:
            final_report = f" This ECG is: {report}"
            
        return final_report
    
    def parse_metadata(self):
        """
        Extract patient demographics and ECG measurements from parsed data.
        
        Processes patient information including age, gender, diagnostic statements,
        and standard ECG measurements. Generates augmented reports if background
        information is available.
        """
        output_dict = {}
        output_dict['age'] = self.data.get('age', 'unknown')
        output_dict['gender'] = self.data.get('gender', 'unknown')
        
        # Extract diagnostic labels (use filter_labels if available)
        if 'filter_labels' in self.data:
            dx_statements = self.data['filter_labels']
        elif 'labels' in self.data:
            dx_statements = self.data['labels'] if isinstance(self.data['labels'], list) else [self.data['labels']]
        else:
            dx_statements = []
        output_dict['dx_statements'] = dx_statements
        
        # Generate augmented report if available
        if 'report' in self.data and self.background_info:
            augmented_report = self.generate_augmented_report(self.data['report'], dx_statements)
            output_dict['augmented_report'] = augmented_report
        else:
            output_dict['augmented_report'] = self.data.get('report', '')
        
        # Map MIMIC measurement fields to standard ECG measurement names
        discrete_measures = {
            'heart_rate': 'Ventricular Rate',
            'pr_interval': 'PR Interval', 
            'qrs_duration': 'QRS Duration',
            'qt_interval': 'QT Interval',
            'p_axis': 'P Axis',
            'qrs_axis': 'R Axis',
            't_axis': 'T Axis'
        }
        
        for key, display_name in discrete_measures.items():
            output_dict[display_name] = self.data.get(key, 'unknown')
            
        self.text_data = output_dict
    
    def _flatten_dictionary(self, dictionary: dict, parent_key: str = '', separator: str = '/') -> dict:
        """
        Recursively flatten nested dictionaries into single-level dictionary.
        
        Args:
            dictionary: Input nested dictionary to flatten
            parent_key: Current parent key for nested traversal
            separator: Separator character for nested keys
            
        Returns:
            dict: Flattened dictionary with concatenated keys
        """
        items = []
        for key, value in dictionary.items():
            new_key = parent_key + separator + key if parent_key else key
            if isinstance(value, MutableMapping):
                items.extend(self._flatten_dictionary(value, new_key, separator=separator).items())
            else:
                try:
                    items.append((new_key, value))
                except:
                    items.append((new_key, str(value)))
        return dict(items)
    
    def load_from_json(self, json_data):
        """
        Load ECG data from JSON format compatible with MimicivDataset.
        
        Args:
            json_data: JSON string or dictionary containing ECG data
        """
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        
        self.data = self._flatten_dictionary(json_data)
        
        # Map filter_labels to labels for compatibility
        if 'filter_labels' in self.data:
            self.data['labels'] = self.data['filter_labels']
    
    def load_from_dataframe_row(self, row):
        """
        Load ECG data from pandas DataFrame row (MimicivDataset compatible).
        
        Args:
            row: pandas Series containing ECG record data
        """
        self.data = {
            'subject_id': str(row.get('subject_id', '')),
            'study_id': str(row.get('study_id', '')),
            'path': row.get('path', ''),
            'report': row.get('report', ''),
            'labels': row.get('labels', []),
            'filter_labels': row.get('filter_labels', [])
        }
    
    def parse(self):
        """
        Main parsing method coordinating all processing steps.
        
        Executes the complete processing pipeline compatible with MimicivDataset:
        1. Decode ECG leads from waveform files
        2. Apply signal filtering (bandpass, median)
        3. Resample signals to target length
        4. Normalize signals if requested
        5. Generate standard 12-lead float array
        6. Parse demographics and generate augmented reports
        
        Raises:
            ValueError: If no data has been loaded
        """
        if not self.data:
            raise ValueError("No data loaded. Use load_from_json() or load_from_dataframe_row() first.")
            
        self.parse_waveforms()
        
        sampling_rate = self.data.get('sampling_rate', 500)
        self.filter(sampling_rate=sampling_rate)
        self.resample()
        
        if self.scale_method is not None:
            scaler = self.get_scaling_method(self.scale_method)
            if scaler is not None:
                scaler()

        self.get_float_array()
        self.parse_metadata()
