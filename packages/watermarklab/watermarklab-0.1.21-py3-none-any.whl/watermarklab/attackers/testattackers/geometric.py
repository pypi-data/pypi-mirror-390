# Copyright (c) 2025 Jiale Chen <chenoly@outlook.com>. All rights reserved.
# SPDX-License-Identifier: MIT
import cv2
import torch
import random
import numpy as np
from numpy import ndarray
from typing import Optional, List
import torchvision.transforms as transforms
import torchvision.transforms.functional as TF
from watermarklab.utils.basemodel import BaseTestAttackModel


class Resize(BaseTestAttackModel):
    """
    A spatial resampling attack that scales an image down and then back up to the original resolution.

    This attack introduces interpolation artifacts (blurring, aliasing) by reducing the image
    to a smaller size and then upsampling it. It simulates common image processing operations like
    thumbnail generation or transmission over bandwidth-limited channels.

    The 'scale_p' parameter controls the downscaling factor:
        - 1.0: No change (identity)
        - 0.8: Reduce to 80% size, then upscale back
        - 0.5: Halve the dimensions, then double back (stronger distortion)

    This implementation uses `torchvision.transforms.Resize` for true batched processing,
    enabling GPU acceleration and eliminating Python loops.

    Note:
        - Input: List of uint8 RGB images [H, W, 3], range [0, 255]
        - Output: List of resized images, same shape and dtype
        - Uses torchvision for batched, GPU-accelerated resizing
    """

    def __init__(self, noisename: str = "Resize", mode: str = "bilinear"):
        """
        Initializes the resize attack.

        Args:
            noisename (str): Name identifier for logging and reporting.
            mode (str): Interpolation method: 'nearest', 'bilinear', 'bicubic'.
        """
        super().__init__(noisename=noisename, factor_inversely_related=True)

        self.interpolation = {
            "nearest": transforms.InterpolationMode.NEAREST,
            "bilinear": transforms.InterpolationMode.BILINEAR,
            "bicubic": transforms.InterpolationMode.BICUBIC
        }.get(mode, transforms.InterpolationMode.BILINEAR)

    @torch.inference_mode()
    def attack(self, stego_img: List[ndarray], cover_img: List[ndarray] = None, scale_p: float = 0.8) -> List[ndarray]:
        """
        Applies resize distortion to a batch of stego images using torchvision's Resize transform.
        Supports both RGB and grayscale images.

        The pipeline:
            1. Stack images into a 4D numpy array [B, H, W, C]
            2. Convert to float32 and normalize to [0,1]
            3. Convert to CHW tensor and move to device
            4. Downsample using transforms.Resize
            5. Upsample back to original size using transforms.Resize
            6. Convert back to HWC uint8 numpy arrays

        Args:
            stego_img (List[ndarray]): Batch of watermarked images, each [H, W] or [H, W, 3], dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored).
            scale_p (float): Downscaling factor, range (0.01, 1.0].

        Returns:
            List[ndarray]: Batch of resized images, each with the same shape and dtype as input.
        """
        if not stego_img:
            return []

        scale_p = np.clip(scale_p, 0.01, 1.0)

        is_grayscale = len(stego_img[0].shape) == 2
        original_shapes = [img.shape[:2] for img in stego_img]
        h, w = original_shapes[0]

        if is_grayscale:
            expanded_imgs = [np.expand_dims(img, axis=-1) for img in stego_img]
        else:
            expanded_imgs = stego_img

        batch_np = np.stack(expanded_imgs, axis=0).astype(np.float32)

        batch_np = batch_np / 255.0

        batch_tensor = torch.from_numpy(batch_np).permute(0, 3, 1, 2)

        new_h, new_w = int(h * scale_p), int(w * scale_p)

        down_transform = transforms.Resize(size=(new_h, new_w), interpolation=self.interpolation)
        up_transform = transforms.Resize(size=(h, w), interpolation=self.interpolation)

        resized_down = down_transform(batch_tensor)
        resized_up = up_transform(resized_down)

        resized_np = (resized_up.permute(0, 2, 3, 1).cpu().numpy() * 255.0).astype(np.uint8)

        if is_grayscale:
            resized_np = resized_np.squeeze(-1)

        return [resized_np[i] for i in range(resized_np.shape[0])]


