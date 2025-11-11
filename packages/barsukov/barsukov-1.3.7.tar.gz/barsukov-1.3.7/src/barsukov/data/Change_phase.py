from barsukov.data.constants import deg2rad
from barsukov.time import time_stamp

from scipy.optimize import curve_fit
from scipy.optimize import differential_evolution
import numpy as np
import matplotlib.pyplot as plt

import glob
import sys
import os


class Change_phase:
        ### the phase you receive from auto, is a phase shift that you need to add to the phase of the original data. 
        ### adding the two phases together gives to you the total effective lock-in phase of the calculated data.
        ### Note that lock-in phase corresponds to the reference, not to the signal itself.
        ### Lock-in phase is an artificial phase delay of the reference
        ### new reference is cos(Wt - phase)
        ### This script's phase, if added to the original phase of the lock-in, will give you a cumulative phase.
        ### The recalculated signal would correspond to lock-in signal if measured with this cumulative phase.
        ### This cumulative phase is the phase delay of your signal with respect to the original unaltered reference.
        ### The automatically recalculated data is correct only if considered together with the automatically calculated phase
        ### This means, you may get positive or negative signals in x-channel. So always consider the cummulative phase when evaluating the data. 

    def __init__(self, x=[], A=[], B=[], initial_phase=0):
        self.x = np.array(x)
        self.A = np.array(A)
        self.B = np.array(B)
        self.initial_phi = initial_phase

        self.phi = initial_phase
        self.newA = None
        self.newB = None


    def read_from_file(self, full_file_path, x_column=0, A_column=1, B_column=2, initial_phase=0):
        self.full_file_path = full_file_path
        data = np.loadtxt(self.full_file_path, skiprows=0, unpack=True, usecols=(x_column, A_column, B_column))
        self.x = data[0]
        self.A = data[1]
        self.B = data[2]
        self.initial_phi = initial_phase


    def offset_phase(self, phi=None):
        if phi is not None:
            self.phi = float(phi)
            self.newA = self.A * np.cos(self.phi*deg2rad) + self.B * np.sin(self.phi*deg2rad)
            self.newB = - self.A * np.sin(self.phi*deg2rad) + self.B * np.cos(self.phi*deg2rad)
        else:
            def to_minimize(phi_val):
                self.phi = phi_val[0] #Differential evolution passes arrays
                self.newA = self.A * np.cos(self.phi*deg2rad) + self.B * np.sin(self.phi*deg2rad)
                self.newB = - self.A * np.sin(self.phi*deg2rad) + self.B * np.cos(self.phi*deg2rad)
                popt, pcov = curve_fit(lambda x,a,b: a+b*x, self.x, self.newB, p0=[0,0])
                return 1-(pcov[0,1]/(pcov[0,0]*pcov[1,1]))**2

            ### MINIMIZES the sum of the data in the Y-channel (B)
            result = differential_evolution(to_minimize, bounds=[(0,359.99)], strategy='best1bin')
            if result.success:
                self.offset_phase(phi=result.x[0])
                print(f"Auto-adjusted phase: {result.x[0]} degrees")
            else:
                self.phi = initial_phase
                print("Optimization failed!")


    def plot_offset(self):
        if not hasattr(self, "fig") or not hasattr(self, "axes"):
            self.fig, self.axes = plt.subplots(nrows=4, ncols=1, figsize=(12,18))

            self.lines = [
                self.axes[0].plot(self.x, self.A ,'b-', label='X-')[0],
                self.axes[0].plot(self.x, self.B, 'r-', label='Y-')[0],
                self.axes[1].plot(self.x, self.newA, 'b-', label='X-')[0],
                self.axes[2].plot(self.x, self.newB, 'r-', label='Y-')[0],
                self.axes[3].plot(self.x, self.newA ,'b-', label='X-')[0],
                self.axes[3].plot(self.x, self.newB, 'r-', label='Y-')[0],
            ]

            self.axes[0].set_title('Original X- & Y-')
            self.axes[1].set_title('Adjusted X-')
            self.axes[2].set_title('Adjusted Y-')
            self.axes[3].set_title('Adjusted X- & Y-')

            for ax in self.axes:
                ax.legend()
        else:
            for line in self.lines:
                line.set_xdata(self.x)

            self.lines[0].set_ydata(self.A)
            self.lines[1].set_ydata(self.B)
            self.lines[2].set_ydata(self.newA)
            self.lines[3].set_ydata(self.newB)
            self.lines[4].set_ydata(self.newA)
            self.lines[5].set_ydata(self.newB)

            for ax in self.axes:
                ax.relim()
                ax.autoscale_view()

        if "IPython" in sys.modules:
            from IPython.display import display
            display(self.fig)
        else:
            plt.ion()
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            plt.show()


    def save_data(self, full_folder_path=None, file_name=None):
        if hasattr(self, "full_file_path"):
            full_folder_path, file_name = os.path.split(self.full_file_path)
            file_name = f"Corrected_{round(self.phi)}_{file_name}"
        else:
            if full_folder_path is None:
                full_folder_path = os.getcwd()
            if file_name is None:
                file_name = f"{time_stamp()}_Corrected_Phase_Lock_in_Data"

        full_folder_path = os.path.join(full_folder_path, 'phase-corrected_data')
        if not os.path.isdir(full_folder_path):
            os.makedirs(full_folder_path)

        full_file_path = os.path.join(full_folder_path, file_name)
        with open(full_file_path, "w") as file:
            for i in range(len(self.x)):
                file.write(f"{self.x[i]} {self.newA[i]} {self.newB[i]} \n")


    def offset_phase_script(self, full_folder_path=None, x_column=0, A_column=1, B_column=2, initial_phase=0, nocheck=False):
        if full_folder_path is None:
            full_folder_path = os.getcwd()
        for file in glob.glob(os.path.join(full_folder_path, '*.txt')):
            self.read_from_file(file, x_column, A_column, B_column, initial_phase)

            self.offset_phase()
            self.plot_offset()

            while True:
                if nocheck is False:
                    manual_input=input('Enter "auto" to auto-calculate phase, a number/float for manual phase, or press ENTER to skip: ')

                    if manual_input == "auto":
                        self.offset_phase()
                        self.plot_offset()
                    elif manual_input:
                        try:
                            self.offset_phase(manual_input)
                            self.plot_offset()
                        except ValueError:
                            print(f"Invalid input: {manual_input}. Please enter a valid phase value or 'auto'.")
                    if not manual_input:
                        print("Phase adjustment completed.")
                        break
            self.save_data()
            print("Adjusted phase data saved.")
