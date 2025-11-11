"""
Core computation and data handling for color map analysis
"""
import re
import numpy as np

# ---------------------------
# CONSTANTS
# ---------------------------
DEFAULT_XY_FILE = "table1.txt"
DEFAULT_Z_FILE = "table2.txt"
DEFAULT_KC = -0.01
DEFAULT_KB = 0.002
DEFAULT_CMAP = 'viridis'


# ---------------------------
# DATA I/O
# ---------------------------
class DataLoader:
    """Handles file I/O operations for XY and matrix data"""
    
    @staticmethod
    def detect_columns(path):
        """Detect the number and names of columns in a data file"""
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                # Read header line
                header = f.readline().strip()
                
                # Read first data line to determine actual column count
                first_data_line = None
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        first_data_line = line
                        break
                
                # Determine delimiter from first data line (more reliable)
                if first_data_line:
                    if '\t' in first_data_line:
                        delim = '\t'
                        splitter = re.compile(r'\t+')
                    elif ',' in first_data_line:
                        delim = ','
                        splitter = re.compile(r',')
                    else:
                        delim = None
                        splitter = re.compile(r'\s+')
                    
                    # Count columns in data line
                    data_parts = [p for p in splitter.split(first_data_line) if p.strip()]
                    num_cols = len(data_parts)
                    
                    # Parse header if present
                    if header:
                        header_parts = [p.strip() for p in splitter.split(header) if p.strip()]
                        # Check if header contains numbers (likely not a header)
                        try:
                            float(header_parts[0])
                            # First line is data, not header
                            return num_cols, [f"Column {i}" for i in range(num_cols)]
                        except:
                            # First line is header, but might have fewer columns
                            # Use actual data column count
                            col_names = header_parts[:num_cols]
                            # Pad with generic names if header has fewer columns
                            while len(col_names) < num_cols:
                                col_names.append(f"Column {len(col_names)}")
                            return num_cols, col_names
                    else:
                        return num_cols, [f"Column {i}" for i in range(num_cols)]
                
                # Fallback: try to parse header
                if header:
                    parts = re.split(r'[,\t\s]+', header)
                    parts = [p.strip() for p in parts if p.strip()]
                    try:
                        float(parts[0])
                        return len(parts), [f"Column {i}" for i in range(len(parts))]
                    except:
                        return len(parts), parts
                
                return 0, []
        except:
            return 0, []
    
    @staticmethod
    def load_xy_data(path, x_col=1, y_col=0):
        """Load X/Y data with column selection
        
        Uses np.genfromtxt to handle missing values gracefully (converts to NaN).
        This matches legacy behavior where missing first column values become NaN in y,
        but the rest of the row still contributes to x.
        """
        delim = None  # Initialize delim before try block
        skip_header = 0
        
        # First detect delimiter and header from first data line (more reliable)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline().strip()
                
                # Check if first line is header by trying to parse first element as float
                try:
                    # Try to parse first element as number
                    float(first_line.split()[0].strip())
                    skip_header = 0
                    # First line is data, use it for delimiter detection
                    test_line = first_line
                except (ValueError, IndexError):
                    # First line is likely header, read next line for delimiter detection
                    skip_header = 1
                    test_line = None
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            test_line = line
                            break
                
                # Detect delimiter from actual data line (more reliable)
                if test_line:
                    if '\t' in test_line:
                        delim = '\t'
                    elif ',' in test_line:
                        delim = ','
                    else:
                        delim = None  # whitespace
        except:
            pass
        
        # Try np.loadtxt first (faster for well-formed data)
        try:
            data = np.loadtxt(path, skiprows=skip_header, dtype=np.float64, ndmin=2, delimiter=delim)
            if data.size == 0:
                raise ValueError("No data found in file")
            
            # Handle single column case
            if data.ndim == 1:
                data = data.reshape(-1, 1)
            
            # Validate column indices
            num_cols = data.shape[1]
            if x_col >= num_cols:
                x_col = min(x_col, num_cols - 1)
            if y_col >= num_cols:
                y_col = min(y_col, num_cols - 1)
            
            return data[:, y_col], data[:, x_col]  # y, x
        except (ValueError, IndexError, UnicodeDecodeError):
            # np.loadtxt failed (likely due to missing values), fall back to np.genfromtxt
            # np.genfromtxt handles missing values by converting them to NaN
            pass
        
        # Use np.genfromtxt (handles missing values gracefully)
        # If delim wasn't set, try to detect it from first data line
        if delim is None:
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    # Skip header
                    first_line = f.readline().strip()
                    try:
                        float(first_line.split()[0].strip())
                        test_line = first_line
                        skip_header = 0
                    except (ValueError, IndexError):
                        skip_header = 1
                        test_line = None
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                test_line = line
                                break
                    
                    if test_line:
                        if '\t' in test_line:
                            delim = '\t'
                        elif ',' in test_line:
                            delim = ','
                        else:
                            delim = None
            except:
                delim = None
        
        # Use np.genfromtxt which handles missing values (converts to NaN)
        # This matches legacy behavior: missing first column -> NaN in y, but row still contributes to x
        try:
            y, x = np.genfromtxt(
                path,
                delimiter=delim,
                dtype=np.float64,
                skip_header=skip_header,
                usecols=(y_col, x_col),
                unpack=True,
                autostrip=True,
                invalid_raise=False,  # Don't raise on invalid values, convert to NaN
            )
            return y, x
        except Exception:
            # If all else fails, try default columns
            y, x = np.genfromtxt(
                path,
                delimiter=delim,
                dtype=np.float64,
                skip_header=skip_header,
                usecols=(0, 1),
                unpack=True,
                autostrip=True,
                invalid_raise=False,
            )
            return y, x
    
    @staticmethod
    def load_matrix_data(path):
        """Optimized matrix loading with better memory usage"""
        # First pass: determine dimensions
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
        
        if not lines:
            raise ValueError("No numeric rows found in file")
        
        first = lines[0]
        if ',' in first:
            sep = ','
            splitter = re.compile(r"\s*,\s*")
        elif '\t' in first:
            sep = '\t'
            splitter = re.compile(r"\t+")
        else:
            sep = ' '  # whitespace
            splitter = re.compile(r"\s+")

        rows = []
        for line in lines:
            try:
                row = np.fromstring(line, sep=sep, dtype=np.float64)
                if row.size:
                    rows.append(row)
                    continue
            except Exception:
                pass
            # Fallback parser (handles stray spaces/commas)
            parts = [p for p in splitter.split(line) if p]
            vals = []
            for p in parts:
                try:
                    vals.append(float(p))
                except ValueError:
                    pass
            if vals:
                rows.append(np.asarray(vals, dtype=np.float64))

        if not rows:
            raise ValueError("No numeric rows found in file")

        widths = np.array([r.size for r in rows], dtype=int)
        modal_w = np.bincount(widths).argmax()
        good_rows = [r for r in rows if r.size == modal_w]
        A = np.vstack(good_rows).astype(np.float64)
        if A.shape[0] > A.shape[1]:
            A = A.T
        return A


# ---------------------------
# COMPUTATION UTILITIES
# ---------------------------
def calculate_effective_range(vmin, vmax, brightness, contrast):
    """Calculate effective value range after brightness/contrast adjustment"""
    vmin_p = (vmin - brightness) / max(1e-12, contrast)
    vmax_p = (vmax - brightness) / max(1e-12, contrast)
    return vmin_p, vmax_p


def calculate_marker_position(brightness, contrast, span, kc=DEFAULT_KC):
    """Calculate control pad marker position from brightness/contrast values"""
    import math
    u = np.clip(0.5 + brightness / max(1e-9, span), 0.0, 1.0)
    v = 0.5
    if contrast > 0:
        v = np.clip(0.5 - math.log(contrast) / (2 * max(1e-9, abs(kc))), 0.0, 1.0)
    return u, v