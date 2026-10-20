"""Download training datasets via matminer into data/raw/ (gitignored)."""
import os
from matminer.datasets import load_dataset

os.makedirs("data/raw", exist_ok=True)
for name in ["brgoch_superhard_training", "matbench_glass"]:
    df = load_dataset(name)
    df.to_csv(f"data/raw/{name}.csv", index=False)
    print(name, df.shape, list(df.columns)[:8])
