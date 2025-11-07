# Copyright (c) 2025 Jiale Chen <chenoly@outlook.com>. All rights reserved.
# SPDX-License-Identifier: MIT
import numpy as np
from typing import List
from numpy import ndarray
from watermarklab.utils.basemodel import BaseTestAttackModel


class PoissonNoise(BaseTestAttackModel):
    """
    A noise attack that adds Poisson-distributed noise to a batch of images.

    Poisson noise models sensor noise in digital imaging systems, where the variance
    of the noise is proportional to the pixel intensity (e.g., photon counting noise).
    This makes it particularly relevant for evaluating watermark robustness under low-light conditions.

    The 'factor' parameter controls the effective signal-to-noise ratio:
        - Lower factor: stronger noise (simulates low light)
        - Higher factor: weaker noise (simulates high light)

    Reference:
        Foi, A., Trimeche, M., Katkovnik, V., & Egiazarian, K. (2008).
        Practical Poissonian-Gaussian noise modeling and denoising based on precise noise parameter estimation.
        IEEE Transactions on Image Processing, 17(6), 10.1109/TIP.2008.921849

    Note:
        - Input: List of uint8 RGB images [H, W, 3], range [0, 255]
        - Output: List of noisy images, same shape and dtype
        - This implementation uses fully vectorized NumPy operations for maximum CPU efficiency
    """

    def __init__(self, noisename: str = "PoissonNoise"):
        """
        Initializes the Poisson noise attack.

        Args:
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=False)

    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: float = 1.0) -> List[ndarray]:
        """
        Applies Poisson noise to a batch of stego images using fully vectorized operations.

        The noise model is:
            noisy_img = clip( Poisson(img / factor) * factor, 0, 255 )

        This preserves the mean while scaling the variance, simulating realistic sensor noise.

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each [H, W, 3], dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored).
            factor (float): Noise intensity scaling factor. Typical range [0.1, 10.0].

        Returns:
            List[ndarray]: Batch of noisy images, each with the same shape and dtype as input.
        """
        if not stego_imgs:
            return []

        batch_np = np.stack(stego_imgs, axis=0).astype(np.float32)
        img_normalized = batch_np / 255.0
        if factor > 1e-6:
            scaled_intensity = img_normalized * (255.0 / factor)
            noisy_intensity = np.random.poisson(scaled_intensity)
            noisy_normalized = noisy_intensity * (factor / 255.0)
        else:
            noisy_normalized = img_normalized  # No noise

        noisy_batch = np.clip(noisy_normalized * 255.0, 0, 255).astype(np.uint8)
        return [noisy_batch[i] for i in range(noisy_batch.shape[0])]



class GaussianNoise(BaseTestAttackModel):
    """
    A noise attack that adds zero-mean Gaussian noise to the input image.

    This attack simulates random pixel perturbations caused by electronic sensor noise or transmission errors.
    It is a fundamental test for watermark robustness under random signal degradation.

    The 'std' parameter controls the standard deviation of the noise:
        - 0.0: No noise (identity)
        - 0.05: Low noise (barely perceptible)
        - 0.15: Medium noise (clearly visible)
        - >0.2: High noise (severe degradation)

    The noise is scaled to the [0, 255] range before addition.

    Reference:
        Foi, A., Trimeche, M., Katkovnik, V., & Egiazarian, K. (2008).
        Practical Poissonian-Gaussian noise modeling and denoising based on precise noise parameter estimation.
        IEEE Transactions on Image Processing, 17(6), 10.1109/TIP.2008.921849

    Note:
        - Input: List of uint8 RGB images [H, W, 3], range [0, 255]
        - Output: List of noisy images, same shape and dtype
        - The noise is generated independently for each image in the batch
    """

    def __init__(self, mu: float = 0.0, noisename: str = "GaussianNoise"):
        """
        Initializes the Gaussian noise attack.

        Args:
            mu (float): Mean of the Gaussian distribution. Default is 0.0.
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=False)
        self.mu = mu

    def attack(self, stego_img: List[ndarray], cover_img: List[ndarray] = None, std: float = 1.5) -> List[
        ndarray]:
        """
        Applies Gaussian noise to a batch of stego images using vectorized operations.

        The noise model is:
            noised_img = clip( stego_img + N(mu, std) * 255, 0, 255 )

        Args:
            stego_img (List[ndarray]): Batch of watermarked images, each [H, W, 3], dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored, for interface compatibility).
            std (float): Standard deviation of the Gaussian noise, relative to [0,1] range.

        Returns:
            List[ndarray]: Batch of noisy images, each with the same shape and dtype as input.
        """
        if not stego_img:
            return []

        batch_np = np.stack(stego_img, axis=0).astype(np.float32)
        noise = np.random.normal(self.mu, std * 255.0, batch_np.shape)
        noised_batch = batch_np + noise
        noised_batch = np.clip(noised_batch, 0, 255).astype(np.uint8)
        return [noised_batch[i] for i in range(noised_batch.shape[0])]


