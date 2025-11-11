from glob import glob
import os
import tifffile as tiff
import numpy as np

import sim_toolkit as sim

from sim_toolkit.datasets.base import BaseDataset

class TifDataset3D(BaseDataset):
    def _load_files(self):
        """
        Load all 3D TIFF volumes from the directory and return a NumPy array.
        Expects data in (N, C, D, H, W) format.
        """
        image_paths = sorted(glob(os.path.join(self.path_data, "*.tif")) + glob(os.path.join(self.path_data, "*.tiff")))
        volumes = []

        for path in image_paths:
            volume = tiff.imread(path)  # Load entire 3D volume
            if volume is not None:
                if volume.ndim == 3:
                    volume = np.expand_dims(volume, axis=0)  # Add channel axis -> (1, D, H, W)
                elif volume.ndim == 4:
                    pass  # Already has channel axis -> (C, D, H, W)
                else:
                    raise ValueError(f"Unsupported volume shape: {volume.shape} in {path}")
                volumes.append(volume)
            else:
                print(f"Warning: Could not load {path}")

        if not volumes:
            raise RuntimeError(f"No 3D TIFF images found in {self.path_data}")

        target_shape = (1, 65, 240, 240)

        padded_volumes = []

        for vol in volumes:
            c, d, h, w = vol.shape

            # Ensure current volume is not larger than target shape
            if (c > target_shape[0] or d > target_shape[1] or
                h > target_shape[2] or w > target_shape[3]):
                raise ValueError(f"Volume shape {vol.shape} is larger than target shape {target_shape}")

            # Compute padding for each axis (centered)
            pad_d_total = max(0, target_shape[1] - d)
            pad_h_total = max(0, target_shape[2] - h)
            pad_w_total = max(0, target_shape[3] - w)

            pad_d_before = pad_d_total // 2
            pad_d_after = pad_d_total - pad_d_before

            pad_h_before = pad_h_total // 2
            pad_h_after = pad_h_total - pad_h_before

            pad_w_before = pad_w_total // 2
            pad_w_after = pad_w_total - pad_w_before

            # np.pad takes pad widths in reverse axis order (last to first)
            # So format is ((w_before, w_after), (h_before, h_after), (d_before, d_after), (c_before, c_after))
            padding = (
                (0, 0),  # Channel dimension — no padding
                (pad_d_before, pad_d_after),
                (pad_h_before, pad_h_after),
                (pad_w_before, pad_w_after),
            )

            # Apply padding
            padded_vol = np.pad(vol, padding, mode='constant', constant_values=0)
            padded_volumes.append(padded_vol)

        data = np.stack(padded_volumes, axis=0)  # Shape: (N, C, D, H, W)
        return data # [batch_size, n_channels, img_resolution, img_resolution]

    def _load_raw_labels(self):
        pass

sim.compute(
    metrics=["fid","kid","is_","prdc","pr_auth","knn"],
    run_dir="./runs/exp3D",
    num_gpus=1,
    batch_size=64,
    data_type="3D",
    padding=True,
    real_dataset=TifDataset3D,
    real_params={"path_data": r"Z:\data\3D_data\C_HL60_3D_real"},
    synth_dataset=TifDataset3D,
    synth_params={"path_data": r"Z:\data\3D_data\C_HL60_3D_synt"},
)