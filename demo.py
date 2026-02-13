#!/usr/bin/env python3
"""
Demo script for WiFi Radar - generates simulated data for testing
This allows testing the system without actual WiFi monitor mode
"""

import time
import numpy as np
from feature_extraction import FeatureExtractor
from spatial_model import SpatialModel
from heatmap_visualizer import HeatmapVisualizer

def generate_simulated_packets(num_packets=50, with_motion=True):
    """Generate simulated packet data"""
    packets = []
    base_rssi = -50
    
    for i in range(num_packets):
        # Simulate motion by adding variance
        if with_motion:
            rssi = base_rssi + np.random.normal(0, 5)
        else:
            rssi = base_rssi + np.random.normal(0, 1)
        
        packet = {
            'timestamp': time.time(),
            'bssid': 'AA:BB:CC:DD:EE:FF',
            'rssi': rssi,
            'phase': np.random.uniform(0, 2 * np.pi),
            'type': 0,
            'subtype': 8,
            'packet': None
        }
        packets.append(packet)
        time.sleep(0.01)  # Small delay
    
    return packets


def demo_feature_extraction():
    """Demo feature extraction"""
    print("\n=== Feature Extraction Demo ===")
    
    extractor = FeatureExtractor()
    
    print("\n1. Packets WITHOUT motion:")
    packets_static = generate_simulated_packets(50, with_motion=False)
    features_static = extractor.extract_features(packets_static)
    print(f"  RSSI Variance: {features_static['rssi_variance']:.3f}")
    print(f"  FFT Energy: {features_static['fft_energy']:.3f}")
    
    print("\n2. Packets WITH motion:")
    packets_motion = generate_simulated_packets(50, with_motion=True)
    features_motion = extractor.extract_features(packets_motion)
    print(f"  RSSI Variance: {features_motion['rssi_variance']:.3f}")
    print(f"  FFT Energy: {features_motion['fft_energy']:.3f}")
    
    disturbance_static = extractor.extract_disturbance_score(features_static)
    disturbance_motion = extractor.extract_disturbance_score(features_motion)
    
    print(f"\n3. Disturbance Scores:")
    print(f"  Static: {disturbance_static:.3f}")
    print(f"  Motion: {disturbance_motion:.3f}")
    print(f"  Ratio: {disturbance_motion/max(disturbance_static, 0.001):.2f}x")


def demo_spatial_model():
    """Demo spatial model"""
    print("\n=== Spatial Model Demo ===")
    
    model = SpatialModel(grid_size=(10, 10), bin_duration=0.5)
    
    print("\n1. Simulating motion events...")
    # Simulate several motion events
    for i in range(10):
        # Varying disturbance levels
        disturbance = np.random.uniform(0.2, 0.8) if i % 2 == 0 else 0.1
        model.update_grid(disturbance)
        time.sleep(0.1)
    
    stats = model.get_statistics()
    print(f"\n2. Grid Statistics:")
    print(f"  Max Value: {stats['max_value']:.3f}")
    print(f"  Mean Value: {stats['mean_value']:.3f}")
    print(f"  Active Cells: {stats['active_cells']}")
    
    grid = model.get_grid()
    print(f"\n3. Grid Sample (top-left 3x3):")
    print(grid[:3, :3])


def demo_visualization():
    """Demo live visualization with simulated data"""
    print("\n=== Live Visualization Demo ===")
    print("Close the plot window to end demo\n")
    
    # Create components
    extractor = FeatureExtractor()
    model = SpatialModel(grid_size=(10, 10), bin_duration=0.5)
    visualizer = HeatmapVisualizer(
        grid_size=(10, 10),
        update_interval=200,  # 200ms updates
        colormap='hot',
        figsize=(10, 8)
    )
    
    # Shared state
    state = {'iteration': 0}
    
    def get_data():
        """Generate and process simulated data"""
        state['iteration'] += 1
        
        # Generate packets (alternate between motion and static)
        has_motion = (state['iteration'] % 10) < 7  # 70% motion, 30% static
        packets = generate_simulated_packets(30, with_motion=has_motion)
        
        # Extract features
        features = extractor.extract_features(packets)
        disturbance = extractor.extract_disturbance_score(features)
        
        # Update spatial model
        model.update_grid(disturbance)
        
        # Get grid and stats
        grid = model.get_grid()
        stats = model.get_statistics()
        stats['packet_count'] = len(packets)
        
        return grid, stats
    
    # Set callback and start
    visualizer.set_data_callback(get_data)
    
    print("Starting visualization...")
    print("You should see a heatmap with changing patterns")
    print("representing simulated motion detection")
    
    visualizer.start()


def main():
    """Run all demos"""
    print("="*60)
    print("WiFi Radar - Demo & Test Script")
    print("="*60)
    
    # Feature extraction demo
    demo_feature_extraction()
    
    # Spatial model demo
    demo_spatial_model()
    
    # Ask user before starting visualization
    print("\n" + "="*60)
    response = input("\nRun live visualization demo? (y/n): ")
    if response.lower() == 'y':
        demo_visualization()
    
    print("\n" + "="*60)
    print("Demo complete!")
    print("="*60)


if __name__ == '__main__':
    main()
