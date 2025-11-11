from PyQt5 import QtWidgets
import pyqtgraph as pg
import numpy as np
import sys

from barsukov.data import Lock_in_emulator, noise

def make_lorentzian(center, HW, amp):
    def l(x):
        return amp / ((x - center)**2 + HW**2)
    return l

def make_antilorentzian(center, HW, amp):
    def al(x):
        return amp * (x - center) / np.abs(HW) / (1 + ( (x - center) / HW)**2)
    return al

params = [
    ("l_center", 2, "Center:", float),
    ("l_HW", 1, "HW:", float),
    ("l_amp", 1e-6, "Amplitude:", float),
    ("al_center", 4, "Center:", float),
    ("al_HW", 2, "HW:", float),
    ("al_amp", 2e-6, "Amplitude:", float),
    ("jT", 300, "Temperature (K):", float),
    ("jR", 200, "Resistance (Ohms):", float),
    ("sI", 1e-3, "Current (Amps):", float),
    ("sR", 200, "Resistance (Ohms):", float),
    ("oRMS", 1e-7, "RMS:", float),
    ("rTU", 0.01, "Tau Up (s):", float),
    ("rTD", 0.01, "Tau Down (s):", float),
    ("rSU", 1e-7, "State Up:", float),
    ("rSD", 1e-7, "State Down:", float),
    ("bD", 64, "Bit Depth (bits):", int),
    ("bMIN", -21, "Minimum Measurement:", float),
    ("bMAX", 21, "Maximum Measurement:", float),
    ("xstart_input", 0, "X Start:", float),
    ("plotpoints_input", 500, "# Plot Points:", int),
    ("time_input", 120, "Sweep Time (s):", float),
    ("xstop_input", 10, "X Stop:", float),
    ("xamp_input", 0.2, "Modulation Amp:", float),
    ("f_input", 1000, "Modulation Freq (Hz):", float),
    ("TC_input", 500e-3, "Time Constant (s):", float),
    ("order_input", 4, "Filter Order:", int),
    ("dt_input", 1e-4, "Sampling Step (s):", float),
    ("buffersize_input", 10000, "Buffer Size:", int),
    ("phase_input", 0, "Phase Offset (deg):", float),
]

class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lock-in Amplifier Emulator")
        self.resize(1000, 800)

        #Window Area (horizontal)
        main_layout = QtWidgets.QHBoxLayout(self)
        self.inputs = {} # (widget, cast, method)
        self.line_edits = {}

        #Interactive Input Box Setup
        for name, default, label, cast in params:
            le = QtWidgets.QLineEdit(str(default))
            #le.editingFinished.connect(self.update_plot)
            self.line_edits[name] = le
            self.inputs[name] = (le, lambda w=le, c=cast: c(w.text()))

