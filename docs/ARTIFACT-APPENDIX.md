# Artifact Appendix

## Claims supported

The artifact supports protocol-state invariants, complete finite checks over the documented toy domains, reachable durable-prefix crash safety, transcript-level one-server privacy checks, evidence classification, deterministic result regeneration, and encoding/parser rejection tests.

It does not empirically establish production throughput, production cryptographic strength, hardware durability, side-channel resistance, network anonymity, or external control-plane consensus.

## Exact entry points

```bash
python -m compileall -q .
python reviewer_symbolic_check.py
python run.py --pilot --out reproduced-pilot
python run.py --out reproduced
python validate.py --out validation-reproduced --transcripts reproduced/signed_transcripts.json
python verify.py results/full reproduced
python check_evidence.py --authorization inputs/authorized_signers.json --transcripts reproduced/signed_transcripts.json
python -m unittest discover -s tests -v
```

## Determinism rule

Scientific JSON/CSV/text outputs are required to agree byte-for-byte across independent runs.  Timing, resident-memory, and profiler files are measurements of a particular host and are excluded explicitly rather than normalized after the fact.

## Interpretation of exhaustive checks

Exhaustive small-domain enumeration is a model-conformance and regression argument.  It can expose algebraic, state-machine, serialization, and boundary errors within the enumerated domain.  It does not turn a toy field or toy group into production cryptography and does not replace the computational assumptions stated in the paper.
