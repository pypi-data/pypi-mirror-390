# Copyright (c) 2025 Jiale Chen <chenoly@outlook.com>. All rights reserved.
# SPDX-License-Identifier: MIT
import torch
import numpy as np
from numpy import ndarray
from diffusers import StableDiffusionPipeline
from typing import List, Optional, Union, Callable
from watermarklab.utils.basemodel import BaseTestAttackModel
from diffusers.pipelines.stable_diffusion import StableDiffusionPipelineOutput


class ReSDPipeline(StableDiffusionPipeline):
    """
    A custom Stable Diffusion pipeline for image generation with support for head-start latents and dual prompts.
    Extends the base StableDiffusionPipeline from the diffusers library.
    """

    @torch.no_grad()
    def __call__(
            self,
            prompt: Union[str, List[str]],
            prompt1_steps: Optional[int] = None,
            prompt2: Optional[str] = None,
            head_start_latents: Optional[Union[torch.FloatTensor, list]] = None,
            head_start_step: Optional[int] = None,
            height: Optional[int] = None,
            width: Optional[int] = None,
            num_inference_steps: int = 50,
            guidance_scale: float = 7.5,
            negative_prompt: Optional[Union[str, List[str]]] = None,
            num_images_per_prompt: Optional[int] = 1,
            eta: float = 0.0,
            generator: Optional[torch.Generator] = None,
            latents: Optional[torch.FloatTensor] = None,
            output_type: Optional[str] = "pil",
            return_dict: bool = True,
            callback: Optional[Callable[[int, int, torch.FloatTensor], None]] = None,
            callback_steps: Optional[int] = 1,
    ):
        """
        Generates images using the Stable Diffusion model with optional head-start latents and dual prompts.

        Args:
            prompt (Union[str, List[str]]): The text prompt(s) to guide image generation.
            prompt1_steps (Optional[int]): Number of steps to use the first prompt before switching to prompt2.
            prompt2 (Optional[str]): Secondary prompt for later denoising steps.
            head_start_latents (Optional[Union[torch.FloatTensor, list]]): Pre-generated latents for head-start.
            head_start_step (Optional[int]): Step to start denoising from when using head-start latents.
            height (Optional[int]): Height of the generated image in pixels.
            width (Optional[int]): Width of the generated image in pixels.
            num_inference_steps (int): Number of denoising steps, defaults to 50.
            guidance_scale (float): Guidance scale for classifier-free guidance, defaults to 7.5.
            negative_prompt (Optional[Union[str, List[str]]]): Negative prompt(s) to avoid in generation.
            num_images_per_prompt (Optional[int]): Number of images to generate per prompt, defaults to 1.
            eta (float): DDIM eta parameter, defaults to 0.0.
            generator (Optional[torch.Generator]): Random number generator for reproducibility.
            latents (Optional[torch.FloatTensor]): Pre-generated noisy latents.
            output_type (Optional[str]): Output format ("pil" or "np.array"), defaults to "pil".
            return_dict (bool): Whether to return a StableDiffusionPipelineOutput object, defaults to True.
            callback (Optional[Callable]): Callback function called during inference.
            callback_steps (Optional[int]): Frequency of callback invocation, defaults to 1.

        Returns:
            StableDiffusionPipelineOutput or tuple: Generated images and NSFW flags if return_dict is True,
                                                  otherwise a tuple of (images, nsfw_content_detected).
        """
        height = height or self.unet.config.sample_size * self.vae_scale_factor
        width = width or self.unet.config.sample_size * self.vae_scale_factor
        self.check_inputs(prompt, height, width, callback_steps)
        batch_size = 1 if isinstance(prompt, str) else len(prompt)
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        text_embeddings = self._encode_prompt(
            prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt
        )
        if prompt2 is not None:
            text_embeddings2 = self._encode_prompt(
                prompt2, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt
            )
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps
        if head_start_latents is None:
            num_channels_latents = self.unet.in_channels
            latents = self.prepare_latents(
                batch_size * num_images_per_prompt,
                num_channels_latents,
                height,
                width,
                text_embeddings.dtype,
                device,
                generator,
                latents,
            )
        else:
            if type(head_start_latents) == list:
                latents = head_start_latents[-1]
                assert len(head_start_latents) == self.scheduler.config.solver_order
            else:
                latents = head_start_latents
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        num_warmup_steps = len(timesteps) - num_inference_steps * self.scheduler.order
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                if not head_start_step or i >= head_start_step:
                    latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
                    latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                    if prompt1_steps is None or i < prompt1_steps:
                        noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=text_embeddings).sample
                    else:
                        noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=text_embeddings2).sample
                    if do_classifier_free_guidance:
                        noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                        noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                        latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs).prev_sample
                if (i + 1) > num_warmup_steps and (i + 1) % self.scheduler.order == 0:
                    progress_bar.update()
                    if callback is not None and i % callback_steps == 0:
                        callback(i, t, latents)
        image = self.decode_latents(latents)
        has_nsfw_concept = False
        if output_type == "pil":
            image = self.numpy_to_pil(image)
        if not return_dict:
            return image, has_nsfw_concept
        return StableDiffusionPipelineOutput(images=image, nsfw_content_detected=has_nsfw_concept)


