import os

import numpy as np
import psutil
from torch.utils.data import DataLoader, Dataset


class MyDataset(Dataset):
    def __init__(self):
        self.data = np.random.rand(10000, 224, 244, 3)

    def __len__(self):
        return self.data.shape[0]

    def __getitem__(self, idx):
        return self.data[idx] + 1.0

if __name__ == "__main__":
    loader = DataLoader(MyDataset(), batch_size=4096, num_workers=os.cpu_count(), persistent_workers=True)
    for epoch in range(9):
        for step, _ in enumerate(loader):
            print("Epoch: {}, step: {}, RAM used: {:.2f} GB".format(epoch, step, psutil.virtual_memory().used / 1e9))
