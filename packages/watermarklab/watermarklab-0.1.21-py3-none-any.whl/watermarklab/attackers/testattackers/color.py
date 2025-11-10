# Copyright (c) 2025 Jiale Chen <chenoly@outlook.com>. All rights reserved.
# SPDX-License-Identifier: MIT
import cv2
import torch
import numpy as np
from typing import List
from numpy import ndarray
import torchvision.transforms as transforms
from watermarklab.utils.basemodel import BaseTestAttackModel


class Identity(BaseTestAttackModel):
    """
    Identity noise model that performs no operation (no-op) on the input images.

    This model returns the input stego images unchanged and is primarily used as:
        - A baseline for robustness testing (e.g., "No Attack" scenario)
        - A control group to verify watermark extraction performance on clean images
        - A placeholder in noise model pipelines

    Since no distortion is applied, it represents the ideal condition where the watermark
    should be perfectly extractable (BER = 0, EA = 100%).

    The model supports batched input (list of images) for efficient processing.
    """

    def __init__(self, noisename: str = "Identity"):
        """
        Initializes the Identity noise model.

        Args:
            noisename (str): Display name for logging and reporting. Defaults to "Identity".
        """
        super().__init__(noisename=noisename, factor_inversely_related=False)

    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: float = None) -> List[ndarray]:
        """
        Alias for `test()`, applying no distortion to the input images.

        Provided for semantic clarity in adversarial testing contexts where "attack"
        implies a degradation process. In this case, the "attack" is null.

        Args:
            stego_imgs (List[ndarray]): Batch of stego images to be "attacked".
            cover_img (List[ndarray], optional): Original cover images (ignored).
            factor (float, optional): Intensity parameter (ignored).

        Returns:
            List[ndarray]: Unmodified stego images.

        Note:
            This method simply delegates to `test()` and adds no additional logic.
        """
        return stego_imgs


