import math
import os
from functools import lru_cache
import numpy as np

try:
    from PyQt5 import QtCore, QtGui, QtWidgets
    Signal = QtCore.pyqtSignal
except ImportError:
    from PySide6 import QtCore, QtGui, QtWidgets
    Signal = QtCore.Signal

import pyqtgraph as pg
import pyqtgraph.exporters

from color_map_core import (
    DEFAULT_KC,
    DEFAULT_KB,
    DEFAULT_CMAP,
    calculate_effective_range
)

# ---------------------------
# UI CONSTANTS
# ---------------------------
CONTROL_PAD_SIZE = 250


# ---------------------------
# CONTROL PAD WIDGET
# ---------------------------
class ControlPad(QtWidgets.QWidget):
    """Simplified interactive control pad for brightness and contrast adjustment"""
    
    changeRequested = Signal(float, float)  # (contrast_factor, brightness_delta)
    
    # Class constants
    MIN_MOVEMENT_THRESHOLD = 1
    WHEEL_FACTOR_UP = 0.9
    WHEEL_FACTOR_DOWN = 1.0 / 0.9
    MARKER_NUDGE = 0.02
    
    def __init__(self, parent=None, kc=DEFAULT_KC, kb=DEFAULT_KB, span=1.0):
        super().__init__(parent)
        self.setMinimumSize(CONTROL_PAD_SIZE, CONTROL_PAD_SIZE)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        self.kc = kc
        self.kb = kb
        self.span = span
        
        # State tracking
        self._dragging = False
        self._button = None
        self._x0 = 0
        self._y0 = 0
        
        # Position markers (0-1 normalized)
        self._u = 0.5
        self._v = 0.5
        
        # Current absolute values for display
        self.current_contrast = 1.0
        self.current_brightness = 0.0
        
        # Accent color
        self.accent = QtGui.QColor(210, 210, 210)
    
    def sizeHint(self):
        return QtCore.QSize(CONTROL_PAD_SIZE, CONTROL_PAD_SIZE)
    
    @lru_cache(maxsize=128)
    def _calculate_marker_position(self, brightness, contrast):
        """Cached calculation of marker position from values"""
        u = np.clip(0.5 + brightness / max(1e-9, self.span), 0.0, 1.0)
        v = 0.5
        if contrast > 0:
            v = np.clip(0.5 - math.log(contrast) / (2 * max(1e-9, abs(self.kc))), 0.0, 1.0)
        return u, v
    
    def updateValues(self, contrast, brightness):
        """Update displayed values from external source"""
        self.current_contrast = contrast
        self.current_brightness = brightness
        
        # Use cached calculation
        self._u, self._v = self._calculate_marker_position(brightness, contrast)
        self.update()
    
    def mousePressEvent(self, event):
        if event.button() in (QtCore.Qt.LeftButton, QtCore.Qt.RightButton):
            self._dragging = True
            self._button = event.button()
            self._x0, self._y0 = event.x(), event.y()
            self._updateMarker(event.x(), event.y())
            self.update()
    
    def mouseMoveEvent(self, event):
        if not self._dragging:
            return
        
        dx = event.x() - self._x0
        dy = event.y() - self._y0
        
        # Skip tiny movements
        if abs(dx) < self.MIN_MOVEMENT_THRESHOLD and abs(dy) < self.MIN_MOVEMENT_THRESHOLD:
            return
        
        contrast_factor = 1.0
        brightness_delta = 0.0
        
        if self._button == QtCore.Qt.LeftButton:
            # X axis controls brightness, Y axis controls contrast
            contrast_factor = math.exp(self.kc * dy)
            brightness_delta = self.kb * dx * self.span
        elif self._button == QtCore.Qt.RightButton:
            brightness_delta = -self.kb * dy * self.span
        
        self._x0, self._y0 = event.x(), event.y()
        self._updateMarker(event.x(), event.y())
        
        # Update current values
        self.current_contrast *= contrast_factor
        self.current_brightness += brightness_delta
        
        # Clear cache when values change
        self._calculate_marker_position.cache_clear()
        
        self.update()
        self.changeRequested.emit(contrast_factor, brightness_delta)
    
    def mouseReleaseEvent(self, event):
        self._dragging = False
        self._button = None
        self.update()
    
    def mouseDoubleClickEvent(self, event):
        """Reset on double-click"""
        old_contrast = self.current_contrast
        old_brightness = self.current_brightness
        
        self._u = 0.5
        self._v = 0.5
        self.current_contrast = 1.0
        self.current_brightness = 0.0
        
        # Clear cache
        self._calculate_marker_position.cache_clear()
        
        self.update()
        # Emit the change needed to reset
        if old_contrast != 0:
            self.changeRequested.emit(1.0 / old_contrast, -old_brightness)
    
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        factor = self.WHEEL_FACTOR_UP if delta > 0 else self.WHEEL_FACTOR_DOWN
        self.current_contrast *= factor
        self.changeRequested.emit(factor, 0.0)
        
        self._v = np.clip(self._v + (-self.MARKER_NUDGE if delta > 0 else self.MARKER_NUDGE), 0.0, 1.0)
        self.update()
    
    def _updateMarker(self, x, y):
        w = max(1, self.width())
        h = max(1, self.height())
        self._u = np.clip(x / w, 0.0, 1.0)
        self._v = np.clip(y / h, 0.0, 1.0)
    
    def paintEvent(self, event):
        """Simplified paint event"""
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        
        rect = self.rect().adjusted(8, 8, -8, -8)
        w = rect.width()
        h = rect.height()
        
        # Simple background
        p.fillRect(rect, QtGui.QColor(30, 30, 35))
        
        # Center lines
        pen_center = QtGui.QPen(QtGui.QColor(100, 100, 110), 2, QtCore.Qt.SolidLine)
        p.setPen(pen_center)
        cx_line = rect.left() + w / 2
        cy_line = rect.top() + h / 2
        p.drawLine(int(cx_line), rect.top(), int(cx_line), rect.bottom())
        p.drawLine(rect.left(), int(cy_line), rect.right(), int(cy_line))
        
        # Current position marker
        cx = rect.left() + int(self._u * w)
        cy = rect.top() + int(self._v * h)
        
        # Crosshair lines
        p.setPen(QtGui.QPen(QtGui.QColor(self.accent.red(), self.accent.green(), 
                                         self.accent.blue(), 60), 1))
        p.drawLine(cx, rect.top(), cx, rect.bottom())
        p.drawLine(rect.left(), cy, rect.right(), cy)
        
        # Marker circle
        pen_marker = QtGui.QPen(self.accent, 2)
        brush_marker = QtGui.QBrush(QtGui.QColor(self.accent.red(), self.accent.green(), 
                                                 self.accent.blue(), 200))
        p.setPen(pen_marker)
        p.setBrush(brush_marker)
        p.drawEllipse(QtCore.QPoint(cx, cy), 6, 6)
        
        # Labels
        p.setPen(QtGui.QColor(200, 200, 210))
        font = QtGui.QFont("Arial", 10, QtGui.QFont.Bold)
        p.setFont(font)
        p.drawText(QtCore.QRect(12, 12, w - 24, 30),
                  QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft,
                  " CONTROL PAD")
        p.drawText(QtCore.QRect(12, h - 30, w - 24, 25),
                  QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft,
                  "← Brightness →")
        
        # Rotated text
        p.save()
        p.translate(15, rect.center().y())
        p.rotate(-90)
        p.drawText(QtCore.QRect(-40, -10, 80, 20),
                  QtCore.Qt.AlignCenter,
                  "Contrast")
        p.restore()
        
        # Current values box
        font.setPointSize(9)
        p.setFont(font)
        value_rect = QtCore.QRect(w - 95, h - 50, 85, 40)
        p.fillRect(value_rect, QtGui.QColor(20, 20, 25, 200))
        p.setPen(QtGui.QColor(100, 100, 110))
        p.drawRect(value_rect)
        p.setPen(QtGui.QColor(255, 255, 255))
        p.drawText(value_rect.adjusted(5, 3, -5, -3),
                  QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop,
                  f"C: {self.current_contrast:.3f}\nB: {self.current_brightness:+.3f}")
        
        # Border
        pen_border = QtGui.QPen(QtGui.QColor(80, 80, 90), 2)
        p.setPen(pen_border)
        p.drawRect(rect)


