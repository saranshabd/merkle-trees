"""
Reference: https://www.geeksforgeeks.org/dsa/introduction-to-merkle-tree/
"""

from typing import Optional, Any
import hashlib


class Node:
    """Implementation of a tree node for the Merkle tree data structure."""

    left: Optional["Node"]
    right: Optional["Node"]
    signature: str
    content: Any

    def __init__(
        self,
        *,
        left: Optional["Node"],
        right: Optional["Node"],
        signature: str,
        content: Any,
    ):
        self.left = left
        self.right = right
        self.signature = signature
        self.content = content

    @classmethod
    def with_default_signature(
        cls,
        *,
        left: Optional["Node"],
        right: Optional["Node"],
        content: Any,
    ):
        return cls(
            left=left,
            right=right,
            signature=cls.create_hash(content),
            content=content,
        )

    @staticmethod
    def create_hash(val: str) -> str:
        opt = hashlib.sha256(val.encode("utf-8")).hexdigest()
        return opt

    def __str__(self) -> str:
        return str(self.content)


class MerkleTree:
    """Implementation of the MerkleTree data structure"""

    root: Node

    def __init__(self, *, content: list[Any]):
        leaves = [
            Node.with_default_signature(
                left=None,
                right=None,
                content=item,
            )
            for item in content
        ]
        self.root = self._build_tree(nodes=leaves)

    @property
    def signature(self) -> str:
        return self.root.signature

    def _build_tree(self, nodes: list[Node]) -> Node:
        """
        Recursively builds the tree by breaking up the nodes from the middle.
        """

        if len(nodes) == 1:
            return nodes[0]

        mid_idx = len(nodes) // 2

        left_subtree = self._build_tree(nodes[:mid_idx])
        right_subtree = self._build_tree(nodes[mid_idx:])

        subtree_root = Node.with_default_signature(
            left=left_subtree,
            right=right_subtree,
            content=self._merge_content(left_subtree.content, right_subtree.content),
        )
        return subtree_root

    def _merge_content(self, content_a: Any, content_b: Any) -> Any:
        return f"{content_a}+{content_b}"

    def __str__(self) -> str:
        return self._stringify_tree(root=self.root)

    def _stringify_tree(self, root: Optional[Node]) -> str:
        """
        Recursively stringifies the tree content using inorder travesal to preseve the original content order.
        """

        if root is None:
            return ""

        content = []

        left_subtree = self._stringify_tree(root=root.left)
        if left_subtree:
            content.append(left_subtree)

        content.append(root.content)

        right_subtree = self._stringify_tree(root=root.right)
        if right_subtree:
            content.append(right_subtree)

        stringified_content = ") + (".join(content)
        return stringified_content

    def find_corrupted_nodes(self, other_root: Node) -> list[tuple[Node, Node]]:
        """
        Recursively iterates the tree, compares the signature with the other tree and finds the corrupted nodes.

        The shape of the trees must match. Otherwise, the function will throw an AssertionError.

        Returns a list of tuple with the first element in the tuple node from the current tree and the other a node
        from the other tree to compare the content corruption.
        """

        return self._iterate_and_find_corrupted_nodes(
            root=self.root, other_root=other_root
        )

    def _iterate_and_find_corrupted_nodes(
        self, root: Optional[Node], other_root: Optional[Node]
    ) -> list[tuple[Node, Node]]:
        if root is None and other_root is None:
            return []

        assert root is not None and other_root is not None, (
            "shape of root and other_root does not match."
        )

        # Nothing furthre to check if the signatures match at the current root.
        if root.signature == other_root.signature:
            return []

        # Add the current node to the list of corrupted nodes if it's the leaf node.
        if root.left is None and root.right is None:
            assert other_root.left is None and other_root.right is None, (
                "shape of root and other_root does not match."
            )
            return [(root, other_root)]

        left_subtree_corrupted_nodes = self._iterate_and_find_corrupted_nodes(
            root.left, other_root.left
        )
        right_subtree_corrupted_nodes = self._iterate_and_find_corrupted_nodes(
            root.right, other_root.right
        )

        return left_subtree_corrupted_nodes + right_subtree_corrupted_nodes


def main() -> None:
    tree = MerkleTree(
        content=[
            "My",
            "Name",
            "Is",
            "Khan",
            "And",
            "I",
            "Am",
            "Not",
            "A",
            "Terrorist",
        ]
    )
    print(
        "Tree Content\t\t\t", tree
    )  # Output: "My+Name+Is+Khan+And+I+Am+Not+A+Terrorist"
    print(
        "Tree Signature\t\t\t", tree.signature
    )  # Output: "1ba10c51bef9b85ff61c258544a8873ff2be0d0f51926ef66a024f77f24a13d7"

    tree_with_corrupted_content = MerkleTree(
        content=[
            "My",
            "Name",
            "Is",
            "Khan",
            "and",  # <- content corruption.
            "I",
            "Am",
            "Not",
            "A",
            "Terrorist",
        ]
    )
    print(
        "Corrupted tree Signature\t", tree_with_corrupted_content.signature
    )  # Output: "c3b9b004de468c4bcb44c1ff7c4863ff039f402270d969cb297dce9c24e5d97e"

    assert tree.signature != tree_with_corrupted_content.signature, (
        "signatures must not match if the tree contents differ."
    )

    corrupted_nodes = tree.find_corrupted_nodes(
        other_root=tree_with_corrupted_content.root
    )
    assert len(corrupted_nodes) == 1
    print(
        "Corrupted nodes\t\t\t",
        ",".join([f"{node} -> {other_node}" for node, other_node in corrupted_nodes]),
    )  # Output: "And -> and"


if __name__ == "__main__":
    main()