class SaltPepperNoise(BaseTestAttackModel):
    """
    A non-linear noise attack that simulates salt-and-pepper noise by randomly setting pixels to extreme values.

    This attack models severe pixel corruption, such as that caused by faulty sensors, bit errors,
    or transmission faults. It flips a random subset of pixels to either the minimum (0, "pepper")
    or maximum (255, "salt") intensity value.

    The 'noise_ratio' parameter controls the proportion of pixels affected:
        - 0.0: No noise (identity)
        - 0.1: 10% of pixels are corrupted (5% salt, 5% pepper)
        - 1.0: All pixels are set to either 0 or 255 (complete destruction)

    The attack is applied independently to each image in the batch and supports both grayscale
    and color images by checking the input dimensionality.

    Reference:
        González, R. C., & Woods, R. E. (2008). Digital Image Processing (3rd ed.). Prentice Hall.

    Note:
        - Input: List of uint8 images, either [H, W] (grayscale) or [H, W, 3] (RGB), range [0, 255]
        - Output: List of noisy images, same shape and dtype
        - The noise is distributed equally between salt (255) and pepper (0) pixels
    """

    def __init__(self, noisename: str = "SaltPepperNoise"):
        """
        Initializes the salt-and-pepper noise attack.

        Args:
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename,
                         factor_inversely_related=False)  # Higher ratio = more noise = stronger attack

    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, noise_ratio: float = 0.1) -> List[ndarray]:
        """
        Applies salt-and-pepper noise to a batch of stego images.

        For each image:
            1. Creates a copy of the input image.
            2. Generates a random noise mask over the spatial dimensions.
            3. Sets pixels below `noise_ratio/2` to 255 ("salt").
            4. Sets pixels between `noise_ratio/2` and `noise_ratio` to 0 ("pepper").
            5. Preserves the remaining pixels.

        The method handles both grayscale and color images:
            - Grayscale: shape [H, W], scalar assignment
            - Color: shape [H, W, 3], vector assignment

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each [H, W] or [H, W, 3], dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored, for interface compatibility).
            noise_ratio (float): Proportion of pixels to corrupt, range [0.0, 1.0].

        Returns:
            List[ndarray]: Batch of noisy images, each with the same shape and dtype as input.
        """
        noised_imgs = []
        noise_ratio = np.clip(noise_ratio, 0.0, 1.0)
        if noise_ratio == 0.0:
            return [img.copy() for img in stego_imgs]

        for stego_img in stego_imgs:
            noisy_image = np.copy(stego_img)
            is_color = len(stego_img.shape) == 3
            mask_shape = stego_img.shape[:2] if is_color else stego_img.shape
            noise_mask = np.random.random(mask_shape)
            if is_color:
                noisy_image[noise_mask < noise_ratio / 2] = [255, 255, 255]
            else:
                noisy_image[noise_mask < noise_ratio / 2] = 255
            pepper_condition = (noise_mask >= noise_ratio / 2) & (noise_mask < noise_ratio)
            if is_color:
                noisy_image[pepper_condition] = [0, 0, 0]
            else:
                noisy_image[pepper_condition] = 0
            noised_imgs.append(noisy_image.astype(np.uint8))
        return noised_imgs

