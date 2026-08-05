# DCRNN Reproduction on METR-LA

## Experiment Information

- Model: DCRNN
- Dataset: METR-LA
- Framework: BasicTS
- BasicTS commit: 9a10e45
- Branch: dcrnn-compatible
- Input length: 12 time steps (60 minutes)
- Output length: 12 time steps (60 minutes)
- Number of sensors: 207
- Sampling interval: 5 minutes
- Epochs: 100
- Batch size: 64
- Initial learning rate: 0.01
- Train/validation/test split: 70% / 10% / 20%

## Final Test Results

| Prediction Horizon | MAE | MAPE | RMSE |
|---|---:|---:|---:|
| Overall | 3.0425 | 8.28% | 6.2756 |
| 15 minutes (Horizon 3) | 2.6722 | 6.83% | 5.1767 |
| 30 minutes (Horizon 6) | 3.0812 | 8.34% | 6.3242 |
| 60 minutes (Horizon 12) | 3.5660 | 10.32% | 7.5326 |

## Saved Model Files

The trained model files are stored locally under:

checkpoints/DCRNN/METR-LA_100_12_12/

Important files:

- DCRNN_best_val_MAE.pt
- DCRNN_100.pt
- test_metrics.json

The checkpoint files and dataset are excluded from Git because they are large.

## Training Command

```powershell
easytrain -c baselines/DCRNN/METR-LA.py --devices 0