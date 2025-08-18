import json
import csv
import os

# Paths
csv_path = "/Users/charanrathore/Desktop/Shuffled_Expanded1.csv"  # Update this
tracking_file = "/Users/charanrathore/Desktop/bolt_tracking.json"  # Update this
stl_files_dir = "/Users/charanrathore/Desktop/stl_files"  # Update this

# Check if all 1000 STL files exist
stl_files = [f for f in os.listdir(stl_files_dir) if f.endswith('.stl')]
print(f"Found {len(stl_files)} STL files (should be 1000)")

# Load tracking data
with open(tracking_file, 'r') as f:
    tracking_data = json.load(f)

used_indices = tracking_data["used_indices"]
last_bolt_num = tracking_data["last_bolt"]

print(f"Last bolt number: {last_bolt_num} (should be 1000)")
print(f"Number of used indices: {len(used_indices)} (should be 1000)")

# Check for duplicates in used indices
if len(used_indices) != len(set(used_indices)):
    print("WARNING: Duplicate indices found in tracking file!")
else:
    print("No duplicate indices found in tracking file.")

# Load CSV and extract dimensions for each used index
dimensions = []
with open(csv_path, 'r') as file:
    # Skip header
    next(file)
    
    # Read all rows
    rows = list(csv.reader(file))
    
    # Extract dimensions for each used index
    for idx in used_indices:
        if idx < len(rows):
            dim = tuple(float(val) for val in rows[idx][1:6])  # Convert to float for comparison
            dimensions.append((idx, dim))

# Check for duplicates in dimensions
dim_set = set()
duplicates = []
for idx, dim in dimensions:
    if dim in dim_set:
        duplicates.append((idx, dim))
    dim_set.add(dim)

if duplicates:
    print(f"WARNING: Found {len(duplicates)} bolts with duplicate dimensions!")
    for idx, dim in duplicates[:5]:  # Show first 5 duplicates
        print(f"  Index {idx}: {dim}")
    if len(duplicates) > 5:
        print(f"  ... and {len(duplicates) - 5} more")
else:
    print("SUCCESS: All bolts have unique dimensions!")

# Print file size distribution as a basic check
sizes = [os.path.getsize(os.path.join(stl_files_dir, f)) for f in stl_files]
avg_size = sum(sizes) / len(sizes)
min_size = min(sizes)
max_size = max(sizes)
print(f"STL file sizes: Min={min_size}, Max={max_size}, Avg={avg_size:.2f}")