class ContrastReduction(BaseTestAttackModel):
    """
    A contrast reduction attack that decreases the intensity difference between light and dark regions of an image.

    This attack scales pixel values toward the overall mean intensity, reducing dynamic range.
    It can weaken watermark signals that rely on contrast variations.

    The 'factor' parameter controls the strength:
        - 1.0: No change (identity)
        - 0.0: All pixels become the mean value (maximum reduction)

    The transformation is: output = mean + (input - mean) * factor

    Note:
        - Input: List of uint8 images, each [H, W] (grayscale) or [H, W, 3] (RGB), range [0, 255]
        - Output: List of contrast-reduced images, same shape and dtype
        - The attack is applied independently to each image in the batch
    """

    def __init__(self, noisename: str = "ContrastReduction"):
        """
        Initializes the contrast reduction attack.

        Args:
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=True)
        self.factor_inversely_related = True

    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: float = 0.7) -> List[ndarray]:
        """
        Applies contrast reduction to a batch of images (grayscale or RGB) using a vectorized implementation.

        The attack reduces the dynamic range by scaling pixel intensities around the image mean.
        This is equivalent to reducing the gain of the image signal.

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each [H, W] (grayscale) or [H, W, 3] (RGB),
                                       dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored, for interface compatibility).
            factor (float): Contrast scaling factor in [0.0, 1.0].
                           1.0 = no change, 0.0 = fully flattened.

        Returns:
            List[ndarray]: Batch of contrast-reduced images, each with the same shape and dtype as input.
        """
        if not stego_imgs:
            return []
        first_img = stego_imgs[0]
        is_grayscale = len(first_img.shape) == 2
        if is_grayscale:
            batch_np = np.stack([img[..., np.newaxis] for img in stego_imgs], axis=0).astype(np.float32)
        else:
            batch_np = np.stack(stego_imgs, axis=0).astype(np.float32)
        mean_values = np.mean(batch_np, axis=(1, 2), keepdims=True)
        noised_batch = mean_values + (batch_np - mean_values) * factor
        noised_batch = np.clip(noised_batch, 0, 255).astype(np.uint8)
        if is_grayscale:
            return [noised_batch[i, :, :, 0] for i in range(noised_batch.shape[0])]
        else:
            return [noised_batch[i] for i in range(noised_batch.shape[0])]


class ContrastEnhancement(BaseTestAttackModel):
    """
    A contrast enhancement attack that amplifies the intensity differences between light and dark areas of an image.

    This attack scales pixel values away from the mean intensity, increasing the dynamic range.
    It can stress watermarking schemes that are sensitive to local contrast changes.

    The 'factor' parameter controls the strength:
        - 1.0: No change (identity)
        - > 1.0: Increased contrast (e.g., 1.5, 2.0, 3.0)

    The transformation is: output = mean + (input - mean) * factor

    Note:
        - Input: List of uint8 images, each [H, W] (grayscale) or [H, W, 3] (RGB), range [0, 255]
        - Output: List of enhanced images, same shape and dtype
        - The attack is applied independently to each image in the batch
    """

    def __init__(self, noisename: str = "ContrastEnhancement"):
        """
        Initializes the contrast enhancement attack.

        Args:
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=False)

    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: float = 1.5) -> List[ndarray]:
        """
        Applies contrast enhancement to a batch of images (grayscale or RGB) using a vectorized implementation.

        The attack increases the dynamic range by scaling pixel intensities around the image mean.
        This is equivalent to increasing the gain of the image signal.

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each [H, W] (grayscale) or [H, W, 3] (RGB),
                                       dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored, for interface compatibility).
            factor (float): Contrast scaling factor >= 1.0.
                           1.0 = no change, higher values = stronger enhancement.

        Returns:
            List[ndarray]: Batch of contrast-enhanced images, each with the same shape and dtype as input.
        """
        if not stego_imgs:
            return []

        first_img = stego_imgs[0]
        is_grayscale = len(first_img.shape) == 2
        if is_grayscale:
            batch_np = np.stack([img[..., np.newaxis] for img in stego_imgs], axis=0).astype(np.float32)
        else:
            batch_np = np.stack(stego_imgs, axis=0).astype(np.float32)

        mean_values = np.mean(batch_np, axis=(1, 2), keepdims=True)
        enhanced_batch = mean_values + (batch_np - mean_values) * factor
        enhanced_batch = np.clip(enhanced_batch, 0, 255).astype(np.uint8)
        if is_grayscale:
            return [enhanced_batch[i, :, :, 0] for i in range(enhanced_batch.shape[0])]
        else:
            return [enhanced_batch[i] for i in range(enhanced_batch.shape[0])]


