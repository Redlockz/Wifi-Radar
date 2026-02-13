"""
Heatmap Visualization Module
Live matplotlib heatmap for motion detection
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
import logging

logger = logging.getLogger(__name__)


class HeatmapVisualizer:
    """Live heatmap visualization using matplotlib"""
    
    def __init__(self, grid_size=(10, 10), update_interval=500, 
                 colormap='hot', figsize=(10, 8)):
        """
        Initialize heatmap visualizer
        
        Args:
            grid_size: Tuple of (rows, cols) for grid dimensions
            update_interval: Update interval in milliseconds
            colormap: Matplotlib colormap name
            figsize: Figure size (width, height)
        """
        self.grid_size = grid_size
        self.update_interval = update_interval
        self.colormap = colormap
        self.figsize = figsize
        
        # Initialize figure and axis
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.fig.suptitle('WiFi Passive Motion Detection Heatmap', 
                         fontsize=16, fontweight='bold')
        
        # Initialize heatmap
        self.grid_data = np.zeros(grid_size)
        self.im = self.ax.imshow(self.grid_data, cmap=colormap, 
                                 interpolation='bilinear',
                                 vmin=0, vmax=1, aspect='auto')
        
        # Add colorbar
        self.cbar = self.fig.colorbar(self.im, ax=self.ax, 
                                     label='Disturbance Level')
        
        # Configure axes
        self.ax.set_xlabel('X Position', fontsize=12)
        self.ax.set_ylabel('Y Position', fontsize=12)
        self.ax.set_title('Motion Activity', fontsize=14)
        
        # Add grid
        self.ax.grid(True, alpha=0.3, linestyle='--')
        
        # Statistics text
        self.stats_text = self.ax.text(0.02, 0.98, '', 
                                       transform=self.ax.transAxes,
                                       verticalalignment='top',
                                       fontsize=10,
                                       bbox=dict(boxstyle='round', 
                                               facecolor='wheat', 
                                               alpha=0.8))
        
        # Animation object
        self.anim = None
        self.running = False
        
        # Data update callback
        self.data_callback = None
        
    def set_data_callback(self, callback):
        """
        Set callback function to get updated grid data
        
        Args:
            callback: Function that returns grid data and statistics dict
        """
        self.data_callback = callback
    
    def _update_frame(self, frame):
        """Update animation frame"""
        if self.data_callback:
            try:
                # Get new data from callback
                grid_data, stats = self.data_callback()
                
                # Update heatmap
                self.im.set_array(grid_data)
                
                # Update statistics text
                stats_str = (
                    f"Max: {stats.get('max_value', 0):.3f}\n"
                    f"Mean: {stats.get('mean_value', 0):.3f}\n"
                    f"Active Cells: {stats.get('active_cells', 0)}\n"
                    f"Packets: {stats.get('packet_count', 0)}"
                )
                self.stats_text.set_text(stats_str)
                
            except Exception as e:
                logger.error(f"Error updating frame: {e}")
        
        return [self.im, self.stats_text]
    
    def start(self):
        """Start live visualization"""
        if self.running:
            logger.warning("Visualization already running")
            return
        
        self.running = True
        logger.info("Starting heatmap visualization")
        
        # Create animation
        self.anim = animation.FuncAnimation(
            self.fig,
            self._update_frame,
            interval=self.update_interval,
            blit=True,
            cache_frame_data=False
        )
        
        # Show plot
        plt.show(block=True)
    
    def stop(self):
        """Stop visualization"""
        logger.info("Stopping visualization")
        self.running = False
        if self.anim:
            self.anim.event_source.stop()
        plt.close(self.fig)
    
    def save_snapshot(self, filename='heatmap_snapshot.png'):
        """
        Save current heatmap to file
        
        Args:
            filename: Output filename
        """
        try:
            self.fig.savefig(filename, dpi=150, bbox_inches='tight')
            logger.info(f"Saved snapshot to {filename}")
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")
