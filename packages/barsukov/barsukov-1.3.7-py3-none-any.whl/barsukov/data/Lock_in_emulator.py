import numpy as np
from barsukov.data import noise

import sympy as sp

class Lock_in_emulator:
    def __init__(self, signal, f, phase, x_start, x_stop, x_amp, time, dt, TC, order, plot_points, buffer_size, 
                 johnson_T=0, johnson_R=0,
                 shot_I=0, shot_R=0,
                 onef_rms=0,
                 rtn_tau_up=0, rtn_tau_down=0, rtn_state_up=0, rtn_state_down=0,
                 bit_depth=0, bit_measure_min=0, bit_measure_max=0):

        #Signal Properties
        self.signal_arr = signal
        self.f = f
        self.phase = np.pi * phase / 180
        self.x_start = x_start
        self.x_stop = x_stop
        self.x_amp = x_amp
        self.time = abs(time)

        #Noise Properties
        self.jT, self.jR = johnson_T, johnson_R
        self.sI, self.sR = shot_I, shot_R
        self.oRMS = onef_rms
        self.rTU, self.rTD, self.rSU, self.rSD = rtn_tau_up, rtn_tau_down, rtn_state_up, rtn_state_down
        self.bD, self.bMIN, self.bMAX = bit_depth, bit_measure_min, bit_measure_max

        #Filter Properties
        self.dt = abs(dt)
        self.TC = TC
        self.n = abs(order)


        #Plotting Properties
        self.plot_points = plot_points
        self.buffer_size = buffer_size
        self.buffer_period = self.buffer_size*self.dt
        self.buffer_offset = np.linspace(-self.buffer_period, 0, self.buffer_size)

    def run(self):
        self.t_plot = np.linspace(self.buffer_period, self.time, self.plot_points)
        self.x_plot = self.x_arr(self.t_plot)

        self.original_signal = self.signal_arr(self.x_plot)
        self.expected_signal = 0.5 * self.x_amp * np.gradient(self.original_signal, self.x_plot)
        self.output_signal = self.signal_output_arr(self.t_plot)

        self.fit()
        #self.plot()

### BEGIN: FIELD
    def x_arr(self, t_arr):
        return self.x_start + t_arr * (self.x_stop - self.x_start) / self.time

    def x_with_mod_arr(self, t_arr):
        return self.x_arr(t_arr) + self.x_amp * np.cos(2 * np.pi * self.f * t_arr)


### BEGIN: NOISE
    def noise(self, t_arr):
        if self.jT and self.jR: self.johnson = noise.johnson(t_arr, self.jT, self.jR)
        else: self.johnson = np.zeros(len(t_arr))
        
        if self.sI and self.sR: self.shot = noise.shot(t_arr, self.sI, self.sR)
        else: self.shot = np.zeros(len(t_arr))
            
        if self.oRMS: self.onef = noise.color(t_arr, self.oRMS)
        else: self.onef = np.zeros(len(t_arr))
        
        if (self.rTU and self.rTD) or (self.rSU and self.rSD): self.rtn = noise.rtn(t_arr, self.rTU, self.rTD, self.rSU, self.rSD)
        else: self.rtn = np.zeros(len(t_arr))
        return self.johnson + self.shot + self.onef + self.rtn


    def lp_filter_arr(self, t_arr):
        t_arr = -(t_arr - t_arr[-1])
        factorial = np.math.factorial(self.n - 1)
        lp_filter_arr = (t_arr ** (self.n - 1)) * np.exp(-t_arr / self.TC) / (self.TC**self.n * factorial)
        return lp_filter_arr / abs(np.sum(lp_filter_arr) * self.dt)

    def signal_output(self, t):
        t_arr = t + self.buffer_offset

        x_arr = self.x_with_mod_arr(t_arr)
        s_arr = self.signal_arr(x_arr)
        noise_arr = self.noise(t_arr)
        filter_arr = self.lp_filter_arr(t_arr)
        ref_X = np.cos(2 * np.pi * self.f * t_arr - self.phase)

        integrand = (s_arr+noise_arr) * ref_X * filter_arr * self.dt
        return np.sum(integrand)

    def signal_output_arr(self, t_arr):
        output = np.array([self.signal_output(t) for t in t_arr])

        if self.bD or (self.bMIN and self.bMAX):
            return noise.bit(output, self.bD, self.bMIN, self.bMAX)
        else:
            return output


