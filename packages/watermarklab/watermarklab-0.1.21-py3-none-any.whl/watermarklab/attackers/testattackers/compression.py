# Copyright (c) 2025 Jiale Chen <chenoly@outlook.com>. All rights reserved.
# SPDX-License-Identifier: MIT
import random

import cv2
import torch
import numpy as np
from numpy import ndarray
import torch.nn.functional as F
from typing import Optional, List
from watermarklab.utils.basemodel import BaseTestAttackModel
from compressai.zoo import cheng2020_anchor, bmshj2018_hyperprior, bmshj2018_factorized, mbt2018_mean, mbt2018


class VAE_BMshj2018FactorizedAttack(BaseTestAttackModel):
    """
    A Variational Autoencoder (VAE)-based attack using the bmshj2018_factorized model.
    Applies lossy compression to the input image to potentially disrupt embedded watermarks.
    Reference: Ballé, J., Laparra, V., & Simoncelli, E. P. (2018). End-to-end optimized image compression.
               International Conference on Learning Representations (ICLR).

    Args:
        device (str): Device to run the model on, defaults to "cuda".
        noisename (str): Name identifier for the model, defaults to "VAE_BMshj2018FactorizedAttack".

    Note:
        The 'factor' parameter controls compression quality (1-8):
        - 1: strongest compression (most aggressive watermark removal).
        - 8: weakest compression (most faithful to input).
        Input and output are uint8 [H, W, 3] [0,255].
    """
    _global_model_cache = {}

    def __init__(self, device: str = "cuda", noisename: str = "VAE_BMshj2018FactorizedAttack"):
        super().__init__(noisename, True)
        self.device = torch.device(device)
        self._cached_models = {}

    def _get_model(self, quality: int):
        """
        Retrieves or loads the VAE model for the specified compression quality, utilizing caching.

        Args:
            quality (int): Compression quality level (1-8).

        Returns:
            torch.nn.Module: The VAE model for the specified quality.
        """
        q = max(1, min(8, quality))
        cache_key = (q, self.device)
        if quality not in self._cached_models:
            if cache_key in VAE_BMshj2018FactorizedAttack._global_model_cache:
                self._cached_models[quality] = VAE_BMshj2018FactorizedAttack._global_model_cache[cache_key]
            else:
                model = bmshj2018_factorized(quality=q, pretrained=True).eval().to(self.device)
                VAE_BMshj2018FactorizedAttack._global_model_cache[cache_key] = model
                self._cached_models[quality] = model
        return self._cached_models[quality]

    @torch.inference_mode()
    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: int = 3) -> List[ndarray]:
        """
        Applies VAE-based compression attack to the input image.

        Args:
            stego_imgs (ndarray): Input image in RGB format, uint8 [H, W, 3] [0,255].
            cover_img (ndarray, optional): Not used.
            factor (int): Compression quality level (1-8).

        Returns:
            ndarray: Reconstructed image after compression, same shape and dtype as input.
        """
        if not stego_imgs:
            return []

        is_grayscale = len(stego_imgs[0].shape) == 2
        original_shapes = [img.shape[:2] for img in stego_imgs]
        target_h, target_w = original_shapes[0]

        if is_grayscale:
            processed_imgs = [np.stack([img, img, img], axis=-1) for img in stego_imgs]
        else:
            processed_imgs = stego_imgs

        batch_np = np.stack(processed_imgs, axis=0).astype(np.float32)
        batch_float = batch_np / 255.0

        batch_tensor = torch.from_numpy(batch_float).permute(0, 3, 1, 2).to(self.device)

        batch_tensor = F.interpolate(
            batch_tensor,
            size=(512, 512),
            mode='bilinear',
            align_corners=False
        )

        model = self._get_model(factor)
        output = model(batch_tensor)
        rec_batch = output["x_hat"].clamp(0, 1)

        rec_batch = F.interpolate(
            rec_batch,
            size=(target_h, target_w),
            mode='bilinear',
            align_corners=False
        )

        rec_np = rec_batch.permute(0, 2, 3, 1).cpu().numpy()
        rec_np = (rec_np * 255).astype(np.uint8)

        if is_grayscale:
            rec_gray = np.dot(rec_np, [0.299, 0.587, 0.114]).astype(np.uint8)
            return [rec_gray[i] for i in range(rec_gray.shape[0])]
        else:
            return [rec_np[i] for i in range(rec_np.shape[0])]


