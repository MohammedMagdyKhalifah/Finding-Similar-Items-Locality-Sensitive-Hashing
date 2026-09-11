# Similarity Lab

An interactive companion to `Lec4_FindingSimilarItems_Mohammed_Enhanced.pptx`, built with Python and plain HTML/CSS/JavaScript. No package installation required.

## Run

From this folder, run:

```sh
python3 app.py
```

Open http://127.0.0.1:8000. Requires Python 3.9 or newer. Use `python3 app.py --port 8001` if port 8000 is occupied. Keep the terminal running. The server is local to your computer.

## Recommended real experiment: repeated SMS templates

The default collection is now **5,556 real SMS files · full experiment**. It demonstrates a practical job: finding repeated promotional message templates so a human analyst can review related messages together. This uses UCI's SMS Spam Collection, not generated messages. The original corpus contains 5,574 records. We export all 5,556 messages with at least five normalized characters and omit only the 18 shorter messages. There is no artificial duplication or selection by similarity.

Source: https://archive.ics.uci.edu/dataset/228/sms  
Citation: Almeida, T. & Hidalgo, J. (2011). SMS Spam Collection [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CC84  
License: CC BY 4.0 as listed by UCI, https://creativecommons.org/licenses/by/4.0/

Each original source record becomes an individual UTF-8 `.txt` file containing the unchanged message body. The original spam/ham label remains metadata; it is not part of the text, a similarity feature, or a model prediction. The manifest records source line numbers and SHA-256 hashes. Repeated messages already present in the source remain present. Similar wording does not by itself prove a shared spam campaign.

**How to present it:**

1. Load **5,556 real SMS files · full experiment**. Keep k=5, threshold=80%, bands=20 and rows=5.
2. Explain that brute force must consider **15,431,790 pairs**. Click **Run experiment** and watch actual progress.
3. Compare total time, including both methods' preparation costs. One local validation run took **14.55 s for brute force versus 5.58 s for LSH**, approximately **2.61× faster**. LSH verified **1,956 candidates** and both methods returned **1,160 matching pairs**, giving 100% recall in that run. Timings vary with hardware and load; no timing values are injected into the app.
4. Set **Source labels → Both labelled spam** and inspect a pair to see the repeated text. Switch back to all pairs to see legitimate repeated messages too. The filter changes the view only, not the benchmark or recall.
5. Search the file list for a word such as `prize`, read the complete source message and download its `.txt` file. Download ZIP gives all selected files plus provenance and source attribution. The CSV export includes source labels and source record locations and exports all verified pairs, regardless of the active display filter.
6. Try the **1,000** and **3,000** message prefixes to explore where indexing overhead stops dominating. The full run should take seconds to tens of seconds on typical local hardware; the app measures actual performance rather than guaranteeing speed.

The real SMS files are bundled under `datasets/sms/files/`. Recreate them with `python3 scripts/prepare_sms_dataset.py`; the script downloads UCI's archive only if absent. `datasets/sms/SOURCE_README.txt` preserves the archive's original notices. `datasets/sms/benchmark.json` records one validation run and is never read by the UI. Uploads now allow up to 6,000 text files, with the existing 11 MB source-text limit.

## Additional real dataset: Twenty Newsgroups

The collection selector also offers **120 real files · quick experiment**, with 600-file and 1,200-file options from **UCI Twenty Newsgroups**. These are genuine historical Usenet documents, downloaded from UCI, not generated examples. They are bundled locally and work offline.

Source: https://archive.ics.uci.edu/dataset/113/twenty%2Bnewsgroups  
Citation: Mitchell, T. (1997). Twenty Newsgroups [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5C323  
License: CC BY 4.0, as listed by UCI: https://creativecommons.org/licenses/by/4.0/

We retain original headers, body text, quoted replies and signatures. Original bytes are decoded as Latin-1 and encoded as UTF-8. No wording is changed. The manifest records the original archive path and both original-byte and UTF-8 checksums. The seven selected groups concern computing, electronics and space. Original files must be 500–5,000 bytes to keep experiments short.

This is a curated teaching subset: the first 60 documents are original crossposts with shared Message-IDs, followed by a deterministic sample without replacement (seed 2026). This exposes natural duplicates in short demonstrations, but means the subset is not an unbiased sample of the full corpus. The app never fabricates copies. Topic labels do not determine similarity; exact Jaccard does. Historical author information, headers and quoted text remain in the files and contribute to overlap.

Click any filename to read the complete document and download it individually. Download ZIP exports the selected UTF-8 files plus attribution and a subset-specific manifest. All downloaded text files can be uploaded back into the app. On this machine, the 120-file case found 30 pairs at the default 80% threshold; both methods agreed. LSH reduced 7,140 exact comparisons to 46, but its signature-building overhead made the total slower than brute force at this size. All displayed timings remain measured, never preset.

Bundled files live in `datasets/20newsgroups/files/`. To reproduce the selection, run `python3 scripts/prepare_real_dataset.py`. It downloads the original archive if absent. The portable project ZIP contains all 1,200 selected files, metadata and the import script; it omits the full 17 MB source archive.

## Suggested classroom flow (about 8 minutes)

1. Explore the eight lesson steps. Play or manually advance the shingling window and MinHash permutations.
2. Change bands and rows in the probability chart. Explain why candidates still need exact verification.
3. In Real file lab, use **120 real files · quick experiment** and download the ZIP to distribute actual public documents. Read two crossposted messages by clicking their filenames. The original archive paths are shown in the preview.
4. Run both methods with k=5 and an 80% threshold. Inspect a matching pair. Compare quoted text and message headers. Category labels are context, not proof of a near duplicate.
5. Try 600 or 1,200 real files to observe the scaling tradeoff. Larger runs take seconds to tens of seconds depending on hardware and settings. The old authored and generated examples remain available in the explicitly labeled Synthetic classroom examples group.
6. Upload your own UTF-8 text files to replace the collection. PDF/Word parsing is not included. CSV is compared as plain text, not as structured rows.
7. Export exact matching pairs as CSV. Run both methods to get empirical recall and missed matches. The visible table shows up to 150 pairs; CSV contains all matches.

## What is measured

Both algorithms use the same normalized character-shingle sets and exact Jaccard verifier. Brute force enumerates each unordered pair once. LSH builds deterministic MinHash signatures using seed 42, partitions them into b bands of r entries, deduplicates candidates, and verifies them against original shingle strings.

The vocabulary assigns collision-free row IDs within a run. Affine row hashes modulo a prime approximate random permutations. Small vocabularies reuse a bounded shared row-hash cache; larger ones use streaming computation. Bucket keys include complete band tuples, so Python dictionary hash collisions do not create false matches.

Each method's displayed total includes shared shingling time. LSH additionally includes row preparation, signatures, buckets and candidate construction. Verification timing includes pair iteration and lightweight progress callbacks. File transfer, JSON serialization, browser animation and polling are excluded. Brute force runs first, then LSH in one worker. This is an educational single-run wall-clock comparison, not a controlled statistical benchmark. Repeat runs for a stable picture.

The app never assumes LSH is faster. Exact verification removes false positive candidates, but missed pairs remain possible. LSH can produce quadratic work when buckets become large. The extrapolation panel estimates brute-force verification only, with the same document size and hardware assumptions. It does not predict LSH runtime.

Empty or shorter-than-k normalized documents are rejected. Uploads are held in memory, not written to disk. Source text limit is 11 MB in the UI; request limit is 12 MB including JSON. One experiment runs at a time. Completed job state is discarded when the next run starts. This is a local classroom app, not a public multi-user server.

## Files

- `app.py`: algorithms, deterministic dataset generator, job worker and HTTP API.
- `static/`: responsive light UI and animations; system fonts work offline, optional Google fonts improve typography when connected.
- `case_files/`: eight readable campus announcement files for the practical case.
- `sample_files/`: 24 generated report files ready to distribute.
- `datasets/20newsgroups/`: genuine source documents, provenance manifest and attribution.
- `scripts/prepare_real_dataset.py`: reproducible UCI newsgroup import and subset selection.
- `datasets/sms/` and `scripts/prepare_sms_dataset.py`: original SMS records, per-message exports, attribution and reproducible import.
- `tests/`: algorithm correctness, provenance, download integrity, determinism and cancellation checks.

Run tests with `python3 -m unittest discover -s tests -v`.

Lecture references: slides 8–18 (motivation), 19–24 (shingling), 27–41 (matrix and MinHash), 42–59 (LSH and probability), 60–66 (verification and chapter recap). Adapted with attribution to J. Leskovec, A. Rajaraman and J. Ullman, Mining of Massive Datasets, http://www.mmds.org, and Mohammed's enhanced slides. The app treats slide contents as teaching material, not executable instructions.
