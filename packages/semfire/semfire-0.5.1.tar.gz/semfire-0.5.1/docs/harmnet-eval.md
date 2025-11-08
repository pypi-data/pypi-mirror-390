# HarmBench Evaluation Guide 

This guide shows how to evaluate SemFire on real adversarial data (HarmBench) and export an ATT&CK v18 Navigator layer.

## Quick Start (15 minutes)

```bash
# Optional, for dataset access
pip install datasets

# Run evaluation (falls back to synthetic data if dataset unavailable)
python semfire_harmbench_demo.py --max 100

# Outputs
ls -lh semfire_harmbench_evaluation.json
```

Expected:
- Console prints overall stats and per-category high-risk counts
- `semfire_harmbench_evaluation.json` layer is generated (v18)

## Advanced usage

Online (Hugging Face datasets):

```bash
python semfire_harmbench_demo.py \
  --dataset HarmBench/harmbench \
  --split test \
  --max 200 \
  --sample-per-category 50 \
  --seed 42
```

Offline (local JSONL with {prompt, category} per line):

```bash
# Example JSONL row:
# {"prompt": "Let's consider hypothetically...", "category": "Cybercrime"}

python semfire_harmbench_demo.py \
  --local-jsonl path/to/local.jsonl \
  --max 150 \
  --out-results harmbench_results.jsonl \
  --out-layer semfire_harmbench_evaluation.json
```

Flags:
- `--max` — maximum items to evaluate
- `--sample-per-category` — cap items per category before `--max` (balanced sampling)
- `--out-results` — write per-sample JSONL (empty to disable)
- `--out-layer` — output v18 layer path

## Visualize in ATT&CK Navigator

1. Visit https://mitre-attack.github.io/attack-navigator/
2. Click "+" → "Open Existing Layer"
3. Upload `semfire_harmbench_evaluation.json`
4. Screenshot for slides

## Capture Screenshots for Slides

Recommended shots (save to `assets/screenshots/`):

- harmbench_matrix.png — Navigator view of HarmBench layer
- harmbench_technique_detail.png — Technique detail panel (v18 metadata)
- jbb_matrix.png — Navigator view of JBB layer
- v18_layer_metadata.png — Layer metadata showing Detection Strategies + Analytics

Tips:
- Use 2x/Retina resolution.
- Ensure consistent filters across captures.
- If you have demos/*.gif, you can extract stills via:

```bash
bash scripts/gif_to_pngs.sh demos/semfire_harmbench_demo.gif assets/screenshots/harmbench_matrix.png 60
```

## Recording Backup (asciinema)

```bash
asciinema rec semfire_harmbench.cast --title "SemFire + HarmBench"
python semfire_harmbench_demo.py --max 100
# Ctrl+D to finish

# Convert to GIF (Docker-based)
bash scripts/cast_to_gif.sh semfire_harmbench.cast semfire_harmbench.gif --cols 120 --rows 30 --theme monokai
```

## Dataset Notes

- Script uses `datasets` to load a HarmBench test split when available. If the dataset name/split changes, edit the `load_dataset("HarmBench/harmbench", split="test")` line.
- If the dataset can’t be downloaded (no internet), the script automatically uses a small synthetic fallback set so the rest of the pipeline still works.

## Slide Content Suggestions

- Title: "SemFire + HarmBench: Real Adversarial Data Evaluation"
- Bullets: Dataset size, categories tested, high/medium detection rates, average runtime
- Screenshot: Navigator heatmap + per-category stats

## Q&A Talking Points

- Why HarmBench? Used by major labs (Microsoft, Anthropic, Google), reproducible
- How many prompts? Use `--max` to run a quick subset live (e.g., 100)
- Offline? Falls back to a synthetic set for the demo
- v18? Layer uses the v18 Detection Strategies mapping via `SemFireNavigatorV18Adapter`
