Meta config (quick guide)
========================

Edit `meta.inference.json` before running. Only these fields typically need changes on a new machine:

1. models.checkpoint (point to your local weight files in `saved.ckpt/`)
2. phase1_test_data_optional.input (path to your NIfTI volume or a directory)
3. longitudinal.patients_glob (if doing Phase 2; keep `longitudinal_data/*` if running from repo root)
4. output_dir (optional; default `outputs` is fine)

Minimal structure:
```
{
  "models": {
    "ss": {"type": "uwavevitnet", "checkpoint": "saved.ckpt/ss.keras", "n_classes": 2},
    "seg": {"type": "uwavevitnet", "checkpoint": "saved.ckpt/seg.keras", "n_classes": 4}
  },
  "phase1_test_data_optional": {"input": "/path/to/volume.nii.gz"},
  "output_dir": "outputs",
  "longitudinal": {"patients_glob": "longitudinal_data/*", "inputs_glob": "*.nii"}
}
```

Optional extras (leave as-is unless you know you need them):
- infer.* (patch sizes, overlap)
- preproc.* (clip, zscore, refs)
- env.* (advanced model sizing knobs)
- registration.* (usually disabled)

Run (Phase 1 single volume):
```bash
source "$HOME/miniforge3/etc/profile.d/conda.sh" && conda activate tf219 \
  && python -m mrilong.cli --meta meta_examples/meta.inference.json --webview
```

Run (Phase 2 longitudinal):
```bash
source "$HOME/miniforge3/etc/profile.d/conda.sh" && conda activate tf219 \
  && python -m mrilong.cli --meta meta_examples/meta.inference.json --longitudinal
```

Notes:
- JSON has no comments; keep this file short.
- CPU is forced; set `use_gpu: false` or ignore.
- Keep relative checkpoints for portability.