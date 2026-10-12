# AirSim Installation & Setup Guide

This guide covers the necessary steps to set up AirSim for the SecureSight Drone Simulation.

## 1. Prerequisites
- **OS**: Windows 10/11
- **Visual Studio 2022**: Make sure to install "Desktop development with C++" and "Windows 10 SDK".

## 2. Install Unreal Engine
AirSim requires Unreal Engine to render the simulation environment.
- Download and install the **Epic Games Launcher**.
- Go to the Unreal Engine tab > Library.
- Install **Unreal Engine 5.1** (or 4.27 depending on compatibility requirements of your specific AirSim fork, but 5.1 is generally recommended for newer builds).

## 3. Build AirSim
Since the official Microsoft AirSim repository is archived, you may need to use a maintained fork (like Colosseum) or build the original from source.

1. Open `Developer Command Prompt for VS 2022`.
2. Clone the repository:
   ```bash
   git clone https://github.com/microsoft/AirSim.git
   cd AirSim
   ```
3. Run the build script:
   ```cmd
   build.cmd
   ```

## 4. Python API Setup
The Python client is required to control the drone from the SecureSight scripts.

1. Activate your SecureSight virtual environment.
2. Install the `msgpack-rpc-python` and `airsim` packages:
   ```bash
   pip install msgpack-rpc-python
   pip install airsim
   ```

## 5. Common Fixes & Troubleshooting
- **Cannot connect to AirSim**: Ensure the Unreal Engine simulation is actively running (Play button clicked) before starting the SecureSight python script.
- **RPC Error**: Check if port `41451` is blocked by a firewall.
- **Python version issues**: AirSim Python packages sometimes struggle with Python 3.12+. Use Python 3.8-3.11 if possible.