class DiffuseAttack(BaseTestAttackModel):
    """
    A single-step diffusion-based attack using ReSDPipeline.
    Adds noise at a specified timestep and regenerates the image via a head-start mechanism to disrupt embedded watermarks.

    This attack leverages classifier-free guidance to regenerate the image with high fidelity while preserving semantic content.
    It is particularly effective against watermarking schemes that rely on high-frequency signals.

    The process:
        1. Encodes the input image into latent space.
        2. Adds diffusion noise at a specified timestep.
        3. Uses "head-start decoding" to regenerate the image from an intermediate step, balancing fidelity and distortion.
    Note:
        - Input: List of uint8 images, each [H, W] (grayscale) or [H, W, 3] (RGB), range [0, 255]
        - Output: List of regenerated images, same shape and dtype
        - For grayscale images, the single channel is replicated to three channels for processing,
          and the output is converted back to grayscale by taking one channel
        - The model uses Stable Diffusion 2.1 base (fp16) and requires CUDA
        - 'factor' controls the noise timestep (1-200): higher = more noise
    """
    _global_model_cache = {}

    def __init__(self, model_id: str = "stabilityai/stable-diffusion-2-1-base", noisename: str = "DiffuseAttack"):
        """
        Initializes the diffusion attack model.

        Args:
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=False)
        self.model_id = model_id
        self.pipe = self._get_pipe()

    def _get_pipe(self):
        """
        Loads and caches the ReSDPipeline (a variant of Stable Diffusion 2.1) for efficient reuse.

        Returns:
            ReSDPipeline: The diffusion pipeline, loaded in fp16 and moved to GPU.

        Raises:
            RuntimeError: If CUDA is not available, as this attack is GPU-only.
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        cache_key = (self.device, "sd2.1-diffuse-attack")
        if cache_key in DiffuseAttack._global_model_cache:
            return DiffuseAttack._global_model_cache[cache_key]

        if not torch.cuda.is_available():
            raise RuntimeError("DiffuseAttack requires CUDA. CPU is not supported.")

        pipe = ReSDPipeline.from_pretrained(
            self.model_id,
            torch_dtype=torch.float16,
            local_files_only=True
        )
        pipe.to(self.device)
        pipe.set_progress_bar_config(disable=True)
        DiffuseAttack._global_model_cache[cache_key] = pipe
        return pipe

    @torch.inference_mode()
    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: int = 60) -> List[ndarray]:
        """
        Applies a single-step diffusion regeneration attack to a batch of images (grayscale or RGB).

        The attack uses a "head-start" decoding strategy:
            - Noise is added at an early diffusion timestep (controlled by 'factor').
            - The decoder starts from a later step (head_start_step), allowing the model
              to regenerate content while preserving some original structure.

        For grayscale images:
            - The single channel is replicated to three channels to create a pseudo-RGB image.
            - After processing, one channel is taken to restore the grayscale shape.

        This method is highly efficient due to batched processing and minimizes CPU-GPU transfer.

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each [H, W] (grayscale) or [H, W, 3] (RGB),
                                       dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored, for interface compatibility).
            factor (int): Diffusion timestep for noise injection, range [1, 200]. Higher values = more noise.

        Returns:
            List[ndarray]: Batch of regenerated images, each with the same shape and dtype as input.
        """
        if not stego_imgs:
            return []

        # Determine if images are grayscale ([H, W]) or RGB ([H, W, 3])
        is_grayscale = len(stego_imgs[0].shape) == 2

        if is_grayscale:
            batch_np = np.stack([np.repeat(img[..., np.newaxis], 3, axis=-1) for img in stego_imgs], axis=0).astype(
                np.float32)
        else:
            batch_np = np.stack(stego_imgs, axis=0).astype(np.float32)

        pipe = self.pipe
        device = self.device
        generator = torch.Generator(device=device).manual_seed(1024)

        noise_step = int(np.clip(factor, 1, 200))
        timestep = torch.tensor([noise_step], device=device)

        batch_np = (batch_np / 127.5) - 1.0
        batch_tensor = torch.from_numpy(batch_np).permute(0, 3, 1, 2).contiguous().half().to(device)

        latents = pipe.vae.encode(batch_tensor).latent_dist.sample(generator)
        latents = latents * pipe.vae.config.scaling_factor

        noise = torch.randn_like(latents)
        noisy_latents = pipe.scheduler.add_noise(latents, noise, timestep).type(torch.float16)

        head_start_step = max(50 - max(noise_step // 20, 1), 1)

        with torch.autocast(device_type="cuda", dtype=torch.float16):
            output_images = pipe(
                prompt=["" for _ in range(len(stego_imgs))],
                head_start_latents=noisy_latents,
                head_start_step=head_start_step,
                guidance_scale=7.5,
                generator=generator,
            ).images

        noised_batch = [np.array(img) for img in output_images]
        if is_grayscale:
            noised_batch = [img[..., 0] for img in noised_batch]
        return noised_batch


class MultiDiffuseAttack(BaseTestAttackModel):
    """
    A multi-step diffusion-based attack that applies DiffuseAttack repeatedly for multiple rounds.
    Each round injects noise and regenerates the image using the same fixed diffusion timestep.

    This attack amplifies the watermark-removal effect by performing sequential regeneration.
    The cumulative distortion can effectively erase subtle, high-frequency watermark signals
    that survive a single diffusion step.

    The 'factor' parameter controls the number of attack rounds (iterations), enabling a
    continuous control over attack strength.

    Note:
        - Input: List of uint8 RGB images [H, W, 3], range [0, 255]
        - Output: List of regenerated images, same shape and dtype
        - Each round uses the same fixed noise timestep (self.noise_step)
        - 'factor' specifies the number of iterations (attack strength)
    """

    def __init__(self, model_id: str = "stabilityai/stable-diffusion-2-1-base", noise_step: int = 30, noisename: str = "MultiDiffuseAttack"):
        """
        Initializes the multi-step diffusion attack.

        Args:
            noise_step (int): Fixed diffusion timestep for noise injection in each round, range [1, 200].
            noisename (str): Name identifier for logging and reporting.
        """
        super().__init__(noisename=noisename, factor_inversely_related=False)
        self.noise_step = int(np.clip(noise_step, 1, 200))
        self.diffuse = DiffuseAttack(noisename=f"{noisename}_inner", model_id=model_id)

    @torch.inference_mode()
    def attack(self, stego_imgs: List[ndarray], cover_img: List[ndarray] = None, factor: int = 1) -> List[ndarray]:
        """
        Applies multiple rounds of diffusion regeneration attack to a batch of stego images.

        The attack pipeline is:
            For round in range(factor):
                x = DiffuseAttack(x, factor=self.noise_step)
        Each round adds noise and regenerates the image, progressively distorting watermark signals.

        Args:
            stego_imgs (List[ndarray]): Batch of watermarked images, each of shape [H, W, 3], dtype=uint8, range [0,255].
            cover_img (List[ndarray], optional): Cover images (ignored, for interface compatibility).
            factor (int): Number of attack rounds (>=1). More rounds = stronger attack.

        Returns:
            List[ndarray]: Final images after `factor` rounds of diffusion attack, same shape and dtype as inputs.
        """
        if not stego_imgs:
            return []

        x = stego_imgs
        num_rounds = int(factor)

        for step in range(num_rounds):
            x = self.diffuse.attack(x, cover_img=None, factor=self.noise_step)
        return x
