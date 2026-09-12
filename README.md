# Similarity Lab

An interactive teaching tool for finding near-duplicate text: character shingling, MinHash signatures, and Locality-Sensitive Hashing (LSH), compared against brute-force exact Jaccard similarity. It is an interactive companion to `Lec4_FindingSimilarItems_Mohammed_Enhanced.pptx`.

The whole app is a single Python file (`app.py`) using only the standard library, plus a plain HTML/CSS/JavaScript front end (`static/`). **There is nothing to install** — no `pip install`, no virtual environment, no build step, and no internet connection required to run it, because the real datasets it uses are already bundled in this repository.

## Requirements

- Python **3.9 or newer** (uses `Path.is_relative_to`, added in 3.9). Check your version:
  ```sh
  python3 --version
  ```
- A modern web browser (Chrome, Firefox, Safari, Edge).
- No third-party Python packages are required to run the app or its tests.

## Quick start

1. Get the project onto your machine — clone this repository (or copy/unzip the folder) so you have `app.py` and its neighboring folders together.
2. Open a terminal in this folder (the one containing `app.py`).
3. Start the server:
   ```sh
   python3 app.py
   ```
   On Windows, if `python3` isn't recognized, use `python app.py` instead (Python launched from python.org registers as `python`).
4. Open **http://127.0.0.1:8000** in your browser.
5. Leave the terminal window open — it is your local web server. Press `Ctrl+C` in the terminal to stop it when you're done.

If port 8000 is already in use, pick another one:
```sh
python3 app.py --port 8001
```
Then open `http://127.0.0.1:8001` instead.

The server only listens on `127.0.0.1` (localhost), so it is reachable only from your own computer, not the network.

## Verify your setup

Run the automated test suite to confirm Python, the algorithms, and the bundled datasets are all working correctly:
```sh
python3 -m unittest discover -s tests -v
```
You should see 18 tests, all `ok`, ending in `OK`. This checks MinHash/LSH correctness against brute force, plus provenance and integrity of the three real datasets described below.

## Troubleshooting

- **`command not found: python3`** — Install Python 3.9+ from https://www.python.org/downloads/, or try `python` instead of `python3` (common on Windows).
- **`OSError: [Errno 48] Address already in use`** (or similar on Windows/Linux) — another program is using port 8000. Run with `--port 8001` (or any free port) as shown above.
- **Page doesn't load in the browser** — confirm the terminal printed `Similarity Lab running at http://127.0.0.1:...` with no errors, and that you're using `http://`, not `https://`.
- **Tests fail on a fresh clone** — make sure `git lfs` isn't required and no files were skipped; the `datasets/` folder should already contain populated `files/` subfolders (thousands of small `.txt` files) without you running anything extra. If `datasets/*/files/` are empty, see "Regenerating datasets from source" below.
- **Nothing to uninstall** — since nothing is installed (no virtual environment, no packages), you can remove the app by simply deleting the folder.

## What the app does

Open the running app in your browser and you'll find:

- An interactive, eight-step walkthrough using two original CUAD sponsorship clauses throughout. All counts, minima, signatures and bands are computed from the source excerpts. Their exact five-character Jaccard is 407 / 444 = 91.67%. Play or manually advance the animations.
- A "Real file lab" where you pick a document collection, set parameters (shingle size `k`, bands `b`, rows per band `r`, similarity threshold), and click **Run experiment** to compare brute-force and LSH side by side, with live progress and measured timings.
- The ability to upload your own UTF-8 `.txt`/`.md`/`.csv`/`.log` files (up to 6,000 files / 11 MB) instead of a bundled dataset.
- Downloadable results: matching pairs as CSV, or the full document collection as a ZIP with provenance metadata.

See "Suggested classroom flow" below for a guided tour.

## Bundled real datasets

All three datasets below are **already generated and committed to this repository** under `datasets/`, so they work immediately, offline, with no setup. You never need to run the `scripts/prepare_*.py` importers unless you want to regenerate them from the original public sources (which does require internet access — see the last section).

### Real contract clause comparison (default in the UI)