class Rotate(BaseTestAttackModel):
    """
    A geometric attack that rotates an image around its center by a specified angle.

    This attack simulates camera rotation or document misalignment, which can disrupt watermark signals
    that are sensitive to spatial orientation or rely on fixed pixel patterns.

    The 'factor' parameter controls the rotation angle in degrees:
        - 0.0: No rotation (identity)
        - 10.0: 10-degree clockwise rotation
        - 360: Maximum rotation (wraps around)

    The rotation is performed around the image center using bilinear interpolation,
    and the borders are filled with black (0, 0, 0).

    This implementation uses `torchvision.transforms.functional.rotate` for true batched processing,
    enabling GPU acceleration and eliminating Python loops.

    Note:
        - Input: List of uint8 RGB images [H, W, 3], range [0, 255]
        - Output: List of rotated images, same shape and dtype
        - Uses torchvision for batched, GPU-accelerated rotation
    """

    def __init__(self, noisename: str = "Rotate"):
        """
        Initializes the rotation attack.

        Args:
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=True)

    @torch.inference_mode()
    def attack(self, stego_img: List[ndarray], cover_img: List[ndarray] = None, factor: float = 10.0) -> List[ndarray]:
        """
        Applies rotation to a batch of stego images using torchvision's rotate function.

        Args:
            stego_img (List[ndarray]): Batch of watermarked images, each [H, W, 3], dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored).
            factor (float): Rotation angle in degrees, range [-180, 180].

        Returns:
            List[ndarray]: Batch of rotated images, each with the same shape and dtype as input.
        """
        if not stego_img:
            return []

        angle = np.clip(factor, 0, 360).item()

        is_grayscale = len(stego_img[0].shape) == 2
        if is_grayscale:
            expanded_imgs = [np.expand_dims(img, axis=-1) for img in stego_img]
        else:
            expanded_imgs = stego_img

        batch_np = np.stack(expanded_imgs, axis=0).astype(np.float32)
        batch_np = batch_np / 255.0

        batch_tensor = torch.from_numpy(batch_np).permute(0, 3, 1, 2)
        rotated_tensor = TF.rotate(
            batch_tensor,
            angle=angle,
            interpolation=TF.InterpolationMode.BILINEAR
        )

        rotated_np = (rotated_tensor.permute(0, 2, 3, 1).cpu().numpy() * 255.0).astype(np.uint8)

        if is_grayscale:
            rotated_np = rotated_np.squeeze(-1)

        return [rotated_np[i] for i in range(rotated_np.shape[0])]


class FlipAttack(BaseTestAttackModel):
    """
    A spatial flip attack that flips images either horizontally or vertically.

    ✅ Assumes all input images have the SAME shape [H, W, C] or [H, W]
    ✅ Fully vectorized batch processing (no Python loops during flip)
    ✅ Supports both grayscale and color images
    ✅ GUARANTEES output dtype is uint8

    The 'factor' parameter controls the flip direction:
        - 'H': Horizontal flip (left-right mirror)
        - 'V': Vertical flip (up-down mirror)

    Note:
        - Input: List of uint8 images, all same shape [H, W] or [H, W, C], range [0, 255]
        - Output: List of flipped images, same shape and guaranteed uint8 dtype
    """

    def __init__(self, noisename: str = "FlipAttack"):
        super().__init__(noisename=noisename, factor_inversely_related=False)

    def attack(self, stego_imgs: List[ndarray[np.uint8]], cover_img: Optional[List[ndarray[np.uint8]]] = None,
               factor: str = 'H') -> List[ndarray[np.uint8]]:
        """
        Applies flip to a batch of images with identical shape using full vectorization.
        GUARANTEES that output dtype is uint8.

        Args:
            stego_imgs (List[ndarray]): List of uint8 images, all same shape [H, W] or [H, W, C].
            cover_img: Ignored (for compatibility).
            factor (str): 'H' for horizontal, 'V' for vertical flip.

        Returns:
            List[ndarray]: Flipped images, same shape and guaranteed uint8 dtype.

        Raises:
            ValueError: If factor is not 'H' or 'V'.
        """
        if not stego_imgs:
            return []
        if factor not in ('H', 'V'):
            raise ValueError(f"factor must be 'H' or 'V', got '{factor}'")
        batch_tensor = np.stack(stego_imgs, axis=0)
        if batch_tensor.ndim == 3:
            batch_tensor = np.expand_dims(batch_tensor, axis=-1)
            is_gray = True
        else:
            is_gray = False
        flip_axis = 2 if factor == 'H' else 1
        flipped_batch = np.flip(batch_tensor, axis=flip_axis)
        if is_gray:
            flipped_batch = flipped_batch.squeeze(axis=-1)
        flipped_batch = flipped_batch.astype(np.uint8)
        return [flipped_batch[i] for i in range(flipped_batch.shape[0])]



class TranslationAttack(BaseTestAttackModel):
    """
    A simplified translation attack using OpenCV's warpAffine for accurate translation.

    - Only one parameter: `percent` (e.g., 0.1 means up to 10% of width/height).
    - The actual shift magnitude is controlled by the input `factor` (0.0 ~ 1.0).
    - Supports both grayscale (H, W) and color (H, W, C) images.
    - Padding is always zero-filled (borderValue=(0,0,0)).
    """

    def __init__(
            self,
            noisename: str = "TranslationAttack"
    ):
        """
        Args:
            noisename (str): Name for logging. Defaults to "TranslationAttack".
        """
        super().__init__(noisename=noisename, factor_inversely_related=False)

    def attack(
            self,
            stego_imgs: List[ndarray],
            cover_img: Optional[List[ndarray]] = None,
            factor: Optional[float] = 0.1
    ) -> List[ndarray]:
        """
        Apply random translation with magnitude controlled by `factor`.

        Final shift = factor * image_dimension.
        If factor is None, it defaults to 1.0 (i.e., full intensity).

        Args:
            stego_imgs: List of images, each (H, W) or (H, W, C).
            cover_img: Ignored.
            factor: Float in [0, 1]. If None, treated as 1.0.

        Returns:
            List of translated images with same shapes and dtypes.
        """
        if factor is None:
            factor = 1.0
        if not (0.0 <= factor <= 1.0):
            raise ValueError("factor must be in [0, 1]")
        if factor == 0.0:
            return [img.copy() for img in stego_imgs]
        eff_factor = max(0.0, min(1.0, factor))
        attacked = []
        for img in stego_imgs:
            H, W = img.shape[:2]
            h_shift = int(np.round(eff_factor * W)) * np.random.choice([-1, 1])
            v_shift = int(np.round(eff_factor * H)) * np.random.choice([-1, 1])
            if h_shift == 0 and eff_factor > 0:
                h_shift = np.random.choice([-1, 1])
            if v_shift == 0 and eff_factor > 0:
                v_shift = np.random.choice([-1, 1])
            M = np.float32([[1, 0, h_shift], [0, 1, v_shift]])
            if len(img.shape) == 2:  # grayscale
                translated = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
            else:
                translated = cv2.warpAffine(
                    img,
                    M,
                    (W, H),
                    flags=cv2.INTER_LINEAR,
                    borderMode=cv2.BORDER_CONSTANT,
                    borderValue=(0, 0, 0)
                )
            attacked.append(translated.astype(img.dtype))
        return attacked



class Crop(BaseTestAttackModel):
    """
    A spatial attack that simulates partial occlusion by cropping a region
    and filling the rest based on a specified mode.

    The 'factor' parameter controls the **area ratio of the kept region**:
        - 1.0: No change (entire image kept)
        - <1.0: A sub-region is preserved, rest is filled

    Supported fill modes:
        - 'constant_replace': Fill with a constant color (e.g., black)
        - 'cover_replace': Fill with the corresponding region from the original cover image

    Supported crop modes:
        - 'center': Keep central region (deterministic)
        - 'random': Keep a randomly positioned region using Gaussian-sampled rectangle (stochastic)
    """

    def __init__(
            self,
            noisename: str = "Crop",
            mode: str = "constant_replace",
            constant: float = 0.0,
            crop_mode: str = "center"
    ):
        super().__init__(noisename=noisename, factor_inversely_related=True)
        if mode not in ["constant_replace", "cover_replace"]:
            raise ValueError("mode must be 'constant_replace' or 'cover_replace'")
        if crop_mode not in ["center", "random"]:
            raise ValueError("crop_mode must be 'center' or 'random'")

        self.mode = mode
        self.constant = float(constant)
        self.crop_mode = crop_mode

    def _random_crop_mask(self, h: int, w: int, keep_ratio: float) -> np.ndarray:
        """
        Generate a binary mask (H, W) where 1 = kept, 0 = cropped.
        Replicates the logic of `random_cropout_mask` for a single image.

        Args:
            h, w: Image height and width.
            keep_ratio: Ratio of area to KEEP (e.g., 0.7 → keep 70%, crop 30%).

        Returns:
            mask: np.ndarray of shape (H, W), dtype=bool or uint8.
        """
        crop_ratio = 1.0 - keep_ratio
        num_pixels_to_crop = int(h * w * crop_ratio)
        num_pixels_to_crop = min(num_pixels_to_crop, h * w)

        if num_pixels_to_crop <= 0:
            return np.ones((h, w), dtype=np.uint8)

        max_width = min(w, num_pixels_to_crop)
        max_height = min(h, num_pixels_to_crop)
        min_width = 1
        min_height = 1

        desired_area = num_pixels_to_crop
        mean_width = min(max_width, max(1, int(np.sqrt(desired_area))))
        std_width = max(1, mean_width * 0.3)
        width = int(np.clip(np.random.normal(mean_width, std_width), min_width, max_width))
        width = max(min_width, min(width, max_width))
        height = min(num_pixels_to_crop // width, max_height)
        height = max(min_height, min(height, max_height))
        if width * height > num_pixels_to_crop:
            if width > height:
                width = min(num_pixels_to_crop, max_width)
                height = min(num_pixels_to_crop // width, max_height)
            else:
                height = min(num_pixels_to_crop, max_height)
                width = min(num_pixels_to_crop // height, max_width)
            width = max(min_width, min(width, max_width))
            height = max(min_height, min(height, max_height))

        max_start_w = w - width
        max_start_h = h - height
        if max_start_w < 0 or max_start_h < 0:
            return np.ones((h, w), dtype=np.uint8)

        rect_w = np.random.randint(0, max_start_w + 1) if max_start_w > 0 else 0
        rect_h = np.random.randint(0, max_start_h + 1) if max_start_h > 0 else 0
        mask = np.ones((h, w), dtype=np.uint8)
        mask[rect_h:rect_h + height, rect_w:rect_w + width] = 0
        return mask

    def attack(
            self,
            stego_imgs: List[ndarray],
            cover_img: Optional[List[ndarray]] = None,
            factor: float = 0.7
    ) -> List[ndarray]:
        if not stego_imgs:
            return []

        factor = np.clip(factor, 0.01, 1.0)
        noised_batch = []

        for i, img in enumerate(stego_imgs):
            h, w = img.shape[:2]

            if self.crop_mode == "center":
                area_to_keep = factor * h * w
                aspect_ratio = w / h
                crop_h = int(np.sqrt(area_to_keep / aspect_ratio))
                crop_w = int(crop_h * aspect_ratio)
                crop_h = max(1, min(crop_h, h))
                crop_w = max(1, min(crop_w, w))
                y = (h - crop_h) // 2
                x = (w - crop_w) // 2
                mask = np.ones((h, w), dtype=np.uint8)
                mask[y:y + crop_h, x:x + crop_w] = 0

            else:
                mask = self._random_crop_mask(h, w, keep_ratio=factor)
            if self.mode == "constant_replace":
                fill_val = int(self.constant * 255)
                noised_img = np.full_like(img, fill_val, dtype=np.uint8)
            else:
                if cover_img is None or i >= len(cover_img):
                    raise ValueError("cover_img required for 'cover_replace'")
                cover = cover_img[i].astype(np.uint8)
                if cover.shape[:2] != (h, w):
                    raise ValueError("cover_img size mismatch")
                noised_img = cover.copy()

            if img.ndim == 2:
                noised_img[mask == 0] = img[mask == 0]
            else:
                mask_exp = mask[:, :, None]
                noised_img = np.where(mask_exp, noised_img, img)
            noised_batch.append(noised_img)
        return noised_batch



class Cropout(BaseTestAttackModel):
    """
    Cropout attack with two modes:
        - 'center': remove a central rectangle (deterministic)
        - 'random': remove a random rectangle using Gaussian-sampled size (your logic)

    factor: proportion of area to REMOVE (0.0 ~ 1.0)
    """

    def __init__(
            self,
            noisename: str = "Cropout",
            constant: float = 0.0,
            mode: str = "constant_replace",
            cropout_mode: str = "random"
    ):
        super().__init__(noisename=noisename, factor_inversely_related=True)
        if mode not in ["constant_replace", "cover_replace"]:
            raise ValueError("mode must be 'constant_replace' or 'cover_replace'")
        if cropout_mode not in ["random", "center"]:
            raise ValueError("cropout_mode must be 'random' or 'center'")

        self.constant = float(constant) * 255.0
        self.mode = mode
        self.cropout_mode = cropout_mode

    def _random_crop_mask(self, h: int, w: int, keep_ratio: float) -> ndarray:
        """
        YOUR EXACT LOGIC: Generate mask where 1=kept, 0=cropped (removed).
        """
        crop_ratio = 1.0 - keep_ratio
        num_pixels_to_crop = int(h * w * crop_ratio)
        num_pixels_to_crop = min(num_pixels_to_crop, h * w)

        if num_pixels_to_crop <= 0:
            return np.ones((h, w), dtype=np.uint8)

        max_width = min(w, num_pixels_to_crop)
        max_height = min(h, num_pixels_to_crop)
        min_width = 1
        min_height = 1

        desired_area = num_pixels_to_crop
        mean_width = min(max_width, max(1, int(np.sqrt(desired_area))))
        std_width = max(1, mean_width * 0.3)
        width = int(np.clip(np.random.normal(mean_width, std_width), min_width, max_width))
        width = max(min_width, min(width, max_width))

        height = min(num_pixels_to_crop // width, max_height)
        height = max(min_height, min(height, max_height))

        if width * height > num_pixels_to_crop:
            if width > height:
                width = min(num_pixels_to_crop, max_width)
                height = min(num_pixels_to_crop // width, max_height)
            else:
                height = min(num_pixels_to_crop, max_height)
                width = min(num_pixels_to_crop // height, max_width)
            width = max(min_width, min(width, max_width))
            height = max(min_height, min(height, max_height))

        max_start_w = w - width
        max_start_h = h - height
        if max_start_w < 0 or max_start_h < 0:
            return np.ones((h, w), dtype=np.uint8)

        rect_w = np.random.randint(0, max_start_w + 1) if max_start_w > 0 else 0
        rect_h = np.random.randint(0, max_start_h + 1) if max_start_h > 0 else 0

        mask = np.ones((h, w), dtype=np.uint8)
        mask[rect_h:rect_h + height, rect_w:rect_w + width] = 0
        return mask

    def _center_cropout_mask(self, h: int, w: int, crop_ratio: float) -> ndarray:
        """Simple center rectangle removal."""
        if crop_ratio <= 0.0:
            return np.ones((h, w), dtype=np.uint8)
        if crop_ratio >= 1.0:
            return np.zeros((h, w), dtype=np.uint8)

        remove_area = int(h * w * crop_ratio)
        aspect_ratio = w / h
        remove_h = int(np.sqrt(remove_area / aspect_ratio))
        remove_w = int(remove_h * aspect_ratio)
        remove_h = max(1, min(remove_h, h))
        remove_w = max(1, min(remove_w, w))

        y = (h - remove_h) // 2
        x = (w - remove_w) // 2

        mask = np.ones((h, w), dtype=np.uint8)
        mask[y:y + remove_h, x:x + remove_w] = 0
        return mask

    def attack(
            self,
            stego_img: List[ndarray],
            cover_img: Optional[List[ndarray]] = None,
            factor: float = 0.3
    ) -> List[ndarray]:
        if not stego_img:
            return []

        factor = np.clip(float(factor), 0.0, 1.0)
        noised_batch = []

        for i, img in enumerate(stego_img):
            h, w = img.shape[:2]
            is_grayscale = (img.ndim == 2)
            c = 1 if is_grayscale else img.shape[2]

            if self.cropout_mode == "random":
                mask = self._random_crop_mask(h, w, keep_ratio=1.0 - factor)
            else:
                mask = self._center_cropout_mask(h, w, crop_ratio=factor)

            mask = mask.astype(np.float32)  # (H, W)
            mask_3d = np.repeat(mask[:, :, np.newaxis], c, axis=2)  # (H, W, C)
            if self.mode == "constant_replace":
                fill_val = self.constant
                replace_value = np.full((h, w, c), fill_val, dtype=np.float32)
            else:
                if cover_img is None or i >= len(cover_img):
                    raise ValueError("cover_img required for 'cover_replace'")
                cover = cover_img[i].astype(np.float32)
                if cover.shape[:2] != (h, w):
                    raise ValueError("cover_img spatial size mismatch")
                if cover.ndim == 2:
                    cover = cover[:, :, np.newaxis]
                if cover.shape[2] != c:
                    if c == 1:
                        cover = cover[:, :, :1]
                    else:
                        cover = np.tile(cover[:, :, :1], (1, 1, c))
                replace_value = cover

            img_float = img.astype(np.float32)
            if img_float.ndim == 2:
                img_float = img_float[:, :, np.newaxis]

            noised_float = img_float * mask_3d + replace_value * (1.0 - mask_3d)
            noised_uint8 = np.clip(noised_float, 0, 255).astype(np.uint8)
            if is_grayscale:
                noised_uint8 = noised_uint8.squeeze(axis=2)
            noised_batch.append(noised_uint8)
        return noised_batch



class RegionZoom(BaseTestAttackModel):
    """
    A spatial attack that simulates digital zoom by cropping a random sub-region and resizing it to full resolution.

    This attack removes peripheral information and enlarges a central portion, potentially disrupting
    watermark signals embedded in image borders or relying on global structure.

    The 'factor' parameter controls the relative area of the cropped region:
        - 1.0: Crop covers almost the entire image (minimal zoom, weakest attack)
        - <1.0: Smaller region is cropped and upscaled (stronger zoom, stronger attack)

    The aspect ratio of the original image is preserved in the cropped region.

    Note:
        - Input: List of uint8 RGB images [H, W, 3], range [0, 255]
        - Output: List of zoomed images, same shape and dtype
        - Uses bilinear interpolation for resizing
    """

    def __init__(self, noisename: str = "RegionZoom"):
        """
        Initializes the region zoom attack.

        Args:
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=True)  # Smaller factor = stronger zoom

    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: float = 0.7) -> List[ndarray]:
        """
        Applies region zoom (crop + resize) distortion to a batch of stego images.

        For each image:
            1. Calculate the size of a sub-region to crop, based on 'factor' and aspect ratio.
            2. Randomly determine the top-left position of the crop.
            3. Crop the image to the sub-region.
            4. Resize the cropped region back to the original dimensions using bilinear interpolation.

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each [H, W, 3], dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored, for interface compatibility).
            factor (float): Ratio of the cropped area to the original image area, range (0.01, 1.0].

        Returns:
            List[ndarray]: Batch of zoomed images, each with the same shape and dtype as input.
        """
        if not stego_imgs:
            return []
        factor = np.clip(factor, 0.01, 1.0)
        noised_batch = []
        for img in stego_imgs:
            h, w = img.shape[:2]
            area_to_crop = factor * h * w
            aspect_ratio = w / h
            crop_h = int(np.sqrt(area_to_crop / aspect_ratio))
            crop_w = int(crop_h * aspect_ratio)
            crop_h = max(1, min(crop_h, h))
            crop_w = max(1, min(crop_w, w))
            x = random.randint(0, w - crop_w)
            y = random.randint(0, h - crop_h)
            cropped = img[y:y + crop_h, x:x + crop_w]
            zoomed = cv2.resize(cropped.astype(np.uint8), (w, h), interpolation=cv2.INTER_LINEAR)
            noised_batch.append(zoomed)
        return noised_batch



