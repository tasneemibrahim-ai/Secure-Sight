import paramiko
import base64

def run():
    # STEP 4 FIX CODE
    cmd_fix = """import os, re, shutil, random
from collections import defaultdict

train_src = '/home/secure-sight/Code/extracted_features_merged'
val_src   = '/home/secure-sight/Code/extracted_featuers_merged_split/test'
clean_root = '/home/secure-sight/Code/clean_split'

def extract_id(name):
    return re.sub(r'_x264\.npz$', '', name)

class_videos = defaultdict(lambda: defaultdict(list))
for src in [train_src, val_src]:
    if not os.path.exists(src): continue
    for root, _, files in os.walk(src):
        class_name = os.path.basename(root)
        for f in files:
            if f.endswith('.npz'):
                vid = extract_id(f)
                class_videos[class_name][vid].append(os.path.join(root, f))

if os.path.exists(clean_root): shutil.rmtree(clean_root)
os.makedirs(os.path.join(clean_root, 'train'), exist_ok=True)
os.makedirs(os.path.join(clean_root, 'val'), exist_ok=True)

for cls, vids_dict in class_videos.items():
    vids = sorted(list(vids_dict.keys()))
    random.seed(42); random.shuffle(vids)
    split = int(len(vids) * 0.8)
    
    for i, vid in enumerate(vids):
        target = 'train' if i < split else 'val'
        dst_dir = os.path.join(clean_root, target, cls)
        os.makedirs(dst_dir, exist_ok=True)
        for fpath in vids_dict[vid]:
            shutil.copy2(fpath, os.path.join(dst_dir, os.path.basename(fpath)))

print('DATASET FIXED')
"""
    b64_fix = base64.b64encode(cmd_fix.encode()).decode()
    remote_cmd_fix = f"echo {b64_fix} | base64 -d | python3"
    
    host = "10.55.205.205"
    user = "secure-sight"
    pw = "S#SiT#$38337"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=pw)
        print("--- STEP 4 ---")
        _, stdout, stderr = client.exec_command(remote_cmd_fix)
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err: print("STDERR:", err)
        
        # Step 5: Verify
        print("--- STEP 5 ---")
        cmd_verify = """import os, re
train_path = '/home/secure-sight/Code/clean_split/train'
val_path   = '/home/secure-sight/Code/clean_split/val'
def extract_id(name): return re.sub(r'_x264\.npz$', '', name)
def collect_ids(path):
    ids = set()
    for root, _, files in os.walk(path):
        for f in files:
            if f.endswith('.npz'): ids.add(extract_id(f))
    return ids
t = collect_ids(train_path); v = collect_ids(val_path); shared = t & v
print(f'Train videos: {len(t)}'); print(f'Val videos: {len(v)}'); print(f'Shared videos: {len(shared)}')
if not shared: print('VERIFICATION PASSED')
else: print('VERIFICATION FAILED')
"""
        b64_v = base64.b64encode(cmd_verify.encode()).decode()
        _, stdout, _ = client.exec_command(f"echo {b64_v} | base64 -d | python3")
        print(stdout.read().decode())
        
    finally:
        client.close()

if __name__ == "__main__":
    run()