#Left Area:
        left_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(left_layout, 1)

        # Signal Type Selector
        signal_combo = QtWidgets.QComboBox()
        signal_combo.addItems(["Lorentzian", "Anti-Lorentzian"])
        #signal_combo.currentIndexChanged.connect(self.update_plot)
        self.inputs["signal_type"] = (signal_combo, lambda w: str(w.currentText()))
        left_layout.addWidget(QtWidgets.QLabel("<b>Signal Type:</b>"))
        left_layout.addWidget(signal_combo)

        # Signal Inputs Stack
        signal_stack = QtWidgets.QStackedWidget()
        left_layout.addWidget(signal_stack)

        #Lorentzian Inputs
        lorentz_widget = QtWidgets.QWidget()
        lorentz_layout = QtWidgets.QFormLayout(lorentz_widget)
        lorentz_layout.addRow("<b>Center:</b>", self.line_edits["l_center"])
        lorentz_layout.addRow("<b>HW:</b>", self.line_edits["l_HW"])
        lorentz_layout.addRow("<b>Amplitude:</b>", self.line_edits["l_amp"])
        signal_stack.addWidget(lorentz_widget)

        #Guassian Inputs
        antilorentz_widget = QtWidgets.QWidget()
        antilorentz_layout = QtWidgets.QFormLayout(antilorentz_widget)
        antilorentz_layout.addRow("<b>Center:</b>", self.line_edits["al_center"])
        antilorentz_layout.addRow("<b>HW:</b>", self.line_edits["al_HW"])
        antilorentz_layout.addRow("<b>Amplitude:</b>", self.line_edits["al_amp"])
        signal_stack.addWidget(antilorentz_widget)

        signal_combo.currentIndexChanged.connect(signal_stack.setCurrentIndex)

        #Noise Options:
        left_layout.addWidget(QtWidgets.QLabel("<b>Noise Options:</b>"))

        noises = [
            ("Johnson Noise", "Temperature (K):,jT", "Resistance (Ohms):,jR"),
            ("Shot Noise", "Current (Amps):,sI", "Resistance (Ohms):,sR"),
            ("1/f Noise", "RMS:,oRMS"),
            ("Random Telegraph Noise", "Tau Up (s):,rTU", "Tau Down (s):,rTD", "State Up:,rSU", "State Down:,rSD"),
            ("Bit Noise", "Bit Depth (bits):,bD", "Minimum Measurement:,bMIN", "Maximum Measurement:,bMAX")
        ]

        for noise in noises:
            #Noise Checkbox
            cb = QtWidgets.QCheckBox(noise[0])
            self.inputs[noise[0]] = (cb, lambda w=cb: w.isChecked())
            left_layout.addWidget(cb)

            # Group of Noise Inputs
            group = QtWidgets.QGroupBox(noise[0] + " Settings")
            group.setCheckable(False)
            group.setVisible(False)
            form = QtWidgets.QFormLayout(group)
            for p in noise[1:]:
                label, name = p.split(",")
                form.addRow("<b>"+label+"</b>", self.line_edits[name])
            left_layout.addWidget(group)

            cb.toggled.connect(group.setVisible)
            #cb.toggled.connect(self.update_plot)

        left_layout.addStretch(1)

        # Simulate Button
        simulate_button = QtWidgets.QPushButton("Simulate")
        simulate_button.clicked.connect(self.update_plot)
        left_layout.addWidget(simulate_button)

        # Reset Button
        reset_button = QtWidgets.QPushButton("Reset")
        reset_button.clicked.connect(self.reset_fields)
        left_layout.addWidget(reset_button)

        # User Notes
        left_layout.addWidget(QtWidgets.QLabel("<b>User Notes:</b>"))
        user_notes = QtWidgets.QLabel()
        user_notes.setText("- SweepTime ≥ SamplingStep*BufferSize*#PlotPoints\n"
                           "- Runs well up to 50 million calculations\n"
                           "   EX: 500 PlotPoints * 100000 BufferSize")
        left_layout.addWidget(user_notes)

