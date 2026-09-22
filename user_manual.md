# FeitCSI User Manual

This manual provides instructions and command examples for using the FeitCSI tool for capturing CSI (Channel State Information).

## Installation and Prerequisites

1.  **Hardware Requirements:** Ensure you have an Intel AX200/AX210/AX211 network interface card (NIC).
2.  **OS Requirements:** Native Ubuntu Linux (22.04 or 24.04). WSL will not work as it lacks the required hardware interface.
3.  **Kernel/Driver:** Ensure the iwlwifi driver is loaded and the CSI debugfs is enabled (`/sys/kernel/debug/iwlwifi/.../iwlmvm/csi_enabled`).

## Running the Application

The executable is located in the `bin/` directory after compilation.

### GUI Mode
To run the application with the graphical user interface:
```bash
./bin/app -x
# OR
./bin/app --gui
```
In the GUI, you can input a target MAC address in the **Target MAC filter** field.

### CLI Mode (Capture/Measure)
To capture CSI data without the GUI, run the `measure` mode. You can filter the capture for a specific MAC address using the `-F` flag.

```bash
# Basic capture
./bin/app -i measure

# Capture and filter only frames from a specific MAC (e.g., AA:BB:CC:DD:EE:FF)
./bin/app -i measure -F AA:BB:CC:DD:EE:FF

# Capture and save to a specific file
./bin/app -i measure -o capture_output.pcap
```

### Full List of Options

*   `-x, --gui`: Run application in GUI
*   `-i, --mode=MODE`: Mode of program (`measure`, `inject`, `measureinject`, `ftm`, etc.)
*   `-F, --filter-mac=MAC`: Keep only CSI frames whose source MAC matches `xx:xx:xx:xx:xx:xx`
*   `-o, --output-file=FILE`: Output file where measurements should be stored
*   `-f, --frequency=FREQUENCY`: Frequency to measure/inject CSI
*   `-w, --channel-width=WIDTH`: Channel width (20, 40, HT40-, 80, 160)
*   `-s, --spatial-streams=NUM`: Number of spatial streams (1 or 2)
*   `-m, --mcs=MCS`: MCS index (0-11)
*   `-p, --plot`: Plot CSI data

For the full list of parameters, run:
```bash
./bin/app --help
```
