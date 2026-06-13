# Binary Star Relativity Simulator

A high-precision C++ simulation of tight binary star systems (such as binary neutron stars or pulsars like PSR B1913+16) incorporating Post-Newtonian (1PN, 2PN, and 2.5PN gravitational radiation reaction) corrections from General Relativity. 

The simulation utilizes the **Dormand-Prince 5(4)** embedded Runge-Kutta method with an adaptive time-step algorithm to guarantee numerical stability and efficiency during close encounters (periastron passages).

---

## Features
- **Adaptive Time-Stepping**: Automatically decreases the step size ($dt$) when the bodies are close to capture high-acceleration dynamics accurately, and increases it when they separate to speed up execution.
- **Relativistic Corrections**: Implements Einstein's General Relativity corrections up to 2.5PN order, capturing orbital precession and orbital decay due to gravitational wave emission.
- **Python Post-Processing**: Includes scripts to automatically plot orbital parameters, trace energy dissipation, and identify local separation minima (periastrons) to measure orbital period decay.

---

## Project Structure
- `src/` - Contains C++ source files (`main.cpp`, `Simulation.cpp`, `Vector.cpp`) and headers (`Simulation.h`, `Vector.h`).
- `build/` - The build directory containing CMake/Ninja configurations and compiled binaries.
- `python/` - Python scripts for visualization and analysis (`draw.py`, `getMins.py`, `getMinsAndDev.py`).

---

## Prerequisites

Ensure you have the following installed on your environment (Linux / WSL Ubuntu / MinGW-w64 is highly recommended):
- A C++17 compatible compiler (e.g., GCC / Clang)
- **CMake** (v3.15+)
- **Ninja** build system (`ninja-build`)
- **Python 3** with `numpy` and `matplotlib` packages installed

To install all dependencies on Ubuntu / WSL, run:
```bash
sudo apt update
sudo apt install cmake build-essential ninja-build python3 python3-pip
pip install numpy matplotlib
```

---

## Compilation & Build Setup (Environment Reset)

If you transition between Windows (e.g., CLion) and Linux/WSL environments, stale windows configurations (`CMakeCache.txt`) will break the compilation with path errors. You must completely clear the build directory first.

1. Open your Linux terminal, navigate to the project root directory and reset the build folder:
```bash
rm -rf build
mkdir build
cd build
```


2. Configure the project with CMake under the native Linux environment:
```bash
cmake ..
```


3. Build the native Linux binary:
```bash
cmake --build .
```



This compiles the source files and generates a native executable named `main` inside the `build` directory.

---

## Running the Simulation

The simulation requires command-line arguments to specify execution parameters. Since it logs output data directly to the standard output (`stdout`), you should redirect the stream to a text file for post-processing.

Run the executable from inside your `build` directory:

```bash
./main <totalTime> [tStepInitial] [sampleInterval] [to2PN] [absTol] [relTol] > out.txt
```

### Argument Reference:

* `<totalTime>` (Required): Total simulation duration in seconds (e.g., `100000`).
* `[tStepInitial]` (Optional): Initial time-step in seconds (default: `1.0`).
* `[sampleInterval]` (Optional): Logging interval in seconds. Set to `0` to log *every* single adaptive step (default: `60.0`).
* `[to2PN]` (Optional): Set to `1` to disable the 2.5PN radiation term (conservative system, no orbital decay), or `0` for full relativistic decay (default: `0`).
* `[absTol]`, `[relTol]` (Optional): Absolute and relative error tolerances for the adaptive step engine (defaults: `1e-3`, `1e-9`).

### Example Command:

```bash
./main 100000 1.0 60.0 0 > out.txt
```

This runs the full relativistic simulation for 100,000 seconds, tracking data points every 60 seconds, and saves all outputs to `out.txt`.

---

## Data Analysis and Visualization

Once `out.txt` is populated inside the `build` directory, change your path back to the directory containing the python scripts to process the results:

1. **Plot Dashboard**: Generates a 4-panel visual layout showing orbital separation, relative velocity, adaptive step tracking, and energy dissipation.
```bash
python3 draw.py
```


2. **Find Periastrons**: Extracts local separation minima to calculate orbital period shifts over time.
```bash
python3 getMins.py
```


3. **Analyze Deviations**: Measures squared differences of periastron timestamps against initial references to quantify cumulative orbital decay.
```bash
python3 getMinsAndDev.py
```