class VAE_BMshj2018HyperpriorAttack(BaseTestAttackModel):
    """
    A Variational Autoencoder (VAE)-based attack using the bmshj2018_hyperprior model.
    Applies learned image compression with a scale hyperprior to disrupt embedded watermarks.

    This attack first resizes the input image to 512x512 using nearest-neighbor interpolation,
    then compresses and reconstructs it using the hyperprior VAE model, and finally resizes it
    back to the original resolution. The resize operations introduce additional geometric distortion,
    making this a stronger attack than compression alone.

    The 'factor' parameter controls the compression quality (1-8):
        - 1: strongest compression (lowest bitrate, highest distortion)
        - 8: weakest compression (highest bitrate, near lossless)

    Reference:
        Ballé, J., Minnen, D., Singh, S., Hwang, S. J., & Johnston, N. (2018).
        Variational image compression with a scale hyperprior. International Conference on Learning Representations (ICLR).
        https://arxiv.org/abs/1802.01436

    Note:
        - Input: List of uint8 RGB images [H, W, 3], range [0, 255]
        - Output: List of reconstructed images, same shape and dtype
        - The model is cached per quality level and device for efficiency
    """
    _global_model_cache = {}

    def __init__(self, device: str = "cuda", noisename: str = "VAE_BMshj2018HyperpriorAttack"):
        """
        Initializes the attack model with the specified device and name.

        Args:
            device (str): Device to run the model on ('cuda' or 'cpu').
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=True)
        self.device = torch.device(device)
        self._cached_models = {}

    def _get_model(self, quality: int):
        """
        Retrieves or loads the bmshj2018_hyperprior model for the given quality level.

        The model is cached globally using (quality, device) as key to prevent redundant loading
        and GPU memory duplication.

        Args:
            quality (int): Compression quality level (1-8).

        Returns:
            torch.nn.Module: The pre-trained VAE model with hyperprior in evaluation mode.
        """
        q = max(1, min(8, quality))
        cache_key = (q, self.device)
        if quality not in self._cached_models:
            if cache_key in VAE_BMshj2018HyperpriorAttack._global_model_cache:
                self._cached_models[quality] = VAE_BMshj2018HyperpriorAttack._global_model_cache[cache_key]
            else:
                model = bmshj2018_hyperprior(quality=q, pretrained=True).eval().to(self.device)
                VAE_BMshj2018HyperpriorAttack._global_model_cache[cache_key] = model
                self._cached_models[quality] = model
        return self._cached_models[quality]

    @torch.inference_mode()
    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: int = 3) -> List[
        ndarray]:
        """
        Applies the VAE-based compression attack with hyperprior and resize pre/post-processing.

        The attack pipeline is:
            1. Resize each input image to 512x512 using nearest-neighbor interpolation.
            2. Batch the preprocessed tensors and move to GPU.
            3. Forward pass through the hyperprior VAE model.
            4. Resize each reconstructed image back to its original size.
            5. Return the batch of distorted images.

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each of shape [H, W, 3], dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (not used in this attack).
            factor (int): Compression quality level (1-8). Higher values preserve more detail.

        Returns:
            List[ndarray]: Batch of reconstructed images, each with the same shape and dtype as the input.
        """
        if not stego_imgs:
            return []

        is_grayscale = len(stego_imgs[0].shape) == 2
        original_shapes = [img.shape[:2] for img in stego_imgs]
        target_h, target_w = original_shapes[0]

        if is_grayscale:
            processed_imgs = [np.stack([img, img, img], axis=-1) for img in stego_imgs]
        else:
            processed_imgs = stego_imgs

        batch_np = np.stack(processed_imgs, axis=0).astype(np.float32)  # [B, H, W, 3]
        batch_float = batch_np / 255.0  # Normalize to [0,1]

        batch_tensor = torch.from_numpy(batch_float).permute(0, 3, 1, 2).to(self.device)

        batch_tensor = F.interpolate(
            batch_tensor,
            size=(512, 512),
            mode='bilinear',
            align_corners=False
        )

        model = self._get_model(factor)
        output = model(batch_tensor)
        rec_batch = output["x_hat"].clamp(0, 1)

        rec_batch = F.interpolate(
            rec_batch,
            size=(target_h, target_w),
            mode='bilinear',
            align_corners=False
        )

        rec_np = rec_batch.permute(0, 2, 3, 1).cpu().numpy()
        rec_np = (rec_np * 255).astype(np.uint8)

        if is_grayscale:
            rec_gray = np.dot(rec_np, [0.299, 0.587, 0.114]).astype(np.uint8)
            return [rec_gray[i] for i in range(rec_gray.shape[0])]
        else:
            return [rec_np[i] for i in range(rec_np.shape[0])]


class VAE_MBT2018MeanAttack(BaseTestAttackModel):
    """
    A Variational Autoencoder (VAE)-based attack using the mbt2018_mean model.
    Applies learned image compression with a mean-scale hyperprior to disrupt embedded watermarks.

    This attack first resizes the input image to 512x512 using nearest-neighbor interpolation,
    then compresses and reconstructs it using the MBT2018 (Minnen et al.) model with mean-scale hyperprior,
    and finally resizes it back to the original resolution. The resize operations introduce additional
    geometric distortion, making this a stronger attack than compression alone.

    The 'factor' parameter controls the compression quality (1-8):
        - 1: strongest compression (lowest bitrate, highest distortion)
        - 8: weakest compression (highest bitrate, near lossless)

    Reference:
        Minnen, D., Ballé, J., & Toderici, G. (2018).
        Joint autoregressive and hierarchical priors for learned image compression.
        Advances in Neural Information Processing Systems (NeurIPS).
        https://arxiv.org/abs/1809.02736

    Note:
        - Input: List of uint8 RGB images [H, W, 3], range [0, 255]
        - Output: List of reconstructed images, same shape and dtype
        - The model is cached per quality level and device for efficiency
    """
    _global_model_cache = {}

    def __init__(self, device: str = "cuda", noisename: str = "VAE_MBT2018MeanAttack"):
        """
        Initializes the attack model with the specified device and name.

        Args:
            device (str): Device to run the model on ('cuda' or 'cpu').
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=True)
        self.device = torch.device(device)
        self._cached_models = {}

    def _get_model(self, quality: int):
        """
        Retrieves or loads the mbt2018_mean model for the given quality level.

        The model is cached globally using (quality, device) as key to prevent redundant loading
        and GPU memory duplication.

        Args:
            quality (int): Compression quality level (1-8).

        Returns:
            torch.nn.Module: The pre-trained VAE model with mean-scale hyperprior in evaluation mode.
        """
        q = max(1, min(8, quality))
        cache_key = (q, self.device)
        if quality not in self._cached_models:
            if cache_key in VAE_MBT2018MeanAttack._global_model_cache:
                self._cached_models[quality] = VAE_MBT2018MeanAttack._global_model_cache[cache_key]
            else:
                model = mbt2018_mean(quality=q, pretrained=True).eval().to(self.device)
                VAE_MBT2018MeanAttack._global_model_cache[cache_key] = model
                self._cached_models[quality] = model
        return self._cached_models[quality]

    @torch.inference_mode()
    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: int = 3) -> List[
        ndarray]:
        """
        Applies the VAE-based compression attack with mean-scale hyperprior and resize pre/post-processing.

        The attack pipeline is:
            1. Resize each input image to 512x512 using nearest-neighbor interpolation.
            2. Batch the preprocessed tensors and move to GPU.
            3. Forward pass through the MBT2018 VAE model.
            4. Resize each reconstructed image back to its original size.
            5. Return the batch of distorted images.

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each of shape [H, W, 3], dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (not used in this attack).
            factor (int): Compression quality level (1-8). Higher values preserve more detail.

        Returns:
            List[ndarray]: Batch of reconstructed images, each with the same shape and dtype as the input.
        """
        if not stego_imgs:
            return []

        is_grayscale = len(stego_imgs[0].shape) == 2
        original_shapes = [img.shape[:2] for img in stego_imgs]
        target_h, target_w = original_shapes[0]

        if is_grayscale:
            processed_imgs = [np.stack([img, img, img], axis=-1) for img in stego_imgs]
        else:
            processed_imgs = stego_imgs

        batch_np = np.stack(processed_imgs, axis=0).astype(np.float32)
        batch_float = batch_np / 255.0

        batch_tensor = torch.from_numpy(batch_float).permute(0, 3, 1, 2).to(self.device)

        batch_tensor = F.interpolate(
            batch_tensor,
            size=(512, 512),
            mode='bilinear',
            align_corners=False
        )

        model = self._get_model(factor)
        output = model(batch_tensor)
        rec_batch = output["x_hat"].clamp(0, 1)

        rec_batch = F.interpolate(
            rec_batch,
            size=(target_h, target_w),
            mode='bilinear',
            align_corners=False
        )

        rec_np = rec_batch.permute(0, 2, 3, 1).cpu().numpy()
        rec_np = (rec_np * 255).astype(np.uint8)

        if is_grayscale:
            rec_gray = np.dot(rec_np, [0.299, 0.587, 0.114]).astype(np.uint8)
            return [rec_gray[i] for i in range(rec_gray.shape[0])]
        else:
            return [rec_np[i] for i in range(rec_np.shape[0])]


