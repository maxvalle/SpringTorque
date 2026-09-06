def estimate_mainspring_torque(
    height_mm: float,
    thickness_mm: float,
    length_mm: float,
    youngs_modulus_gpa: float = 200.0,
) -> dict:
    """
    Estimates the torque of a watch mainspring given its dimensions.

    Parameters:
        height_mm (float): Width/height of the blade (b) in mm
        thickness_mm (float): Thickness of the blade (t) in mm
        length_mm (float): Active length of the spring (L) in mm
        youngs_modulus_gpa (float): Young's Modulus in GPa (default 200.0 GPa for steel/Nivaflex)

    Returns:
        dict: Torque values in N·mm, mN·m, and g·cm
    """
    # Convert GPa to N/mm^2
    E = youngs_modulus_gpa * 1000.0

    b = height_mm
    t = thickness_mm
    L = length_mm

    # Torque formula: M = (E * b * t^3) / (12 * L)
    torque_nmm = (E * b * (t ** 3)) / (12 * L)

    # Unit Conversions
    torque_mnm = torque_nmm  # 1 N·mm = 1 mN·m
    torque_gcm = torque_nmm * 10.19716  # Convert N·mm to g·cm

    return {
        "N_mm": round(torque_nmm, 4),
        "mN_m": round(torque_mnm, 4),
        "g_cm": round(torque_gcm, 2),
    }


DEFAULTS = {
    "height": 1.05,
    "thickness": 0.11,
    "length": 400.0,
    "modulus": 200.0,
}


def _prompt_float(prompt: str, default: float | None = None) -> float:
    suffix = f" [{default}]" if default is not None else ""
    while True:
        raw = input(f"{prompt}{suffix}: ").strip()
        if not raw and default is not None:
            return default
        try:
            value = float(raw)
        except ValueError:
            print("Please enter a number.")
            continue
        if value <= 0:
            print("Please enter a value greater than zero.")
            continue
        return value


def run_cli(args) -> None:
    interactive = any(v is None for v in (args.height, args.thickness, args.length))

    height = args.height if args.height is not None else _prompt_float("Height (mm)")
    thickness = args.thickness if args.thickness is not None else _prompt_float("Thickness (mm)")
    length = args.length if args.length is not None else _prompt_float("Length (mm)")
    if args.modulus is not None:
        modulus = args.modulus
    elif interactive:
        modulus = _prompt_float("Elastic modulus (GPa, optional)", default=200.0)
    else:
        modulus = 200.0

    results = estimate_mainspring_torque(height, thickness, length, modulus)

    print("--- Estimated Mainspring Torque ---")
    print(f"Dimensions: {height} × {thickness} × {length} mm  |  E = {modulus} GPa")
    print(f"Torque: {results['N_mm']} N·mm  |  {results['mN_m']} mN·m  |  {results['g_cm']} g·cm")