class GammaCorrection(BaseTestAttackModel):
    """
    A brightness adjustment attack using gamma curve transformation.

    Gamma correction applies a non-linear power-law transformation to the image intensity,
    which can simulate display calibration differences or intentional brightness attacks.
    This can affect watermark robustness, especially for methods sensitive to non-linear pixel shifts.

    The 'factor' parameter is the gamma value:
        - factor < 1.0: brightens the image (expands dark tones)
        - factor = 1.0: no change
        - factor > 1.0: darkens the image (compresses bright tones)

    Reference:
        Poynton, C. (1998). Digital Video and HDTV: Algorithms and Interfaces.

    Note:
        - Input: List of uint8 images, each [H, W] (grayscale) or [H, W, 3] (RGB), range [0, 255]
        - Output: List of gamma-corrected images, same shape and dtype
        - The transformation is applied per-channel for RGB images and to the single channel for grayscale
    """

    def __init__(self, noisename: str = "GammaCorrection"):
        """
        Initializes the gamma correction attack.

        Args:
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=False)

    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: float = 1.5) -> List[ndarray]:
        """
        Applies gamma correction to a batch of images (grayscale or RGB) using a lookup table (LUT) for efficiency.

        The transformation: output = input ** (1/gamma)
        A lookup table is precomputed for all 256 possible pixel values and applied via cv2.LUT.

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each [H, W] (grayscale) or [H, W, 3] (RGB),
                                       dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored, for interface compatibility).
            factor (float): Gamma value, typically in [0.1, 3.0].
                           <1.0 brightens, >1.0 darkens.

        Returns:
            List[ndarray]: Batch of gamma-corrected images, each with the same shape and dtype as input.
        """
        if not stego_imgs:
            return []

        inv_gamma = 1.0 / max(factor, 1e-6)
        table = np.array([(i / 255.0) ** inv_gamma * 255 for i in range(256)]).astype(np.uint8)

        noised_batch = []
        is_grayscale = len(stego_imgs[0].shape) == 2

        for img in stego_imgs:
            if is_grayscale:
                img = np.ascontiguousarray(img, dtype=np.uint8)
                corrected_img = cv2.LUT(img, table)
            else:
                bgr_img = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_RGB2BGR)
                bgr_img = np.ascontiguousarray(bgr_img, dtype=np.uint8)
                corrected_img = cv2.LUT(bgr_img, table)
                corrected_img = cv2.cvtColor(corrected_img, cv2.COLOR_BGR2RGB)
            noised_batch.append(corrected_img)

        return noised_batch


class ChromaticAberration(BaseTestAttackModel):
    """
    A color distortion attack that simulates chromatic aberration by laterally shifting color channels.

    This attack mimics an optical phenomenon where different wavelengths (colors) are focused
    at different positions, causing red and blue fringes at high-contrast edges. It can disrupt
    watermark signals that rely on precise color alignment.

    The 'factor' parameter controls the pixel shift amount:
        - Positive values: blue shifts right, red shifts left
        - Higher magnitude = stronger visual artifact

    Note:
        - Input: List of uint8 images, each [H, W] (grayscale) or [H, W, 3] (RGB), range [0, 255]
        - Output: List of distorted images, same shape and dtype as input
        - For grayscale images, the single channel is replicated to three channels for processing,
          and the output is converted back to grayscale by taking one channel
        - For RGB images, the attack shifts red and blue channels while keeping green unchanged
        - The shift wraps around the horizontal edges (using np.roll)
    """

    def __init__(self, noisename: str = "ChromaticAberration"):
        """
        Initializes the chromatic aberration attack.

        Args:
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=False)

    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: int = 2) -> List[ndarray]:
        """
        Applies chromatic aberration to a batch of images (grayscale or RGB) using vectorized NumPy operations.

        For RGB images:
            - Blue channel (index 2) is shifted to the right by 'factor' pixels
            - Red channel (index 0) is shifted to the left by 'factor' pixels
            - Green channel (index 1) remains unchanged
        For grayscale images:
            - The single channel is replicated to three channels ([H, W] -> [H, W, 3]) for processing
            - After applying the attack, one channel is taken to return a grayscale image ([H, W])

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each [H, W] (grayscale) or [H, W, 3] (RGB),
                                       dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored, for interface compatibility).
            factor (int): Number of pixels to shift the red and blue channels. Typical range [1, 10].

        Returns:
            List[ndarray]: Batch of images with chromatic aberration applied, same shape and dtype as input.
        """
        if not stego_imgs:
            return []

        first_img = stego_imgs[0]
        is_grayscale = len(first_img.shape) == 2
        if is_grayscale:
            batch_np = np.stack([np.repeat(img[..., np.newaxis], 3, axis=-1) for img in stego_imgs], axis=0)
        else:
            batch_np = np.stack(stego_imgs, axis=0)

        r = batch_np[..., 0]
        g = batch_np[..., 1]
        b = batch_np[..., 2]
        shift = int(factor)
        b_shifted = np.roll(b, shift=shift, axis=2)
        r_shifted = np.roll(r, shift=-shift, axis=2)
        noised_batch = np.stack([r_shifted, g, b_shifted], axis=-1)
        if is_grayscale:
            return [noised_batch[i, :, :, 0] for i in range(noised_batch.shape[0])]
        else:
            return [noised_batch[i] for i in range(noised_batch.shape[0])]


