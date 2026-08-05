# DCRNN Reproduction on METR-LA

## Experiment information

- Model: DCRNN
- Dataset: METR-LA
- Framework: BasicTS
- BasicTS base commit: `9a10e45`
- Reproduction branch: `dcrnn-compatible`
- Input length: 12 time steps (60 minutes)
- Output length: 12 time steps (60 minutes)
- Number of sensors: 207
- Sampling interval: 5 minutes
- Epochs: 100
- Batch size: 64
- Initial learning rate: 0.01
- Train/validation/test split: 70% / 10% / 20%

## Final test results

| Prediction horizon | MAE | MAPE | RMSE |
|---|---:|---:|---:|
| Overall | 3.0425 | 8.28% | 6.2756 |
| 15 minutes (horizon 3) | 2.6722 | 6.83% | 5.1767 |
| 30 minutes (horizon 6) | 3.0812 | 8.34% | 6.3242 |
| 60 minutes (horizon 12) | 3.5660 | 10.32% | 7.5326 |

These are metrics over the full METR-LA test set. The 60-minute forecast has the largest error, showing the expected increase in uncertainty at longer horizons.

## Training command

Run from the BasicTS repository root:

```powershell
python experiments\train.py -c baselines\DCRNN\METR-LA.py -g 0
```

## Evaluation and result export

The completed run used the best validation-MAE checkpoint. The run ID below is the ID generated during this reproduction:

```powershell
python experiments\evaluate.py `
  -cfg baselines\DCRNN\METR-LA.py `
  -ckpt checkpoints\DCRNN\METR-LA_100_12_12\5d3dc5d562e4ccea45b0f616d274b0a7\DCRNN_best_val_MAE.pt `
  -g 0 `
  -d gpu
```

The local run directory contains:

```text
checkpoints/DCRNN/METR-LA_100_12_12/5d3dc5d562e4ccea45b0f616d274b0a7/
├── DCRNN_best_val_MAE.pt
├── DCRNN_100.pt
├── test_metrics.json
└── test_results/
    ├── inputs.npy
    ├── predictions.npy
    └── targets.npy
```

The checkpoint files, dataset, and large prediction arrays are excluded from Git.

## Exported array format

The three exported arrays have shape:

```text
(6831, 12, 207, 1)
```

The dimensions mean 6,831 test samples, 12 forecast steps, 207 sensors, and one speed feature. Although their filenames end in `.npy`, this BasicTS version creates them with `numpy.memmap`, so they are raw binary arrays without a standard NumPy header. They must be read with `numpy.memmap`, not `numpy.load`.

## Visualization

The comparison script plots sensor 0 over the first 288 test samples (24 hours) at three horizons:

```powershell
python scripts\plot_dcrnn_comparison.py `
  --result-dir "checkpoints\DCRNN\METR-LA_100_12_12\5d3dc5d562e4ccea45b0f616d274b0a7\test_results"
```

Local MAE values shown in this one-sensor, one-day figure were:

| Horizon | Local figure MAE (mph) |
|---|---:|
| 15 minutes | 2.973 |
| 30 minutes | 2.751 |
| 60 minutes | 3.442 |

These local values are for visualization only and do not replace the full test-set metrics above. The prediction follows stable traffic periods well but is smoother than the ground truth around sudden speed drops and recovery.