#Right Area (vertical) - right side of window
        right_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(right_layout, 4)

        #Graph 1:
        plot1 = pg.PlotWidget(title="Original Signal vs X", background='w')
        legend1 = plot1.addLegend()
        legend1.anchor((1,0), (1,0))
        right_layout.addWidget(plot1)

        #Input Area 1:
        input_layout1 = QtWidgets.QGridLayout()
        cols = 4
        for i, p in enumerate(params[18:22]):
            name, label = p[0], p[2]
            row = i // cols
            col = i % cols

            h_layout = QtWidgets.QHBoxLayout()
            h_layout.addWidget(QtWidgets.QLabel("<b>"+label+"</b>"))
            h_layout.addWidget(self.line_edits[name])
            input_layout1.addLayout(h_layout, row, col)
        right_layout.addLayout(input_layout1)

        #Fit Results:
        result_layout = QtWidgets.QHBoxLayout()
        self.result_text = QtWidgets.QLabel()
        result_layout.addWidget(self.result_text)
        result_layout.addStretch(1)

        #Label:
        output2expected = QtWidgets.QLabel()
        output2expected.setText("Output ≈ <sup>1</sup>&frasl;<sub>Diminish</sub> * Expected(<sup>x</sup>&frasl;<sub>Stretch</sub> - Shift)")
        right_layout.addWidget(output2expected)

        #Graph 2:
        plot2 = pg.PlotWidget(title="Demodulated Signal vs X", background='w')
        legend2 = plot2.addLegend()
        legend2.anchor((1,0), (1,0))
        right_layout.addWidget(plot2)

        #Input Area 2:
        input_layout2 = QtWidgets.QGridLayout()
        for i, p in enumerate(params[22:]):
            name, label = p[0], p[2]
            row = i // cols
            col = i % cols

            h_layout = QtWidgets.QHBoxLayout()
            h_layout.addWidget(QtWidgets.QLabel("<b>"+label+"</b>"))
            h_layout.addWidget(self.line_edits[name])
            input_layout2.addLayout(h_layout, row, col)
        right_layout.addLayout(input_layout2)

        #Plot Curve Initialization:
        self.curve_orig = plot1.plot(pen=pg.mkPen(color='r', width=2), name="Original Signal")
        self.curve_out = plot2.plot(pen=pg.mkPen(color='b', width=2), name="Output Signal")
        self.curve_expected = plot2.plot(pen=pg.mkPen(color='r', width=2), name="Expected Signal")
        self.curve_adjusted = plot2.plot(pen=pg.mkPen(color='g', width=2), name="Adjusted Signal")

        #Show Curves Options:
        curve_params = [ ("Output", self.curve_out), ("Expected", self.curve_expected), ("Adjusted", self.curve_adjusted) ]
        for name, curve in curve_params:
            cb = QtWidgets.QCheckBox(f"Show {name} Signal")
            cb.setChecked(True)
            cb.stateChanged.connect(lambda state, c=curve, box=cb: c.setVisible(box.isChecked()))
            result_layout.addWidget(cb)
        right_layout.insertLayout(2, result_layout)

        self.update_plot()

    def update_plot(self):
        try:
            # Read input v
            v = {}
            for name, (widget, extract) in self.inputs.items():
                v[name] = extract(widget)

            #Signal Setup
            signal = 0
            if v["signal_type"] == "Lorentzian": 
                signal = make_lorentzian(v["l_center"], v["l_HW"], v["l_amp"])
            else:
                signal = make_antilorentzian(v["al_center"], v["al_HW"], v["al_amp"])

            #Noise Setup
            jT = jR = sI = sR = oRMS = rTU = rTD = rSU = rSD = bD = bMIN = bMAX = 0
            if v["Johnson Noise"]:
                jT, jR = v["jT"], v["jR"]
            if v["Shot Noise"]:
                sI, sR = v["sI"], v["sR"]
            if v["1/f Noise"]:
                oRMS = v["oRMS"]
            if v["Random Telegraph Noise"]:
                rTU, rTD, rSU, rSD = v["rTU"], v["rTD"], v["rSU"], v["rSD"]
            if v["Bit Noise"]:
                bD, bMIN, bMAX = v["bD"], v["bMIN"], v["bMAX"]

            # Run lock-in emulator
            LI = Lock_in_emulator(
                signal,
                v["f_input"],
                v["phase_input"],
                v["xstart_input"],
                v["xstop_input"],
                v["xamp_input"],
                v["time_input"],
                v["dt_input"],
                v["TC_input"],
                v["order_input"],
                v["plotpoints_input"],
                v["buffersize_input"],
                jT, jR, sI, sR, oRMS, rTU, rTD, rSU, rSD, bD, bMIN, bMAX
            )
            LI.run()

            # Update plots
            self.curve_orig.setData(LI.x_plot, LI.original_signal)
            self.curve_out.setData(LI.x_plot, LI.output_signal)
            self.curve_expected.setData(LI.x_plot, LI.expected_signal)
            self.curve_adjusted.setData(LI.x_plot, LI.adjusted_signal)

            # Update results
            self.result_text.setText(f"<b>Diminish:</b> {LI.diminish:.6f},  "
                                     f"<b>Shift:</b> {LI.shift:.6f},  "
                                     f"<b>Stretch:</b> {LI.stretch:.6f},  "
                                     f"<b>SNR</b>: {LI.snr:.6f}")

        except Exception as e:
            self.result_text.setText(f"Error: {e}")

    def reset_fields(self):
        for p in params:
            name, default = p[0], p[1]
            self.line_edits[name].clear()
            self.line_edits[name].setText(str(default))
        self.update_plot()

def run():
    app = QtWidgets.QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()