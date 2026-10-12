import os
import sys
import json
import time
import subprocess
from pathlib import Path

def run_script(script_name):
    print(f"\n>>> Running {script_name}...")
    try:
        subprocess.check_call([sys.executable, str(Path(__file__).parent / script_name)])
        return True
    except subprocess.CalledProcessError:
        print(f"  [FAIL] Execution of {script_name} failed.")
        return False

def generate_final_report():
    setup_dir = Path(__file__).parent
    
    env_report_file = setup_dir / ".env_report.json"
    model_report_file = setup_dir / ".model_report.json"
    stack_report_file = setup_dir / ".stack_report.json"
    
    env_data = json.loads(env_report_file.read_text()) if env_report_file.exists() else {}
    model_data = json.loads(model_report_file.read_text()) if model_report_file.exists() else {}
    stack_data = json.loads(stack_report_file.read_text()) if stack_report_file.exists() else {}
    
    deps = env_data.get("dependencies", {})
    installed_deps = [pkg for pkg, stat in deps.items() if stat.get("installed")]
    missing_deps = [pkg for pkg, stat in deps.items() if not stat.get("installed")]
    
    report = {
        "report_type": "SETUP_VALIDATION_REPORT",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "environment": {
            "installed_dependencies": installed_deps,
            "missing_dependencies": missing_deps,
            "cuda_readiness": env_data.get("gpu", {}).get("cuda_available", False),
            "device": env_data.get("gpu", {}).get("device_name", "CPU")
        },
        "simulation_readiness": {
            "airsim_readiness": "airsim" in installed_deps,
            "unreal_readiness": "Manual verification required (see unreal_engine_setup.md)",
            "simulation_stack_verified": stack_data.get("stack_verified", False)
        },
        "model_readiness": {
            "models_found": model_data.get("models_found", 0),
            "best_model_path": model_data.get("best_model_path", None),
            "inference_readiness": model_data.get("loadable", False)
        },
        "exact_next_manual_step": ""
    }

    if missing_deps:
        report["exact_next_manual_step"] = "Run 'python setup/install_python_deps.py' to install missing dependencies."
    elif not report["model_readiness"]["inference_readiness"]:
        report["exact_next_manual_step"] = "Place 'best_model.pth' in the 'models/' directory to enable real inference instead of demo mode."
    elif not report["simulation_readiness"]["airsim_readiness"]:
        report["exact_next_manual_step"] = "Follow 'setup/install_airsim_guide.md' to install AirSim and Unreal Engine for full 3D simulation."
    else:
        report["exact_next_manual_step"] = "Setup complete. Run 'python simulation/START_SIMULATION.py' to launch the full system."

    out_file = setup_dir / "SETUP_VALIDATION_REPORT.json"
    with open(out_file, "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"\n[OK] Final report generated at: {out_file.relative_to(setup_dir.parent)}")
    
    # Clean up temp files
    for f in [env_report_file, model_report_file, stack_report_file]:
        if f.exists():
            f.unlink()

def main():
    print("========================================")
    print("  SecureSight Full Stack Setup Test     ")
    print("========================================")

    run_script("check_environment.py")
    run_script("check_model_checkpoint.py")
    run_script("verify_simulation_stack.py")
    
    print("\n>>> Running Integration Smoke Test...")
    project_root = Path(__file__).resolve().parent.parent
    start_sim_script = project_root / "simulation" / "START_SIMULATION.py"
    
    try:
        # Run a quick 10 frame simulation test
        subprocess.check_call([sys.executable, str(start_sim_script), "--frames", "10", "--device", "cpu"])
        print("\n  [OK] Smoke test completed successfully.")
    except subprocess.CalledProcessError:
        print("\n  [FAIL] Smoke test failed.")

    generate_final_report()

if __name__ == "__main__":
    main()
