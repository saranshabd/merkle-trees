import time
from typing import Optional
import hashlib

from numpy.typing import NDArray

from image_diff_viewer.photoshop import Photoshop


class ImageTileMerkleTreeNode:

    row_idx: int
    col_idx: int

    signature: str

    left: Optional["ImageTileMerkleTreeNode"]
    right: Optional["ImageTileMerkleTreeNode"]

    def __init__(
        self,
        row_idx: int,
        col_idx: int,
        flat_tile_bytes: Optional[NDArray],
        signature: Optional[str] = None,
        left: Optional["ImageTileMerkleTreeNode"] = None,
        right: Optional["ImageTileMerkleTreeNode"] = None
    ):
        """
        flat_tile_bytes are only used for creating the signature. Raw file bytes are not stored in the tree.
        """

        if flat_tile_bytes is not None:
            assert len(flat_tile_bytes.shape) == 1, "tile bytes must be flat."

        self.row_idx = row_idx
        self.col_idx = col_idx
        self.left = left
        self.right = right
        self.signature = signature or self._create_signature(flat_tile_bytes)

    def _create_signature(self, tile_bytes: Optional[NDArray]) -> str:
        assert tile_bytes is not None
        return hashlib.sha256(tile_bytes).hexdigest()


class ImageTileMerkleTree:

    image_bytes: NDArray
    root_node: ImageTileMerkleTreeNode

    def __init__(self, image_bytes: NDArray):
        self.image_bytes = image_bytes

        root_node = self._build_tree(indices=self._linear_indices())
        assert root_node is not None
        self.root_node = root_node

    def _build_tree(self, indices: list[tuple[int, int]]) -> ImageTileMerkleTreeNode | None:
        """
        Recursively build Merkle Tree by iterating over the list of available indices.
        """

        if len(indices) == 0:
            return None

        if len(indices) == 1:
            row_idx, col_idx = indices[0]
            subtree_root = ImageTileMerkleTreeNode(
                row_idx=row_idx,
                col_idx=col_idx,
                flat_tile_bytes=self.image_bytes[row_idx][col_idx].flatten(),
            )
            return subtree_root

        mid_idx = len(indices) // 2

        row_idx, col_idx = indices[mid_idx]
        left_subtree = self._build_tree(indices=indices[mid_idx:])
        right_subtree = self._build_tree(indices=indices[:mid_idx])

        subtree_signature = ""
        if left_subtree is not None:
            subtree_signature = left_subtree.signature
        if right_subtree is not None:
            subtree_signature += f"-{right_subtree.signature}"

        subtree_root = ImageTileMerkleTreeNode(
            row_idx=row_idx,
            col_idx=col_idx,
            flat_tile_bytes=None,
            signature=subtree_signature,
        )
        subtree_root.left = left_subtree
        subtree_root.right = right_subtree

        return subtree_root

    def _linear_indices(self) -> list[tuple[int, int]]:
        """
        Creates a flat list of indexes from the image bytes. This list is used to build the tree.
        """
        n_rows = self.image_bytes.shape[0]
        n_cols = self.image_bytes.shape[1]
        indices = [
            (i, j)
            for j in range(n_cols)
            for i in range(n_rows)
        ]
        return indices

    def find_corrupted_nodes(self, other_root: ImageTileMerkleTreeNode) -> list[tuple[int, int]]:
        assert other_root is not None
        return self._find_corrupted_nodes(self.root_node, other_root)

    def _find_corrupted_nodes(
        self, root: Optional[ImageTileMerkleTreeNode], other_root: Optional[ImageTileMerkleTreeNode],
    ) -> list[tuple[int, int]]:
        if root is None and other_root is None:
            return []

        assert root is not None and other_root is not None

        if root.signature == other_root.signature:
            return []

        if root.left is None and root.right is None:
            assert other_root.left is None and other_root.right is None
            return [(root.row_idx, root.col_idx)]

        corrupted_nodes = []
        corrupted_nodes.extend(self._find_corrupted_nodes(root.left, other_root.left))
        corrupted_nodes.extend(self._find_corrupted_nodes(root.right, other_root.right))

        return corrupted_nodes


if __name__ == "__main__":
    photoshop = Photoshop()

    og_image = photoshop.load(path="resources/original.png")
    corrupted_image = photoshop.load(path="resources/corrupted.png")
    og_image, corrupted_image = photoshop.compare_and_resize(og_image, corrupted_image)
    assert og_image.size == corrupted_image.size

    og_bytes = photoshop.image_to_bytes(og_image)
    corrupted_bytes = photoshop.image_to_bytes(corrupted_image)

    og_tree = ImageTileMerkleTree(image_bytes=og_bytes)
    corrupted_tree = ImageTileMerkleTree(image_bytes=corrupted_bytes)

    start_time = time.perf_counter()
    corrupted_tiles_idx = og_tree.find_corrupted_nodes(corrupted_tree.root_node)
    elapsed_time = time.perf_counter() - start_time

    print("number of corrupted tiles", len(corrupted_tiles_idx))

    # Brute Force: 0.024843708029948175 seconds
    # 5.604099715128541e-05 ~ 0.00005604099715128541 seconds
    # x443 speed up on a roughly ~5M image
    print(f"took {elapsed_time} seconds to calculate diff using a Merkle tree.")

    masked_corrupted_image = photoshop.create_mask_over_tiles(corrupted_image, corrupted_tiles_idx)
    masked_corrupted_image.show()

    with open("resources/diff_view.png", "wb") as file:
        masked_corrupted_image.save(file)
