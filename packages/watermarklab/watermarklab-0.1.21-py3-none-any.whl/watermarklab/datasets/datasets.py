# Copyright (c) 2025 Jiale Chen <chenoly@outlook.com>. All rights reserved.
# SPDX-License-Identifier: MIT
import os
import glob
import json
import random
import hashlib
import numpy as np
from typing import Tuple, List
from PIL import Image, ImageOps
from watermarklab.utils.basemodel import BaseDataset

# --------------------------------------------------------------------
# Configuration: Hugging Face Repository
# --------------------------------------------------------------------
_REPO_ID = "chenoly/watermarklab"

# Dataset file mappings and expected SHA256
_DATASET_CONFIG = {
    "usc_sipi": {
        "filename": "datasets/USC-SIPI.zip",
        "sha256": "7e1b679ceb71f810c8019a58df3e7cd7a38e61f1d43ee0275ea2c09102ec8b70",
        "folder": "USC-SIPI",
    },
    "kodak24": {
        "filename": "datasets/KODAK24.zip",
        "sha256": "a0df8e6e2fd3b268042adf2c04ca2b16badc721efd86776cb24cc816819a3a35",
        "folder": "KODAK24",
    },
    "coco_prompts": {
        "filename": "datasets/MS-COCO-PROMPTS.zip",
        "sha256": "f7791519211abc8d1c302a0b3c2bc327657b5676c8f09f9577f40f2234f9b354",
        "folder": "MS-COCO-PROMPTS",
    },
    "mscoco2017val": {
        "filename": "datasets/MSCOCO2017VAL.zip",
        "sha256": "4f7e2ccb2866ec5041993c9cf2a952bbed69647b115d0f74da7ce8f4bef82f05",
        "folder": "MS-COCO-2017-VAL",
    }
}

# Import logger
from watermarklab.utils.logger import logger


def _download_and_extract_hf(repo_id: str, filename: str, sha256: str, target_folder: str,
                             local_files_only: bool = False) -> str:
    """
    Download a dataset ZIP from Hugging Face and extract it if not already present.
    Uses hf_hub_download for caching and integrity.

    Args:
        repo_id (str): Hugging Face repo ID.
        filename (str): Path within repo.
        sha256 (str): Expected SHA256 hash.
        target_folder (str): Local folder name to extract into.

    Returns:
        str: Path to extracted folder.
    """
    try:
        from huggingface_hub import hf_hub_download
        import sys
        import os
        from zipfile import ZipFile

        RED = "\033[91m"
        GREEN = "\033[92m"
        BLUE = "\033[94m"
        RESET = "\033[0m"

        basename = os.path.basename(filename)

        # Start progress on one line
        sys.stdout.write(f"[{GREEN}WatermarkLab{RESET} INFO] ")
        sys.stdout.flush()

        # Step 1: Download
        sys.stdout.write(f"Downloading {basename}... ")
        sys.stdout.flush()
        try:
            archive_path = hf_hub_download(repo_id=repo_id, filename=filename, use_auth_token=True,
                                           local_files_only=local_files_only)
            sys.stdout.write(f"{GREEN}✓{RESET} | ")
        except Exception as e:
            sys.stdout.write(f"{RED}✗{RESET}\n")
            logger.error(f"Failed to download {basename}: {e}")
            raise RuntimeError(f"Failed to download {basename}: {e}")

        # Step 2: Verify SHA256
        sys.stdout.write("Verifying SHA256... ")
        sys.stdout.flush()
        if not _check_sha256(archive_path, sha256):
            sys.stdout.write(f"{RED}✗{RESET}\n")
            logger.error(f"SHA256 mismatch for {filename}")
            raise ValueError(f"SHA256 mismatch for {filename}")
        sys.stdout.write(f"{BLUE}✓{RESET} | ")

        # Step 3: Extract
        extract_path = os.path.join(os.path.dirname(archive_path), target_folder)
        if os.path.exists(extract_path) and os.listdir(extract_path):
            sys.stdout.write(f"Using cached {target_folder}/ {GREEN}✓{RESET} | ")
        else:
            sys.stdout.write("Extracting... ")
            sys.stdout.flush()
            os.makedirs(extract_path, exist_ok=True)
            try:
                with ZipFile(archive_path, 'r') as zipf:
                    zipf.extractall(extract_path)
                sys.stdout.write(f"{GREEN}✓{RESET} | ")
            except Exception as e:
                sys.stdout.write(f"{RED}✗{RESET}\n")
                logger.error(f"Failed to extract {basename}: {e}")
                raise RuntimeError(f"Failed to extract {basename}: {e}")

        # Final success
        sys.stdout.write(f"{GREEN}Done.{RESET}\n")
        return extract_path

    except ImportError:
        sys.stdout.write(f"\n[ERROR] Missing 'huggingface_hub'. Install with: pip install huggingface_hub\n")
        logger.error("Missing 'huggingface_hub'. Install with: pip install huggingface_hub")
        raise ImportError("huggingface_hub is required to download datasets.")
    except Exception as e:
        # Ensure error breaks line for clarity
        if not str(e).startswith("\n"):
            sys.stdout.write("\n")
        raise e


