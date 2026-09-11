# Real contract clause comparison

Hendrycks, D., Burns, C., Chen, A. & Ball, S. (2021). CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review. NeurIPS. The Atticus Project.

Source: https://www.atticusprojectai.org/cuad/

License: CC BY 4.0 https://creativecommons.org/licenses/by/4.0/

All 4609 unique annotated spans of 180–1,600 characters in 18 substantive clause categories. 346 repeated spans were removed after lowercasing and whitespace normalization. No edits, generated variants or artificially duplicated files. No selection based on a target similarity score.

Every excerpt is checked byte-for-byte against its annotated character range in a real source contract. Files are clause excerpts, not whole contracts. Full source contract text is included. Matching compares different source contracts, requires at least 90% character-shingle Jaccard by default, and excludes 100% set matches.

Purpose: retrieve similar clauses from other agreements and inspect actual wording differences. Text similarity does not establish legal equivalence or determine which agreement is preferable.
