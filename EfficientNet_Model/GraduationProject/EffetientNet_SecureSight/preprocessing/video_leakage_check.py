import os
import re

def check_video_leakage(train_dir, val_dir):
    def get_video_ids(directory):
        video_ids = set()
        if not os.path.exists(directory):
            print(f"Directory not found: {directory}")
            return video_ids
            
        for root, _, files in os.walk(directory):
            for f in files:
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    # Extract video ID: everything before the last underscore (frame part)
                    # Example: v_Arrest_001_frame010.jpg -> v_Arrest_001
                    match = re.match(r'(v_.*?_\d+)_frame', f)
                    if match:
                        video_ids.add(match.group(1))
                    else:
                        # Fallback: everything before the first underscore with a number
                        parts = f.split('_')
                        if len(parts) >= 3:
                            video_ids.add('_'.join(parts[:3]))
        return video_ids

    print(f"Scanning Train: {train_dir}")
    train_ids = get_video_ids(train_dir)
    print(f"Scanning Val:   {val_dir}")
    val_ids = get_video_ids(val_dir)

    intersection = train_ids.intersection(val_ids)

    print("\n" + "="*40)
    print("VIDEO-LEVEL LEAKAGE REPORT")
    print("="*40)
    print(f"Total unique videos in train: {len(train_ids)}")
    print(f"Total unique videos in val:   {len(val_ids)}")
    print(f"Number of shared video IDs:   {len(intersection)}")

    if len(intersection) > 0:
        print("\nShared Video ID Examples (Top 10):")
        for vid in list(intersection)[:10]:
            print(f"  - {vid}")
        print("\nCRITICAL LEAKAGE DETECTED (same video in train and val)")
    else:
        print("\nNo video-level leakage detected")
    print("="*40)

if __name__ == "__main__":
    # Standard paths from config
    TRAIN_DIR = "/home/secure-sight/Code/extracted_features_merged"
    VAL_DIR = "/home/secure-sight/Code/extracted_featuers_merged_split/Val"
    
    check_video_leakage(TRAIN_DIR, VAL_DIR)