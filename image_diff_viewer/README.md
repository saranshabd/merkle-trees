# Image Diff Viewer

Merkle trees are powerful for comparing diffs at scale. Git uses them to pinpoint 2 changed files in a directory of tens of thousands without reading the unchanged ones. This project applies the same idea to images.

The use case: design teams iterate constantly on brand images, UI screenshots, and other assets, storing different versions over time. Most diff tools are built for text. This one is built for images.

A brute force comparison finds exactly where two images differ, but it's `O(n)` every single time, re-reading every pixel on every comparison. The Merkle tree does the same thing in `O(log n)`, by pruning unchanged regions at the root without re-examining them. The catch is that this only holds once the original image's tree is pre-built and cached. This is exactly the way Git indexes a repository as well. Pay the `O(n)` build cost once, and every subsequent comparison is `O(log n)`.

The benchmark bears this out on a ~5 MB image:

| Method      | Time (seconds) |
|-------------|----------------|
| Brute force | 0.024843       |
| Merkle tree | 0.000056       |

~443x faster per comparison against a cached index.

This pays off at scale. Pre-index every version of an asset library once, and every subsequent diff is `O(log n)` regardless of image size.

---

## Sample diff

![diff_view](../resources/diff_view.png)

---

Such algorithms are useful for quickly understanding the progression and evolution of visual assets for designers and the people they work with.
