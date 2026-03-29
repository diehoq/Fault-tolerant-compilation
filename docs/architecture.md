# Repository Architecture for `concatenated_steane_memory`

## Purpose of this document

This document defines the repository structure and execution flow for a pedagogy-first Python project that studies memory-only error suppression in the concatenated Steane `[[7,1,3]]` code.

At this stage, this is an architecture document, not a claim that every historical detail of Steane-style or Gottesman-style fault tolerance has already been implemented. The goal is to choose a clean baseline that is:

- physically meaningful,
- inspectable,
- compatible with real Stim circuits,
- extensible toward noisier and more historically faithful protocols later.

## Design goals

The repository is organized around five teaching goals.

1. Make the Steane code itself explicit.
2. Separate mathematical objects from simulation machinery.
3. Make Stim usage visible instead of hiding it behind opaque wrappers.
4. Support both low-level literal simulations and higher-level scalable estimates.
5. Keep every modeling choice isolated so it can be swapped out later.

## Proposed repository tree

The project should use the following tree.

```text
concatenated_steane_memory/
├─ pyproject.toml
├─ README.md
├─ requirements.txt
├─ AGENTS.md
├─ src/
│  └─ concatenated_steane/
│     ├─ __init__.py
│     ├─ config.py
│     ├─ pauli.py
│     ├─ steane_code.py
│     ├─ syndromes.py
│     ├─ decoder.py
│     ├─ noise.py
│     ├─ circuits/
│     │  ├─ __init__.py
│     │  ├─ physical_memory.py
│     │  ├─ steane_ec.py
│     │  ├─ logical_memory_cycle.py
│     │  └─ concatenation.py
│     ├─ simulation/
│     │  ├─ __init__.py
│     │  ├─ direct_stim.py
│     │  ├─ effective_channel.py
│     │  ├─ observables.py
│     │  └─ monte_carlo.py
│     ├─ analysis/
│     │  ├─ __init__.py
│     │  ├─ suppression.py
│     │  ├─ thresholds.py
│     │  └─ plotting.py
│     └─ utils/
│        ├─ bitops.py
│        └─ rng.py
├─ tests/
│  ├─ test_steane_code.py
│  ├─ test_syndromes.py
│  ├─ test_decoder.py
│  ├─ test_noise.py
│  ├─ test_steane_ec.py
│  ├─ test_direct_stim.py
│  └─ test_effective_channel.py
├─ scripts/
│  ├─ run_level_scan.py
│  ├─ run_pseudothreshold.py
│  └─ inspect_single_cycle.py
└─ docs/
   ├─ architecture.md
   ├─ modeling_assumptions.md
   ├─ mathematics.md
   ├─ references.md
   ├─ full_walkthrough.md
   └─ explained/
      ├─ pauli.md
      ├─ steane_code.md
      ├─ syndromes.md
      ├─ decoder.md
      ├─ noise.md
      ├─ steane_ec.md
      ├─ concatenation.md
      └─ ...
```

## Why each major file exists

### Root files

- `pyproject.toml`: defines the package, Python version, test tooling, and entry points.
- `README.md`: gives the shortest project-level explanation for a new reader.
- `requirements.txt`: pins the first reproducible dependency set, including `stim`, `pytest`, `numpy`, `matplotlib`, and `pandas`.
- `AGENTS.md`: documents repository-specific working conventions for future automated or human contributors.

### Core mathematical modules

- `pauli.py`: defines a transparent Pauli representation, because almost every later module needs a common language for `I`, `X`, `Y`, and `Z`.
- `steane_code.py`: defines stabilizers, logical operators, CSS structure, and the classical Hamming-code connection.
- `syndromes.py`: computes syndrome bits from Pauli errors and stabilizer checks.
- `decoder.py`: maps syndromes to corrections. This starts with a simple lookup-table decoder for weight-1 errors.
- `noise.py`: defines physical memory noise models and translates them into either analytic or Stim-facing forms.

### Circuit-construction modules

