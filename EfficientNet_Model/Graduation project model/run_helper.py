import os
import subprocess

def main():
    python_exe = r"e:\tasnim\GraduationProject\SecureSight\venv310\Scripts\python.exe"
    script = r"e:\tasnim\GraduationProject\SecureSight\prepare_model.py"
    
    # Run the script
    if os.path.exists(python_exe) and os.path.exists(script):
        print(f"Running {script} using {python_exe}...")
        result = subprocess.run([python_exe, script], capture_output=True, text=True, cwd=r"e:\tasnim\GraduationProject\SecureSight")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        print("Return code:", result.returncode)
    else:
        print("Paths do not exist.")
        if not os.path.exists(python_exe): print(f"Missing: {python_exe}")
        if not os.path.exists(script): print(f"Missing: {script}")

if __name__ == "__main__":
    main()
