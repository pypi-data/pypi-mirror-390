import numpy as np
import wfdb
import json
from scipy import signal as ss


class WFDBDataLoader:
    def __init__(self, record_path=None, annotation_path=None):
        self.record_path = record_path
        self.annotation_path = annotation_path

    def resample(self, sig, rate, new_rate):
        """Resample signal from original rate to new rate"""
        num = int(len(sig) * new_rate / rate)
        y = ss.resample(sig, num)
        return y

    def load_record(self):
        """Load ECG record from WFDB format"""
        if not self.record_path:
            print("No record path specified")
            return None
            
        try:
            sig, fields = wfdb.rdsamp(self.record_path)
            fs = fields['fs']
            rhythm_type = fields['comments']

            return {
                'signal': sig,
                'fs': fs,
                'rhythm_type': rhythm_type,
                'fields': fields
            }
        except Exception as e:
            print(f"Error loading record: {e}")
            return None

    def load_annotation(self):
        """Load annotations from WFDB format"""
        if self.annotation_path:
            try:
                annotation = wfdb.rdann(self.annotation_path, 'atr')
                return annotation
            except Exception as e:
                print(f"Error loading annotation: {e}")
                return None
        return None

    def wfdb_wrap(self, sig, raw_fs, target_fs, beat_location=None, annotation=None):
        """Process signal and create data structure"""
        if beat_location is not None:
            beat_loc = np.array(beat_location).astype(int)
        else:
            beat_loc = None
        
        sig = np.array(sig)
        if raw_fs != target_fs:
            sig = self.resample(sig, raw_fs, target_fs)

        data = {
            'signal': sig,
            'fs': target_fs,
            'beat_location': beat_loc,
            'annotation': annotation
        }
        
        return data

    def write_record(self, record_name, signal, fs, units=None, sig_name=None, comments=None):
        """Write ECG signal to WFDB format"""
        if signal.ndim == 1:
            signal = signal.reshape(-1, 1)
            
        if units is None:
            units = ['mV'] * signal.shape[1]
        
        if sig_name is None:
            sig_name = [f'Lead_{i}' for i in range(signal.shape[1])]
        
        try:
            wfdb.wrsamp(record_name, fs=fs, units=units, sig_name=sig_name, 
                       p_signal=signal, comments=comments)
            print(f"Record '{record_name}' written successfully")
        except Exception as e:
            print(f"Error writing record: {e}")

    def write_annotation(self, record_name, ann_extension, sample_positions, symbols, comments=None):
        """Write annotations to WFDB format"""
        try:
            sample_positions = np.array(sample_positions, dtype=int)
            symbols = np.array(symbols)
            
            if comments is not None:
                comments = np.array(comments, dtype=str)
            
            wfdb.wrann(record_name, ann_extension, sample_positions, symbols, aux_note=comments)
            print(f"Annotations '{record_name}.{ann_extension}' written successfully")
        except Exception as e:
            print(f"Error writing annotation: {e}")

    def write_ecg_with_annotations(self, record_name, signal, fs, annotations=None, 
                                 units=None, sig_name=None, comments=None):
        """Write ECG record with global annotations to WFDB format
        
        Parameters:
        - record_name: Name of the record (without extension)
        - signal: ECG signal array (samples x leads) or (samples,) for single lead
        - fs: Sampling frequency
        - annotations: Dict with 'positions', 'symbols', and optionally 'comments'
        - units: Units for each signal (default: ['mV'])
        - sig_name: Names for each signal/lead
        - comments: Comments for the record
        """
        # Write the signal
        self.write_record(record_name, signal, fs, units, sig_name, comments)
        
        # Write annotations if provided
        if annotations:
            positions = annotations.get('positions', [])
            symbols = annotations.get('symbols', [])
            ann_comments = annotations.get('comments', None)
            
            if positions and symbols:
                self.write_annotation(record_name, 'atr', positions, symbols, ann_comments)
            else:
                print("Warning: Annotations provided but missing positions or symbols")

    def save_to_json(self, data, filename):
        """Save data to JSON file"""
        try:
            # Convert numpy arrays to lists for JSON serialization
            if isinstance(data, dict):
                json_data = {}
                for key, value in data.items():
                    if isinstance(value, np.ndarray):
                        json_data[key] = value.tolist()
                    else:
                        json_data[key] = value
            else:
                json_data = data
                
            with open(filename, 'w') as f:
                json.dump(json_data, f, indent=2)
            print(f"Data saved to {filename}")
        except Exception as e:
            print(f"Error saving to JSON: {e}")

    def load_from_json(self, filename):
        """Load data from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            print(f"Data loaded from {filename}")
            return data
        except Exception as e:
            print(f"Error loading from JSON: {e}")
            return None