def launch_gui(
    height: float | None = None,
    thickness: float | None = None,
    length: float | None = None,
    modulus: float | None = None,
) -> None:
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import (
        QApplication,
        QDoubleSpinBox,
        QFrame,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QSlider,
        QVBoxLayout,
        QWidget,
    )

    height = DEFAULTS["height"] if height is None else height
    thickness = DEFAULTS["thickness"] if thickness is None else thickness
    length = DEFAULTS["length"] if length is None else length
    modulus = DEFAULTS["modulus"] if modulus is None else modulus

    class ParamRow(QWidget):
        changed = Signal()

        def __init__(
            self,
            label: str,
            minimum: float,
            maximum: float,
            step: float,
            decimals: int,
            value: float,
        ):
            super().__init__()
            self._step = step

            layout = QHBoxLayout(self)
            layout.setContentsMargins(0, 4, 0, 4)

            name = QLabel(label)
            name.setMinimumWidth(170)
            layout.addWidget(name)

            self.slider = QSlider(Qt.Orientation.Horizontal)
            self.slider.setRange(
                round(minimum / step),
                round(maximum / step),
            )
            layout.addWidget(self.slider, stretch=1)

            self.spin = QDoubleSpinBox()
            self.spin.setRange(minimum, maximum)
            self.spin.setSingleStep(step)
            self.spin.setDecimals(decimals)
            self.spin.setKeyboardTracking(True)
            self.spin.setMinimumWidth(100)
            self.spin.setAlignment(Qt.AlignmentFlag.AlignRight)
            layout.addWidget(self.spin)

            self.slider.valueChanged.connect(self._from_slider)
            self.spin.valueChanged.connect(self._from_spin)
            self.set_value(value)

        def value(self) -> float:
            return float(self.spin.value())

        def set_value(self, value: float) -> None:
            self.spin.blockSignals(True)
            self.slider.blockSignals(True)
            self.spin.setValue(value)
            self.slider.setValue(round(self.spin.value() / self._step))
            self.spin.blockSignals(False)
            self.slider.blockSignals(False)

        def _from_slider(self, ticks: int) -> None:
            self.spin.blockSignals(True)
            self.spin.setValue(ticks * self._step)
            self.spin.blockSignals(False)
            self.changed.emit()

        def _from_spin(self, value: float) -> None:
            self.slider.blockSignals(True)
            self.slider.setValue(round(value / self._step))
            self.slider.blockSignals(False)
            self.changed.emit()

    class MainWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("SpringTorque")
            self.setMinimumWidth(560)

            root = QVBoxLayout(self)
            root.setContentsMargins(20, 20, 20, 20)
            root.setSpacing(10)

            title = QLabel("Mainspring torque")
            title_font = QFont()
            title_font.setPointSize(22)
            title_font.setBold(True)
            title.setFont(title_font)
            root.addWidget(title)

            hint = QLabel("Drag a slider or type a value — torque updates immediately.")
            hint.setStyleSheet("color: #666;")
            root.addWidget(hint)

            self.rows: dict[str, ParamRow] = {}
            specs = (
                ("height", "Height / width (mm)", 0.40, 3.00, 0.01, 2, height),
                ("thickness", "Thickness (mm)", 0.040, 0.250, 0.001, 3, thickness),
                ("length", "Active length (mm)", 80.0, 800.0, 1.0, 0, length),
                ("modulus", "Elastic modulus (GPa)", 100.0, 250.0, 1.0, 0, modulus),
            )
            for key, label, lo, hi, step, decimals, default in specs:
                row = ParamRow(label, lo, hi, step, decimals, default)
                row.changed.connect(self.refresh)
                root.addWidget(row)
                self.rows[key] = row

            group = QGroupBox("Estimated torque")
            group_layout = QVBoxLayout(group)

            self.nmm_label = QLabel()
            torque_font = QFont()
            torque_font.setPointSize(24)
            torque_font.setBold(True)
            self.nmm_label.setFont(torque_font)
            group_layout.addWidget(self.nmm_label)

            extras = QHBoxLayout()
            self.mnm_label = QLabel()
            self.gcm_label = QLabel()
            extras.addWidget(self.mnm_label)
            extras.addWidget(QLabel("·"))
            extras.addWidget(self.gcm_label)
            extras.addStretch()
            group_layout.addLayout(extras)
            root.addWidget(group)

            formula = QLabel(
                "M = (E · b · t³) / (12 · L)    ·    defaults match a typical ETA 2824-2"
            )
            formula.setStyleSheet("color: #777;")
            root.addWidget(formula)

            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setStyleSheet("color: #ddd;")
            root.addWidget(line)

            buttons = QHBoxLayout()
            buttons.addStretch()
            reset = QPushButton("Reset to ETA 2824-2 defaults")
            reset.clicked.connect(self.reset)
            buttons.addWidget(reset)
            root.addLayout(buttons)

            self.refresh()

        def refresh(self) -> None:
            try:
                results = estimate_mainspring_torque(
                    self.rows["height"].value(),
                    self.rows["thickness"].value(),
                    self.rows["length"].value(),
                    self.rows["modulus"].value(),
                )
            except (ZeroDivisionError, ValueError):
                self.nmm_label.setText("—")
                self.mnm_label.setText("—")
                self.gcm_label.setText("—")
                return
            self.nmm_label.setText(f"{results['N_mm']:.4f}  N·mm")
            self.mnm_label.setText(f"{results['mN_m']:.4f}  mN·m")
            self.gcm_label.setText(f"{results['g_cm']:.2f}  g·cm")

        def reset(self) -> None:
            self.rows["height"].set_value(DEFAULTS["height"])
            self.rows["thickness"].set_value(DEFAULTS["thickness"])
            self.rows["length"].set_value(DEFAULTS["length"])
            self.rows["modulus"].set_value(DEFAULTS["modulus"])
            self.refresh()

    app = QApplication.instance() or QApplication([])
    app.setApplicationName("SpringTorque")
    window = MainWindow()
    window.show()
    app.exec()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Estimate watch mainspring torque from blade dimensions."
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Use the command-line interface instead of the GUI",
    )
    parser.add_argument("-H", "--height", type=float, help="Blade height/width in mm")
    parser.add_argument("-t", "--thickness", type=float, help="Blade thickness in mm")
    parser.add_argument("-L", "--length", type=float, help="Active length in mm")
    parser.add_argument(
        "-E",
        "--modulus",
        type=float,
        default=None,
        help="Elastic modulus (Young's modulus) in GPa (default: 200)",
    )
    args = parser.parse_args()

    if args.cli:
        run_cli(args)
        return

    launch_gui(args.height, args.thickness, args.length, args.modulus)


if __name__ == "__main__":
    main()
