import numpy as np


def fft(x, y, equidistant_check=True, equidistant_rel_error=1e-4, remove_negative_f=False, mathematica_convention=False, inverse=False):
    """
    Perform Fast Fourier Transform (FFT) or Inverse FFT on one-dimensional or multi-dimensional data,
    with optional handling for non-equidistant sampling, mandatory normalization to continuous Fourier definition.
    Allows for +- in exp for scientific and engineering definition for Fourier Transform.

    Parameters
    ----------
    x (array_like): 
        The time or spatial domain axis (1D array). Must be increasing, doesn't need to be equidistant.
    y (array_like): 
        The signal to be transformed. Can be 1D or 2D array (if 2D, the FFT is applied along axis 1).
    equidistant_check (bool, optional): 
        If True (default), checks whether `x` is uniformly spaced. If not, interpolates to uniform spacing.
    equidistant_rel_error : float, optional
        Relative tolerance for equidistant spacing check. Default is 1e-4.
    remove_negative_f : bool, optional
        If True, removes negative frequencies from output. Default is False.
    mathematica_convention : bool, optional
        If True, uses Mathematica-style conventions: forward Fourier ~ exp(i2pift).
        If False (default), uses NumPy convention: forward Fourier ~ exp(-i2pift)
    inverse : bool, optional
        If True, computes the inverse FFT. Default is False (forward transform).

    Returns
    -------
    fft_x : ndarray
        Ordered frequency domain axis corresponding to the transformed data (negative frequencies can be removed if remove_negative_f is True).
        Ordered time domain axis if inverse is True (time axis starts at 0).
    fft_y : ndarray
        Transformed signal. Shape matches `y`.

    Notes
    -----
    - The function supports both real and complex-valued input `y`.
    - If `x` is not equidistant and `equidistant_check=True`, the function interpolates `y` using `make_equidistant`.

    Examples
    --------
    >>> t = np.linspace(0, 1, 1000)
    >>> y = np.sin(2 * np.pi * 50 * t)
    >>> f, Y = fft(t, y)

    >>> # Inverse transform
    >>> t_rec, y_rec = fft(f, Y, inverse=True)
    """

    x, y = np.array(x), np.array(y)

    # Handle non-equidistant input
    if equidistant_check:
        diffs = np.diff(x)
        if not np.allclose(diffs, diffs[0], rtol=equidistant_rel_error):
            # x is not equidistant, must start interpolating
            x, y = make_equidistant(x, y, step=None)

    # Determine shape and axis
    if y.ndim == 1:
        n, axis = len(y), -1
    else:
        n, axis = y.shape[1], 1

    #Determine Convention
    if mathematica_convention is False:
        fft_func, fft_norm = np.fft.fft, "backward"
        ifft_func, ifft_norm = np.fft.ifft, "forward"
    else:
        fft_func, fft_norm = np.fft.ifft, "forward"
        ifft_func, ifft_norm = np.fft.fft, "backward"

    # Compute FFT and normalize
    sample_spacing = (x[-1] - x[0]) / (n-1.0)

    if inverse is True:
        y = np.fft.ifftshift(y, axes=axis) # Reorder y to match np.fft.ifft convention
        fft_x = np.arange(0, n) / (n * sample_spacing) # Time domain creation
        fft_y = ifft_func(y, axis=axis, norm=ifft_norm) * sample_spacing # Sample Spacing is the Fourier consistent normalization
    else:
        fft_x = np.fft.fftfreq(n, d=sample_spacing) # Frequency domain creation
        fft_y = fft_func(y, axis=axis, norm=fft_norm) * sample_spacing
        fft_x, fft_y = np.fft.fftshift(fft_x), np.fft.fftshift(fft_y, axes=axis) # Reorder x, y for plotting

    # Remove negative frequencies
    if remove_negative_f is True:
        mask = fft_x >= 0
        fft_x = fft_x[mask]
        if y.ndim == 1:
            fft_y = fft_y[mask]
        else:
            fft_y = fft_y[:, mask]

    return fft_x, fft_y

# NOTES For Developer:
        # Mathematica has convention exp(i*2pi*t)
        # np.fft.fft takes x input -3,-2,-1,0,1,2,3 and np.fft.ifft takes x input 0,1,2,3,-3,-2,-1
        # Our fft(np.fft.ifft) takes x input -3,-2,-1,0,1,2,3 and our ifft(np.fft.fft) takes x input 0,1,2,3,-3,-2,-1
        # Numpy outputs in 0,1,2,3,-3,-2,-1 order, our function sorts to -3,-2,-1,0,1,2,3

        #Tested with Lorentzian, Gaussian, and Rectangular Signals

def ifft(x, y, equidistant_check=True, equidistant_rel_error=1e-4, remove_negative_f=False, mathematica_convention=False):
    return fft(x, y, equidistant_check=equidistant_check, equidistant_rel_error=equidistant_rel_error, remove_negative_f=remove_negative_f, mathematica_convention=mathematica_convention, inverse=True)



def make_equidistant(x, y, step=None):
    import scipy.interpolate as sp
    ### Takes one column x and one or more columns y and makes them equidistant in x
    ### Returns new_x, new_y. The number of points will likely change.
    if step is None:
        # Calculate the smallest difference between consecutive elements
        min_step = np.min(np.diff(x))
    else:
        min_step = step

    # Generate the new equidistant x array
    new_x = np.arange(x[0], x[-1] + min_step, min_step)

    if isinstance(y[0], (list, np.ndarray)):  # If y contains multiple columns
        new_y = []
        for y_column in y:
            interpolation_function = sp.interpolate.interp1d(x, y_column, kind='linear', fill_value='extrapolate')
            new_y.append(interpolation_function(new_x))
    else:  # If y is a single column
        interpolation_function = sp.interpolate.interp1d(x, y, kind='linear', fill_value='extrapolate')
        new_y = interpolation_function(new_x)

    return np.array(new_x), np.array(new_y)