class VAE_MBT2018Attack(BaseTestAttackModel):
    """
    A Variational Autoencoder (VAE)-based attack using the mbt2018 model.
    Applies learned image compression to disrupt embedded watermarks.

    This attack first resizes the input image to 512x512 using nearest-neighbor interpolation,
    then compresses and reconstructs it using the MBT2018 (Minnen et al.) model,
    and finally resizes it back to the original resolution. The resize operations introduce additional
    geometric distortion, making this a stronger attack than compression alone.

    The 'factor' parameter controls the compression quality (1-8):
        - 1: strongest compression (lowest bitrate, highest distortion)
        - 8: weakest compression (highest bitrate, near lossless)

    Reference:
        Minnen, D., Ballé, J., & Toderici, G. (2018).
        Joint autoregressive and hierarchical priors for learned image compression.
        Advances in Neural Information Processing Systems (NeurIPS).
        https://arxiv.org/abs/1809.02736

    Note:
        - Input: List of uint8 RGB images [H, W, 3], range [0, 255]
        - Output: List of reconstructed images, same shape and dtype
        - The model is cached per quality level and device for efficiency
    """
    _global_model_cache = {}

    def __init__(self, device: str = "cuda", noisename: str = "VAE_MBT2018Attack"):
        """
        Initializes the attack model with the specified device and name.

        Args:
            device (str): Device to run the model on ('cuda' or 'cpu').
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=True)
        self.device = torch.device(device)
        self._cached_models = {}

    def _get_model(self, quality: int):
        """
        Retrieves or loads the mbt2018 model for the given quality level.

        The model is cached globally using (quality, device) as key to prevent redundant loading
        and GPU memory duplication.

        Args:
            quality (int): Compression quality level (1-8).

        Returns:
            torch.nn.Module: The pre-trained VAE model in evaluation mode.
        """
        q = max(1, min(8, quality))
        cache_key = (q, self.device)
        if quality not in self._cached_models:
            if cache_key in VAE_MBT2018Attack._global_model_cache:
                self._cached_models[quality] = VAE_MBT2018Attack._global_model_cache[cache_key]
            else:
                model = mbt2018(quality=q, pretrained=True).eval().to(self.device)
                VAE_MBT2018Attack._global_model_cache[cache_key] = model
                self._cached_models[quality] = model
        return self._cached_models[quality]

    @torch.inference_mode()
    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: int = 3) -> List[
        ndarray]:
        """
        Applies the VAE-based compression attack with resize pre/post-processing.

        The attack pipeline is:
            1. Resize each input image to 512x512 using nearest-neighbor interpolation.
            2. Batch the preprocessed tensors and move to GPU.
            3. Forward pass through the MBT2018 VAE model.
            4. Resize each reconstructed image back to its original size.
            5. Return the batch of distorted images.

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each of shape [H, W, 3], dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (not used in this attack).
            factor (int): Compression quality level (1-8). Higher values preserve more detail.

        Returns:
            List[ndarray]: Batch of reconstructed images, each with the same shape and dtype as the input.
        """
        if not stego_imgs:
            return []

        is_grayscale = len(stego_imgs[0].shape) == 2
        original_shapes = [img.shape[:2] for img in stego_imgs]
        target_h, target_w = original_shapes[0]

        if is_grayscale:
            processed_imgs = [np.stack([img, img, img], axis=-1) for img in stego_imgs]
        else:
            processed_imgs = stego_imgs

        batch_np = np.stack(processed_imgs, axis=0).astype(np.float32)
        batch_float = batch_np / 255.0

        batch_tensor = torch.from_numpy(batch_float).permute(0, 3, 1, 2).to(self.device)

        batch_tensor = F.interpolate(
            batch_tensor,
            size=(512, 512),
            mode='bilinear',
            align_corners=False
        )

        model = self._get_model(factor)
        output = model(batch_tensor)
        rec_batch = output["x_hat"].clamp(0, 1)

        rec_batch = F.interpolate(
            rec_batch,
            size=(target_h, target_w),
            mode='bilinear',
            align_corners=False
        )

        rec_np = rec_batch.permute(0, 2, 3, 1).cpu().numpy()
        rec_np = (rec_np * 255).astype(np.uint8)

        if is_grayscale:
            rec_gray = np.dot(rec_np, [0.299, 0.587, 0.114]).astype(np.uint8)
            return [rec_gray[i] for i in range(rec_gray.shape[0])]
        else:
            return [rec_np[i] for i in range(rec_np.shape[0])]


class VAE_Cheng2020Attack(BaseTestAttackModel):
    """
    A Variational Autoencoder (VAE)-based attack using the cheng2020_anchor model.
    Applies learned image compression with attention modules to disrupt embedded watermarks.

    This attack first resizes the input image to 512x512 using nearest-neighbor interpolation,
    then compresses and reconstructs it using the Cheng2020 (CVPR 2020) model,
    and finally resizes it back to the original resolution. The resize operations introduce additional
    geometric distortion, making this a stronger attack than compression alone.

    The 'factor' parameter controls the compression quality (1-6):
        - 1: strongest compression (lowest bitrate, highest distortion)
        - 6: weakest compression (highest bitrate, near lossless)

    Reference:
        Cheng, Z., Sun, H., & Takeuchi, M. (2020).
        Learned image compression with discretized Gaussian mixture likelihoods and attention modules.
        IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR).
        https://arxiv.org/abs/2001.01568

    Note:
        - Input: List of uint8 RGB images [H, W, 3], range [0, 255]
        - Output: List of reconstructed images, same shape and dtype
        - The model is cached per quality level and device for efficiency
    """
    _global_model_cache = {}

    def __init__(self, device: str = "cuda", noisename: str = "VAE_Cheng2020Attack"):
        """
        Initializes the attack model with the specified device and name.

        Args:
            device (str): Device to run the model on ('cuda' or 'cpu').
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=True)
        self.device = torch.device(device)
        self._cached_models = {}

    def _get_model(self, quality: int):
        """
        Retrieves or loads the cheng2020_anchor model for the given quality level.

        The model is cached globally using (quality, device) as key to prevent redundant loading
        and GPU memory duplication.

        Args:
            quality (int): Compression quality level (1-6).

        Returns:
            torch.nn.Module: The pre-trained VAE model in evaluation mode.
        """
        if quality not in self._cached_models:
            q = max(1, min(6, quality))
            cache_key = (q, self.device)
            if cache_key in VAE_Cheng2020Attack._global_model_cache:
                model = VAE_Cheng2020Attack._global_model_cache[cache_key]
                self._cached_models[quality] = model
            else:
                model = cheng2020_anchor(quality=q, pretrained=True).eval().to(self.device)
                VAE_Cheng2020Attack._global_model_cache[cache_key] = model
                self._cached_models[quality] = model
        return self._cached_models[quality]

    @torch.inference_mode()
    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: int = 3) -> List[ndarray]:
        """
        Applies the VAE-based compression attack with resize pre/post-processing.

        The attack pipeline is:
            1. Resize each input image to 512x512 using nearest-neighbor interpolation.
            2. Batch the preprocessed tensors and move to GPU.
            3. Forward pass through the Cheng2020 VAE model.
            4. Resize each reconstructed image back to its original size.
            5. Return the batch of distorted images.

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each of shape [H, W, 3], dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (not used in this attack).
            factor (int): Compression quality level (1-6). Higher values preserve more detail.

        Returns:
            List[ndarray]: Batch of reconstructed images, each with the same shape and dtype as the input.
        """
        if not stego_imgs:
            return []

        is_grayscale = len(stego_imgs[0].shape) == 2
        original_shapes = [img.shape[:2] for img in stego_imgs]
        target_h, target_w = original_shapes[0]

        if is_grayscale:
            processed_imgs = [np.stack([img, img, img], axis=-1) for img in stego_imgs]
        else:
            processed_imgs = stego_imgs

        batch_np = np.stack(processed_imgs, axis=0).astype(np.float32)
        batch_float = batch_np / 255.0

        batch_tensor = torch.from_numpy(batch_float).permute(0, 3, 1, 2).to(self.device)

        batch_tensor = F.interpolate(
            batch_tensor,
            size=(512, 512),
            mode='bilinear',
            align_corners=False
        )

        model = self._get_model(factor)
        output = model(batch_tensor)
        rec_batch = output["x_hat"].clamp(0, 1)

        rec_batch = F.interpolate(
            rec_batch,
            size=(target_h, target_w),
            mode='bilinear',
            align_corners=False
        )

        rec_np = rec_batch.permute(0, 2, 3, 1).cpu().numpy()
        rec_np = (rec_np * 255).astype(np.uint8)

        if is_grayscale:
            rec_gray = np.dot(rec_np, [0.299, 0.587, 0.114]).astype(np.uint8)
            return [rec_gray[i] for i in range(rec_gray.shape[0])]
        else:
            return [rec_np[i] for i in range(rec_np.shape[0])]


