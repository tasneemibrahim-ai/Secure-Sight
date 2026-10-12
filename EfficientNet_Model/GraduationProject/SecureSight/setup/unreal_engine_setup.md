# Unreal Engine Setup for SecureSight

This document outlines how to set up an Unreal Engine project to work with AirSim and the SecureSight drone simulation.

## 1. Create a New Unreal Project
1. Open Unreal Engine.
2. Create a new C++ project. Choose a template like "Blank" or one of the automotive/architecture templates if you want a pre-built city/environment.
3. Name your project (e.g., `SecureSightEnv`).
4. Ensure "No Starter Content" is selected to keep the project size manageable, unless you need it.

## 2. Add the AirSim Plugin
1. Locate the `AirSim` folder you built (see `install_airsim_guide.md`).
2. Copy the `Unreal/Plugins` folder from the AirSim directory.
3. Paste it into your newly created Unreal project directory (e.g., `Documents\Unreal Projects\SecureSightEnv\Plugins`).

## 3. Configure the Project
1. Open the `.uproject` file in a text editor.
2. Add the AirSim plugin dependency:
   ```json
   "Plugins": [
     {
       "Name": "AirSim",
       "Enabled": true
     }
   ]
   ```
3. Right-click the `.uproject` file and select **"Generate Visual Studio project files"**.

## 4. Build and Run
1. Open the `.sln` file in Visual Studio.
2. Set your configuration to "Development Editor" and "Win64".
3. Press `F5` to build and open the Unreal Editor.

## 5. Setup Game Mode and Start Simulation
1. In the Unreal Editor, go to `Window` > `World Settings`.
2. Set the **GameMode Override** to `AirSimGameMode`.
3. Press the **Play** button in the editor.
4. When prompted by AirSim (usually a popup asking for vehicle type), choose **Multirotor**.

Your environment is now ready to receive commands from `START_SIMULATION.py`!
