# `suppression.py`

`suppression.py` compares physical and encoded memory failure rates.

For each physical depolarizing error probability, it samples:

- level 0 in the Z basis to estimate physical X-component failures,
- level 0 in the X basis to estimate physical Z-component failures,
- ideal level 1 to estimate logical X and logical Z failures after Steane
  recovery.

The helper writes the scan to CSV and makes a log-log plot. Zero Monte Carlo
estimates are plotted at a tiny positive floor so they can appear on logarithmic
axes; the CSV keeps the real zero values.