class PixelDropout(BaseTestAttackModel):
    """
    A pixel-level occlusion attack that randomly drops (replaces) pixels to simulate data loss or noise.

    This attack sets a random subset of pixels to a replacement value, disrupting local texture and
    high-frequency information where many watermark signals are embedded.

    The 'factor' parameter controls the dropout probability:
        - 0.0: No pixels dropped (identity)
        - 0.1: 10% of pixels replaced
        - 1.0: All pixels replaced (complete destruction)

    Supported replacement modes:
        - 'constant_replace': Replace with a constant color (e.g., black)
        - 'cover_replace': Replace with the corresponding pixel from the original cover image

    Note:
        - Input: List of uint8 RGB images [H, W, 3], range [0, 255]
        - Output: List of modified images, same shape and dtype
        - For 'cover_replace', `cover_img` must be provided and at least as large as `stego_img`
    """

    def __init__(self, noisename: str = "PixelDropout", mode: str = "constant_replace", constant: int = 0):
        """
        Initializes the pixel dropout attack.

        Args:
            noisename (str): Name identifier for logging and reporting.
            mode (str): Replacement strategy: 'constant_replace' or 'cover_replace'.
            constant (int): Pixel value (0-1) for 'constant_replace' mode. Default is 0 (black).

        Raises:
            AssertionError: If mode is not supported.
        """
        super().__init__(noisename=noisename, factor_inversely_related=False)
        assert mode in ["constant_replace",
                        "cover_replace"], f"Invalid mode: {mode}. Choose from 'constant_replace', 'cover_replace'."
        self.mode = mode
        self.constant = constant

    def attack(self, stego_img: List[ndarray], cover_img: List[ndarray] = None, factor: float = 0.1) -> List[
        ndarray]:
        """
        Applies pixel dropout to a batch of stego images.

        For each image:
            1. Generates a random binary mask based on the dropout probability ('factor').
            2. Keeps pixels where mask is True.
            3. Replaces pixels where mask is False with either a constant value or the cover image content.

        Args:
            stego_img (List[ndarray]): Batch of watermarked images, each [H, W, 3], dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images for 'cover_replace' mode.
            factor (float): Probability of dropping a pixel, range [0.0, 1.0].

        Returns:
            List[ndarray]: Batch of images with pixel dropout applied, each with the same shape and dtype as input.
        """
        if not stego_img:
            return []
        drop_prob = np.clip(factor, 0.0, 1.0)
        if drop_prob == 0.0:
            return [img.copy() for img in stego_img]
        noised_batch = []
        for i, img in enumerate(stego_img):
            img_uint8 = img.astype(np.uint8)
            h, w = img_uint8.shape[:2]
            is_grayimage = img_uint8.ndim == 2
            if is_grayimage:
                keep_mask = np.random.rand(h, w) > drop_prob
            else:
                keep_mask = np.random.rand(h, w, img_uint8.shape[2]) > drop_prob
            if self.mode == "constant_replace" or cover_img is None or len(cover_img) <= i:
                replace_value = np.full_like(img_uint8, self.constant * 255, dtype=np.uint8)
            elif self.mode == "cover_replace":
                cover = cover_img[i].astype(np.uint8)
                if cover.shape[0] < h or cover.shape[1] < w:
                    raise ValueError("cover_img must be at least as large as stego_img.")
                replace_value = cover[:h, :w]
            else:
                raise ValueError(f"Unsupported mode: {self.mode}")
            noised_img = np.where(keep_mask, img_uint8, replace_value)
            noised_batch.append(noised_img)
        return noised_batch


