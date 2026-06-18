# Merkle Trees

This morning, I was reading an article that Epic Games posted on Hacker News. They were talking about Lore, an open-source, highly scalable version control system. The article mentioned Merkle trees several times, and I remembered hearing about them in the context of blockchains. So, I thought I would read up on them, their applications, use cases, and implementation.

It turns out that Merkle trees are fairly straightforward to implement, yet very powerful.

In isolation, this code is not particularly useful, but I might use this repository to experiment with more interesting ideas around this data structure. I want to play around with files, maybe even audio files, by breaking their contents into chunks and writing a small algorithm to verify file integrity.

Merkle trees are interesting because, given two versions to compare, they let us narrow down corrupted or changed chunks in `O(log n)` time. I think that's pretty cool.

I am aware that none of this is cutting-edge. I am mostly using this repository as a way to learn by implementing things from scratch.

## Resources

* Epic Games article: https://epicgames.github.io/lore/explanation/system-design/
* Merkle Trees: https://www.geeksforgeeks.org/dsa/introduction-to-merkle-tree/
