# Week 4 — Embeddings and similarity

Deliverable: a notebook with the similarity matrix and the cluster plot.

## Layout

| Path | Purpose |
|---|---|
| `docs/` | Source documents (public model-risk guidance) as PDF plus extracted text, with a README on each source |
| `figures/` | Saved plots (`clusters.png`) |
| `embeddings.ipynb` | The deliverable notebook: paragraph splitting, embeddings, similarity matrix, k-means (k=4), PCA plot, cluster labels and notes |

## Sources

| File | What it is |
|---|---|
| `docs/SR2602.pdf` / `.txt` | Federal Reserve SR 26-2 (April 17, 2026): the cover letter plus the guidance, 14 pages |
| `docs/SR2602a1.pdf` / `.txt` | The guidance on its own, 12 pages. The notebook uses this one, because `SR2602` repeats the same text |
| `docs/OCC-model-risk-booklet-2021.pdf` / `.txt` | OCC Comptroller's Handbook, *Model Risk Management*, version 1.0, August 2021, 109 pages. Rescinded by OCC Bulletin 2026-13 and no longer hosted by the OCC; this copy is from radicalcompliance.com. The notebook takes 12 evenly spaced paragraphs from its body |

## Steps (from the study plan)

1. Read the embeddings guide: vectors and cosine similarity.
2. Compute embeddings locally with `sentence-transformers` (model: `all-MiniLM-L6-v2`).
3. Embed 30–50 paragraphs from public model-risk documents, compute pairwise cosine similarity, cluster with k-means.
4. Plot the clusters in 2D (PCA or t-SNE) and label what each cluster is about.

## Result

50 paragraphs (38 from SR 26-2, 12 from the OCC booklet) embedded with `all-MiniLM-L6-v2` (384 dimensions). Silhouette scores for k=3 to 8 were low and close together (0.06–0.10, best 0.098 at k=4), so the clusters are soft. At k=4 each cluster mixes both sources, so the clusters follow topic and not document. The 2D PCA plot keeps about 25% of the variance. Cluster labels and notes are in the notebook.

Status: complete.