class ColorQuantization(BaseTestAttackModel):
    """
    A color reduction attack that reduces the number of distinct colors in an image.

    This attack simulates low-color-depth displays or aggressive image compression by
    quantizing pixel values to the nearest multiple of the 'factor'. It can disrupt
    watermark signals that rely on fine color gradients or high color fidelity.

    The 'factor' parameter controls the quantization step size:
        - 4: Very coarse (16^3 = 4096 colors)
        - 16: Medium (16^3 = 4096 colors, but coarser steps)
        - 32: Very coarse (8^3 = 512 colors)

    The transformation is: output = (input // factor) * factor

    Note:
        - Input: List of uint8 RGB images [H, W, 3], range [0, 255]
        - Output: List of quantized images, same shape and dtype
        - The operation is applied independently to each channel
    """

    def __init__(self, noisename: str = "ColorQuantization"):
        """
        Initializes the color quantization attack.

        Args:
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=False)

    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: int = 16) -> List[
        ndarray]:
        """
        Applies color quantization to a batch of stego images using vectorized integer arithmetic.

        The attack reduces color precision by flooring each pixel value to the nearest
        multiple of 'factor'. This creates visible banding and eliminates subtle color variations.

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each [H, W, 3], dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored, for interface compatibility).
            factor (int): Quantization step size, typically in [4, 32]. Higher values = fewer colors.

        Returns:
            List[ndarray]: Batch of color-quantized images, each with the same shape and dtype as input.
        """
        if not stego_imgs:
            return []

        batch_np = np.stack(stego_imgs, axis=0).astype(np.uint8)
        if factor > 1:
            quantized_batch = (batch_np // factor) * factor
        else:
            quantized_batch = batch_np
        quantized_batch = np.clip(quantized_batch, 0, 255).astype(np.uint8)
        return [quantized_batch[i] for i in range(quantized_batch.shape[0])]


class HueShiftAttack(BaseTestAttackModel):
    """
    A color transformation attack that shifts the hue of an image in the HSV color space.

    This attack modifies the perceived color of the image by rotating the hue channel,
    which can disrupt watermark signals that rely on specific color distributions or
    chrominance components.

    The 'factor' parameter controls the degree of hue shift in degrees:
        - 0.0: No change (identity)
        - 30.0: Moderate color shift (e.g., red → orange)
        - 180.0: Maximum shift (complementary colors)

    The hue is cyclic modulo 180 (OpenCV convention), so shifts wrap around.

    Reference:
        Smith, A. R. (1978). Color gamut transform pairs.
        In Proceedings of the 5th annual conference on Computer graphics and interactive techniques (SIGGRAPH '78).

    Note:
        - Input: List of uint8 images, each [H, W] (grayscale) or [H, W, 3] (RGB), range [0, 255]
        - Output: List of hue-shifted images, same shape and dtype
        - For grayscale images, the single channel is replicated to three channels for HSV processing,
          and the output is converted back to grayscale by taking one channel
        - For RGB images, the attack shifts the hue channel in HSV space
        - Uses OpenCV's HSV representation (H: 0–180, S: 0–255, V: 0–255)
        - Supports batch processing for efficiency
    """

    def __init__(self, noisename: str = "Hue"):
        """
        Initializes the hue shift attack.

        Args:
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=False)

    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: float = 30.0) -> List[ndarray]:
        """
        Applies hue shift to a batch of images (grayscale or RGB) in HSV color space.

        For RGB images:
            1. Converts from RGB to HSV.
            2. Adds the shift value to the H channel, modulo 180.
            3. Converts back to RGB.
        For grayscale images:
            1. Replicates the single channel to three channels to create a pseudo-RGB image.
            2. Applies the hue shift in HSV space.
            3. Converts back to grayscale by taking one channel.

        This operation preserves luminance and saturation while altering color appearance for RGB images.
        For grayscale images, the effect may be limited due to the lack of initial color information.

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each [H, W] (grayscale) or [H, W, 3] (RGB),
                                       dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored, for interface compatibility).
            factor (float): Hue shift amount in degrees, range [0, 180].

        Returns:
            List[ndarray]: Batch of hue-shifted images, each with the same shape and dtype as input.
        """
        if not stego_imgs:
            return []

        shift = float(factor) % 180.0
        noised_imgs = []
        for stego in stego_imgs:
            is_gray = stego.ndim == 2
            if is_gray:
                stego = np.stack([stego, stego, stego], axis=-1).astype(np.uint8)
            hsv = cv2.cvtColor(stego.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[..., 0] = (hsv[..., 0] + shift) % 180.0
            hsv_uint8 = hsv.astype(np.uint8)
            rgb = cv2.cvtColor(hsv_uint8, cv2.COLOR_HSV2RGB)
            if is_gray:
                rgb = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
            noised_imgs.append(rgb)
        return noised_imgs


class DarkenAttack(BaseTestAttackModel):
    """
    A brightness reduction attack that darkens the image by scaling the V (value) channel in HSV color space.

    This attack simulates low-light conditions or display dimming, which can degrade watermark signals
    embedded in darker regions of the image. It preserves hue and saturation while reducing overall luminance.

    The 'factor' parameter controls the brightness level:
        - 1.0: No change (identity)
        - 0.0: Completely black (maximum attack strength)
        - Values in between: Proportional darkening

    Reference:
        Smith, A. R. (1978). Color gamut transform pairs.
        In Proceedings of the 5th annual conference on Computer graphics and interactive techniques (SIGGRAPH '78).

    Note:
        - Input: List of uint8 images, each [H, W] (grayscale) or [H, W, 3] (RGB), range [0, 255]
        - Output: List of darkened images, same shape and dtype
        - For grayscale images, the single channel is replicated to three channels for HSV processing,
          and the output is converted back to grayscale by taking one channel
        - For RGB images, the attack scales the V channel in HSV space
        - Uses OpenCV's HSV representation (V ∈ [0, 255])
    """

    def __init__(self, noisename: str = "Darken"):
        """
        Initializes the darken attack.

        Args:
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=True)

    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: float = 0.7) -> List[ndarray]:
        """
        Applies a darkening effect to a batch of images (grayscale or RGB) using HSV color space transformation.

        For RGB images:
            1. Converts RGB to HSV.
            2. Scales the value channel (V) by 'factor'.
            3. Clips the result to the valid range [0, 255].
            4. Converts back to RGB.
        For grayscale images:
            1. Replicates the single channel to three channels to create a pseudo-RGB image.
            2. Applies the darkening in HSV space by scaling the V channel.
            3. Converts back to grayscale by taking one channel.

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each [H, W] (grayscale) or [H, W, 3] (RGB),
                                       dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored, for interface compatibility).
            factor (float): Brightness scaling factor in [0.0, 1.0].
                           1.0 = no change, 0.0 = completely black.

        Returns:
            List[ndarray]: Batch of darkened images, each with the same shape and dtype as input.
        """
        if not stego_imgs:
            return []

        factor = np.clip(factor, 0.0, 1.0)
        noised_imgs = []
        for stego in stego_imgs:
            is_gray = stego.ndim == 2
            if is_gray:
                stego = np.stack([stego, stego, stego], axis=-1).astype(np.uint8)
            hsv = cv2.cvtColor(stego.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[..., 2] = np.clip(hsv[..., 2] * factor, 0, 255)
            hsv_uint8 = hsv.astype(np.uint8)
            rgb = cv2.cvtColor(hsv_uint8, cv2.COLOR_HSV2RGB)
            if is_gray:
                rgb = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
            noised_imgs.append(rgb)
        return noised_imgs


class BrightenAttack(BaseTestAttackModel):
    """
    A brightness enhancement attack that increases image luminance by amplifying the V (value) channel in HSV color space.

    This attack simulates overexposure or display brightening, which can wash out subtle details and degrade watermark signals
    embedded in mid-to-dark tone regions. It preserves hue and saturation while increasing overall brightness.

    The 'factor' parameter controls the amplification level:
        - 1.0: No change (identity)
        - >1.0: Increased brightness (e.g., 1.5, 2.0)
        - Values are clipped to the valid range [0, 255] to prevent overflow

    Reference:
        Smith, A. R. (1978). Color gamut transform pairs.
        In Proceedings of the 5th annual conference on Computer graphics and interactive techniques (SIGGRAPH '78).

    Note:
        - Input: List of uint8 images, each [H, W] (grayscale) or [H, W, 3] (RGB), range [0, 255]
        - Output: List of brightened images, same shape and dtype
        - For grayscale images, the single channel is replicated to three channels for HSV processing,
          and the output is converted back to grayscale by taking one channel
        - For RGB images, the attack scales the V channel in HSV space
        - Uses OpenCV's HSV representation (V ∈ [0, 255])
    """

    def __init__(self, noisename: str = "Brighten"):
        """
        Initializes the brighten attack.

        Args:
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=False)

    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: float = 2.0) -> List[ndarray]:
        """
        Applies a brightening effect to a batch of images (grayscale or RGB) using HSV color space transformation.

        For RGB images:
            1. Converts RGB to HSV.
            2. Scales the value channel (V) by 'factor'.
            3. Clips the result to the valid range [0, 255].
            4. Converts back to RGB.
        For grayscale images:
            1. Replicates the single channel to three channels to create a pseudo-RGB image.
            2. Applies the brightening in HSV space by scaling the V channel.
            3. Converts back to grayscale by taking one channel.

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each [H, W] (grayscale) or [H, W, 3] (RGB),
                                       dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored, for interface compatibility).
            factor (float): Brightness amplification factor, typically >= 1.0.
                           1.0 = no change, higher values = brighter image.

        Returns:
            List[ndarray]: Batch of brightened images, each with the same shape and dtype as input.
        """
        if not stego_imgs:
            return []

        noised_imgs = []
        factor = max(1.0, factor)
        for stego in stego_imgs:
            is_gray = stego.ndim == 2
            if is_gray:
                stego = np.stack([stego, stego, stego], axis=-1).astype(np.uint8)
            hsv = cv2.cvtColor(stego.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[..., 2] = np.clip(hsv[..., 2] * factor, 0, 255)
            hsv_uint8 = hsv.astype(np.uint8)
            rgb = cv2.cvtColor(hsv_uint8, cv2.COLOR_HSV2RGB)
            if is_gray:
                rgb = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
            noised_imgs.append(rgb)
        return noised_imgs


class DesaturateAttack(BaseTestAttackModel):
    """
    A color degradation attack that reduces image saturation by scaling the S (saturation) channel in HSV space.

    This attack weakens color-based watermark signals by making the image appear more grayscale.
    It simulates poor display conditions or intentional color suppression.

    The 'factor' parameter controls the saturation level:
        - 1.0: No change (full color)
        - 0.0: Complete desaturation (grayscale)
        - Values in between: Partial desaturation

    Reference:
        Smith, A. R. (1978). Color gamut transform pairs.
        In Proceedings of the 5th annual conference on Computer graphics and interactive techniques (SIGGRAPH '78).

    Note:
        - Input: List of uint8 images, each [H, W] (grayscale) or [H, W, 3] (RGB), range [0, 255]
        - Output: List of desaturated images, same shape and dtype
        - For grayscale images, the single channel is replicated to three channels for HSV processing,
          and the output is converted back to grayscale by taking one channel
        - For RGB images, the attack scales the S channel in HSV space
        - Uses OpenCV's HSV representation (S ∈ [0, 255])
        - Desaturation has minimal effect on grayscale images due to their lack of color information
    """

    def __init__(self, noisename: str = "Desaturate"):
        """
        Initializes the desaturation attack.

        Args:
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=True)

    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: float = 0.5) -> List[ndarray]:
        """
        Applies desaturation to a batch of images (grayscale or RGB) using HSV color space transformation.

        For RGB images:
            1. Converts RGB to HSV.
            2. Scales the saturation channel (S) by 'factor'.
            3. Clips to valid range [0, 255].
            4. Converts back to RGB.
        For grayscale images:
            1. Replicates the single channel to three channels to create a pseudo-RGB image.
            2. Applies desaturation in HSV space by scaling the S channel.
            3. Converts back to grayscale by taking one channel.

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each [H, W] (grayscale) or [H, W, 3] (RGB),
                                       dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored, for interface compatibility).
            factor (float): Saturation scaling factor in [0.0, 1.0].
                           1.0 = no change, 0.0 = grayscale.

        Returns:
            List[ndarray]: Batch of desaturated images, each with the same shape and dtype as input.
        """
        if not stego_imgs:
            return []

        noised_imgs = []
        factor = np.clip(factor, 0., 1.)
        for stego in stego_imgs:
            is_gray = stego.ndim == 2
            if is_gray:
                stego = np.stack([stego, stego, stego], axis=-1).astype(np.uint8)
            hsv = cv2.cvtColor(stego.astype(np.uint8), cv2.COLOR_RGB2HSV)
            hsv = hsv.astype(np.float32)
            hsv[..., 1] = np.clip(hsv[..., 1] * factor, 0, 255)
            hsv = hsv.astype(np.uint8)
            rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
            if is_gray:
                rgb = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
            noised_imgs.append(rgb)
        return noised_imgs


class OversaturateAttack(BaseTestAttackModel):
    """
    A color enhancement attack that increases image saturation by amplifying the S (saturation) channel in HSV space.

    This attack pushes colors towards their most vivid state, potentially causing clipping and color distortion.
    It can disrupt watermark signals that rely on subtle color variations or are sensitive to chrominance changes.

    The 'factor' parameter controls the amplification level:
        - 1.0: No change (identity)
        - >1.0: Increased saturation (e.g., 1.5, 2.0, 3.0)

    Reference:
        Smith, A. R. (1978). Color gamut transform pairs.
        In Proceedings of the 5th annual conference on Computer graphics and interactive techniques (SIGGRAPH '78).

    Note:
        - Input: List of uint8 images, each [H, W] (grayscale) or [H, W, 3] (RGB), range [0, 255]
        - Output: List of oversaturated images, same shape and dtype
        - For grayscale images, the single channel is replicated to three channels for HSV processing,
          and the output is converted back to grayscale by taking one channel
        - For RGB images, the attack scales the S channel in HSV space
        - Uses OpenCV's HSV representation (S ∈ [0, 255])
        - Oversaturation has minimal effect on grayscale images due to their lack of color information
    """

    def __init__(self, noisename: str = "Oversaturate"):
        """
        Initializes the oversaturation attack.

        Args:
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=False)

    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: float = 2.0) -> List[ndarray]:
        """
        Applies oversaturation to a batch of images (grayscale or RGB) using HSV color space transformation.

        For RGB images:
            1. Converts RGB to HSV.
            2. Scales the saturation channel (S) by 'factor'.
            3. Clips the result to the valid range [0, 255].
            4. Converts back to RGB.
        For grayscale images:
            1. Replicates the single channel to three channels to create a pseudo-RGB image.
            2. Applies oversaturation in HSV space by scaling the S channel.
            3. Converts back to grayscale by taking one channel.

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each [H, W] (grayscale) or [H, W, 3] (RGB),
                                       dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored, for interface compatibility).
            factor (float): Saturation amplification factor, typically >= 1.0.
                           1.0 = no change, higher values = stronger saturation.

        Returns:
            List[ndarray]: Batch of oversaturated images, each with the same shape and dtype as input.
        """
        if not stego_imgs:
            return []

        noised_imgs = []
        factor = max(1.0, float(factor))
        for stego in stego_imgs:
            is_gray = stego.ndim == 2
            if is_gray:
                stego = np.stack([stego, stego, stego], axis=-1).astype(np.uint8)
            hsv = cv2.cvtColor(stego.astype(np.uint8), cv2.COLOR_RGB2HSV)
            hsv = hsv.astype(np.float32)
            hsv[..., 1] = np.clip(hsv[..., 1] * factor, 0, 255)
            hsv = hsv.astype(np.uint8)
            rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
            if is_gray:
                rgb = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
            noised_imgs.append(rgb)
        return noised_imgs


