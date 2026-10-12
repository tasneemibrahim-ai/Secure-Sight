import numpy as np
import os
paths = [
    '/home/secure-sight/Code/clean_split/train/Arrest/Arrest001_x264.npz',
    '/home/secure-sight/Code/clean_split/train/Normal_Videos/1_Normal_Videos001_x264.npz'
]
for path in paths:
    print(f"--- {os.path.basename(path)} ---")
    if os.path.exists(path):
        data = np.load(path)
        for k in data.files:
            print(f"{k}: {data[k].shape}")
    else:
        print("Path not found at " + path)