class WebPCompression(BaseTestAttackModel):
    """
    A lossy compression attack that simulates WebP encoding artifacts.

    This attack encodes the input image into the WebP format at a specified quality level
    and then decodes it back to RGB. The recompression introduces compression artifacts
    such as blockiness, blurring, and color banding, which can disrupt embedded watermarks.

    The 'factor' parameter controls the compression quality:
        - 10: Very low quality (high compression, severe artifacts)
        - 100: Lossless (no artifacts, for baseline testing)

    This attack is highly relevant for evaluating watermark robustness against
    web-based image delivery systems where WebP is widely used.

    Reference:
        Google. (2023). WebP Image Format.
        https://developers.google.com/speed/webp

    Note:
        - Input: List of uint8 RGB images [H, W, 3], range [0, 255]
        - Output: List of compressed images, same shape and dtype
        - Requires OpenCV with WebP support enabled
    """

    def __init__(self, noisename: str = "WebPCompression"):
        """
        Initializes the WebP compression attack.

        Args:
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename,
                         factor_inversely_related=True)  # Higher factor = less compression = weaker attack

    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: int = 20) -> List[
        ndarray]:
        """
        Applies WebP compression to a batch of stego images using OpenCV.

        For each image:
            1. Converts from RGB to BGR (OpenCV default).
            2. Encodes to WebP format with specified quality.
            3. Decodes back to BGR.
            4. Converts back to RGB.

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each [H, W, 3], dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored, for interface compatibility).
            factor (int): WebP quality factor in [10, 100].
                         10 = high compression, 100 = lossless.

        Returns:
            List[ndarray]: Batch of WebP-compressed images, each with the same shape and dtype as input.
        """
        if not stego_imgs:
            return []

        noised_batch = []
        is_color = stego_imgs[0].ndim == 3
        encode_param = [cv2.IMWRITE_WEBP_QUALITY, int(np.clip(factor, 10, 100))]
        for img in stego_imgs:
            if is_color:
                img = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_RGB2BGR)
                _, encoded_img = cv2.imencode('.webp', img, encode_param)
                decoded_img = cv2.imdecode(encoded_img, cv2.IMREAD_COLOR)
                decoded_img = cv2.cvtColor(decoded_img, cv2.COLOR_BGR2RGB)
            else:
                _, encoded_img = cv2.imencode('.webp', img.astype(np.uint8), encode_param)
                decoded_img = cv2.imdecode(encoded_img, cv2.IMREAD_GRAYSCALE)
            noised_batch.append(decoded_img)
        return noised_batch


class Jpeg(BaseTestAttackModel):
    """
    A lossy compression attack that applies JPEG encoding to introduce compression artifacts.

    This attack simulates common image degradation from web publishing, social media sharing,
    or storage optimization. It introduces blockiness, ringing, and high-frequency loss,
    which are particularly effective at disrupting watermark signals embedded in AC coefficients
    or high-frequency DCT components.

    The 'factor' parameter controls the JPEG quality setting:
        - 100: Near-lossless (very weak attack)
        - 95: High quality (minimal artifacts)
        - 50: Medium quality (visible block artifacts)
        - 20: Low quality (severe degradation, strong attack)
        - 1: Lowest quality (maximum compression, extreme distortion)

    This implementation uses OpenCV's imencode/imdecode for JPEG compression.

    Note:
        - Input: List of uint8 RGB images [H, W, 3], range [0, 255]
        - Output: List of JPEG-compressed images, same shape and dtype
        - Uses OpenCV with JPEG quality factor [1, 100]
    """

    def __init__(self, noisename: str = "Jpeg"):
        """
        Initializes the JPEG compression attack.

        Args:
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename,
                         factor_inversely_related=True)  # Higher factor = less compression = weaker attack

    def attack(self, stego_img: List[ndarray], cover_img: List[ndarray] = None, factor: int = 20) -> List[
        ndarray]:
        """
        Applies JPEG compression to a batch of stego images using OpenCV.

        For each image:
            1. Converts from RGB to BGR (OpenCV default).
            2. Encodes to JPEG format with specified quality.
            3. Decodes back to BGR.
            4. Converts back to RGB.

        Args:
            stego_img (List[ndarray]): Batch of watermarked images, each [H, W, 3], dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored, for interface compatibility).
            factor (int): JPEG quality factor in [1, 100].
                         100 = best quality, 1 = worst quality.

        Returns:
            List[ndarray]: Batch of JPEG-compressed images, each with the same shape and dtype as input.
        """
        if not stego_img:
            return []

        # Clip factor to valid range
        quality = max(1, min(100, int(factor)))
        noised_batch = []
        encode_param = [cv2.IMWRITE_JPEG_QUALITY, quality]
        is_color = stego_img[0].ndim == 3
        for img in stego_img:
            if is_color:
                img = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_RGB2BGR)
                _, encoded_img = cv2.imencode('.jpg', img, encode_param)
                decoded_img = cv2.imdecode(encoded_img, cv2.IMREAD_COLOR)
                decoded_img = cv2.cvtColor(decoded_img, cv2.COLOR_BGR2RGB)
            else:
                _, encoded_img = cv2.imencode('.jpg', img.astype(np.uint8), encode_param)
                decoded_img = cv2.imdecode(encoded_img, cv2.IMREAD_GRAYSCALE)
            noised_batch.append(decoded_img.astype(np.float32))
        return noised_batch