class UnsharpMasking(BaseTestAttackModel):
    """
    An image sharpening attack using unsharp masking technique with full batch support.

    This attack enhances high-frequency details by amplifying the residuals between the original
    and a blurred version of the image. It is effective against watermarking methods sensitive
    to edge enhancement.

    The 'factor' parameter controls the sharpening strength:
        - 0.0: No change
        - >0.0: Increasing sharpening (may amplify artifacts)

    This implementation uses torchvision for true batched Gaussian blur, enabling GPU acceleration
    and eliminating the need for Python loops.

    Reference:
        Pizer, S. M., et al. (1987). Adaptive histogram equalization and its variations.
        Computer Vision, Graphics, and Image Processing, 39(3), 355–368.

    Note:
        - Input: List of uint8 RGB images [H, W, 3], range [0, 255]
        - Output: List of sharpened images, same shape and dtype
        - Uses torchvision for batched Gaussian blur (supports GPU)
    """

    def __init__(self, noisename: str = "UnsharpMasking", sigma: float = 3.0, threshold: float = 0):
        """
        Initializes the unsharp masking attack.

        Args:
            noisename (str): Name identifier for logging and reporting.
            sigma (float): Standard deviation of the Gaussian kernel. Default is 3.0.
            threshold (float): Threshold for high-frequency components (0 = no thresholding).
        """
        super().__init__(noisename=noisename, factor_inversely_related=False)
        self.sigma = sigma
        self.threshold = threshold
        self.blur_op = transforms.GaussianBlur(kernel_size=int(6 * sigma + 1) // 2 * 2 + 1, sigma=sigma)

    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: float = 1.0) -> List[
        ndarray]:
        """
        Applies unsharp masking to a batch of stego images using fully vectorized operations.

        The pipeline:
            1. Stack images into a 4D numpy array
            2. Convert to float32 and normalize to [0,1]
            3. Convert to CHW tensor and move to device
            4. Apply batched Gaussian blur using torchvision
            5. Compute high-frequency residuals
            6. Apply thresholding (optional)
            7. Sharpen and clamp
            8. Convert back to numpy HWC uint8

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each [H, W, 3], dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored).
            factor (float): Sharpening strength factor, typically in [0.0, 5.0].

        Returns:
            List[ndarray]: Batch of sharpened images, each with the same shape and dtype as input.
        """
        if not stego_imgs:
            return []

        device = "cuda" if torch.cuda.is_available() else "cpu"
        batch_np = np.stack(stego_imgs, axis=0).astype(np.float32)
        is_color = batch_np.ndim == 4
        if batch_np.ndim == 3:
            batch_np = np.expand_dims(batch_np, axis=-1)
        batch_np = batch_np / 255.0
        batch_tensor = torch.from_numpy(batch_np).permute(0, 3, 1, 2).to(device)
        with torch.no_grad():
            blurred_tensor = self.blur_op(batch_tensor)
        high_freq = batch_tensor - blurred_tensor
        if self.threshold > 0:
            high_freq = torch.where(torch.abs(high_freq) > self.threshold / 255.0, high_freq, torch.tensor(0.0, device=device))
        sharpened_tensor = batch_tensor + factor * high_freq
        sharpened_tensor = torch.clamp(sharpened_tensor, 0.0, 1.0)
        sharpened_np = (sharpened_tensor.permute(0, 2, 3, 1).cpu().numpy() * 255.0).astype(np.uint8)
        noised_imgs = []
        for i in range(sharpened_np.shape[0]):
            if is_color:
                noised_img = sharpened_np[i]
            else:
                noised_img = sharpened_np[i][:, :, 0]
            noised_imgs.append(noised_img)
        return noised_imgs
