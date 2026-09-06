# SpringTorque

Calculation of a watch mainspring torque from blade height, thickness, active length, and elastic modulus.

Torque is estimated with:

```
M = (E · b · t³) / (12 · L)
```

Results are shown in **N·mm**, **mN·m**, and **g·cm**. The default values match a typical ETA 2824-2 mainspring (1.05 × 0.11 × 400 mm, *E* = 200 GPa).
The default value for the elastic module is the typical value for stainless steel and Nivaflex.

## Requirements

- Python 3.10 or later
- macOS or Linux (the GUI uses Qt / PySide6)

## Run

Create a virtual environment, install dependencies, and start the app:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python springtorque.py
```

The GUI opens with sliders and numeric fields. Changing a value updates the torque immediately.

### Command line

Pass starting dimensions to the GUI, or use `--cli` for a one-shot calculation:

```bash
python springtorque.py -H 1.05 -t 0.11 -L 400
python springtorque.py -H 1.05 -t 0.11 -L 400 -E 210
python springtorque.py --cli -H 1.05 -t 0.11 -L 400
```

| Option | Meaning |
| --- | --- |
| `-H`, `--height` | Blade height / width (mm) |
| `-t`, `--thickness` | Blade thickness (mm) |
| `-L`, `--length` | Active length (mm) |
| `-E`, `--modulus` | Elastic modulus (GPa), default 200 |
| `--cli` | Print the result instead of opening the GUI |

## Build

`build.sh` installs dependencies in a temporary `venv`, compiles with [Nuitka](https://nuitka.net/), then removes that environment.

```bash
chmod +x build.sh
./build.sh
```

- **macOS:** produces `dist/SpringTorque.app` (ad-hoc signed)
- **Linux:** produces a single `dist/SpringTorque` binary

A C compiler is required (Xcode Command Line Tools on macOS, or `gcc`/`clang` on Linux).
