from pathlib import Path

from PIL import Image, ImageDraw

import numpy as np
from numpy.typing import NDArray


class Photoshop:

    tile_size: int

    def __init__(self, tile_size: int = 32):
        self.tile_size = tile_size

    @staticmethod
    def load(path: str) -> Image.Image:
        """
        Load images into memory and resize them so they are compatible with each other.
        """
        path = Path(path)
        assert path.exists()
        image = Image.open(path)
        assert image is not None
        return image

    def image_to_bytes(self, image: Image.Image) -> NDArray:
        """
        Converts the input images to bytes using a constant tile size. The image is not padded and therefore the
        leftover bytes at the image end are simply dropped.
        """

        n_cols = image.width // self.tile_size
        n_rows = image.height // self.tile_size

        tiles: list[list] = []
        for i in range(n_rows):
            row_tiles = []
            for j in range(n_cols):
                start_i = i * self.tile_size
                start_j = j * self.tile_size
                tile = image.crop((start_j, start_i, start_j+self.tile_size, start_i+self.tile_size))
                row_tiles.append(np.array(tile).astype(np.int16))
            tiles.append(row_tiles)

        return np.array(tiles)

    @staticmethod
    def compare_and_resize(image1: Image.Image, image2: Image.Image) -> tuple[Image.Image, Image.Image]:
        """
        Compares shapes of the input images and resizes them to a compatible size.
        """

        if image1.size == image2.size:
            return image1, image2

        min_width = min(image1.width, image2.width)
        min_height = min(image1.height, image2.height)

        image1 = image1.resize((min_width, min_height))
        image2 = image2.resize((min_width, min_height))

        return image1, image2

    def create_mask_over_tiles(self, image: Image.Image, tiles_idx: list[tuple[int, int]]) -> Image.Image:
        """
        Create a mask over the input image over the input tiles.
        """
        image_copy = image.copy()
        draw = ImageDraw.Draw(image_copy, mode="RGBA")
        for i, j in tiles_idx:
            start_i = i * self.tile_size
            start_j = j * self.tile_size
            draw.rectangle(
                xy=[start_j, start_i, start_j+self.tile_size, start_i+self.tile_size],
                fill=(255, 0, 0, 120),
            )
        return image_copy
