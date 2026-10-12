import base64
cmd = """import os, re
train_path = '/home/secure-sight/Code/extracted_features_merged'
val_path = '/home/secure-sight/Code/extracted_featuers_merged_split/test'
extract_id = lambda name: re.sub(r'_x264\.npz$', '', name)
def collect_ids(path):
    ids = set()
    if not os.path.exists(path): return ids
    for root, _, files in os.walk(path):
        for f in files:
            if f.endswith('.npz'):
                ids.add(extract_id(f))
    return ids
train_ids = collect_ids(train_path)
val_ids = collect_ids(val_path)
shared = train_ids & val_ids
print(f'Train videos: {len(train_ids)}')
print(f'Val videos: {len(val_ids)}')
print(f'Shared videos: {len(shared)}')
if shared:
    print('🚨 LEAKAGE DETECTED')
    print(sorted(list(shared))[:10])
else:
    print('✅ NO LEAKAGE')
"""
print(base64.b64encode(cmd.encode()).decode())
