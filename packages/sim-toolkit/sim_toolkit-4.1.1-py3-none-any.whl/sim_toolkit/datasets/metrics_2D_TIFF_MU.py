from glob import glob
import os
import numpy as np
import cv2

import sim_toolkit as sim

from sim_toolkit.datasets.base import BaseDataset

class TifDataset2D(BaseDataset):
    def _load_files(self):
        """
        Load all TIFF images from the directory and return a NumPy array.
        Expects images to be in (N, C, H, W) format.
        """
        image_paths = sorted(glob(os.path.join(self.path_data, "*.tif")) + glob(os.path.join(self.path_data, "*.tiff")))
        images = []

        for path in image_paths:
            image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if image is not None:
                if len(image.shape) == 2:
                    image = np.expand_dims(image, axis=-1)  # Ensure single-channel images have (H, W, 1)
                images.append(image)
            else:
                print(f"Warning: Could not load {path}")

        if not images:
            raise RuntimeError(f"No TIFF images found in {self.path_data}")

        data = np.stack(images, axis=0)  # Shape: (N, H, W, C)
        data = np.moveaxis(data, -1, 1)  # Convert to (N, C, H, W) format
        return data # [batch_size, n_channels, img_resolution, img_resolution]

    def _load_raw_labels(self):
        pass

sim.compute(
    metrics=["fid","kid","is_","prdc","pr_auth","knn"],
    run_dir="./runs/exp2D",
    num_gpus=1,
    batch_size=64,
    data_type="2D",
    padding=True,
    real_dataset=TifDataset2D,
    real_params={"path_data": r"Z:\data\2D_data\A_PapSmear_2D_real"},
    synth_dataset=TifDataset2D,
    synth_params={"path_data": r"Z:\data\2D_data\A_PapSmear_2D_synt"},
)