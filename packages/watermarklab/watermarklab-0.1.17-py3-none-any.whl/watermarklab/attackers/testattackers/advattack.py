# Copyright (c) 2025 Jiale Chen <chenoly@outlook.com>. All rights reserved.
# SPDX-License-Identifier: MIT
import torch
import numpy as np
import torch.nn as nn
from typing import List, Optional
from torchvision import transforms, models
from torchvision.transforms import functional as F
from watermarklab.utils.basemodel import BaseTestAttackModel


class ClipEmbeddingAttack(BaseTestAttackModel):
    """
    An adversarial attack that perturbs stego images to maximally distort their CLIP image embeddings.

    This attack uses Projected Gradient Descent (PGD) to generate minimal L∞-bounded perturbations
    that cause significant deviation in the CLIP embedding space. It represents a strong adaptive
    adversary with full knowledge of the feature extractor, commonly used to evaluate watermark robustness.

    The 'strength' parameter controls the perturbation budget:
        - strength = 2 → ε = 2/255
        - strength = 4 → ε = 4/255
        - strength = 6 → ε = 6/255
        - strength = 8 → ε = 8/255

    Implementation details:
        - Uses CLIP-ViT-B/32 from OpenAI
        - Applies 200-step PGD with α = 0.05 × ε
        - Automatically converts grayscale images to RGB for processing
        - Attack is performed in original resolution; CLIP input is temporarily resized to 224×224
        - Output preserves original spatial dimensions and color mode (grayscale or RGB)

        Radford, A., Kim, J. W., Hallacy, C., Ramesh, A., Goh, G., Agarwal, S., Sastry, G., Askell, A., Mishkin, P., Clark,
        J., et al. Learning transferable visual models from natural language supervision. In International conference on machine learning, pp. 8748–8763. PMLR, 2021.

    Note:
        - Input: List of uint8 images, [H, W], [H, W, 1], or [H, W, 3], range [0, 255]
        - Output: List of uint8 images with same shape and color mode as input
        - First run downloads ~600MB CLIP model from Hugging Face
    """

    def __init__(self, noisename: str = "ClipEmbeddingAttack"):
        super().__init__(noisename=noisename, factor_inversely_related=False)
        self.OPENAI_CLIP_MEAN = [0.48145466, 0.4578275, 0.40821073]
        self.OPENAI_CLIP_STD = [0.26862954, 0.26130258, 0.27577711]

    def attack(
            self,
            stego_imgs: List[np.ndarray],
            cover_img: Optional[List[np.ndarray]] = None,
            strength: float = 2.0,
    ) -> List[np.ndarray]:
        if not stego_imgs:
            return []

        rgb_images = []
        for img in stego_imgs:
            if img.ndim == 2:
                rgb_img = np.stack([img, img, img], axis=-1)
            elif img.ndim == 3:
                if img.shape[2] == 1:
                    rgb_img = np.concatenate([img, img, img], axis=-1)
                elif img.shape[2] == 3:
                    rgb_img = img
                else:
                    raise ValueError(f"Unsupported number of channels: {img.shape[2]}")
            else:
                raise ValueError(f"Unsupported image shape: {img.shape}")
            rgb_images.append(rgb_img)

        batch_np = np.stack(rgb_images, axis=0).astype(np.float32)
        batch_np = np.clip(batch_np, 0, 255) / 255.0
        batch_tensor = torch.from_numpy(batch_np).permute(0, 3, 1, 2)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        from transformers import CLIPModel
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device).eval()
        normalizer = transforms.Normalize(mean=self.OPENAI_CLIP_MEAN, std=self.OPENAI_CLIP_STD)

        eps = strength / 255.0
        alpha = 0.05 * eps
        steps = 200
        loss_fn = nn.MSELoss()

        images_full = batch_tensor.to(device)
        images_224 = F.resize(images_full, [224, 224], antialias=True)
        original_emb = model.get_image_features(pixel_values=normalizer(images_224)).detach()

        adv_full = images_full + torch.empty_like(images_full).uniform_(-eps, eps)
        adv_full = torch.clamp(adv_full, 0.0, 1.0).detach()

        for _ in range(steps):
            adv_full.requires_grad_(True)
            adv_224 = F.resize(adv_full, [224, 224], antialias=True)
            adv_emb = model.get_image_features(pixel_values=normalizer(adv_224))
            loss = loss_fn(adv_emb, original_emb)
            grad = torch.autograd.grad(loss, adv_full)[0]
            with torch.no_grad():
                adv_full = adv_full.detach() + alpha * grad.sign()
                delta = torch.clamp(adv_full - images_full, min=-eps, max=eps)
                adv_full = torch.clamp(images_full + delta, 0.0, 1.0)

        adv_np = (adv_full.permute(0, 2, 3, 1).cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)

        output_imgs = []
        for i, orig_img in enumerate(stego_imgs):
            adv_rgb = adv_np[i]
            if orig_img.ndim == 2:
                gray = np.dot(adv_rgb, [0.2989, 0.5870, 0.1140])
                output_imgs.append(gray.astype(np.uint8))
            elif orig_img.ndim == 3 and orig_img.shape[2] == 1:
                gray = np.dot(adv_rgb, [0.2989, 0.5870, 0.1140])
                output_imgs.append(gray.astype(np.uint8)[:, :, np.newaxis])
            else:
                output_imgs.append(adv_rgb)
        return output_imgs


