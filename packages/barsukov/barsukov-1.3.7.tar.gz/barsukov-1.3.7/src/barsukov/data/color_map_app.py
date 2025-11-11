import sys
import os
import argparse
import numpy as np

try:
    from PyQt5 import QtCore, QtWidgets
except ImportError:
    from PySide6 import QtCore, QtWidgets

from color_map_core import (
    DataLoader,
    DEFAULT_XY_FILE,
    DEFAULT_Z_FILE,
    DEFAULT_CMAP
)

from color_map_widget import InteractiveHeatmapWidget


def build_arg_parser():
    """Build command line argument parser"""
    p = argparse.ArgumentParser(
        description="Interactive heatmap viewer (CSV/TSV/space-delimited supported)."
    )
    p.add_argument("--xy", dest="xy_file", default=DEFAULT_XY_FILE,
                   help="Path to XY file (X,Y vectors; header optional).")
    p.add_argument("--z", dest="z_file", default=DEFAULT_Z_FILE,
                   help="Path to Z matrix file (rows form image lines).")
    p.add_argument("--x-col", type=int, default=1,
                   help="Zero-based column index to use for X (default: 1).")
    p.add_argument("--y-col", type=int, default=0,
                   help="Zero-based column index to use for Y (default: 0).")
    p.add_argument("--cmap", default=DEFAULT_CMAP,
                   help="Colormap to use (e.g., viridis, plasma, inferno, magma, cividis, gray, jet).")
    return p


def main():
    """Main CLI entry point"""
    # Parse command line arguments
    parser = build_arg_parser()
    args = parser.parse_args()
    
    # Load data with data loader
    loader = DataLoader()
    
    # Use command line arguments
    xy_file = args.xy_file
    z_file = args.z_file
    x_col = args.x_col
    y_col = args.y_col
    cmap = args.cmap
    
    try:
        # Check if file exists and detect columns
        if os.path.exists(xy_file):
            num_cols, col_names = loader.detect_columns(xy_file)
            if num_cols > 0:
                # Load with specified columns
                y, x = loader.load_xy_data(xy_file, x_col=x_col, y_col=y_col)
                # Use column names for labels if available
                if col_names and len(col_names) > max(x_col, y_col):
                    x_label = f'X ({col_names[x_col]})'
                    y_label = f'Y ({col_names[y_col]})'
                else:
                    x_label = 'X'
                    y_label = 'Y'
            else:
                raise ValueError("No columns detected")
        else:
            raise FileNotFoundError(f"{xy_file} not found")
            
        Z = loader.load_matrix_data(z_file)
    except Exception as e:
        print(f"Error loading files: {e}")
        print("Creating demo data...")
        # Create demo data if files not found
        x = np.linspace(0, 10, 100)
        y = np.linspace(0, 10, 100)
        xx, yy = np.meshgrid(x, y)
        Z = np.sin(xx) * np.cos(yy)
        x_label = 'X'
        y_label = 'Y'
    
    # Calculate ranges
    xmin, xmax = float(np.nanmin(x)), float(np.nanmax(x))
    ymin, ymax = float(np.nanmin(y)), float(np.nanmax(y))
    
    # Create the app
    app = QtWidgets.QApplication.instance()
    created_app = False
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
        created_app = True
        # Enable high DPI support
        try:
            app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
            app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
        except:
            pass  # Older Qt version
    
    # Initial vmin/vmax from data
    vmin = float(np.nanmin(Z))
    vmax = float(np.nanmax(Z))
    
    # Create widget
    win = InteractiveHeatmapWidget(
        data=Z,
        x_range=(xmin, xmax),
        y_range=(ymin, ymax),
        x_label=x_label,
        y_label=y_label,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax
    )
    
    win.show()
    
    # For CLI, run the event loop
    if created_app:
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()