**4,609 real clauses · different contracts** (with a 1,000-clause quick option) from the CUAD (Contract Understanding Atticus Dataset) legal contract corpus. This is the dataset selected by default when you open the app.

- Source: https://www.atticusprojectai.org/cuad/
- Citation: Hendrycks, D., Burns, C., Chen, A. & Ball, S. (2021). *CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review*. NeurIPS. The Atticus Project.
- License: CC BY 4.0

Each file is a real, unedited excerpt (180–1,600 characters) of a clause from a commercial contract, in one of 18 substantive categories (liability caps, anti-assignment, exclusivity, termination, etc.). By default the app compares clauses across *different* source contracts only, at a 90%+ threshold excluding exact (100%) matches — the task is to find a similarly-worded clause in another agreement and inspect how it differs, not to find copies of the same document. The “Exclude 100% similarity matches” checkbox is optional and applies to both methods; uncheck it before running to include exact shingle-set matches. Your choice persists when loading another collection. Identical excerpt texts were already removed during dataset preparation. Full source contracts are available to read for context. Bundled under `datasets/contracts/files/`; reproduce with `python3 scripts/prepare_contract_dataset.py`.

### Real SMS message templates

**5,556 real SMS files · full experiment** (with 1,000 and 3,000-message presets), from UCI's SMS Spam Collection. Demonstrates finding repeated promotional message templates so an analyst can review related messages together.

- Source: https://archive.ics.uci.edu/dataset/228/sms
- Citation: Almeida, T. & Hidalgo, J. (2011). *SMS Spam Collection* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CC84
- License: CC BY 4.0

Each of the original 5,574 records becomes an individual UTF-8 `.txt` file with the unchanged message body; 18 messages shorter than 5 normalized characters are omitted, with no artificial duplication. The original spam/ham label is kept only as metadata (visible as a results filter), never as a similarity input. Bundled under `datasets/sms/files/`; reproduce with `python3 scripts/prepare_sms_dataset.py`.

### Twenty Newsgroups

**120 real files · quick experiment** (with 600 and 1,200-file options), from UCI's Twenty Newsgroups — genuine historical Usenet posts from computing, electronics and space discussion groups.

- Source: https://archive.ics.uci.edu/dataset/113/twenty%2Bnewsgroups
- Citation: Mitchell, T. (1997). *Twenty Newsgroups* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5C323
- License: CC BY 4.0

Original headers, bodies, quoted replies and signatures are preserved (decoded Latin-1 → UTF-8, no wording changed). The subset is curated for teaching: the first 60 documents are genuine crossposts sharing Message-IDs (built-in near-duplicates), followed by a deterministic random sample (seed 2026) — so it is not an unbiased sample of the full corpus. Bundled under `datasets/20newsgroups/files/`; reproduce with `python3 scripts/prepare_real_dataset.py`.

### Synthetic classroom examples

Also available in the dataset picker, clearly labeled as synthetic: an 8-file authored campus-announcement case (`case_files/`) and generated report-revision families of various sizes (24 to 1,200 files) for scaling demonstrations. These are created by the app itself, not sourced from the internet.

### Portable offline copy

`similarity-lab.zip` is a self-contained snapshot of the app (code, static assets, case files, and the SMS and Newsgroups datasets) for sharing or running elsewhere without git. Unzip it and run `python3 app.py` from inside, the same as above.

### Regenerating datasets from source (optional, needs internet)

You do not need to do this to use the app — it's only useful if you want to rebuild a dataset from its original public source (e.g., to verify provenance yourself or pick up an update):
```sh
python3 scripts/prepare_contract_dataset.py   # downloads CUAD_v1.json from Hugging Face
python3 scripts/prepare_sms_dataset.py        # downloads the UCI SMS Spam Collection zip
python3 scripts/prepare_real_dataset.py       # downloads the UCI 20 Newsgroups tar.gz
```
Each script skips its download if the source archive is already present in `datasets/<name>/`, and writes back into `datasets/<name>/files/` plus a `manifest.json` with checksums and provenance.

## Suggested classroom flow (about 8 minutes)

