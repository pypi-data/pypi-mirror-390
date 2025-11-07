# Copyright (c) 2025 Jiale Chen <chenoly@outlook.com>. All rights reserved.
# SPDX-License-Identifier: MIT
from typing import List, Dict
from watermarklab.attackers.testattackers import *
from watermarklab.utils.basemodel import BaseDiffAttackModel, AttackerWithFactors

__all__ = ["DistortionLoader", "AttackersWithFactorsModel"]


class DistortionLoader(nn.Module):
    """
    A module that applies a sequence of noise layers to an image, simulating distortions.

    Parameters:
    -----------
    noise_list : List[BaseDiffNoiseModel]
        A list of noise models that will be applied sequentially.
    max_step : int, optional (default=100)
        The maximum training step, used for scheduling the number of applied noise layers.
    k_min : int, optional (default=1)
        The minimum number of noise layers to apply.
    k_max : int, optional (default=2)
        The maximum number of noise layers to apply. If larger than `len(noise_list)`, it will be clipped.

    Methods:
    --------
    stair_k(now_step: int) -> int:
        Determines the number of noise layers (`k`) to apply based on a step-wise (staircase) schedule.
    parabolic_k(now_step: int, gamma: float = 1.3) -> int:
        Determines `k` using a parabolic function, allowing a smooth increase over time.
    forward(marked_img: torch.Tensor, cover_img: torch.Tensor, now_step: int = 0) -> torch.Tensor:
        Applies `k` randomly selected noise layers sequentially to the marked image.
    """

    def __init__(self, noise_list: List[BaseDiffAttackModel], k_mode: str = "stair_k", k_min: int = 1, k_max: int = 2,
                 max_step=1):
        super(DistortionLoader, self).__init__()
        assert k_mode in ["stair_k", "parabolic_k"]
        self.k_mode = k_mode
        self.max_step = max_step
        self.k_min = k_min
        self.k_max = min(k_max, len(noise_list))

        self.noise_list = noise_list

    def stair_k(self, now_step: int) -> int:
        """
        Determines the number of noise layers (`k`) to apply using a staircase function.
        The number of noise layers increases in discrete steps as training progresses.

        Parameters:
        -----------
        now_step : int
            The current training step.

        Returns:
        --------
        k : int
            The number of noise layers to apply.
        """
        if self.k_max == self.k_min:
            return self.k_min

        total_steps = self.k_max - self.k_min + 1
        max_steps_per_k = self.max_step / total_steps
        step_index = int(now_step // max_steps_per_k)
        k = self.k_min + step_index
        return min(k, self.k_max)

    def parabolic_k(self, now_step: int, gamma: float = 1.3) -> int:
        """
        Determines the number of noise layers (`k`) using a parabolic growth function.
        The number of layers smoothly increases over time.

        Parameters:
        -----------
        now_step : int
            The current training step.
        gamma : float, optional (default=1.3)
            A parameter controlling the curvature of the growth function.

        Returns:
        --------
        k : int
            The number of noise layers to apply.
        """
        factor = 1.0 if now_step >= self.max_step else (now_step / self.max_step) ** gamma
        k = self.k_min + (self.k_max - self.k_min) * factor
        return max(self.k_min, int(k))

    def forward(self, marked_img: torch.Tensor, cover_img: torch.Tensor, now_step: int = 0) -> torch.Tensor:
        """
        Applies randomly selected noise layers to the marked image.

        Parameters:
        -----------
        marked_img : torch.Tensor
            The input image to which noise is applied.
        cover_img : torch.Tensor
            The original reference image (may be used by noise models).
        now_step : int, optional (default=0)
            The current training step, used to determine `k`.

        Returns:
        --------
        noised_img : torch.Tensor
            The distorted image after applying `k` noise layers.
        """
        if self.k_mode == "stair_k":
            k = self.stair_k(now_step)
        else:
            k = self.parabolic_k(now_step)
        selected_keys = random.sample(range(len(self.noise_list)), k)
        noised_img = marked_img
        for key in selected_keys:
            noised_img = self.noise_list[key](noised_img, cover_img, now_step)

        return noised_img.clamp(0, 1)


class AttackersWithFactorsModel(list):
    """
    A class that extends Python's built-in list to hold attackers with their factors.
    This class behaves exactly like a regular list but provides a convenient way
    to initialize with a comprehensive set of default image attackers for adversarial attacks.

    The list is lazily initialized to prevent creation when the module is imported,
    only creating the attackers when actually needed. This improves import performance
    and memory usage.

    The default attackers cover various categories of image transformations and attacks:
    - Diffusion-based attacks for regenerating images
    - Neural compression attacks using VAE models
    - Noise injection attacks (salt & pepper, Gaussian, Poisson)
    - Blur attacks (Gaussian, median, mean, unsharp masking)
    - Image compression attacks (JPEG, JPEG2000, WebP)
    - Geometric transformations (resize, rotate, crop, etc.)
    - Color transformations (contrast, saturation, hue shifts, etc.)
    """

    def __init__(self, default_attackers: List[AttackerWithFactors] = None, attacker_groups: Dict = None):
        """
        Initialize the AttackersWithFactorsModel with either provided attackers or defaults.

        Args:
            default_attackers (List[AttackerWithFactors]): A list of pre-defined attackers.
                If provided, these attackers will be used instead of the default comprehensive set.
                If None, a default set of 40+ different attackers across multiple categories
                will be automatically created and populated.
        """
        super().__init__()

        self.attacker_groups = {
            "Compression": [
                "BMshj2018Factorized",
                "BMshj2018Hyperprior",
                "MBT2018Mean",
                "MBT2018",
                "Cheng2020",
                "JPEGCompression",
                "Multi-JPEG",
                "JPEG2000Compression",
                "Multi-JPEG2000",
                "WebPCompression"
            ],
            "AdvEmbAttack": [
                "Resnet18EmbAttack",
                "SDXL-VAEEmbAttack",
                "ClipEmbAttack",
                "KL-VAE8EmbAttack",
            ],
            "Noise": [
                "Salt&PepperNoise",
                "GaussianNoise",
                "PoissonNoise",
                "PixelDropout"
            ],
            "Blur": [
                "GaussianBlur",
                "MedianFilter",
                "MeanFilter"
            ],
            "Geometric": [
                "Resize",
                "Rotation",
                "Crop",
                "Cropout",
                "RandomCrop",
                "RandomCropout",
                "Flip",
                "RegionZoom",
                "TranslationAttack"
                "ShearAttack"
            ],
            "Color": [
                "ContrastReduction",
                "UnsharpMasking"
                "ContrastEnhancement",
                "ColorQuantization",
                "ChromaticAberration",
                "GammaCorrection",
                "HueShift",
                "Darken",
                "Brighten",
                "Desaturate",
                "Oversaturate"
            ],
            "Diffusion": [
                "Diffusion-Regen",
                "Mult-Diffusion"
            ]
        }
        if attacker_groups is not None:
            self.attacker_groups = attacker_groups
        if default_attackers is not None:
            self.extend(default_attackers)
        else:
            default_attackers_list = [
                # ===================================================================
                # Diffusion Attacks - Regenerate images using diffusion models
                # These attacks attempt to reconstruct images through diffusion processes
                # ===================================================================
                AttackerWithFactors(
                    attacker=DiffuseAttack(),
                    attackername="Diffusion-Regen",
                    factors=[20, 40, 60, 80, 100, 120, 140, 160, 180, 200],
                    factorsymbol=r"$t$"
                ),
                AttackerWithFactors(
                    attacker=MultiDiffuseAttack(noise_step=60),
                    attackername="Mult-Diffusion",
                    factors=[1, 2, 3, 4, 6],
                    factorsymbol=r"$N$"
                ),
                # ===================================================================
                # Adverbial Attacks - PGD
                # ===================================================================
                AttackerWithFactors(
                    attacker=ClipEmbeddingAttack(),
                    attackername="ClipEmbAttack",
                    factors=[2, 4, 6, 8, 10, 12, 14, 16, 18],
                    factorsymbol=r"$\eta$"
                ),
                AttackerWithFactors(
                    attacker=VAEEmbeddingAttack(model_name="stabilityai/sd-vae-ft-mse"),
                    attackername="KL-VAE8EmbAttack",
                    factors=[2, 4, 6, 8, 10, 12, 14, 16, 18],
                    factorsymbol=r"$\eta$"
                ),
                AttackerWithFactors(
                    attacker=VAEEmbeddingAttack(model_name="stabilityai/sdxl-vae"),
                    attackername="SDXL-VAEEmbAttack",
                    factors=[2, 4, 6, 8, 10, 12, 14, 16, 18],
                    factorsymbol=r"$\eta$"
                ),
                AttackerWithFactors(
                    attacker=ResNet18EmbeddingAttack(layer="last"),
                    attackername="Resnet18EmbAttack",
                    factors=[2, 4, 6, 8, 10, 12, 14, 16, 18],
                    factorsymbol=r"$\eta$"
                ),
                # ===================================================================
                # Neural Compression Attacks - Compress images using learned models  ***************BMshj2018
                # Variational AutoEncoder (VAE) based compression from different papers
                # ===================================================================

                AttackerWithFactors(
                    attacker=VAE_BMshj2018FactorizedAttack(),
                    attackername="BMshj2018Factorized",
                    factors=[1, 2, 3, 4, 5, 6, 7, 8],
                    factorsymbol=r"$q$"
                ),
                AttackerWithFactors(
                    attacker=VAE_BMshj2018HyperpriorAttack(),
                    attackername="BMshj2018Hyperprior",
                    factors=[1, 2, 3, 4, 5, 6, 7, 8],
                    factorsymbol=r"$q$"
                ),
                AttackerWithFactors(
                    attacker=VAE_MBT2018MeanAttack(),
                    attackername="MBT2018Mean",
                    factors=[1, 2, 3, 4, 5, 6, 7, 8],
                    factorsymbol=r"$q$"
                ),
                AttackerWithFactors(
                    attacker=VAE_MBT2018Attack(),
                    attackername="MBT2018",
                    factors=[1, 2, 3, 4, 5, 6, 7, 8],
                    factorsymbol=r"$q$"
                ),
                AttackerWithFactors(
                    attacker=VAE_Cheng2020Attack(),
                    attackername="Cheng2020",
                    factors=[1, 2, 3, 4, 5, 6],  # Quality levels
                    factorsymbol=r"$q$"  # Quality parameter symbol
                ),

                # ===================================================================
                # Image Compression Attacks - Compress images using standard codecs
                # Simulate lossy compression artifacts from common image formats
                # ===================================================================
                AttackerWithFactors(
                    attacker=Jpeg(),
                    attackername="JPEGCompression",
                    factors=[90, 80, 70, 60, 50, 40, 30, 20, 10],
                    factorsymbol=r"$q$"
                ),
                AttackerWithFactors(
                    attacker=MultiJpeg(quality_factor=80),
                    attackername="Multi-JPEG",
                    factors=[1, 2, 3, 4, 5, 6],
                    factorsymbol=r"$t$"
                ),
                AttackerWithFactors(
                    attacker=Jpeg2000(),
                    attackername="JPEG2000Compression",
                    factors=[90, 80, 70, 60, 50, 40, 30, 20, 10],
                    factorsymbol=r"$c$"
                ),
                AttackerWithFactors(
                    attacker=MultiJpeg2000(quality_factor=80),
                    attackername="Multi-JPEG2000",
                    factors=[1, 2, 3, 4, 5, 6],
                    factorsymbol=r"$t$"
                ),
                AttackerWithFactors(
                    attacker=WebPCompression(),
                    attackername="WebPCompression",
                    factors=[90, 80, 70, 60, 50, 40, 30, 20, 10],
                    factorsymbol=r"$q$"
                ),
                # ===================================================================
                # Noise Attacks - Add various types of noise to images
                # Simulate real-world sensor noise and transmission errors
                # ===================================================================
                AttackerWithFactors(
                    attacker=SaltPepperNoise(),
                    attackername="Salt&PepperNoise",
                    factors=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
                    factorsymbol=r"$p$"
                ),
                AttackerWithFactors(
                    attacker=GaussianNoise(),
                    attackername="GaussianNoise",
                    factors=[0.01, 0.03, 0.05, 0.07, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9],
                    factorsymbol=r"$\sigma$"
                ),
                AttackerWithFactors(
                    attacker=PoissonNoise(),
                    attackername="PoissonNoise",
                    factors=[30., 25., 20., 15., 10.0, 5.0, 2.0, 1.0, 0.5, 0.3],
                    factorsymbol=r"$\alpha$"
                ),

                # ===================================================================
                # Blur Attacks - Apply various blur filters to images
                # Simulate camera motion, defocus, and image processing artifacts
                # ===================================================================
                AttackerWithFactors(
                    attacker=GaussianBlur(),
                    attackername="GaussianBlur",
                    factors=[0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],
                    factorsymbol=r"$\sigma$"
                ),
                AttackerWithFactors(
                    attacker=MedianFilter(),
                    attackername="MedianFilter",
                    factors=[3, 5, 7, 9, 11, 13, 15, 17, 21, 23],
                    factorsymbol=r"$k$"
                ),
                AttackerWithFactors(
                    attacker=MeanFilter(),
                    attackername="MeanFilter",
                    factors=[3, 5, 7, 9, 11, 13, 15, 17, 21, 23],
                    factorsymbol=r"$k$"
                ),

                # ===================================================================
                # Geometric Transformations - Spatial transformations of images
                # Simulate camera movements, cropping, and scaling artifacts
                # ===================================================================
                AttackerWithFactors(
                    attacker=Resize(),
                    attackername="Resize",
                    factors=[0.01, 0.03, 0.05, 0.07, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9],
                    factorsymbol=r"$s$"
                ),
                AttackerWithFactors(
                    attacker=Rotate(),
                    attackername="Rotation",
                    factors=[30, 60, 90, 120, 150, 180, 210, 240, 270],
                    factorsymbol=r"$\theta$"
                ),
                AttackerWithFactors(
                    attacker=FlipAttack(),
                    factors=['H', 'V'],
                    factorsymbol='$d$',
                    attackername='FlipAttack'
                ),
                AttackerWithFactors(
                    attacker=TranslationAttack(),
                    factors=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
                    factorsymbol='$r$',
                    attackername='TranslationAttack'
                ),
                AttackerWithFactors(
                    attacker=Crop(),
                    attackername="Crop",
                    factors=[0.01, 0.03, 0.05, 0.07, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9],
                    factorsymbol=r"$r$"
                ),
                AttackerWithFactors(
                    attacker=Crop(crop_mode='random'),
                    attackername="RandomCrop",
                    factors=[0.01, 0.03, 0.05, 0.07, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9],
                    factorsymbol=r"$r$"
                ),
                AttackerWithFactors(
                    attacker=Cropout(),
                    attackername="Cropout",
                    factors=[0.01, 0.03, 0.05, 0.07, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9],
                    factorsymbol=r"$r$"
                ),
                AttackerWithFactors(
                    attacker=Cropout(cropout_mode='random'),
                    attackername="RandomCropout",
                    factors=[0.01, 0.03, 0.05, 0.07, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9],
                    factorsymbol=r"$r$"
                ),
                AttackerWithFactors(
                    attacker=RegionZoom(),
                    attackername="RegionZoom",
                    factors=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
                    factorsymbol=r"$r$"
                ),
                AttackerWithFactors(
                    attacker=PixelDropout(),
                    attackername="PixelDropout",
                    factors=[0.01, 0.03, 0.05, 0.07, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9],
                    factorsymbol=r"$p$"
                ),
                AttackerWithFactors(
                    attacker=ShearAttack(),
                    attackername="ShearAttack",
                    factors=[5, 15, 25, 35, 45, 55, 65, 75, 85],
                    factorsymbol=r"$d$"
                ),
                # ===================================================================
                # Color Transformations - Modify color properties of images
                # Simulate display variations, lighting changes, and color effects
                # ===================================================================
                AttackerWithFactors(
                    attacker=ContrastReduction(),
                    attackername="ContrastReduction",
                    factors=[0.01, 0.03, 0.05, 0.07, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9],
                    factorsymbol=r"$\alpha$"
                ),
                AttackerWithFactors(
                    attacker=ContrastEnhancement(),
                    attackername="ContrastEnhancement",
                    factors=[1.1, 1.3, 1.5, 2.0, 3.0, 5.0, 7.0, 9.0, 10.0, 11.0],
                    factorsymbol=r"$\gamma$"
                ),
                AttackerWithFactors(
                    attacker=ColorQuantization(),
                    attackername="ColorQuantization",
                    factors=[4, 8, 12, 16, 20, 28, 36, 42, 50, 76],
                    factorsymbol=r"$q$"
                ),
                AttackerWithFactors(
                    attacker=ChromaticAberration(),
                    attackername="ChromaticAberration",
                    factors=[1, 3, 5, 7, 9, 13, 17, 21, 25, 30],
                    factorsymbol=r"$s$"
                ),
                AttackerWithFactors(
                    attacker=GammaCorrection(),
                    attackername="GammaCorrection",
                    factors=[1.5, 3, 6, 7, 9, 13, 21, 37, 69, 133],
                    factorsymbol=r"$\gamma$"
                ),
                AttackerWithFactors(
                    attacker=HueShiftAttack(),
                    attackername="HueShift",
                    factors=[1, 3, 7, 15, 28, 48, 77, 115, 145, 170],
                    factorsymbol=r"$\Delta h$"
                ),
                AttackerWithFactors(
                    attacker=DarkenAttack(),
                    attackername="Darken",
                    factors=[0.006, 0.018, 0.047, 0.119, 0.269, 0.5, 0.731, 0.881, 0.953, 0.982],
                    factorsymbol=r"$\beta$"
                ),
                AttackerWithFactors(
                    attacker=BrightenAttack(),
                    attackername="Brighten",
                    factors=[1.1, 1.3, 1.6, 2.0, 3.0, 7.0, 15.0, 31.0, 63.0, 95.0],
                    factorsymbol=r"$\beta$"
                ),
                AttackerWithFactors(
                    attacker=DesaturateAttack(),
                    attackername="Desaturate",
                    factors=[0.006, 0.018, 0.047, 0.119, 0.269, 0.5, 0.731, 0.881, 0.953, 0.982],
                    factorsymbol=r"$\sigma_{\text{d}}$"
                ),
                AttackerWithFactors(
                    attacker=OversaturateAttack(),
                    attackername="Oversaturate",
                    factors=[1.1, 1.3, 1.6, 2.0, 3.0, 7.0, 11.0, 15.0, 19.0, 23.0],
                    factorsymbol=r"$\sigma_{\text{o}}$"
                ),
                AttackerWithFactors(
                    attacker=UnsharpMasking(),
                    attackername="UnsharpMasking",
                    factors=[0.1, 0.3, 0.6, 1.05, 1.73, 2.74, 4.26, 6.53, 9.95, 15.08],
                    factorsymbol=r"$\lambda$"
                ),
            ]
            self.extend(default_attackers_list)

    def __repr__(self):
        """
        Return a string representation of the AttackersWithFactorsModel.

        Returns:
            str: A string showing the class name and the number of attackers.
        """
        return f"AttackersWithFactorsModel({len(self)} attackers)"


# Execute the test
if __name__ == "__main__":
    print(len(AttackersWithFactorsModel()))