class MultiJpeg(BaseTestAttackModel):
    """
    A multiple JPEG compression attack that applies repeated JPEG encoding
    with quality factors varying in a range around a central value.

    - Class parameter `quality_factor`: central JPEG quality (e.g., 80)
    - Class parameter `quality_range`: half-width of quality variation (e.g., 10 → [70, 90])
    - Method parameter `factor`: number of compression rounds (e.g., 1, 3, 5)

    Simulates real-world scenarios where an image undergoes multiple saves
    with slightly different compression settings, accumulating artifacts.

    Note:
        - Input: List of uint8 images [H, W] (grayscale) or [H, W, 3] (RGB), range [0, 255]
        - Output: Same shape and dtype
        - Uses OpenCV's imencode/imdecode via self.jpeg.attack()
    """

    def __init__(
            self,
            noisename: str = "Multi-Jpeg",
            quality_factor: int = 80,
            quality_range: int = 5,
    ):
        """
        Args:
            noisename (str): Name for logging. Defaults to "Multi-Jpeg".
            quality_factor (int): Central JPEG quality in [1, 100]. Default is 80.
            quality_range (int): Half-range of quality variation. Final QF ∈ [qf−range, qf+range] ∩ [1,100].
                                 If 0, uses fixed quality (original behavior). Default: 5.
        """
        super().__init__(noisename=noisename, factor_inversely_related=False)
        if not (1 <= quality_factor <= 100):
            raise ValueError("quality_factor must be in [1, 100]")
        if quality_range < 0:
            raise ValueError("quality_range must be non-negative")
        self.quality_factor = int(quality_factor)
        self.quality_range = int(quality_range)
        self.jpeg = Jpeg()

    def attack(
            self,
            stego_img: List[np.ndarray],
            cover_img: Optional[List[np.ndarray]] = None,
            factor: int = 1,
    ) -> List[np.ndarray]:
        """
        Applies JPEG compression `factor` times.
        Each round uses a quality factor sampled from:
            [quality_factor - quality_range, quality_factor + quality_range],
        clamped to [1, 100].

        Args:
            stego_img: List of images, each [H, W] or [H, W, 3], dtype=uint8, range [0,255].
            cover_img: Ignored (for interface compatibility).
            factor: Number of JPEG compression rounds (≥1). Default: 1.

        Returns:
            List of images after repeated JPEG compression.
        """
        if not stego_img:
            return []

        num_rounds = max(1, int(factor))
        noised_batch = []

        q_min = max(1, self.quality_factor - self.quality_range)
        q_max = min(100, self.quality_factor + self.quality_range)

        for img in stego_img:
            current_img = img.copy().astype(np.uint8)
            for _ in range(num_rounds):
                if self.quality_range == 0:
                    qf = self.quality_factor
                else:
                    qf = random.randint(q_min, q_max)
                current_img = self.jpeg.attack([current_img], None, factor=qf)[0]
            noised_batch.append(current_img.astype(np.uint8))
        return noised_batch