1. Explore the eight lesson steps. Play or manually advance the shingling window and MinHash row hashes.
2. Change bands and rows in the probability chart. Explain why candidates still need exact verification.
3. In Real file lab, inspect the verified contract example: “a controlling interest” versus “an interest”. Read the original source contracts and download the ZIP with exact source offsets.
4. Run both methods on 1,000 real clauses with k=5 and a 90% threshold. Check or uncheck “Exclude 100% similarity matches” before running; the results explain which setting was used.
5. Try all 4,609 real clauses to observe scaling. Compare total time including signature construction, comparisons, recall and highlighted wording differences.
6. Upload your own UTF-8 text files to replace the collection. PDF/Word parsing is not included; CSV is compared as plain text, not as structured rows.
7. Export exact matching pairs as CSV. Run both methods to get empirical recall and missed matches. The visible table shows up to 150 pairs; the CSV export contains all matches.

For a real-world "does this actually save time" demonstration, load **5,556 real SMS files · full experiment** (SMS Spam Collection): brute force must consider 15,431,790 pairs, while LSH builds signatures and only verifies the candidates its buckets produce. One local validation run measured 14.55 s for brute force versus 5.58 s for LSH (≈2.61× faster), with both methods returning the same 1,160 matching pairs (100% recall in that run). Timings vary with hardware and load; the app never injects or presets a timing value — everything shown is measured live.

## What is measured

Both algorithms use the same normalized character-shingle sets and exact Jaccard verifier. Brute force enumerates each unordered pair once. LSH builds deterministic MinHash signatures using seed 42, partitions them into `b` bands of `r` entries, deduplicates candidates, and verifies them against original shingle strings.

The vocabulary assigns collision-free row IDs within a run. Affine row hashes modulo a prime approximate random permutations. Each hash column is computed once for the shared vocabulary, used by all documents, then discarded to bound memory. The teaching example assigns row IDs using its two-clause vocabulary; full lab runs use their own corpus vocabulary. Bucket keys include complete band tuples, so Python dictionary hash collisions do not create false matches.

Each method's displayed total includes shared shingling time. LSH additionally includes row preparation, signatures, buckets and candidate construction. Verification timing includes pair iteration and lightweight progress callbacks. File transfer, JSON serialization, browser animation and polling are excluded. Brute force runs first, then LSH, in one worker. This is an educational single-run wall-clock comparison, not a controlled statistical benchmark — repeat runs for a stable picture.

The app never assumes LSH is faster. Exact verification removes false-positive candidates, but missed pairs remain possible. LSH can produce quadratic work when buckets become large. The extrapolation panel estimates brute-force verification only, with the same document size and hardware assumptions; it does not predict LSH runtime.

Empty or shorter-than-`k` normalized documents are rejected. Uploads are held in memory, not written to disk. Source text limit is 11 MB in the UI; request limit is 12 MB including JSON. One experiment runs at a time; completed job state is discarded when the next run starts. This is a local, single-user classroom app, not a public multi-user server — do not expose it to the internet as-is.

## Project structure

```
app.py                 Algorithms, dataset loading, job worker and HTTP API (stdlib only)
static/                Front-end UI: index.html, app.js, style.css, favicon.svg
case_files/             8 authored campus-announcement files for the synthetic practical case
sample_files/           24 generated report-revision files ready to distribute
datasets/contracts/     Real CUAD contract clauses, manifest and attribution (default dataset)
datasets/sms/           Real SMS Spam Collection messages, manifest and attribution
datasets/20newsgroups/  Real Twenty Newsgroups posts, manifest and attribution
scripts/                Reproducible importers that (re)build the three datasets above from their original public sources
tests/                  Algorithm correctness, provenance, download integrity, determinism and cancellation checks
similarity-lab.zip      Portable, offline snapshot of the app for sharing without git
```

## Lecture references

Slides 8–18 (motivation), 19–24 (shingling), 27–41 (matrix and MinHash), 42–59 (LSH and probability), 60–66 (verification and chapter recap). Adapted with attribution to J. Leskovec, A. Rajaraman and J. Ullman, *Mining of Massive Datasets*, http://www.mmds.org, and Mohammed's enhanced slides. The app treats slide contents as teaching material, not executable instructions.
