# SPDX-FileCopyrightText: 2025 Matteo Lai <matteo.lai3@unibo.it>
# SPDX-License-Identifier: NPOSL-3.0

import os
import numpy as np
from glob import glob

from sim_toolkit.datasets.base import BaseDataset, BidsDataset

def _to_chw(arr: np.ndarray) -> np.ndarray:
    """
    Convert a single image array to CHW (C,H,W).
    Accepts:
      - (H, W) -> (1, H, W)
      - (H, W, C) with C in {1,3,4} -> (C, H, W)
      - (C, H, W) with C in {1,3,4} -> (C, H, W)
    Raises on ambiguous shapes (e.g., volumetric).
    """
    if arr.ndim == 2:
        return arr[np.newaxis, ...]  # (1,H,W)
    if arr.ndim == 3:
        # Treat last-dim-small as channels (H,W,C)
        if arr.shape[-1] in (1, 3, 4) and arr.shape[0] > 8 and arr.shape[1] > 8:
            return np.moveaxis(arr, -1, 0)  # (C,H,W)
        # Already CHW?
        if arr.shape[0] in (1, 3, 4) and arr.shape[1] > 8 and arr.shape[2] > 8:
            return arr  # (C,H,W)
        # Looks like a volume or multi-slice (H,W,D) with D not small
        raise ValueError(f"Ambiguous 3D shape {arr.shape}: looks like a volume/multi-slice; use a 3D loader.")

    raise ValueError(f"Unsupported array shape {arr.shape} (expected 2D image or 2D+channels).")

def _require_nibabel():
    try:
        import nibabel as nib  # noqa: F401
    except Exception as e:
        raise RuntimeError(
            "NIfTI support requires 'nibabel'. Install with: pip install 'sim_toolkit[nifti]'"
        ) from e    

class NiftiDataset2D(BaseDataset):
    def _load_files(self):
        """
        Load 2D NIfTI data and return NumPy array in (N, C, H, W) format.

        - If `path_data` is a file (.nii / .nii.gz):
            Assumes data stored as (W, H, C, N) and converts to (N, C, H, W).
        - If `path_data` is a folder:
            Loads all *.nii / *.nii.gz in the folder. Each file must contain a
            single 2D image (H,W) or (H,W,C) with C in {1,3,4}. Stacks to (N,C,H,W).
        """
        _require_nibabel()
        import nibabel as nib

        p = os.path.abspath(self.path_data)

        # --- Case A: single file ---
        if os.path.isfile(p) and (p.endswith(".nii") or p.endswith(".nii.gz")):
            data = nib.load(p)
            data = np.asanyarray(data.dataobj) # numpy array of shape (W,H,C,N)
            data = np.float64(data)

            # Swap axes to have the format (N,C,W,H)
            data = np.swapaxes(data, 0,3)
            data = np.swapaxes(data, 1,2)   # after swapping axes, array shape (N,C,H,W)

            return data # [batch_size, n_channels, img_resolution, img_resolution]

        # --- Case B: folder of files ---
        if os.path.isdir(p):
            file_paths = sorted(
                glob(os.path.join(p, "*.nii")) + glob(os.path.join(p, "*.nii.gz"))
            )
            if not file_paths:
                raise RuntimeError(
                    f"No NIfTI files (.nii/.nii.gz) found under directory: {p}"
                )

            images = []
            bad = []

            for fp in file_paths:
                try:
                    img = nib.load(fp)
                    arr = np.asanyarray(img.dataobj)

                    # Allow 2D or 2D+channels images only
                    if arr.ndim == 4:
                        # Many NIfTI files store (H,W,C,N) with N=1 for a single image.
                        # Accept this special case and squeeze N if feasible.
                        if arr.shape[-1] == 1 and arr.shape[2] in (1, 3, 4):
                            arr = arr[..., 0]  # (H,W,C)
                        else:
                            raise ValueError(f"{os.path.basename(fp)}: 4D array {arr.shape} not supported for 2D dataset.")

                    arr = arr.astype(np.float32, copy=False)
                    chw = _to_chw(arr)  # (C,H,W)
                    images.append(chw)
                except Exception as e:
                    bad.append((os.path.basename(fp), str(e)))

            if not images:
                lines = [f"No readable 2D NIfTI images loaded from {p}."]
                if bad:
                    lines.append("Some reasons:")
                    for name, reason in bad[:5]:
                        lines.append(f"  - {name}: {reason}")
                raise RuntimeError("\n".join(lines))

            # Ensure consistent (C,H,W)
            shapes = {im.shape for im in images}
            if len(shapes) != 1:
                raise ValueError(
                    f"Inconsistent image shapes in folder: {sorted(shapes)}. "
                    "Please resample/crop to a uniform (C,H,W) shape."
                )

            data = np.stack(images, axis=0)  # (N,C,H,W)
            return data

        # --- Neither file nor folder ---
        raise RuntimeError(
            f"`path_data` must be a NIfTI file (.nii/.nii.gz) or a directory; got: {p}"
        )

    def _load_raw_labels(self):
        pass