# ---------------------------
# MAIN WIDGET
# ---------------------------
class InteractiveHeatmapWidget(QtWidgets.QMainWindow):
    """Reusable interactive heatmap widget for notebooks and scripts"""
    
    # Class constants
    DEFAULT_WIDTH = 1200
    DEFAULT_HEIGHT = 750
    
    def __init__(self, data, x_range, y_range, x_label='X', y_label='Y', 
                 cmap=DEFAULT_CMAP, vmin=None, vmax=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Interactive Heatmap Viewer")
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        
        # Apply dark theme
        self._apply_dark_theme()
        
        # Initialize data
        self.data = np.asarray(data, dtype=np.float64)
        # Replace any NaN values to avoid rendering issues
        self.data = np.nan_to_num(self.data, copy=False, nan=0.0)
        if vmin is None: 
            vmin = float(np.nanmin(self.data))
        if vmax is None: 
            vmax = float(np.nanmax(self.data))
        self.base_vmin = float(vmin)
        self.base_vmax = float(vmax)
        self.span = max(1e-12, self.base_vmax - self.base_vmin)
        
        self.contrast = 1.0
        self.brightness = 0.0
        self.kc = DEFAULT_KC
        self.kb = DEFAULT_KB
        self.cmap = cmap

        self.xmin, self.xmax = map(float, x_range)
        self.ymin, self.ymax = map(float, y_range)
        self.x_label = x_label
        self.y_label = y_label
        
        # Setup UI
        self._setup_ui()
    
    def _apply_dark_theme(self):
        """Apply dark theme styling"""
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QLabel { color: #e0e0e0; }
            QPushButton {
                background-color: #3a3a3a; color: #e0e0e0;
                border: 1px solid #555; padding: 6px 12px; border-radius: 4px;
            }
            QPushButton:hover { background-color: #4a4a4a; }
            QPushButton:pressed { background-color: #2a2a2a; }
        """)
    
    def _create_left_panel(self):
        """Create left control panel"""
        left_panel = QtWidgets.QVBoxLayout()
        left_panel.setSpacing(10)
        
        title_label = QtWidgets.QLabel("Interactive Controls")
        title_font = QtGui.QFont("Arial", 12, QtGui.QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        left_panel.addWidget(title_label)
        
        self.pad = ControlPad(kc=self.kc, kb=self.kb, span=self.span)
        self.pad.changeRequested.connect(self._apply_pad_change)
        left_panel.addWidget(self.pad, 0, QtCore.Qt.AlignTop)
        
        instructions = QtWidgets.QLabel(
            "Controls:\n"
            "• Drag: Adjust brightness (X) and contrast (Y)\n"
            "• Scroll: Fine-tune contrast\n"
            "• Double-click: Reset to default\n"
            "• R key: Reset values\n"
            "• S key: Save image"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("font-size: 10px; color: #c0c0c0; padding: 10px;")
        left_panel.addWidget(instructions)
        
        reset_btn = QtWidgets.QPushButton("Reset All Values")
        reset_btn.clicked.connect(self.reset_values)
        left_panel.addWidget(reset_btn)
        
        self.stats_label = QtWidgets.QLabel()
        self.stats_label.setStyleSheet("font-size: 10px; color: #a0a0a0; padding: 5px;")
        self._update_stats()
        left_panel.addWidget(self.stats_label)
        
        left_panel.addStretch()
        return left_panel
    
    def _create_right_panel(self):
        """Create right visualization panel"""
        right_panel = QtWidgets.QVBoxLayout()
        
        self.info = QtWidgets.QLabel(self._fmt_info())
        info_font = QtGui.QFont("Consolas", 11)
        self.info.setFont(info_font)
        self.info.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                color: #00ff88;
                padding: 8px;
                border: 1px solid #404040;
                border-radius: 4px;
            }
        """)
        right_panel.addWidget(self.info)
        
        self.graph = pg.GraphicsLayoutWidget()
        self.graph.setBackground('#1e1e1e')
        right_panel.addWidget(self.graph, 1)
        
        # Graph 1:
        self.plot = self.graph.addPlot(row=0, col=0)
        self.plot.setAspectLocked(False)
        self.plot.setLabel('left', self.y_label)
        self.plot.setLabel('bottom', self.x_label)
        
        # Enable OpenGL for better performance with large datasets
        try:
            self.plot.enableGL()
        except:
            pass  # OpenGL not available
        
        # Image item
        clean_data = np.nan_to_num(self.data, copy=True, nan=0.0)
        self.img_item = pg.ImageItem(clean_data, axisOrder='row-major')
        self.img_item.setOpts(axisOrder='row-major')
        self.img_item.setAutoDownsample(False)
        
        self.plot.addItem(self.img_item)

        # Map image to real-world X/Y
        rect = QtCore.QRectF(self.xmin, self.ymin, 
                            (self.xmax - self.xmin), 
                            (self.ymax - self.ymin))
        self.img_item.setRect(rect)

        # Set view
        self.plot.setXRange(self.xmin, self.xmax, padding=0.0)
        self.plot.setYRange(self.ymin, self.ymax, padding=0.0)
        
        # Colormap and colorbar
        try:
            cm = pg.colormap.get(self.cmap)
        except Exception:
            cm = pg.colormap.get('viridis')
        self.lut = cm.getLookupTable(0.0, 1.0, 256)
        self.img_item.setLookupTable(self.lut)
        
        self.cbar = pg.ColorBarItem(
            values=(self.base_vmin, self.base_vmax),
            colorMap=cm,
            width=20
        )
        self.cbar.setImageItem(self.img_item)
        self.graph.addItem(self.cbar, row=0, col=1)
        
        # Interactions
        self.plot.scene().sigMouseClicked.connect(self._on_plot_click)
        
        return right_panel
    
    def _setup_ui(self):
        """Setup UI components"""
        cw = QtWidgets.QWidget(self)
        self.setCentralWidget(cw)
        main_layout = QtWidgets.QHBoxLayout(cw)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Left panel
        left_panel = self._create_left_panel()
        main_layout.addLayout(left_panel)

        # Right panel with pyqtgraph
        right_panel = self._create_right_panel()
        right_container = QtWidgets.QWidget()
        right_container.setLayout(right_panel)
        main_layout.addWidget(right_container, 1)
        
        self._apply_levels()
    
    @lru_cache(maxsize=256)
    def _calculate_effective_range(self, vmin, vmax, brightness, contrast):
        """Cached calculation of effective range"""
        return calculate_effective_range(vmin, vmax, brightness, contrast)
    
    def _fmt_info(self):
        vmin_p, vmax_p = self._calculate_effective_range(
            self.base_vmin, self.base_vmax, self.brightness, self.contrast
        )
        return (f"Contrast: {self.contrast:.3f}  |  "
                f"Brightness: {self.brightness:+.3f}  |  "
                f"Effective Range: [{vmin_p:.3f}, {vmax_p:.3f}]")
    
    def _update_stats(self):
        if self.data.size > 0:
            # Use cached statistics if available
            if not hasattr(self, '_stats_cache'):
                self._stats_cache = {
                    'min': np.nanmin(self.data),
                    'max': np.nanmax(self.data),
                    'mean': np.nanmean(self.data),
                    'std': np.nanstd(self.data)
                }
            
            stats_text = (
                f"Data Statistics:\n"
                f"Shape: {self.data.shape}\n"
                f"Min: {self._stats_cache['min']:.6g}\n"
                f"Max: {self._stats_cache['max']:.6g}\n"
                f"Mean: {self._stats_cache['mean']:.6g}\n"
                f"Std: {self._stats_cache['std']:.6g}\n"
                f"Memory: {self.data.nbytes / 1024 / 1024:.1f} MB"
            )
            self.stats_label.setText(stats_text)
    
    def _apply_levels(self):
        """Apply brightness and contrast adjustments"""
        vmin_prime, vmax_prime = self._calculate_effective_range(
            self.base_vmin, self.base_vmax, self.brightness, self.contrast
        )
        if vmin_prime > vmax_prime:
            vmin_prime, vmax_prime = vmax_prime, vmin_prime
        
        self.img_item.setLevels((vmin_prime, vmax_prime))
        self.cbar.setLevels((vmin_prime, vmax_prime))
        self.info.setText(self._fmt_info())
    
    def _apply_pad_change(self, contrast_factor, brightness_delta):
        """Handle changes from control pad"""
        self.contrast = max(0.01, self.contrast * float(contrast_factor))
        self.brightness += float(brightness_delta)
        
        # Clear cache when values change
        self._calculate_effective_range.cache_clear()
        
        self._apply_levels()
        self.pad.updateValues(self.contrast, self.brightness)
    
    def _on_plot_click(self, event):
        if event.double():
            self.reset_values()
    
    def reset_values(self):
        self.contrast = 1.0
        self.brightness = 0.0
        self.pad.updateValues(self.contrast, self.brightness)
        self._calculate_effective_range.cache_clear()
        self._apply_levels()
    
    def wheelEvent(self, event):
        if self.graph.geometry().contains(event.pos()):
            delta = event.angleDelta().y()
            factor = 0.9 if delta > 0 else (1 / 0.9)
            self.contrast = max(0.01, self.contrast * factor)
            self.pad.updateValues(self.contrast, self.brightness)
            self._calculate_effective_range.cache_clear()
            self._apply_levels()
            event.accept()
        else:
            super().wheelEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_R:
            self.reset_values()
            event.accept()
        elif event.key() == QtCore.Qt.Key_S:
            self._save_image()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def _save_image(self):
        """Save current view with error handling"""
        try:
            filename = 'heatmap_export.png'
            exporter = pg.exporters.ImageExporter(self.plot)
            exporter.export(filename)
            self.info.setText(f"View saved to {filename}")
        except Exception as e:
            self.info.setText(f"Save failed: {str(e)}")


# ---------------------------
# NOTEBOOK INTEGRATION
# ---------------------------
def show_heatmap(data, x_range, y_range, x_label='X', y_label='Y', 
                 cmap=DEFAULT_CMAP, vmin=None, vmax=None, block=False):
    """
    Show an interactive heatmap widget (for notebooks and scripts).
    
    This function does not call sys.exit(), making it suitable for notebooks.
    
    Parameters
    ----------
    data : numpy.ndarray
        The 2D data matrix to display
    x_range : tuple
        (xmin, xmax) range for X axis
    y_range : tuple
        (ymin, ymax) range for Y axis
    x_label : str
        Label for X axis
    y_label : str
        Label for Y axis
    cmap : str
        Colormap name (default: 'viridis')
    vmin, vmax : float, optional
        Value range for colormap. If None, uses data min/max.
    block : bool
        If True, blocks until window is closed. If False (default), returns immediately.
        
    Returns
    -------
    InteractiveHeatmapWidget
        The widget instance
    """
    from IPython import get_ipython
    
    # Get or create QApplication
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
        # Enable high DPI support
        try:
            app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
            app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
        except:
            pass  # Older Qt version
    
    # Create widget
    widget = InteractiveHeatmapWidget(
        data=data,
        x_range=x_range,
        y_range=y_range,
        x_label=x_label,
        y_label=y_label,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax
    )
    
    widget.show()
    
    # Integration with IPython event loop
    ipython = get_ipython()
    if ipython:
        # Use IPython's GUI event loop integration
        try:
            # For IPython 7.0+
            ipython.enable_gui('qt')
        except:
            pass
    
    if block:
        app.exec_()
    
    return widget

