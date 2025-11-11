import numpy as np

K_b = 1.380649e-23
q = 1.602176634e-19

def johnson(time_arr, T, R):
    #CHECKED
    """
    Generates Johnson-Nyquist noise voltage signal in the time domain, for a given time array.

    Parameters:
    time_arr (array-like): Array of ordered time values in Seconds (assumed to be evenly spaced).
    T (float): Temperature in Kelvin.
    R (float): Resistance in Ohms.

    Returns:
    np.ndarray: Array of normally distributed noise values with RMS amplitude corresponding to the thermal noise voltage.
    """
    size = len(time_arr)
    Df = 0.5 * (size - 1) / (time_arr[-1] - time_arr[0]) # Nyquist Frequency is this correct. Becomes noise's bandwidth
    # Nyquist Frequency used for bandwidth as it is the maximum resolvable frequency that can be detected. Generating noise purely by itself, before any filtering is being simulated. 

    V_rms = np.sqrt(4 * K_b * T * R * Df)
    return np.random.normal(0, V_rms, size)

def shot(time_arr, I, R):
    #CHECKED
    """
    Generates Shot noise voltage signal in the time domain, for a given time array.

    Parameters:
    time_arr (array-like): Array of ordered time values in Seconds (assumed to be evenly spaced).
    I (float): Current in Amperes.
    R (float): Resistance in Ohms.

    Returns:
    np.ndarray: Array of normally distributed voltage noise values with RMS amplitude corresponding to shot noise.

    Note:
    Ideally, shot noise follows a Poisson distribution, but for large mean values (lambda), the Poisson distribution approximates a normal distribution.
    """
    
    size = len(time_arr)
    Df = 0.5 * (size - 1) / (time_arr[-1] - time_arr[0])

    I_rms = np.sqrt(2 * q * I * Df) # Shot noise current
    V_rms = R * I_rms # Recalculating to Shot noise voltage
    return np.random.normal(0, V_rms, size) #poisson should be used, but lamda is too large for np.random.poisson

def color(time_arr, V_rms, exponent=1):
    """
    Generates 1/f^(exponent) noise (pink noise by default, exp=1) in the time domain.

    Parameters:
    time_arr (array-like): Array of ordered time values in Seconds (assumed to be evenly spaced).
    V_rms (float): RMS value of the generated noise.
    exponent (float, optional): Power of the frequency dependence. Default is 1, which gives 1/f noise (pink noise). Set to 0 for white noise, 2 for brown noise, etc...

    Returns:
    np.ndarray: Array of noise values with PSD proportional to 1/f^(exponent).
    """
    #Generate Guassian White Noise in time domain
    size = len(time_arr)
    dt = (time_arr[-1] - time_arr[0]) / (size-1.0)
    white = np.random.standard_normal(size)

    #Fourier Transform to Frequency Domain
    freqs = np.fft.rfftfreq(size, d=dt)
    fft = np.fft.rfft(white, norm='backward') * dt

    #Scale Fourier Transform by 1/f^(exponent/2) for 1/f^exponent PSD (psd proportional to fft^2) 
    freqs[0] = freqs[1] #Avoid division by zero
    fft = fft / (freqs**(exponent*0.5))

    #Convert back to time domain
    ifft = (np.fft.irfft(fft, n=size, norm='forward') / dt).real
    ifft_rms = np.sqrt(np.mean(ifft**2))

    return V_rms * ifft / ifft_rms #Ensure V_rms is as specified


def rtn(time_arr, tau_up, tau_down, state_up=1, state_down=0, initial_state=None):
    """
    Generate random telegraph noise on a user-supplied time array.

    Parameters:
        time_arr (np.ndarray): Array of ordered time values in Seconds (assumed to be evenly spaced).
        tau_up (float): Mean dwell time in the 'up' state.
        tau_down (float): Mean dwell time in the 'down' state.
        state_up (float): Value of the up state (default: 1).
        state_down (float): Value of the down state (default: 0).
        initial_state (float): Value of the first state (default: None = random(up, down))

    Returns:
        signal (np.ndarray): RTN signal array, same shape as time_arr.

    Notes:
    - PSD of RTN will have lorentzian profile: S(f) = 4*A^2*tau / (1 + (2pi*f*tau)^2), 
    with correlation time: tau = tau_up*tau_down / (tau_up+tau_down)
    - Characteristic (roll-off) frequency corresponds to 1 / (2pi*tau)
    """
    if tau_up <= 0 or tau_down <= 0:
        raise ValueError("tau_up and tau_down must be positive to avoid infinite loops.")

    time_arr = np.asarray(time_arr)
    signal = np.zeros_like(time_arr)

    if initial_state is None:
        current_state = np.random.choice([state_up,state_down])
    else: current_state = initial_state

    current_time = time_arr[0]
    i = 0

    while i < len(time_arr):
        # Sample dwell time
        dwell_time = np.random.exponential(tau_up if current_state == state_up else tau_down)
        dwell_end_time = current_time + dwell_time

        # Assign current state until dwell time is over
        while i < len(time_arr) and time_arr[i] < dwell_end_time:
            signal[i] = current_state
            i += 1

        # Flip state
        current_time = dwell_end_time
        current_state = state_down if current_state == state_up else state_up

    return signal


