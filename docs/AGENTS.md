Your job is to build a pedagogy-first Python repository that simulates memory-only error suppression in the concatenated Steane 
[
[
7
,
1
,
3
]
]
[[7,1,3]] code using Steane error correction at each level, with real Stim integration, and with documentation detailed enough that I can understand the implementation line by line.

You are not just writing code. You are also building a repository that teaches me how the code works.

Core objective

Create a Python codebase that estimates logical memory error rates versus physical noise rate and concatenation level for a concatenated Steane-code memory experiment.

The codebase must support:

Steane 
[
[
7
,
1
,
3
]
]
[[7,1,3]] code representation,
syndrome extraction using Steane error correction,
memory-only simulation,
logical error estimation at levels 
𝐿
=
0
,
1
,
2
,
3
L=0,1,2,3 if feasible,
level-by-level noise suppression analysis,
real Stim circuit generation and sampling,
extensive explanation of every important line and design choice.
Important interpretation rule

The phrase “as done by Gottesman” is historically meaningful but potentially ambiguous.

You must therefore:

identify the exact modeling choices that are ambiguous,
choose a clean baseline implementation,
document what is faithful to standard Steane / concatenated-FT ideas,
document what is simplified,
isolate those choices so the project can later be made more historically faithful.

Do not claim exact fidelity to a specific Gottesman protocol unless the implementation really matches a cited protocol.

Working style

You must work in small, inspectable steps.

For every substantial step:

explain what you are about to build,
explain why this piece matters,
implement it,
explain the implementation line by line,
add tests,
run tests,
summarize what is verified and what remains uncertain.

Do not dump a huge codebase all at once.

Required behavior
1. Be explicit, not clever
Prefer simple, transparent code over compact code.
Avoid hidden abstractions.
Avoid “magic” helpers unless they are fully explained.
Use type hints throughout.
Put top-level docstrings on every nontrivial module.
Put docstrings on every class and nontrivial function.
2. Teach aggressively

Assume I want to maintain and extend the project myself.

That means:

explain notation,
define acronyms the first time they appear,
explain why each file exists,
explain why each test exists,
explain what each result means physically,
explain where Stim is exact and where we are doing Monte Carlo estimation.
3. Never hide assumptions

Whenever a modeling choice is required, state it explicitly.

Examples:

phenomenological memory noise vs full circuit-level noise,
ideal EC vs noisy EC,
verified ancillas vs unverified ancillas,
correction applied physically vs Pauli-frame tracking,
per-cycle failure probability vs lifetime,
direct simulation vs recursive effective-channel approximation.

If uncertain, give 2–3 options with pros/cons, pick one, and document it.

4. Use real Stim

Use the actual Python stim package.

At minimum:

generate Stim circuits,
insert Pauli-compatible noise,
sample outcomes or detector-related data where appropriate,
expose clean interfaces for future extensions.

Do not fake Stim integration.

5. Be honest about technical limits

If something is difficult, expensive, or only approximately representable in Stim, say so clearly.

Examples:

non-Clifford coherent noise,
fully faithful ancilla-verification protocols,
rapidly growing direct concatenated circuits.
Baseline modeling target

Start with an MVP that is simple, defensible, and extensible.

Baseline MVP assumptions
one logical qubit,
memory-only simulation,
repeated rounds of:
memory noise,
Steane EC,
logical failure classification,
independent single-qubit Pauli memory noise,
separate tracking of logical X and logical Z failures,
level 
0
0 = physical qubit,
level 
1
1 = Steane encoded block,
higher levels via recursive composition,
first decoder = lookup-table minimum-weight decoder for the 7-qubit code.
Important baseline simplification

For the first working version, it is acceptable to begin with one of these approaches:

Option A: idealized EC map

use Stim for noisy memory evolution,
model EC ideally at first,
then extend to noisy EC.

Option B: minimally noisy Steane EC

include noisy memory plus noisy syndrome extraction,
but omit ancilla verification initially.

You must compare these options and recommend one MVP.

Simulation architecture requirement

You must evaluate and compare these architecture choices before implementing:

Strategy 1: direct Stim circuit simulation

Construct explicit circuits for:

encoded preparation,
memory noise,
Steane EC,
logical observable checks.

Pros:

more literal,
easier to inspect physically.

Cons:

scales badly with concatenation level.
Strategy 2: recursive effective logical channel

Estimate level-
𝐿
L logical noise from level-
𝐿
−
1
L−1, then reuse that as an effective channel.

Pros:

scalable,
well-suited to suppression studies.

Cons:

less literal,
can hide circuit details.
Strategy 3: hybrid

Use direct Stim at low levels, effective-channel recursion at higher levels.

You must recommend one baseline strategy and justify it.

Required repository layout