def _check_sha256(file_path: str, expected_hash: str) -> bool:
    """Verify SHA256 checksum of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest().lower() == expected_hash.lower()


class USC_SIPI(BaseDataset):
    """
    USC-SIPI dataset loader.

    Loads images from the USC-SIPI image database (typically the 'misc' subset), supporting both RGB and grayscale modes.
    Automatically downloads and extracts the dataset from Hugging Face Hub if not present locally.
    Only valid TIFF images that can be successfully opened and converted to the target color mode are retained.
    """

    def __init__(self, im_size: int, bit_len: int, iter_num: int = 1,
                 dataset_name: str = "USC_SIPI",
                 random_seed: int = 99,
                 local_files_only: bool = False,
                 color_mode: str = "RGB"):
        """
        Initializes the USC-SIPI dataset loader.

        Args:
            im_size (int): Target image size (height and width) after resizing. Images are center-cropped and resized to (im_size, im_size).
            bit_len (int): Length of the randomly generated binary secret sequence for each image.
            iter_num (int, optional): Number of iterations over the dataset during evaluation. Default is 1.
            dataset_name (str, optional): Human-readable name of the dataset. Default is "USC_SIPI".
            random_seed (int, optional): Seed for random number generators to ensure reproducible shuffling and secret generation. Default is 99.
            local_files_only (bool, optional): If True, skips downloading and only uses files already present locally. Default is False.
            color_mode (str, optional): Desired color mode for loaded images. Must be either "RGB" (3-channel) or "GRAY" (1-channel). Default is "RGB".
        """
        super().__init__(im_size, bit_len, iter_num, dataset_name)
        self.im_size = im_size
        self.bit_length = bit_len
        self.random_seed = random_seed
        self.color_mode = color_mode
        assert self.color_mode in ["RGB", "GRAY"], "color_mode must be 'RGB' or 'GRAY'"

        config = _DATASET_CONFIG["usc_sipi"]
        self.root_path = _download_and_extract_hf(
            _REPO_ID, config["filename"], config["sha256"], config["folder"], local_files_only
        )
        self.covers = []
        self.load_paths()

    def load_paths(self):
        """
        Recursively scans the dataset root for TIFF files, filters them by color mode compatibility,
        and builds a list of valid image paths. Only images that can be opened and converted to the
        target color mode are included. The list is shuffled using the configured random seed.
        """
        pattern = os.path.join(self.root_path, "*.tiff")
        self.covers = sorted(glob.glob(pattern))
        random.seed(self.random_seed)
        random.shuffle(self.covers)
        logger.info(f"[USC_SIPI] Loaded {len(self.covers)} {self.color_mode} images.")

    def load_data(self, index: int) -> Tuple[np.ndarray, List[int]]:
        """
        Loads and preprocesses a single image from the USC-SIPI dataset.

        The image is opened, converted to the specified color mode ("RGB" or "L"), resized to (im_size, im_size)
        using center crop via ImageOps.fit, and returned as a float32 NumPy array with pixel values in [0.0, 255.0].
        A deterministic random secret bit sequence is generated using the sample index as seed.

        Args:
            index (int): Index of the image in the shuffled covers list.

        Returns:
            Tuple[np.ndarray, List[int]]: A tuple containing:
                - cover: float32 array of shape (H, W, 3) for RGB or (H, W) for GRAY.
                - secret: list of `bit_length` bits (0/1).
        """
        if index >= len(self.covers):
            raise IndexError(f"Index {index} out of range.")
        img_path = self.covers[index]
        img = Image.open(img_path)
        if self.color_mode == "RGB":
            img = img.convert("RGB")
        else:
            img = img.convert("L")
        img = ImageOps.fit(img, (self.im_size, self.im_size))
        cover = np.float32(img)
        random.seed(index)
        secret = [random.randint(0, 1) for _ in range(self.bit_length)]
        return cover, secret

    def get_num_covers(self) -> int:
        """
        Returns the number of valid cover images loaded from the USC-SIPI dataset.

        Returns:
            int: Number of usable images.
        """
        return len(self.covers)


class KODAK24(BaseDataset):
    """
    KODAK24 dataset loader.

    Loads the standard 24 high-quality KODAK images (originally in BMP format) from Hugging Face Hub.
    Supports both RGB and grayscale output modes. The dataset is small and commonly used for image quality evaluation.
    """

    def __init__(self, im_size: int, bit_len: int, iter_num: int = 1,
                 dataset_name: str = "KODAK24",
                 random_seed: int = 99,
                 local_files_only: bool = False,
                 color_mode: str = "RGB"):
        """
        Initializes the KODAK24 dataset loader.

        Args:
            im_size (int): Target image size (height and width) after resizing. Images are center-cropped and resized to (im_size, im_size).
            bit_len (int): Length of the randomly generated binary secret sequence for each image.
            iter_num (int, optional): Number of iterations over the dataset during evaluation. Default is 1.
            dataset_name (str, optional): Human-readable name of the dataset. Default is "KODAK24".
            random_seed (int, optional): Seed for random number generators to ensure reproducible shuffling and secret generation. Default is 99.
            local_files_only (bool, optional): If True, skips downloading and only uses files already present locally. Default is False.
            color_mode (str, optional): Desired color mode for loaded images. Must be either "RGB" (3-channel) or "GRAY" (1-channel). Default is "RGB".
        """
        super().__init__(im_size, bit_len, iter_num, dataset_name)
        self.im_size = im_size
        self.bit_length = bit_len
        self.random_seed = random_seed
        self.color_mode = color_mode
        assert self.color_mode in ["RGB", "GRAY"], "color_mode must be 'RGB' or 'GRAY'"

        config = _DATASET_CONFIG["kodak24"]
        self.root_path = _download_and_extract_hf(
            _REPO_ID, config["filename"], config["sha256"], config["folder"], local_files_only
        )
        self.covers = []
        self.load_paths()

    def load_paths(self):
        """
        Loads all BMP files from the KODAK24 root directory.

        The original KODAK24 dataset contains exactly 24 images. A warning is logged if the count differs.
        The list is shuffled using the configured random seed for reproducibility.
        """
        pattern = os.path.join(self.root_path, "*.BMP")
        self.covers = sorted(glob.glob(pattern))
        if len(self.covers) != 24:
            logger.warning(f"[KODAK24] Expected 24 images, found {len(self.covers)}")
        random.seed(self.random_seed)
        random.shuffle(self.covers)
        logger.info(f"[KODAK24] Loaded {len(self.covers)} {self.color_mode} images.")

    def load_data(self, index: int) -> Tuple[np.ndarray, List[int]]:
        """
        Loads a single KODAK24 image, converts it to the specified color mode, resizes it to (im_size, im_size),
        and generates a deterministic random secret.

        Args:
            index (int): Index of the image in the shuffled covers list.

        Returns:
            Tuple[np.ndarray, List[int]]: A tuple containing:
                - cover: float32 array of shape (H, W, 3) for RGB or (H, W) for GRAY.
                - secret: list of `bit_length` bits (0/1).
        """
        if index >= len(self.covers):
            raise IndexError(f"Index {index} out of range.")
        img_path = self.covers[index]
        img = Image.open(img_path)
        if self.color_mode == "RGB":
            img = img.convert("RGB")
        else:
            img = img.convert("L")
        img = ImageOps.fit(img, (self.im_size, self.im_size))
        cover = np.float32(img)
        random.seed(index)
        secret = [random.randint(0, 1) for _ in range(self.bit_length)]
        return cover, secret

    def get_num_covers(self) -> int:
        """
        Returns the number of KODAK24 images loaded (typically 24).

        Returns:
            int: Number of images.
        """
        return len(self.covers)


class KODAK24_AND_USC_SIPI(BaseDataset):
    """
    A combined dataset loader that aggregates images from both the KODAK24 and USC-SIPI image databases.

    This class loads RGB or grayscale images from the two datasets, filters out non-RGB or corrupted files,
    resizes them to a common square dimension, and generates random binary secrets for watermarking tasks.
    The combined image list is shuffled using a fixed random seed to ensure reproducibility.
    """

    def __init__(self, im_size: int, bit_len: int, iter_num: int = 1,
                 dataset_name: str = "KODAK24_AND_USC_SIPI",
                 random_seed: int = 99,
                 local_files_only: bool = False,
                 color_mode: str = "RGB"):
        """
        Initializes the combined KODAK24 + USC-SIPI dataset loader.

        Downloads (if needed) and loads images from both datasets, then merges their file lists.
        Only images that can be successfully opened and match the desired color mode are retained.

        Args:
            im_size (int): Target image size (height and width) after resizing. Images are center-cropped and resized to (im_size, im_size).
            bit_len (int): Length of the randomly generated binary secret sequence for each image.
            iter_num (int, optional): Number of iterations over the dataset during evaluation. Default is 1.
            dataset_name (str, optional): Human-readable name of the dataset. Default is "KODAK24_AND_USC_SIPI".
            random_seed (int, optional): Seed for random number generators to ensure reproducible shuffling and secret generation. Default is 99.
            local_files_only (bool, optional): If True, skips downloading and only uses files already present locally. Default is False.
            color_mode (str, optional): Desired color mode for loaded images. Must be either "RGB" (3-channel) or "GRAY" (1-channel). Default is "RGB".
        """
        super().__init__(im_size, bit_len, iter_num, dataset_name)
        self.im_size = im_size
        self.bit_length = bit_len
        self.random_seed = random_seed
        self.color_mode = color_mode
        assert self.color_mode in ["RGB", "GRAY"], "color_mode must be 'RGB' or 'GRAY'"

        # Initialize sub-datasets to get their root paths
        usc_dataset = USC_SIPI(im_size=im_size, bit_len=bit_len, iter_num=iter_num,
                               local_files_only=local_files_only)
        kodak_dataset = KODAK24(im_size=im_size, bit_len=bit_len, iter_num=iter_num,
                                local_files_only=local_files_only)

        self.covers = usc_dataset.covers + kodak_dataset.covers
        random.seed(self.random_seed)
        random.shuffle(self.covers)
        logger.info(f"[KODAK24_AND_USC_SIPI] Loaded {len(self.covers)} {self.color_mode} images.")


    def load_data(self, index: int) -> Tuple[np.ndarray, List[int]]:
        """
        Loads a single image by index, converts it to the specified color mode, resizes it,
        and generates a deterministic random secret bit sequence.

        The image is opened, converted to "RGB" or "L" (grayscale) based on `color_mode`,
        then resized to `(im_size, im_size)` using `ImageOps.fit` (preserving aspect ratio via center crop).
        Pixel values are returned as a float32 NumPy array in the range [0.0, 255.0].
        The secret is a list of `bit_length` bits (0/1), seeded by the sample index for reproducibility.

        Args:
            index (int): Index of the image in the shuffled `self.covers` list.

        Returns:
            Tuple[np.ndarray, List[int]]: A tuple containing:
                - cover: A float32 NumPy array of shape (H, W, 3) for RGB or (H, W) for GRAY.
                - secret: A list of `bit_length` integers (0 or 1).
        """
        if index >= len(self.covers):
            raise IndexError(f"Index {index} out of range.")
        img_path = self.covers[index]
        img = Image.open(img_path)
        if self.color_mode == "RGB":
            img = img.convert("RGB")
        else:
            img = img.convert("L")
        img = ImageOps.fit(img, (self.im_size, self.im_size))
        cover = np.float32(img)
        random.seed(index)
        secret = [random.randint(0, 1) for _ in range(self.bit_length)]
        return cover, secret

    def get_num_covers(self) -> int:
        """
        Returns the total number of valid cover images loaded from both KODAK24 and USC-SIPI datasets.

        This count reflects only the images that passed format and color mode compatibility checks.

        Returns:
            int: Number of usable cover images.
        """
        return len(self.covers)


class MS_COCO_2017_VAL_IMAGES(BaseDataset):
    """
    A dataset class that loads images from the MS-COCO 2017 validation set.

    This class automatically downloads and extracts the 'val2017' subset from the Hugging Face Hub
    if not already present locally. It supports loading images in either RGB or grayscale mode,
    resizing them to a specified square dimension, and generating random binary secrets of fixed length
    for watermarking or steganography tasks. The image list is shuffled using a fixed random seed
    to ensure reproducibility. Users can optionally limit the number of images loaded via `image_num`.
    """

    def __init__(self, im_size: int, bit_len: int, iter_num: int = 1, image_num: int = -1,
                 color_mode: str = "RGB", dataset_name: str = "MS-COCO 2017 VAL IMAGES",
                 random_seed: int = 99, local_files_only: bool = False):
        """
        Initializes the MS-COCO 2017 validation dataset loader.

        Downloads and extracts the dataset from Hugging Face if not available locally (unless
        `local_files_only=True`). Sets up internal parameters including image size, secret bit length,
        color mode, and random seed for deterministic behavior.

        Args:
            im_size (int): Target image size (height and width) after resizing. Images are square-cropped and resized to (im_size, im_size).
            bit_len (int): Length of the randomly generated binary secret sequence for each image.
            iter_num (int, optional): Number of iterations over the dataset during evaluation. Default is 1.
            image_num (int, optional): Maximum number of images to load from the validation set.
                If -1 or greater than available images, all images are used. Default is -1.
            color_mode (str, optional): Color mode for loaded images. Must be either "RGB" (3-channel) or "GRAY" (1-channel). Default is "RGB".
            dataset_name (str, optional): Human-readable name of the dataset for logging and identification. Default is "MS-COCO 2017 VAL IMAGES".
            random_seed (int, optional): Seed for random number generators to ensure reproducible shuffling and secret generation. Default is 99.
            local_files_only (bool, optional): If True, skips downloading and only uses files already present locally.
                Useful in offline environments. Default is False.
        """
        super().__init__(im_size, bit_len, iter_num, dataset_name)
        self.im_size = im_size
        self.image_num = image_num
        self.bit_len = bit_len
        self.random_seed = random_seed
        self.color_mode = color_mode
        assert self.color_mode in ["RGB", "GRAY"]

        config = _DATASET_CONFIG["mscoco2017val"]
        self.root_path = _download_and_extract_hf(
            _REPO_ID,
            config["filename"],
            config["sha256"],
            config["folder"],
            local_files_only
        )
        self.covers = []
        self.load_paths()

    def load_paths(self):
        """
        Scans the 'val2017' directory for valid JPEG images, collects their file paths,
        shuffles them using the configured random seed, and trims the list according to `image_num`.

        The method searches for files matching common JPEG extensions (e.g., .jpg, .jpeg in various cases).
        If no images are found or the 'val2017' folder is missing, a RuntimeError is raised.
        The resulting list is stored in `self.covers` for later access by `load_data`.
        """
        val_folder = os.path.join(self.root_path, "val2017")
        if not os.path.exists(val_folder):
            raise RuntimeError(f"Expected 'val2017' folder not found: {val_folder}")

        patterns = ['*.jpg', '*.jpeg', '*.JPG', '*.JPEG']
        covers = []
        for pattern in patterns:
            for img_path in glob.glob(os.path.join(val_folder, pattern), recursive=False):
                covers.append(img_path)

        if len(covers) == 0:
            raise RuntimeError(f"No valid images found in {val_folder}")

        random.seed(self.random_seed)
        random.shuffle(covers)

        if 0 < self.image_num <= len(covers):
            self.covers = covers[:self.image_num]
        else:
            self.covers = covers

        logger.info(f"[MS_COCO_2017_VAL] Loaded {len(self.covers)} images from 'val2017'.")

    def load_data(self, index: int) -> Tuple[np.ndarray, List[int]]:
        """
        Loads and preprocesses a single image and generates a corresponding random secret bit sequence.

        The image is opened using PIL, converted to the specified color mode ('RGB' or 'L' for grayscale),
        then center-cropped and resized to `(im_size, im_size)` using `ImageOps.fit` to preserve aspect ratio.
        The output image is converted to a float32 NumPy array with pixel values in [0.0, 255.0].
        If loading fails (e.g., corrupted file), a random float32 image of the correct shape is used as fallback.
        A secret bit sequence of length `bit_len` is generated using `random.randint(0, 1)`, with the random
        seed set to the sample `index` to ensure deterministic secret generation across runs.

        Args:
            index (int): Index of the image in the shuffled `self.covers` list.

        Returns:
            Tuple[np.ndarray, List[int]]: A tuple containing:
                - cover: A float32 NumPy array of shape (H, W, C) or (H, W) depending on `color_mode`.
                - secret: A list of `bit_len` integers (0 or 1) representing the random binary secret.
        """
        if index >= len(self.covers):
            raise IndexError(f"Index {index} out of range.")
        img_path = self.covers[index]
        if self.color_mode == "RGB":
            img = Image.open(img_path).convert("RGB")
        else:
            img = Image.open(img_path).convert("L")
        img = ImageOps.fit(img, (self.im_size, self.im_size))
        cover = np.float32(img)
        random.seed(index)
        secret = [random.randint(0, 1) for _ in range(self.bit_len)]
        return cover, secret

    def get_num_covers(self) -> int:
        """
        Returns the total number of cover images available in the dataset after filtering and sampling.

        This number reflects the actual count of images that will be used during evaluation,
        which may be less than the full validation set if `image_num` was set to a positive integer.

        Returns:
            int: Number of cover images loaded and ready for use.
        """
        return len(self.covers)


class MS_COCO_2017_VAL_PROMPTS(BaseDataset):
    """
    Loads text prompts from MS-COCO val2017 captions.
    Each image has 5 captions; this class samples exactly ONE prompt per image,
    selected randomly but deterministically based on the seed.

    The dataset zip contains 'captions_val2017.json'.
    By default, loads all images (5k). Can optionally load a fixed subset.
    """

    def __init__(self, bit_len: int, iter_num: int = 1, prompts_len: int = -1,
                 dataset_name: str = "MS-COCO 2017 VAL PROMPT", random_seed: int = 99, local_files_only: bool = False):
        """
        Initialize the MS_COCO_VAL_PROMPTS dataset.

        Args:
            bit_len (int): Length of watermark bits.
            iter_num (int): Number of iterations.
            prompts_len (int, optional): Number of image-prompt pairs to use.
                If None or >=5000, loads all. Otherwise, selects a fixed random subset.
            dataset_name (str): Name of the dataset.
            seed (int): Seed for deterministic behavior (prompt selection and secret generation).
        """
        super().__init__(512, bit_len, iter_num, dataset_name)
        self.random_seed = random_seed
        self.bit_length = bit_len
        self.prompts_len = prompts_len
        self.prompts = []

        # Download and extract the prompts zip
        config = _DATASET_CONFIG["coco_prompts"]
        extracted_dir = _download_and_extract_hf(_REPO_ID, config["filename"], config["sha256"], config["folder"], local_files_only)

        # Locate the JSON file
        json_path = os.path.join(extracted_dir, "captions_val2017.json")
        if not os.path.exists(json_path):
            logger.error(f"Expected captions file not found: {json_path}")
            raise RuntimeError(f"Expected captions file not found: {json_path}")

        self._load_prompts_from_json(json_path)

    def _load_prompts_from_json(self, json_path: str):
        """
        Load one prompt per image from the COCO annotations JSON file.
        Uses deterministic random sampling based on self.seed.

        Args:
            json_path (str): Path to captions_val2017.json.
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Group captions by image_id
        captions_per_image = {}
        for ann in data['annotations']:
            img_id = ann['image_id']
            if img_id not in captions_per_image:
                captions_per_image[img_id] = []
            captions_per_image[img_id].append(ann['caption'].strip())

        # Use deterministic RNG
        rng = random.Random(self.random_seed)

        # Sample one prompt per image
        all_prompts = []
        image_ids = sorted(captions_per_image.keys())
        for img_id in image_ids:
            captions = captions_per_image[img_id]
            selected_caption = rng.choice(captions)
            all_prompts.append(selected_caption)

        # Shuffle image order if subset is used
        rng = random.Random(self.random_seed)
        if self.prompts_len <= 0 or self.prompts_len >= len(all_prompts):
            self.prompts = all_prompts
            logger.info(
                f"[MS_COCO 2017 VAL CAPTIONS] Loaded {len(self.prompts)} prompts (1 per image) from 'captions_val2017.json'.")
        else:
            # Select a fixed random subset of image-prompt pairs
            self.prompts = rng.sample(all_prompts, self.prompts_len)
            logger.info(
                f"[MS_COCO 2017 VAL CAPTIONS] Loaded {len(self.prompts)} / {len(all_prompts)} prompts (1 per image, deterministic subset).")

    def load_data(self, index: int) -> Tuple[str, List[int]]:
        """
        Return a prompt and a random secret.

        Args:
            index (int): Index of the prompt.

        Returns:
            Tuple[str, List[int]]: Prompt and binary secret.
        """
        if index < 0 or index >= len(self.prompts):
            raise IndexError(f"Prompt index {index} out of range.")
        prompt = self.prompts[index]
        random.seed(self.random_seed + 1000 + index)
        secret = [random.randint(0, 1) for _ in range(self.bit_length)]
        return prompt, secret

    def get_num_covers(self) -> int:
        """
        Return the number of available prompts.

        Returns:
            int: Number of prompts.
        """
        return len(self.prompts)