### BEGIN: FIT:
    def fit(self):
        from scipy.interpolate import interp1d
        from scipy.optimize import curve_fit

        interp = interp1d(self.x_plot, self.expected_signal, kind='cubic', fill_value=0.0, bounds_error=False)

        def model(x, diminish, stretch, shift):
            x_trans = (x / stretch) - shift
            return (1.0 / diminish) * interp(x_trans)

        expected_max_idx, expected_min_idx = np.argmax(self.expected_signal), np.argmin(self.expected_signal)
        output_max_idx, output_min_idx = np.argmax(self.output_signal), np.argmin(self.output_signal)

        expected_peak_xdif = np.abs(self.x_plot[expected_max_idx] - self.x_plot[expected_min_idx])
        output_peak_xdif = np.abs(self.x_plot[output_max_idx] - self.x_plot[output_min_idx])

        initial_stretch = np.abs(output_peak_xdif / expected_peak_xdif)
        initial_diminish = np.ptp(self.expected_signal) / np.ptp(self.output_signal)

        initial_transform = model(self.x_plot, initial_diminish, initial_stretch, 0)
        transform_max_idx = np.argmax(initial_transform)

        initial_shift = (self.x_plot[output_max_idx] - self.x_plot[transform_max_idx]) / initial_stretch

        initial_guess = [np.max([1,initial_diminish]), np.max([1,initial_stretch]), np.max([-np.ptp(self.x_plot),initial_shift])]

        bounds = [(1, 1, -np.ptp(self.x_plot)), (10, 0.5*np.ptp(self.x_plot), np.ptp(self.x_plot) )]
        popt, _ = curve_fit(model, self.x_plot, self.output_signal, sigma=1e-4, p0=initial_guess, bounds=bounds, method='trf')

        #print(f"initial diminish: {initial_diminish}\ninitial stretch: {initial_stretch}\ninitial shift: {initial_shift}")
        self.diminish = popt[0]
        self.stretch = popt[1]
        self.shift = popt[2]
        self.adjusted_signal = model(self.x_plot, self.diminish, self.stretch, self.shift)

        #SNR Calculation
        p2p = np.max(self.adjusted_signal) - np.min(self.adjusted_signal)
        noise_sample = self.output_signal[int(len(self.adjusted_signal) * 0.9):] #last 10% of the output signal
        v_rms = np.sqrt(np.mean(noise_sample**2))

        self.snr = p2p / v_rms

    def plot(self):
        import matplotlib.pyplot as plt

        print(f'diminish: {self.diminish}')
        print(f'stretch: {self.stretch}')
        print(f'shift: {self.shift}')
        print(f'Signal to Noise Ratio: {self.snr}')

        self.fig, self.axes = plt.subplots(nrows=2, ncols=1, figsize=(12,18))

        self.lines = [
            self.axes[0].plot(self.x_plot, self.original_signal, 'r-', label='Original Signal')[0],
            self.axes[1].plot(self.x_plot, self.output_signal, 'b-', label='Demodulated Signal (Lock-In)')[0],
            self.axes[1].plot(self.x_plot, self.expected_signal, 'r-', label='Demodulated Signal (Expected)')[0],
            self.axes[1].plot(self.x_plot, self.adjusted_signal, 'g-', label=f'Demodulated Signal (Adjusted)\n  Diminish: {self.diminish}\n  Stretch:{self.stretch}\n  Shift: {self.shift}')[0],
        ]

        self.axes[0].set_title('Original Signal vs x')
        self.axes[1].set_title('Demodulated Signal vs x')

        plt.legend()
        plt.show()

    def spectrum_average(self, num):
        result = np.zeros_like(self.t_plot)
        for i in range(0, num):
            result += self.signal_output_arr(self.t_plot)

        return result / num