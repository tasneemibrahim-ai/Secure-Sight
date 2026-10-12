import os
from pathlib import Path

def main():
    print("========================================")
    print("  SecureSight Checkpoint Validator      ")
    print("========================================")

    setup_dir = Path(__file__).resolve().parent
    project_root = setup_dir.parent
    
    search_paths = [
        project_root / "models",
        project_root / "exports",
        project_root / "deployment_simulation",
        project_root / "training" / "output" / "checkpoints"
    ]
    
    found_pth = []
    found_onnx = []
    
    for path in search_paths:
        if path.exists() and path.is_dir():
            found_pth.extend(list(path.glob("*.pth")))
            found_onnx.extend(list(path.glob("*.onnx")))
            
    print("\n--- Discovered Models ---")
    if not found_pth and not found_onnx:
        print("  [WARN] No .pth or .onnx models found in standard directories.")
    else:
        for m in found_pth:
            print(f"  [PTH]  {m.relative_to(project_root)}")
        for m in found_onnx:
            print(f"  [ONNX] {m.relative_to(project_root)}")

    # Check loadability if torch is installed
    loadable = False
    best_model_path = None
    
    try:
        import torch
        if found_pth:
            # Try to load the first one, preferably best_model.pth
            target = next((m for m in found_pth if m.name == "best_model.pth"), found_pth[0])
            best_model_path = str(target.relative_to(project_root))
            print(f"\n--- Validation ---")
            print(f"  Attempting to load: {target.name}...")
            
            # Simple load test (metadata only if possible, or full load to CPU)
            try:
                checkpoint = torch.load(target, map_location="cpu", weights_only=False)
                print("  [OK] Successfully loaded checkpoint to CPU.")
                loadable = True
            except Exception as e:
                print(f"  [FAIL] Failed to load checkpoint: {e}")
        else:
             print("\n--- Validation ---")
             print("  [SKIP] No .pth files to load.")
    except ImportError:
        print("\n--- Validation ---")
        print("  [SKIP] PyTorch not installed, cannot validate .pth loadability.")

    # Save results for final report
    out_path = Path(__file__).parent / ".model_report.json"
    import json
    with open(out_path, "w") as f:
        json.dump({
            "models_found": len(found_pth) + len(found_onnx),
            "best_model_path": best_model_path,
            "loadable": loadable
        }, f, indent=2)

if __name__ == "__main__":
    main()
