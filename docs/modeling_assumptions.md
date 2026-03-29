# Modeling Assumptions for the Steane Memory Project

## Purpose of this document

This document records the modeling decisions behind the first version of the repository. Its main purpose is honesty. Concatenated Steane-code memory simulations can be defined in several defensible ways, and the phrase “as done by Gottesman” is too ambiguous to use without further qualification.

For that reason, this document distinguishes among:

- what is standard and faithful to textbook Steane or concatenated-code ideas,
- what is simplified for the MVP,
- what is deferred to later versions.

## The ambiguous choices we must make explicitly

Before implementing anything, the following choices must be fixed.

### 1. What kind of noise is being modeled?

Possible choices:

- phenomenological memory noise only,
- full circuit-level stochastic Pauli noise,
- coherent or non-Pauli noise.

Why this matters:

- Stim naturally supports stabilizer circuits with stochastic Pauli-compatible noise.
- Memory-only noise is much simpler to explain and much cheaper to simulate.
- Full circuit-level noise is more faithful to a full fault-tolerant protocol, but it requires many additional assumptions.

### 2. How realistic is error correction?

Possible choices:

- ideal error correction,
- minimally noisy Steane error correction,
- more realistic Steane error correction with ancilla verification.

Why this matters:

- Ideal error correction isolates the protective power of encoding from the added failure modes of the correction gadget.
- Noisy error correction is closer to a physical protocol, but it creates more moving parts and more room for hidden assumptions.
- Verified ancillas are historically important in many Steane-style fault-tolerance discussions, but they add major implementation complexity.

### 3. How are corrections represented?

Possible choices:

- apply corrections physically in the simulated circuit,
- track corrections in a Pauli frame.

Why this matters:

- Pauli-frame tracking is simpler and often more transparent for stabilizer simulations.
- Physical corrections are more literal, but they can clutter the circuit without changing the logical content.

### 4. What exactly counts as a failure?

Possible choices:

- per-cycle logical `X` and logical `Z` failure probabilities,
- total logical lifetime over many cycles,
- full logical Pauli-channel estimation.

Why this matters:

- Per-cycle failure is the cleanest quantity for suppression studies.
- Lifetime depends on how many cycles are run and how stopping rules are defined.
- A full logical channel is richer, but the MVP can begin by separately tracking logical `X` and logical `Z`.

### 5. How is concatenation simulated?

Possible choices:

- direct expansion into explicit lower-level circuits,
- recursive effective-channel approximation,
- a hybrid of the two.

Why this matters:

- Direct expansion is more literal.
- Effective channels scale better.
- The hybrid approach can use direct simulation to validate the effective approximation.

## Comparison of MVP candidates for error correction

The first major implementation fork is between two plausible MVPs.

### Option A: idealized error-correction map

Definition:

- Use Stim for the noisy memory evolution and other stabilizer-compatible circuit pieces.
- Model the Steane error-correction step as ideal syndrome extraction plus ideal recovery.
- Implement the recovery logic transparently in Python using the Steane decoder.

Strengths:

- Simplest path to a correct and inspectable first implementation.
- Keeps the core code, syndrome, and decoder logic front and center.
- Makes it easier to validate low-level behavior before adding noisy gadgets.
- Reduces the risk of building a large but poorly explained syndrome-extraction circuit too early.

Weaknesses:

- Not yet a fully noisy Steane-EC gadget.
- Can overestimate performance compared with a realistic fault-tolerant circuit.
- Does not answer detailed questions about ancilla preparation faults.

Pedagogical value:

- Very high.

### Option B: minimally noisy Steane error correction

Definition:

- Use Stim for memory noise and for an explicit syndrome-extraction circuit.
- Include noisy syndrome extraction, but initially omit ancilla verification.

Strengths:

- More literal than Option A.
- Closer to a circuit-level story from the start.
- Gives earlier visibility into how error correction itself can fail.

Weaknesses:

- Harder to keep clean and trustworthy in a first version.
- Introduces many extra assumptions at once: ancilla preparation method, gate scheduling, measurement noise placement, and fault propagation details.
- Risks obscuring the core coding ideas under protocol details.

Pedagogical value:

- Medium to high, but only if implemented very carefully.

## Recommended MVP for error correction

The recommended MVP is **Option A: idealized error-correction map**.

The reason is not that noisy Steane error correction is unimportant. The reason is that the first version of this repository is meant to teach, and the cleanest teaching path is:

1. define the Steane code,
2. define its syndromes,
3. define a transparent decoder,
4. show memory-noise suppression under ideal recovery,
5. then add noisy syndrome extraction as a controlled extension.

This sequence keeps the baseline understandable and makes later complexity additive instead of entangled.

## Baseline assumptions for the first implementation

The first implementation should adopt the following assumptions.

### Physical setting

- One logical qubit only.
- Memory-only experiment, not a computation with logical gates.
- Independent single-qubit Pauli memory noise.
- No coherent noise in the MVP.

Interpretation:

Each memory cycle consists of an idle period where stochastic Pauli faults may occur, followed by an error-correction step.

### Error-correction setting