- `circuits/physical_memory.py`: builds literal Stim circuits for unencoded memory experiments.
- `circuits/steane_ec.py`: builds the pieces needed for Steane-style syndrome extraction or its idealized surrogate in the MVP.
- `circuits/logical_memory_cycle.py`: assembles one full logical cycle: wait, apply noise, extract syndrome, decode, classify failure.
- `circuits/concatenation.py`: explains how a level-`L` block expands into seven level-`L-1` subblocks.

### Simulation modules

- `simulation/direct_stim.py`: runs low-level, literal Stim-based simulations.
- `simulation/effective_channel.py`: recursively promotes a lower-level logical channel into a higher-level effective channel.
- `simulation/observables.py`: defines how logical `X` and logical `Z` failures are detected and reported.
- `simulation/monte_carlo.py`: handles repeated sampling, aggregation, confidence estimates, and result containers.

### Analysis modules

- `analysis/suppression.py`: compares logical error rates across levels and computes suppression factors.
- `analysis/thresholds.py`: estimates pseudo-thresholds from crossings or level-comparison criteria.
- `analysis/plotting.py`: centralizes plotting so scripts stay small and readable.

### Utility modules

- `utils/bitops.py`: keeps small binary-linear-algebra helpers away from the physics-facing modules.
- `utils/rng.py`: provides reproducible random seeding rules for Monte Carlo runs.

### Tests

Each test file mirrors one conceptual module. This is deliberate: a reader should be able to open a source file and then immediately open the matching test to see the intended behavior.

### Scripts

- `run_level_scan.py`: sweeps physical error rate and concatenation level.
- `run_pseudothreshold.py`: estimates where encoding starts to help.
- `inspect_single_cycle.py`: prints or visualizes one cycle in a way that is useful for debugging and teaching.

### Documentation files

- `architecture.md`: this document.
- `modeling_assumptions.md`: records every major simplification and why it was chosen.
- `mathematics.md`: explains the code and decoder mathematically.
- `references.md`: tracks the specific literature and Stim references used.
- `full_walkthrough.md`: follows one experiment end to end.
- `docs/explained/*.md`: gives line-by-line file walkthroughs after the corresponding source files exist.

## Execution flow

The intended execution flow of the repository is:

1. Load a simulation configuration from `config.py`.
2. Use `steane_code.py`, `syndromes.py`, and `decoder.py` to define the code and its recovery logic.
3. Build either a physical-memory circuit or a level-1 logical-memory cycle.
4. Choose a backend:
   - direct Stim simulation for literal low-level experiments,
   - effective-channel recursion for scalable higher-level estimates.
5. Run Monte Carlo sampling.
6. Convert samples into physical or logical failure rates.
7. Aggregate results across physical noise values and concatenation levels.
8. Save CSV data and generate plots.

This flow deliberately separates “what the code is” from “how the experiment is run.” That separation makes the project easier to debug and easier to teach.

## The three candidate simulation strategies

The project needs two different virtues that pull in opposite directions:

- literal circuit inspectability,
- scalability to higher concatenation levels.

That is why the strategy decision matters early.

### Strategy 1: direct Stim circuit simulation

Build explicit Stim circuits for the encoded memory experiment, including memory noise, syndrome extraction primitives, and logical checks.

Advantages:

- Most literal and easiest to connect to physical circuit pictures.
- Best for teaching what one cycle actually contains.
- Makes Stim usage completely visible.

Disadvantages:

- Concatenation grows extremely quickly.
- A level-2 or level-3 direct implementation can become hard to inspect and expensive to sample.
- If the error-correction protocol is made more realistic, the circuit size grows even faster.

Best use:

- Level 0.
- Level 1.
- Small spot checks at level 2.

### Strategy 2: recursive effective logical channel

Estimate the logical channel of level `L-1`, then use that channel as the noise model seen by a level-`L` block.

Advantages:

