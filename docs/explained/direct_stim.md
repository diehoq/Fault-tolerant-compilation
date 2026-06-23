# `direct_stim.py`

`direct_stim.py` owns the sampling step for circuits that are already built.

For the first level-0 memory experiment, it compiles the Stim circuit, samples a
requested number of shots, and counts measurement result `1` as a memory
failure.

The circuit builder and the sampler are intentionally separate. That keeps the
physical circuit inspectable before any Monte Carlo aggregation happens.