- Use Steane-code syndrome logic.
- Start with ideal syndrome extraction and ideal recovery.
- Separate `X`-error decoding and `Z`-error decoding, consistent with the CSS structure.
- Track corrections in a Pauli frame unless a literal correction is pedagogically clearer in a specific module.

Interpretation:

The MVP teaches what the correction *means* without yet claiming that the full ancilla-based gadget has been simulated with all of its own noise sources.

### Decoder setting

- Start with a lookup-table decoder that corrects all weight-1 `X`, `Y`, and `Z` errors on a Steane block.
- Treat two errors that differ by a stabilizer as equivalent for recovery purposes.
- Make the syndrome-to-correction map explicit and inspectable.

Interpretation:

This is not a maximum-likelihood decoder for arbitrary noise. It is a transparent first decoder chosen because the Steane code is distance 3 and corrects all single-qubit Pauli errors.

### Failure metric

- Report logical `X` failure probability per cycle.
- Report logical `Z` failure probability per cycle.
- Optionally report joint logical `Y` failure events when both occur together.

Interpretation:

These are Monte Carlo estimates of per-cycle logical failure probabilities, not exact symbolic thresholds and not full logical lifetimes unless the experiment script explicitly studies repeated cycles.

### Concatenation setting

- Level `0` means an unencoded physical qubit.
- Level `1` means one Steane `[[7,1,3]]` block built from seven physical qubits.
- Level `L` means a Steane block whose seven subblocks are themselves level `L-1` encoded qubits.

Interpretation:

This recursive definition is standard for concatenated codes, but the simulation method may differ by level.

## Recommended baseline simulation strategy

The recommended baseline is:

- **Strategy 3: hybrid architecture**
- combined with
- **Option A: idealized error-correction map**

Concretely, that means:

- direct Stim simulation for level `0`,
- direct Stim-backed encoded simulations for level `1` wherever the circuits remain readable,
- recursive effective-channel promotion for higher levels,
- low-level cross-checks between the two methods wherever feasible.

This pairing is the best compromise between interpretability and scalability.

## What is faithful to standard Steane and concatenated-code ideas

The following aspects are faithful to standard textbook or broadly accepted constructions.

- The Steane code is treated as a CSS code built from the classical `[7,4,3]` Hamming code.
- `X` and `Z` syndromes are decoded separately.
- A distance-3 code corrects any single-qubit Pauli error.
- Concatenation is defined recursively.
- Logical suppression is assessed by comparing logical error rates across levels.

## What is simplified in the MVP

The following are deliberate simplifications.

- Memory-only noise instead of full circuit-level noise.
- Idealized error-correction map instead of a fully noisy Steane-EC gadget.
- No ancilla verification in the first version.
- Pauli-frame tracking instead of always applying physical corrections.
- Separate `X` and `Z` logical-failure reporting instead of a fully general correlated logical channel model.
- Effective-channel recursion at higher levels instead of literal direct circuits everywhere.

These simplifications are not bugs. They are the mechanism that makes the first version buildable and teachable.

## What is specifically *not* claimed about “Gottesman”

The repository should **not** claim that the MVP is an exact implementation of a specific Gottesman protocol unless later documentation pins down and implements the exact details. In particular, the MVP does not yet specify:

- which ancilla-verification routine is used,
- how many syndrome rounds are repeated before accepting a correction,
- which gate-level noise model is applied during syndrome extraction,
- whether postselection or verification rejection is modeled,
- whether correlated fault sets are analyzed in a historically faithful way.

A better wording for the MVP is:

> This repository studies a clean baseline concatenated-Steane memory model inspired by standard Steane-code and concatenated fault-tolerance ideas.

That wording is accurate without overclaiming.

## Role of Stim in the project

Stim is used because it is excellent for stabilizer-circuit simulation with stochastic Pauli noise.

What Stim gives us exactly:

- exact stabilizer evolution for Clifford circuits,
- exact handling of Pauli-compatible stochastic noise channels inside a sampled stabilizer simulation,
- fast sampling for Monte Carlo estimation.

What Stim does not give us automatically:

- exact treatment of coherent non-Clifford noise,
- automatic construction of historically faithful Steane ancilla factories,
- a guarantee that our chosen fault-tolerant protocol details match any specific paper.

So when we say “real Stim integration,” we mean the project uses actual Stim circuits and actual Stim sampling where appropriate. We do **not** mean that every conceptual step must already be encoded as one giant low-level Stim circuit in the first milestone.

## Known limitations of the baseline model

Even if implemented correctly, the MVP will still have limitations.

- It will study memory protection, not universal computation.
- It will estimate logical failure by Monte Carlo sampling, so small probabilities require many shots.
- It may miss correlations that would appear in a more detailed noisy error-correction gadget.
- It will give pseudo-threshold-style evidence, not a rigorous asymptotic threshold proof.

These limitations should be stated near every plot and experiment script.

## Planned upgrade path after the MVP

The natural sequence of extensions is:

1. Add explicit encoded-state preparation circuits for level `1`.
2. Add a minimally noisy Steane syndrome-extraction circuit.
3. Add optional measurement and gate noise.
4. Add ancilla-verification variants.
5. Refine the effective-channel model to preserve more correlation information.
6. Compare direct and recursive estimates more systematically.

This order preserves the core teaching value of the repository while steadily increasing realism.