def bit(signal_arr, bit_depth, measure_min, measure_max, noise_only = False):
    """
    Quantize an analog signal to simulate ADC behavior with given bit depth.

    Parameters:
    signal_arr (array-like): Input analog signal values.
    bit_depth (int): number of bits used in quantization (e.g., 8, 12, 16).
    measure_min (float): Minimum measurable value of the ADC range.
    measure_max (float): Maximum measurable value of the ADC range.
    noise_only (bool, optional): If True, quantization noise only. If False (default), return the quantized signal.

    Returns:
    np.ndarray: Quantized signal or Quantization noise, depending on 'noise_only'.

    Notes:
    - The signal is clipped to the measurement range before quantization.
    - The number of quantization levels is 2^bit_depth.
    """
    levels = int(2**int(bit_depth)) # 1<<int(bit_depth)
    quantization_step = (measure_max - measure_min) / (levels - 1)

    signal_clipped = np.clip(signal_arr, measure_min, measure_max)
    quantized_signal = np.round((signal_clipped - measure_min) / quantization_step) * quantization_step + measure_min

    if noise_only is False:
        return quantized_signal
    else:
        return quantized_signal - signal_arr


def psd(time_arr, signal_arr, return_onesided=True):
    """
    Computes the Power Spectral Density (PSD) of a time-domain signal using Welch's method.

    Parameters:
    time_arr (array-like): Ordered time values in Seconds (assumed to be increasing).
    signal_arr (array-like): Signal values as a function of time.

    Returns:
    tuple:
        - f_welch (np.ndarray): Array of frequency values corresponding to the PSD.
        - psd_welch (np.ndarray): Power Spectral Density values in (signal_unit)^2/Hz.
        - msg (str): Message describing the PSD normalization and units.

    Notes:
    - Welch's method averages overlapping FFTs to reduce variance in the PSD estimate.
    - The RMS value of the signal over a bandwidth B can be computed from the PSD as:
        V_rms = sqrt( ∫ PSD(f) df ) over bandwidth.
    - The PSD values follow the convention:
        mean(PSD) ≈ 2 × (b.fft)^2 / total duration
    -When dealing with real signals, (one sided, only positive frequencies) the relationship is psd = np.abs(fft)**2 / total_time * 2, where factor of 2 is applied everywhere except at the DC and Nyquist bins. When dealing with complex signals (positive and negative) the relationship is psd = np.abs(fft)**2 / total_time.
    """
    from scipy import signal as sp_signal
    #make equidistant
    size = len(time_arr)
    sampling_freq = (size-1) / (time_arr[-1] - time_arr[0])

    f_welch, psd_welch = sp_signal.welch(signal_arr, sampling_freq, nperseg=min(size, 4024), return_onesided=return_onesided)
    return f_welch, psd_welch

def noise_help(noise):
    import matplotlib.pyplot as plt

    doc = {}

    if noise == "johnson":
        time = np.arange(0,100)

        doc = {
            "name": "Johnson Noise",
            "time": time,
            "function": johnson,
            "params": [300, 200],
            "text_title_size": 20,
            "text_midbreak_size": 15,
            "text_main_size": 10,
            "text_bullet_size": 10,
            "text_title_x": .5,
            "text_title_y": 9,
            "text_main_x": .3,
            "text_main_y": 8,
        }
        
    if noise == "johnson2":
        time = np.arange(0,100)

        doc = {
            "name": "Johnson Noise",
            "time": time,
            "function": johnson,
            "params": [300, 200],
            "text_title_size": 20,
            "text_midbreak_size": 15,
            "text_main_size": 10,
            "text_bullet_size": 10,
            "text_title_x": .5,
            "text_title_y": 9,
            "text_main_x": .3,
            "text_main_y": 6,
        }

    if noise == "shot":
        time = np.arange(0,100)

        doc = {
            "name": "Shot Noise",
            "time": time,
            "function": shot,
            "params": [1, 200],
            "text_title_size": 30,
            "text_midbreak_size": 15,
            "text_main_size": 15,
            "text_bullet_size":10,
            "text_title_x": .5,
            "text_title_y": 9,
            "text_main_x": .5,
            "text_main_y": 8,
        }

        
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(22,7))
    fig.suptitle(doc["name"], fontsize=20)
    ax1.plot(doc["time"], doc["function"](doc["time"], *doc["params"]), 'red', label='(t^2)*exp(-(t^2))')


    ax1.set(title="2 lines chart", xlabel="t", ylabel="y")
    ax1.legend(loc="upper right")


    # Set both x- and y-axis limits to [0, 10] instead of default [0, 1]


    ax2.axis([0, 10, 0, 10])
    ax2.tick_params(axis='x', colors='white')
    ax2.tick_params(axis='y', colors='white')

    ax2.text(doc["text_title_x"], doc["text_title_y"], doc["name"], weight='bold', fontsize=doc["text_title_size"],
             bbox={'facecolor': 'red', 'alpha': 0.3, 'pad': 10})
    ax2.text(doc["text_main_x"], doc["text_main_y"], doc["function"].__doc__, wrap="false", fontsize=doc["text_main_size"])


    #use for bullet points#ax2.text(0.5, 5.5, 'Topic 2', weight='bold', fontsize=doc["text_midbreak_size"])
    #use for bullet points#ax2.text(0.5, 4.5, '- Bullet pont 1\n- Bullet point 2', fontsize= doc["text_bullet_size"])

    #use to display function # ax2.text(2, 3, r'a function to plot: $t^2*exp(-t^2)$', fontsize=12)