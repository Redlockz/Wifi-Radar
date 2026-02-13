"""
Spatial Model Module
Maps WiFi disturbances to 2D spatial grid
"""

import numpy as np
import logging
from collections import deque
import time

logger = logging.getLogger(__name__)


class SpatialModel:
    """2D spatial grid model for motion heatmap"""
    
    def __init__(self, grid_size=(10, 10), bin_duration=1.0, normalize=True):
        """
        Initialize spatial model
        
        Args:
            grid_size: Tuple of (rows, cols) for grid dimensions
            bin_duration: Time duration for accumulating disturbances (seconds)
            normalize: Whether to normalize grid values to 0-1
        """
        self.grid_size = grid_size
        self.bin_duration = bin_duration
        self.normalize = normalize
        
        # Initialize grid
        self.grid = np.zeros(grid_size)
        
        # History of disturbance scores
        self.disturbance_history = deque(maxlen=1000)
        self.last_bin_time = time.time()
        self.current_bin_scores = []
        
    def update_grid(self, disturbance_score):
        """
        Update grid with new disturbance score
        
        Args:
            disturbance_score: Overall disturbance score (0-1)
        """
        current_time = time.time()
        
        # Add to current bin
        self.current_bin_scores.append(disturbance_score)
        
        # Check if bin duration has elapsed
        if current_time - self.last_bin_time >= self.bin_duration:
            self._update_grid_from_bin()
            self.last_bin_time = current_time
            self.current_bin_scores = []
    
    def _update_grid_from_bin(self):
        """Update grid based on accumulated bin scores"""
        if not self.current_bin_scores:
            return
        
        # Calculate average disturbance for this bin
        avg_disturbance = np.mean(self.current_bin_scores)
        
        # Store in history
        self.disturbance_history.append(avg_disturbance)
        
        # Update grid with spatial distribution
        # For passive sensing, we distribute the disturbance across the grid
        # with some randomness to simulate spatial uncertainty
        self._distribute_disturbance(avg_disturbance)
    
    def _distribute_disturbance(self, disturbance):
        """
        Distribute disturbance score across grid
        
        Args:
            disturbance: Disturbance score to distribute
        """
        # Create a disturbance pattern
        # In a real system, this would use spatial information from multiple APs
        # For PoC, we'll create a pattern that shows activity
        
        rows, cols = self.grid_size
        
        # Decay existing values
        self.grid *= 0.95
        
        # Add new disturbance with spatial pattern
        if disturbance > 0.1:  # Threshold for significant activity
            # Create center point with some randomness
            center_row = np.random.randint(0, rows)
            center_col = np.random.randint(0, cols)
            
            # Create Gaussian-like distribution around center
            for i in range(rows):
                for j in range(cols):
                    # Distance from center
                    dist = np.sqrt((i - center_row)**2 + (j - center_col)**2)
                    
                    # Gaussian decay
                    influence = disturbance * np.exp(-dist**2 / (2 * 2**2))
                    
                    # Add to grid
                    self.grid[i, j] += influence
        
        # Normalize if enabled
        if self.normalize and np.max(self.grid) > 0:
            self.grid = self.grid / np.max(self.grid)
    
    def get_grid(self):
        """
        Get current grid state
        
        Returns:
            2D numpy array representing the heatmap
        """
        return self.grid.copy()
    
    def reset_grid(self):
        """Reset grid to zeros"""
        self.grid = np.zeros(self.grid_size)
        self.disturbance_history.clear()
        self.current_bin_scores = []
        self.last_bin_time = time.time()
    
    def get_statistics(self):
        """
        Get statistics about the spatial model
        
        Returns:
            Dictionary of statistics
        """
        return {
            'grid_size': self.grid_size,
            'max_value': float(np.max(self.grid)),
            'mean_value': float(np.mean(self.grid)),
            'active_cells': int(np.sum(self.grid > 0.1)),
            'history_length': len(self.disturbance_history)
        }