class VAEEmbeddingAttack(BaseTestAttackModel):
    """
    An adversarial attack that perturbs stego images to maximally distort their VAE latent representations.

    This attack uses Projected Gradient Descent (PGD) to generate minimal L∞-bounded perturbations
    that cause significant deviation in the VAE's latent space (mode of the posterior). It simulates
    an adaptive adversary aware of the generative prior, commonly used in diffusion-based watermarking.

    Supported VAEs:
        - "stabilityai/sd-vae-ft-mse"   (SD 1.x VAE)

        - "stabilityai/sdxl-vae"        (SDXL VAE)
        Podell, D., English, Z., Lacey, K., Blattmann, A., Dockhorn, T., Müller, J., Penna, J., and Rombach, R.
        Sdxl: Improving latent diffusion models for high-resolution image synthe sis. arXiv preprint arXiv:2307.01952, 2023.

    The 'strength' parameter controls the perturbation budget:
        - strength = 2 → ε = 2/255
        - strength = 4 → ε = 4/255
        - strength = 6 → ε = 6/255
        - strength = 8 → ε = 8/255

    Implementation details:
        - Input images normalized to [-1, 1] before VAE encoding
        - Uses 200-step PGD with α = 0.05 × ε and L2 loss
        - Attack performed in original resolution
        - Output preserves original spatial dimensions and color mode

    Note:
        - Input: List of uint8 images, [H, W], [H, W, 1], or [H, W, 3], range [0, 255]
        - Output: List of uint8 images with same shape and color mode as input
    """

    def __init__(self, model_name: str = "stabilityai/sd-vae-ft-mse", noisename: str = "VAEEmbeddingAttack"):
        super().__init__(noisename=noisename, factor_inversely_related=False)
        self.model_name = model_name

    def attack(
            self,
            stego_imgs: List[np.ndarray],
            cover_img: Optional[List[np.ndarray]] = None,
            strength: float = 2.0,
    ) -> List[np.ndarray]:
        if not stego_imgs:
            return []

        rgb_images = []
        for img in stego_imgs:
            if img.ndim == 2:
                rgb_img = np.stack([img, img, img], axis=-1)
            elif img.ndim == 3:
                if img.shape[2] == 1:
                    rgb_img = np.concatenate([img, img, img], axis=-1)
                elif img.shape[2] == 3:
                    rgb_img = img
                else:
                    raise ValueError(f"Unsupported channel count: {img.shape[2]}")
            else:
                raise ValueError(f"Unsupported image shape: {img.shape}")
            rgb_images.append(rgb_img)

        batch_np = np.stack(rgb_images, axis=0).astype(np.float32)
        batch_np = np.clip(batch_np, 0, 255) / 255.0
        batch_tensor = torch.from_numpy(batch_np).permute(0, 3, 1, 2)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        from diffusers.models import AutoencoderKL
        vae = AutoencoderKL.from_pretrained(self.model_name).to(device).eval()

        eps = strength / 255.0
        alpha = 0.05 * eps
        steps = 200
        loss_fn = nn.MSELoss()

        images_full = batch_tensor.to(device)
        images_vae = 2.0 * images_full - 1.0
        with torch.no_grad():
            original_latents = vae.encode(images_vae).latent_dist.mode().detach()

        adv_full = images_full + torch.empty_like(images_full).uniform_(-eps, eps)
        adv_full = torch.clamp(adv_full, 0.0, 1.0).detach()

        for _ in range(steps):
            adv_full.requires_grad_(True)
            adv_vae = 2.0 * adv_full - 1.0
            adv_latents = vae.encode(adv_vae).latent_dist.mode()
            loss = loss_fn(adv_latents, original_latents)
            grad = torch.autograd.grad(loss, adv_full)[0]
            with torch.no_grad():
                adv_full = adv_full.detach() + alpha * grad.sign()
                delta = torch.clamp(adv_full - images_full, min=-eps, max=eps)
                adv_full = torch.clamp(images_full + delta, 0.0, 1.0)

        adv_np = (adv_full.permute(0, 2, 3, 1).cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)

        output_imgs = []
        for i, orig_img in enumerate(stego_imgs):
            adv_rgb = adv_np[i]
            if orig_img.ndim == 2:
                gray = np.dot(adv_rgb, [0.2989, 0.5870, 0.1140])
                output_imgs.append(gray.astype(np.uint8))
            elif orig_img.ndim == 3 and orig_img.shape[2] == 1:
                gray = np.dot(adv_rgb, [0.2989, 0.5870, 0.1140])
                output_imgs.append(gray.astype(np.uint8)[:, :, np.newaxis])
            else:
                output_imgs.append(adv_rgb)
        return output_imgs