class ShearAttack(BaseTestAttackModel):
    """
    A shear attack controlled by angle (in degrees) and explicit direction.

    - `factor`: shear angle in degrees (e.g., 15, 30, 45).
    - `direction`: one of "x" (horizontal), "y" (vertical), or "random".
    - Shear magnitude = tan(radians(angle)).
    - Supports grayscale (H, W) and color (H, W, C).
    - Padding is zero-filled (black).
    """

    def __init__(
            self,
            noisename: str = "ShearAttack",
            direction: str = "random"
    ):
        """
        Args:
            noisename (str): Name for logging.
            direction (str): Shear direction. Must be one of:
                - "x": horizontal shear (columns slant)
                - "y": vertical shear (rows slant)
                - "random": randomly choose x or y per image
        """
        if direction not in {"x", "y", "random"}:
            raise ValueError('direction must be one of "x", "y", or "random"')

        super().__init__(noisename=noisename, factor_inversely_related=False)
        self.direction = direction

    def attack(
            self,
            stego_imgs: List[ndarray],
            cover_img: Optional[List[ndarray]] = None,
            factor: Optional[float] = 15.0
    ) -> List[ndarray]:
        """
        Apply shear using angle in degrees and predefined direction.

        Args:
            stego_imgs: List of images, each (H, W) or (H, W, C).
            cover_img: Ignored.
            factor: Shear angle in degrees (e.g., 15.0). If None, defaults to 15°.

        Returns:
            List of sheared images with same shape and dtype.
        """
        if factor is None:
            factor = 15.0

        angle_deg = float(factor)

        # Prevent extreme distortion
        if abs(angle_deg) >= 90:
            raise ValueError("Shear angle must be in (-90, 90) degrees.")

        if abs(angle_deg) < 1e-6:
            return [img.copy() for img in stego_imgs]

        shear_rad = np.radians(angle_deg)
        shear_factor = np.tan(shear_rad)
        attacked = []
        for img in stego_imgs:
            H, W = img.shape[:2]
            if self.direction == "random":
                shear_dir = np.random.choice(["x", "y"])
            else:
                shear_dir = self.direction
            if shear_dir == "x":
                M = np.float32([[1, shear_factor, 0], [0, 1, 0]])
            else:
                M = np.float32([[1, 0, 0], [shear_factor, 1, 0]])
            border_value = 0 if len(img.shape) == 2 else (0, 0, 0)
            sheared = cv2.warpAffine(
                img,
                M,
                (W, H),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=border_value
            )
            attacked.append(sheared.astype(img.dtype))
        return attacked