Use this structure unless you have a compelling reason to adjust it:

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
Required conceptual modules
A. Steane code representation

Implement:

stabilizer generators,
logical 
𝑋
𝐿
X
L
	​

 and 
𝑍
𝐿
Z
L
	​

,
CSS structure,
Hamming-code parity relations,
syndrome computation,
correctable error representatives.

Explain exactly how the classical 
[
7
,
4
,
3
]
[7,4,3] Hamming structure produces the Steane CSS code.

B. Decoder

Implement:

a transparent lookup-table decoder for weight-1 errors first,
clear syndrome-to-correction mapping,
explicit tests over all single-qubit X, Y, Z errors.

Explain the difference between:

error,
correction,
recovery up to stabilizers.
C. Noise model

Implement:

configurable Pauli memory noise,
optional placeholders for gate and measurement noise,
translation of model assumptions into actual Stim operations.

Explain where noise is inserted and why.

D. Steane error correction

Implement an explicit Steane-EC module.

Explain:

what X and Z syndrome extraction are doing,
where 
∣
0
⟩
𝐿
∣0⟩
L
	​

 and 
∣
+
⟩
𝐿
∣+⟩
L
	​

 ancillas conceptually enter,
what is idealized in the first version,
where ancilla verification would be added later.
E. Concatenation

Implement recursive level handling.

Be explicit about:

what a level-
𝐿
L encoded qubit means,
how a level-
𝐿
L memory cycle expands into level-
𝐿
−
1
L−1 operations,
how logical failure is determined at each level.
F. Simulation backends

Provide, if feasible:

direct Stim backend for small levels,
effective-channel recursion backend for higher levels.

Explain when to use each.

Required development phases
Phase 1: foundations

Build first:

pauli.py
steane_code.py
syndromes.py
decoder.py

Add tests that verify:

stabilizer commutation,
logical operator commutation/anticommutation,
all weight-1 X/Y/Z errors are correctly decoded.

Also create explanatory docs for each file.

Phase 2: physical memory in Stim

Build a simple physical memory simulator using Stim.

Show:

circuit construction,
noise insertion,
sampling,
estimation of raw physical error rates.

Explain every Stim API call.

Phase 3: level-1 encoded memory

Build:

encoded state preparation,
one memory round,
Steane EC,
decoding,
logical failure classification.

Start with the simplest defensible implementation and label simplifications clearly.

Phase 4: concatenation

Add recursive levels and compare:

direct low-level simulation,
effective-channel recursion.

Document computational scaling and limitations.

Phase 5: experiments

Add scripts that produce:

logical error rate vs physical error rate,
curves for levels 0, 1, 2, 3 where feasible,
suppression factors,
pseudo-threshold estimates.

Save raw data as CSV and plots as PNG/PDF.

Required docs

Create these documents:

docs/architecture.md

Must explain:

repository structure,
execution flow,
why each major module exists,
direct vs recursive strategy comparison.
docs/modeling_assumptions.md

Must explain:

noise assumptions,
EC assumptions,
decoding assumptions,
what is faithful to standard Steane/Gottesman ideas,
what is simplified.
docs/mathematics.md

Must explain:

the Steane code as a CSS code,
parity-check matrices,
stabilizers,
logical operators,
decoding,
concatenation,
logical channels,
pseudo-thresholds,
why memory-only is simpler than full FT computation.
docs/full_walkthrough.md

Must explain the full execution path:

config,
circuit generation,
noise insertion,
simulation,
decoding,
logical failure classification,
aggregation,
plotting.
docs/explained/*.md

For each major source file, write a line-by-line walkthrough.

Required testing standards

Use pytest.

At minimum, include tests that verify:

all 21 single-qubit X/Y/Z errors on a Steane block are handled correctly,
syndrome computation is consistent,
decoder corrections clear the syndrome,
logical operators have the right commutation relations,
level-0 Stim simulation matches expected physical error behavior within Monte Carlo tolerance,
level-1 logical error is lower than level-0 physical error in a sufficiently low-noise regime,
effective-channel estimates are reasonably consistent with direct simulation where both are feasible.
Required output style while working

Whenever you respond during implementation, structure the response as:

What we are building now
Why it matters
The code
Line-by-line explanation
Tests and results
Active assumptions
Remaining gaps

Do not skip the line-by-line explanation.

Definition of done

The project is done when all of the following exist:

working Python package,
real Stim integration,
passing tests,
reproducible experiment scripts,
plots for suppression vs level,
clear documentation,
line-by-line explanations for major files,
honest accounting of simplifications,
a final walkthrough that lets me trace the full execution path.
First task only

Do only the following first:

write docs/architecture.md,
write docs/modeling_assumptions.md,
propose the repository tree,
compare the simulation strategies,
recommend a baseline MVP,
then stop and wait.

Do not write implementation code yet.