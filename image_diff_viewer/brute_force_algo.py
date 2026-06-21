import numpy as np
from numpy.typing import NDArray

import time

from image_diff_viewer.photoshop import Photoshop


class BruteForceDiffAlgo:
    """
    Brute-force algorithm to compare two images and highlight tiles with meaningful diffs.
    """

    image_1: NDArray
    image_2: NDArray
    threshold: float # range [0, 255] -> these are the meaningful diffs. HYPERPARAMETER.

    def __init__(self, image_1: NDArray, image_2: NDArray, threshold: float = 30.):
        self.image_1 = image_1
        self.image_2 = image_2
        self.threshold = threshold

    def exec(self) -> list[tuple[int, int]]:
        total_tiles = 0
        corrupted_tiles = 0
        corrupted_tiles_idx: list[tuple[int, int]] = []

        n_rows = self.image_1.shape[0]
        n_cols = self.image_1.shape[1]

        for i in range(n_rows):
            for j in range(n_cols):
                total_tiles += 1
                if self._compare_tiles(self.image_1[i, j], self.image_2[i, j]):
                    corrupted_tiles += 1
                    corrupted_tiles_idx.append((i, j))

        print(f"total tiles = {total_tiles}")
        print(f"corrupted tiles = {corrupted_tiles}")
        print(f"perc of corrupted tiles = {((corrupted_tiles / total_tiles) * 100):.2f}%")

        return corrupted_tiles_idx

    def _compare_tiles(self, tile_1: NDArray, tile_2: NDArray) -> bool:
        diff = np.mean(
            np.abs(tile_1.astype(np.int16) - tile_2.astype(np.int16)),
        )
        return diff > self.threshold


if __name__ == "__main__":
    photoshop = Photoshop()

    og_image = photoshop.load(path="resources/original.png")
    corrupted_image = photoshop.load(path="resources/corrupted.png")
    og_image, corrupted_image = photoshop.compare_and_resize(og_image, corrupted_image)
    assert og_image.size == corrupted_image.size

    og_bytes = photoshop.image_to_bytes(og_image)
    corrupted_bytes = photoshop.image_to_bytes(corrupted_image)

    start_time = time.perf_counter()
    corrupted_tiles_idx = BruteForceDiffAlgo(og_bytes, corrupted_bytes).exec()
    elapsed_time = time.perf_counter() - start_time

    print(f"took {elapsed_time} seconds to calculate diff using the brute-force algorithm.")

    masked_corrupted_image = photoshop.create_mask_over_tiles(corrupted_image, corrupted_tiles_idx)
    masked_corrupted_image.show()