class Jpeg2000(BaseTestAttackModel):
    """
    A lossy wavelet-based compression attack using the JPEG2000 format.

    This attack applies JPEG2000 compression, which uses discrete wavelet transform (DWT) instead of DCT,
    resulting in different artifacts (e.g., less blockiness, more ringing) compared to standard JPEG.
    It is effective for evaluating watermark robustness against modern compression standards.

    The 'factor' parameter controls the compression ratio:
        - 1: Minimal compression (highest quality)
        - 100: Maximum compression (lowest quality)
        Higher values = stronger attack.

    This implementation uses OpenCV's imencode/imdecode for JPEG2000 compression.
    Note: OpenCV relies on external libraries (e.g., Jasper, OpenJPEG) for JP2 support.

    Reference:
        Skodras, A., Christopoulos, C., & Ebrahimi, T. (2001).
        The JPEG 2000 still image compression standard.
        IEEE Signal Processing Magazine, 18(5), 36–58.

    Note:
        - Input: List of uint8 RGB images [H, W, 3], range [0, 255]
        - Output: List of JPEG2000-compressed images, same shape and dtype
        - Requires OpenCV with JPEG2000 support (IMWRITE_JPEG2000_COMPRESSION_X1000)
    """

    def __init__(self, noisename: str = "Jpeg2000"):
        """
        Initializes the JPEG2000 compression attack.

        Args:
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=False)

    def attack(self, stego_img: List[ndarray], cover_img: List[ndarray] = None, factor: int = 20) -> List[ndarray]:
        """
        Applies JPEG2000 compression to a batch of stego images using OpenCV.

        For each image:
            1. Converts from RGB to BGR (OpenCV default).
            2. Encodes to JPEG2000 (.jp2) format with specified compression ratio.
            3. Decodes back to BGR.
            4. Converts back to RGB.

        Args:
            stego_img (List[ndarray]): Batch of watermarked images, each [H, W, 3], dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored, for interface compatibility).
            factor (int): Compression ratio factor in [1, 100].
                         1 = low compression, 100 = high compression.

        Returns:
            List[ndarray]: Batch of JPEG2000-compressed images, each with the same shape and dtype as input.
        """
        if not stego_img:
            return []

        # Clip factor to valid range
        noised_batch = []
        is_color = stego_img[0].ndim == 3
        compression_ratio = np.clip(factor, 0, 1000)
        encode_param = [cv2.IMWRITE_JPEG2000_COMPRESSION_X1000, compression_ratio]
        for img in stego_img:
            if is_color:
                img = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_RGB2BGR)
                _, encoded_img = cv2.imencode('.jp2', img, encode_param)
                decoded_img = cv2.imdecode(encoded_img, cv2.IMREAD_COLOR)
                decoded_img = cv2.cvtColor(decoded_img, cv2.COLOR_BGR2RGB)
            else:
                _, encoded_img = cv2.imencode('.jp2', img.astype(np.uint8), encode_param)
                decoded_img = cv2.imdecode(encoded_img, cv2.IMREAD_GRAYSCALE)
            noised_batch.append(decoded_img.astype(np.float32))
        return noised_batch



class MultiJpeg2000(BaseTestAttackModel):
    """
    An attack model that applies JPEG2000 compression multiple times to stego images,
    with quality factor varying around a central value during repeated rounds.

    - quality_factor: central quality level (higher = less compression)
    - quality_range: half-width of variation (e.g., range=10 → [qf-10, qf+10])
    - factor: number of compression rounds

    Simulates real-world scenarios where images undergo multiple saves
    with slightly different JPEG2000 settings.
    """

    def __init__(
            self,
            quality_factor: int = 80,
            quality_range: int = 5,
            noisename: str = "Multi-Jpeg2000"
    ):
        """
        Initialize the MultiJpeg2000 attack.

        Args:
            quality_factor (int): Central quality level for JPEG2000 (e.g., 80).
            quality_range (int): Half-range for quality variation. Final QF ∈ [qf−range, qf+range] ∩ [1, 100].
                                 Set to 5 for fixed quality (default).
            noisename (str): Name identifier for this noise/attack type.
        """
        super().__init__(noisename=noisename, factor_inversely_related=False)
        if not (1 <= quality_factor <= 100):
            raise ValueError("quality_factor must be in [1, 100]")
        if quality_range < 0:
            raise ValueError("quality_range must be non-negative")
        self.quality_factor = quality_factor
        self.quality_range = quality_range
        self.jpeg2000 = Jpeg2000()

    def attack(
            self,
            stego_img: List[ndarray],
            cover_img: Optional[List[ndarray]] = None,
            factor: int = 3
    ) -> List[ndarray]:
        """
        Apply multiple rounds of JPEG2000 compression.
        Each round uses a quality factor sampled from [quality_factor ± quality_range],
        clamped to [1, 100].

        Args:
            stego_img (List[ndarray]): List of stego images (uint8, [0,255], shape [H,W] or [H,W,3]).
            cover_img (List[ndarray], optional): Ignored.
            factor (int): Number of compression rounds (≥1).

        Returns:
            List[ndarray]: Attacked images after repeated JPEG2000 compression.
        """
        if not stego_img:
            return []

        num_rounds = max(1, int(factor))
        noised_batch = []

        q_min = max(1, self.quality_factor - self.quality_range)
        q_max = min(100, self.quality_factor + self.quality_range)

        for img in stego_img:
            current_img = img.copy()
            for _ in range(num_rounds):
                if self.quality_range == 0:
                    qf = self.quality_factor
                else:
                    qf = random.randint(q_min, q_max)
                current_img = self.jpeg2000.attack([current_img], None, qf)[0]
            noised_batch.append(current_img)
        return noised_batch