- Scales far better than direct concatenated circuits.
- Matches the natural recursive structure of concatenated coding.
- Well suited to suppression studies and pseudo-threshold plots.

Disadvantages:

- Less literal physically.
- Risks hiding where logical correlations come from.
- Can quietly bake in approximations if the effective channel model is too simple.

Best use:

- Level 2 and above.
- Fast scans across many physical error rates.

### Strategy 3: hybrid

Use direct Stim simulation where the circuits are still readable and use effective-channel recursion where direct simulation becomes too expensive.

Advantages:

- Keeps the repository pedagogically grounded.
- Still reaches levels where suppression trends can be studied.
- Gives a built-in cross-check: low levels can be simulated both ways.

Disadvantages:

- Requires maintaining two backends.
- Requires extra care when comparing “literal” and “effective” results.

Best use:

- The overall repository architecture.

## Recommended baseline strategy

The recommended baseline is **Strategy 3: hybrid**.

More specifically:

- `L = 0`: use direct Stim simulation only.
- `L = 1`: use direct Stim simulation as the main pedagogical backend.
- `L = 2`: support both methods if feasible, with direct simulation used mainly for validation and small runs.
- `L = 3`: rely primarily on effective-channel recursion.

This recommendation is driven by the project’s dual goal. A pure recursive implementation would scale well but would teach less about the actual circuits. A pure direct implementation would be the most literal but would likely stall before the higher-level suppression study becomes useful. The hybrid approach preserves both tractability and transparency.

## Recommended MVP scope

The first implementation milestone should target the following:

- one logical qubit,
- memory-only noise,
- stochastic Pauli noise only,
- separate reporting of logical `X` and logical `Z` failures,
- Steane `[[7,1,3]]` code only,
- level `0` and level `1` direct simulations first,
- recursive effective-channel support after level `1` works,
- level `2` and `3` estimates produced with the recursive backend once validated.

This is intentionally narrower than “full fault-tolerant computation.” The repository is about understanding memory protection first.

## Architecture choices that are intentionally isolated

Several design choices are separated into their own modules so that later versions can become more realistic without a rewrite.

- Noise model isolation: `noise.py` should be swappable without rewriting the decoder.
- Decoder isolation: `decoder.py` should be replaceable by a more sophisticated decoder later.
- Circuit isolation: `circuits/steane_ec.py` should be where ancilla verification or noisier extraction is added later.
- Backend isolation: `simulation/direct_stim.py` and `simulation/effective_channel.py` should agree on result formats, not on implementation details.

These boundaries are not accidental. They are the main mechanism that keeps the MVP simple without trapping the project in its first approximation.

## What this architecture is faithful to

The planned architecture is faithful to the following broad ideas from standard Steane-code and concatenated-code practice:

- The Steane code is treated as a CSS code derived from the classical Hamming structure.
- Error correction is decomposed into `X`-type and `Z`-type syndrome handling.
- Higher concatenation levels are built recursively from lower ones.
- Logical suppression is studied by comparing per-cycle logical failure against underlying physical noise.

## What this architecture does not yet claim

This repository architecture does **not** by itself claim exact historical fidelity to any specific Gottesman protocol. In particular, exact fidelity would depend on detailed choices about:

- ancilla preparation and verification,
- noise placement on gates, measurements, and idle periods,
- whether corrections are applied physically or tracked in a Pauli frame,
- how repeated syndrome rounds are scheduled,
- how malignant sets or correlated faults are treated.

Those details are deferred to `docs/modeling_assumptions.md` and later implementation phases.

## Immediate next implementation phases

After this architecture document, the recommended order of implementation is:

1. Foundations: Pauli representation, Steane code structure, syndromes, decoder.
2. Physical Stim memory: level-0 unencoded memory simulation.
3. Level-1 encoded memory: one memory round with Steane-style error correction under the chosen MVP assumptions.
4. Recursive promotion: effective-channel estimation for higher levels.
5. Experiment scripts and plots.

This order front-loads conceptual clarity and testability before circuit complexity.