class ResNet18EmbeddingAttack(BaseTestAttackModel):
    """
    Adversarial attack that perturbs stego images to maximally distort ResNet-18 feature embeddings.

    This attack uses PGD to generate minimal L∞-bounded perturbations that cause large deviations
    in the feature map of a specified ResNet-18 layer (e.g., "last" for global average pooled features).

    Supported layers:
        - "layer1", "layer2", "layer3", "layer4": intermediate feature maps
        - "last": final global average pooled vector (512-dim)

    The 'strength' parameter controls the perturbation budget:
        - strength = 2 → ε = 2/255
        - strength = 4 → ε = 4/255
        - strength = 6 → ε = 6/255
        - strength = 8 → ε = 8/255

    Implementation details:
        - Attack performed in original resolution
        - Images temporarily resized to 224×224 for ResNet feature extraction
        - Normalized with ImageNet mean/std
        - 200-step PGD with α = 0.05 × ε and L2 loss
        - Output preserves original spatial dimensions and color mode

    Note:
        - Input: List of uint8 images, [H, W], [H, W, 1], or [H, W, 3], range [0, 255]
        - Output: List of uint8 images with same shape and color mode as input
        - First run downloads ResNet-18 (~45MB) from torchvision
    """

    def __init__(self, layer: str = "last", noisename: str = "ResNet18EmbeddingAttack"):
        super().__init__(noisename=noisename, factor_inversely_related=False)
        if layer not in {"layer1", "layer2", "layer3", "layer4", "last"}:
            raise ValueError("layer must be one of {'layer1', 'layer2', 'layer3', 'layer4', 'last'}")
        self.layer = layer
        self._model = None
        self.IMAGENET_MEAN = [0.485, 0.456, 0.406]
        self.IMAGENET_STD = [0.229, 0.224, 0.225]

    def _build_model(self):
        original = models.resnet18(pretrained=True)
        if self.layer == "layer1":
            features = nn.Sequential(*list(original.children())[:-6])
        elif self.layer == "layer2":
            features = nn.Sequential(*list(original.children())[:-5])
        elif self.layer == "layer3":
            features = nn.Sequential(*list(original.children())[:-4])
        elif self.layer == "layer4":
            features = nn.Sequential(*list(original.children())[:-3])
        elif self.layer == "last":
            features = nn.Sequential(*list(original.children())[:-1])
        else:
            raise RuntimeError("Unexpected layer")
        features.eval()
        return features

    def attack(
            self,
            stego_imgs: List[np.ndarray],
            cover_img: Optional[List[np.ndarray]] = None,
            strength: float = 2.0,
    ) -> List[np.ndarray]:
        if not stego_imgs:
            return []

        rgb_images = []
        for img in stego_imgs:
            if img.ndim == 2:
                rgb_img = np.stack([img, img, img], axis=-1)
            elif img.ndim == 3:
                if img.shape[2] == 1:
                    rgb_img = np.concatenate([img, img, img], axis=-1)
                elif img.shape[2] == 3:
                    rgb_img = img
                else:
                    raise ValueError(f"Unsupported channel count: {img.shape[2]}")
            else:
                raise ValueError(f"Unsupported image shape: {img.shape}")
            rgb_images.append(rgb_img)

        batch_np = np.stack(rgb_images, axis=0).astype(np.float32)
        batch_np = np.clip(batch_np, 0, 255) / 255.0
        batch_tensor = torch.from_numpy(batch_np).permute(0, 3, 1, 2)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if self._model is None:
            self._model = self._build_model()
        model = self._model.to(device)

        mean = torch.tensor(self.IMAGENET_MEAN).view(1, 3, 1, 1).to(device)
        std = torch.tensor(self.IMAGENET_STD).view(1, 3, 1, 1).to(device)

        eps = strength / 255.0
        alpha = 0.05 * eps
        steps = 200
        loss_fn = nn.MSELoss()

        images_full = batch_tensor.to(device)
        images_224 = F.resize(images_full, [224, 224], antialias=True)
        images_224_norm = (images_224 - mean) / std
        with torch.no_grad():
            original_features = model(images_224_norm).detach()

        adv_full = images_full + torch.empty_like(images_full).uniform_(-eps, eps)
        adv_full = torch.clamp(adv_full, 0.0, 1.0).detach()

        for _ in range(steps):
            adv_full.requires_grad_(True)
            adv_224 = F.resize(adv_full, [224, 224], antialias=True)
            adv_224_norm = (adv_224 - mean) / std
            adv_features = model(adv_224_norm)
            loss = loss_fn(adv_features, original_features)
            grad = torch.autograd.grad(loss, adv_full)[0]
            with torch.no_grad():
                adv_full = adv_full.detach() + alpha * grad.sign()
                delta = torch.clamp(adv_full - images_full, min=-eps, max=eps)
                adv_full = torch.clamp(images_full + delta, 0.0, 1.0)

        adv_np = (adv_full.permute(0, 2, 3, 1).cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)

        output_imgs = []
        for i, orig_img in enumerate(stego_imgs):
            adv_rgb = adv_np[i]
            if orig_img.ndim == 2:
                gray = np.dot(adv_rgb, [0.2989, 0.5870, 0.1140])
                output_imgs.append(gray.astype(np.uint8))
            elif orig_img.ndim == 3 and orig_img.shape[2] == 1:
                gray = np.dot(adv_rgb, [0.2989, 0.5870, 0.1140])
                output_imgs.append(gray.astype(np.uint8)[:, :, np.newaxis])
            else:
                output_imgs.append(adv_rgb)
        return output_imgs
