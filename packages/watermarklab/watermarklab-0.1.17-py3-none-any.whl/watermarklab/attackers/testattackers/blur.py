# Copyright (c) 2025 Jiale Chen <chenoly@outlook.com>. All rights reserved.
# SPDX-License-Identifier: MIT
import cv2
import torch
import numpy as np
from typing import List
from numpy import ndarray
from torchvision.transforms import transforms
from watermarklab.utils.basemodel import BaseTestAttackModel


class GaussianBlur(BaseTestAttackModel):
    """
    A spatial smoothing attack that applies Gaussian blur to reduce image details.

    This attack convolves the image with a Gaussian kernel, suppressing high-frequency components
    where many watermark signals are embedded. It simulates defocus blur or motion blur effects.

    The 'sigma' parameter controls the standard deviation of the Gaussian kernel:
        - Higher sigma = larger blur radius = stronger smoothing
        - Lower sigma = milder blur

    This implementation uses torchvision for true batched processing, enabling GPU acceleration
    and eliminating Python loops for maximum efficiency.

    Reference:
        Gonzalez, R. C., & Woods, R. E. (2008). Digital Image Processing (3rd ed.). Prentice Hall.

    Note:
        - Input: List of uint8 RGB images [H, W, 3], range [0, 255]
        - Output: List of blurred images, same shape and dtype
        - Uses torchvision for batched, GPU-accelerated Gaussian blur
    """

    def __init__(self, noisename: str = "GaussianBlur"):
        """
        Initializes the Gaussian blur attack.

        Args:
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=False)  # Higher sigma = stronger blur

    @torch.inference_mode()
    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, sigma: float = 1.0) -> List[
        ndarray]:
        """
        Applies Gaussian blur to a batch of stego images using torchvision's batched implementation.

        The pipeline:
            1. Stack images into a 4D numpy array [B, H, W, 3]
            2. Convert to float32 and normalize to [0,1]
            3. Convert to CHW tensor and move to device
            4. Apply batched Gaussian blur using torchvision
            5. Convert back to HWC uint8

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each [H, W, 3], dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored).
            sigma (float): Standard deviation of the Gaussian kernel, controls blur strength.

        Returns:
            List[ndarray]: Batch of blurred images, each with the same shape and dtype as input.
        """
        if not stego_imgs:
            return []
        batch_np = np.stack(stego_imgs, axis=0).astype(np.float32)
        is_color = batch_np.ndim == 4
        if batch_np.ndim == 3:
            batch_np = np.expand_dims(batch_np, axis=-1)
        batch_np = batch_np / 255.0
        batch_tensor = torch.from_numpy(batch_np).permute(0, 3, 1, 2)
        gaussianblur = transforms.GaussianBlur(kernel_size=int(6 * sigma + 1) // 2 * 2 + 1, sigma=sigma)
        blurred_tensor = gaussianblur(batch_tensor)
        blurred_np = (blurred_tensor.permute(0, 2, 3, 1).cpu().numpy() * 255.0).astype(np.uint8)

        noised_imgs = []
        for i in range(blurred_np.shape[0]):
            if is_color:
                noised_img = blurred_np[i]
            else:
                noised_img = blurred_np[i][:, :, 0]
            noised_imgs.append(noised_img)
        return noised_imgs


class MedianFilter(BaseTestAttackModel):
    """
    Applies a median filter to the input image to reduce noise and smooth details.

    Args:
        noisename (str): Name identifier for the model, defaults to "MedianFilter".
    """

    def __init__(self, noisename: str = "MedianFilter"):
        super().__init__(noisename)

    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, kernel_size: int = 3) -> List[ndarray]:
        """
        Applies a median filter to the input image to smooth details and reduce noise.

        Args:
            stego_imgs (ndarray): Input image in RGB format, uint8 [H, W, 3] [0,255].
            cover_img (ndarray, optional): Not used.
            kernel_size (int): Size of the median filter kernel (must be odd and > 1).

        Returns:
            ndarray: Filtered image, same shape and dtype as input.
        """
        noise_imgs = []
        for stego in stego_imgs:
            result_img = cv2.medianBlur(np.uint8(np.clip(stego, 0., 255.)), kernel_size)
            noise_imgs.append(result_img)
        return noise_imgs


class MeanFilter(BaseTestAttackModel):
    """
    Applies a mean (average) filter to the input image to smooth details.

    Args:
        noisename (str): Name identifier for the model, defaults to "MeanFilter".
    """

    def __init__(self, noisename: str = "MeanFilter"):
        super().__init__(noisename)

    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, kernel_size: int = 5) -> List[ndarray]:
        """
        Applies a mean filter to the input image to smooth details.

        Args:
            stego_imgs (ndarray): Input image in RGB format, uint8 [H, W, 3] [0,255].
            cover_img (ndarray, optional): Not used.
            kernel_size (int): Size of the mean filter kernel (must be odd).

        Returns:
            ndarray: Filtered image, same shape and dtype as input.
        """
        noised_imgs = []
        for stego in stego_imgs:
            kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size * kernel_size)
            filtered_img = cv2.filter2D(stego.astype(np.uint8), -1, kernel)
            noised_imgs.append(filtered_img)
        return noised_imgs
