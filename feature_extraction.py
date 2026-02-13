"""
Feature Extraction Module
Extracts motion-sensitive features from WiFi packets
"""

import numpy as np
import logging
from scipy.fft import fft
from collections import defaultdict

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extract features from WiFi packets for motion detection"""
    
    def __init__(self):
        """Initialize feature extractor"""
        self.previous_features = {}
        self.history = defaultdict(lambda: {
            'rssi': [],
            'phase': [],
            'timestamps': []
        })
        
    def extract_features(self, packets):
        """
        Extract features from packet list
        
        Args:
            packets: List of packet information dictionaries
            
        Returns:
            Dictionary of extracted features
        """
        if not packets:
            return {
                'rssi_mean': 0.0,
                'rssi_variance': 0.0,
                'phase_variance': 0.0,
                'fft_energy': 0.0,
                'phase_delta': 0.0,
                'packet_count': 0
            }
        
        # Extract RSSI values
        rssi_values = [p['rssi'] for p in packets if p['rssi'] is not None]
        
        # Extract phase values (use timestamp as proxy if phase not available)
        phase_values = []
        for p in packets:
            if p['phase'] is not None:
                phase_values.append(p['phase'])
            else:
                # Use timestamp modulo as phase proxy
                phase_values.append((p['timestamp'] % 1.0) * 2 * np.pi)
        
        # Calculate RSSI features
        rssi_mean = np.mean(rssi_values) if rssi_values else 0.0
        rssi_variance = np.var(rssi_values) if rssi_values else 0.0
        
        # Calculate phase features
        phase_variance = np.var(phase_values) if phase_values else 0.0
        
        # Calculate FFT energy change
        fft_energy = self._calculate_fft_energy(rssi_values)
        
        # Calculate phase delta (change from previous)
        phase_delta = self._calculate_phase_delta(phase_values)
        
        features = {
            'rssi_mean': float(rssi_mean),
            'rssi_variance': float(rssi_variance),
            'phase_variance': float(phase_variance),
            'fft_energy': float(fft_energy),
            'phase_delta': float(phase_delta),
            'packet_count': len(packets)
        }
        
        # Store for next iteration
        self.previous_features = features.copy()
        
        return features
    
    def _calculate_fft_energy(self, values):
        """Calculate FFT energy from signal values"""
        if len(values) < 2:
            return 0.0
        
        try:
            # Perform FFT
            values_array = np.array(values)
            fft_result = fft(values_array)
            
            # Calculate energy (sum of squared magnitudes)
            energy = np.sum(np.abs(fft_result) ** 2)
            
            # Normalize by length
            energy = energy / len(values)
            
            return float(energy)
        except Exception as e:
            logger.debug(f"FFT calculation error: {e}")
            return 0.0
    
    def _calculate_phase_delta(self, phase_values):
        """Calculate phase change from previous measurement"""
        if not phase_values:
            return 0.0
        
        current_mean = np.mean(phase_values)
        
        if 'phase_mean' in self.previous_features:
            previous_mean = self.previous_features.get('phase_mean', current_mean)
            delta = abs(current_mean - previous_mean)
        else:
            delta = 0.0
        
        # Store for next iteration
        self.previous_features['phase_mean'] = current_mean
        
        return float(delta)
    
    def extract_disturbance_score(self, features):
        """
        Calculate overall disturbance score from features
        
        Args:
            features: Dictionary of feature values
            
        Returns:
            Normalized disturbance score (0-1)
        """
        # Weight different features for motion sensitivity
        score = 0.0
        
        # RSSI variance indicates signal fluctuation (motion)
        score += features['rssi_variance'] * 0.3
        
        # Phase variance indicates multipath changes (motion)
        score += features['phase_variance'] * 0.2
        
        # FFT energy indicates temporal changes
        score += features['fft_energy'] * 0.3
        
        # Phase delta indicates phase shift over time
        score += features['phase_delta'] * 0.2
        
        # Normalize to 0-1 range (heuristic scaling)
        score = min(score / 100.0, 1.0)
        
        return float(score)
