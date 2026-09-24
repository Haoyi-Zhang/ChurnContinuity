# Assumptions, interfaces, and evidence map

| Object | Implemented | Assumed or excluded |
|---|---|---|
| Stable request admission | `Ledger.admit`: stable ID, immutable commitment, idempotent retry | Client authentication; indefinite identifier retention |
| Epoch cut | Immutable snapshot, increasing epoch numbers and nondecreasing contents | Consensus and authorization for the cut root |
| Replicated sharing | Three additive vectors; server `i` stores components `j != i` | Prime-field application state encoding |
| One-slot transfer | Two survivor masks, two peer mask openings, two replacement mask+component deliveries, refreshed physical holdings, no reconstruction | Confidential authenticated private channels; authorized one-slot membership change |
| Vector commitments | Homomorphic toy vector-Pedersen equations | Large secure group, unknown generator relations, binding assumption |
| Public certificate | 3 old + 3 new + 2 mask commitments; 2 proposals + 6 receipts | Public-key infrastructure and activation-log consensus |
| Durability | Immutable dictionaries unaffected by the explicit crash transition; `issue_receipt` requires a matching durable component first | Real `fsync`, media loss, rollback-resistant signing hardware |
| Crash replay | Session-bound deterministic outboxes and idempotent writes | Eventually resuming participants and message delivery |
| Static privacy | Exact `F_5` view distributions; written hybrid proof | No mobile corruption, no two-server collusion, declared metadata leakage |
| Positive blame | Invalid signed random-mask opening; same-context equivocation | No complete blame for silence or unverifiable private behavior |
| Nudge integration | Threat-model and 2-of-3 layout used as motivation | No `Z_(2^b)` commitment instantiation; no recommendation engine patch |

## Certificate acceptance predicate

The verifier accepts only when all of the following hold:

1. The context hash recomputes from the service, epoch, cut root, ordered old and
   new membership, replaced slot, session, generation, dimension, and arithmetic
   domain.
2. Exactly one declared physical slot changes.
3. The two mask commitments are signed by the two correct survivors and target
   the correct refreshed components.
4. The three homomorphic equations connect the old and new component
   commitments.
5. Exactly six unique persistence receipts are present: the two physical holders
   of every component, for the same context, generation, and commitment.
6. Every signature verifies under a separately supplied authorized key.

Test-only switches in `verify_certificate` omit one predicate at a time solely
for negative controls.  The protocol verifier uses all checks.

## Private-delivery acceptance predicate

A recipient accepts a private envelope only when all of the following hold:

1. The Ed25519 signature verifies for the survivor assigned to the target
   component, and the statement carries the exact transfer context identifier.
2. The recipient is the unique peer survivor for `MASK_OPENING`, or the unique
   replacement identity for `MASK_COMPONENT_OPENING`; the two schemas are not
   interchangeable.
3. The mask opening recomputes the public mask commitment.
4. A replacement-directed envelope names the same target component and its
   component opening recomputes the corresponding new public commitment.
5. Only after these checks may the recipient persist the opening.  A persistence
   receipt is unavailable until that durable record exists.

The private component opening is deliberately not copied into the public
certificate or into the public blame sample.  A signed invalid *mask* opening
can be disclosed because the mask is independent of the application state; no
claim is made that disclosing a refreshed component opening is privacy-safe.

## Frozen finite domains

- Mixed-generation replicated and Shamir checks: `F_5` main domain, `F_3` pilot.
- Cyclic-ring image controls: moduli 4, 8, and 16.
- Legacy schedule/fault cases: 968.
- Physical continuity cases: 31, bringing the total to the frozen bound of 999.
- Exact privacy oracle: `5^4` randomness assignments for each of five secrets
  and three server roles, or 9,375 view obligations.
- Certificate-size points: vector dimensions 1, 8, 32, and 64.

The privacy oracle excludes commitments and signatures from enumeration.  The
written proof treats commitments through perfect hiding and signatures through
standard post-processing/hybrid reasoning.

## Selection and negative-control rules

The legacy A/B fixture differs by component deltas `(1,2,-3)` modulo 101 in
every coordinate.  Every nonempty proper subset has nonzero sum, so every mixed
latest-state selection is wrong while either homogeneous generation is correct.
This is a falsification fixture, not a random workload.

The continuity mutations are fixed by class rather than selected after seeing
results: changed new commitment, changed mask commitment, proposal signature
bit flip, missing receipt, signer substitution, component substitution, context
epoch substitution, and changed old commitment.  The three ablations remove
algebraic linkage, receipt-generation binding, or the second physical receipt.
All are benign local transformations of synthetic material.

## Evidence privacy

The continuity blame sample exposes only a signed random resharing mask and its
blinding.  The mask is independent of the shared recommendation vector.  The
older generic contradiction corpus can expose opaque root strings only.  The
artifact does not claim that arbitrary diagnostic transcripts are safe to
publish, nor that repeated disclosures remain private under mobile corruption.
