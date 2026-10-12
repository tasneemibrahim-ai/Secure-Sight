import subprocess
import os
import sys

def run_command(cmd):
    print(f"\nExecuting: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"!!! Command failed with return code {result.returncode}")
    return result.returncode

def main():
    # Parameters for the rerun
    start_batch = 5
    end_batch = 9
    runs_per_batch = 5
    epochs = 20
    
    print(f"============================================================")
    print(f"  SecureSight Batch Rerun Script (Batches {start_batch}-{end_batch})")
    print(f"============================================================")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    train_script = os.path.join(script_dir, "train.py")
    report_script = os.path.join(script_dir, "generate_reports.py")
    
    for b in range(start_batch, end_batch + 1):
        print(f"\n{'='*60}")
        print(f"  STARTING BATCH {b}")
        print(f"{'='*60}")
        
        for r in range(1, runs_per_batch + 1):
            run_name = f"batch{b}_run{r}"
            print(f"\n--- Batch {b} | Run {r}/{runs_per_batch} ({run_name}) ---")
            
            cmd = [
                "python", train_script,
                "--epochs", str(epochs),
                "--batch", str(b),
                "--run_name", run_name
            ]
            
            run_command(cmd)
            
    print(f"\n\n============================================================")
    print(f"  All batches {start_batch}-{end_batch} completed!")
    print(f"  Regenerating consolidated reports...")
    print(f"============================================================")
    
    # Regenerate all reports at the end
    run_command(["python", report_script, "--all"])

if __name__ == "__main__":
    main()
