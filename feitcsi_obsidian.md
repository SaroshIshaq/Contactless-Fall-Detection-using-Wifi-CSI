---
title: FeitCSI Master Software
tags: [csi, wifi, feitcsi, machine-learning, networking]
date: 2026-09-21
---

# FeitCSI Master Software

The FeitCSI Master is a tool designed to capture and extract WiFi Channel State Information (CSI) natively from compatible Intel NICs (such as AX200, AX210, and AX211) running on Ubuntu Linux (22.04 / 24.04).

## Features

- **Passive Target-Device Capture**: Extracts CSI natively from supported NICs.
- **Target MAC Filtering**: Includes a functional `--filter-mac` flag (and a GUI field) to listen and isolate traffic coming from specific MAC addresses, drastically reducing noise and storage footprint for targeted experiments.
- **Graphical Interface & Plots**: Supports plotting tools including a **Waterfall Plot** and **Status Light**, implemented in GTK (requires `gtkmm-3.0`).
- **Offline ML Pipeline**: Capable of reading extracted `.npz` and `.csv` files into a machine-learning baseline (`test_baseline_realpath.py`) to run fall detection models like Random Forests over time-series data.

## Project Structure

*   `src/`: C++ source code for packet injection, Netlink socket communication, arguments parsing, CSI logic.
*   `src/gui/`: GTK interface logic (Plots, StatusLights, MainWindow).
*   `bin/app`: Compiled binary executable.
*   `feitcsi_parse.py`: Extracts and standardizes `.csv` CSI logs into `.npz`.
*   `baseline_fall_detection.py`: Applies scikit-learn models to extracted CSI formats for activity recognition.

## Requirements

1.  Native Linux OS (WSL is unsupported).
2.  `iwlwifi` driver enabled with `csi_enabled` debugfs.
3.  C++ development headers: `libnl-3-dev`, `libnl-genl-3-dev`, `libpcap-dev`, `libgtkmm-3.0-dev`.
4.  Python stack for offline validation: `numpy`, `scipy`, `scikit-learn`, `matplotlib`.

## Quick Start
```bash
# Setup Workspace & Compile
cd FeitCSI-master
make clean && make -j$(nproc)

# Run Capture on Specific Device MAC
sudo ./bin/app -i measure -F AA:BB:CC:DD:EE:FF -o capture.pcap
```
