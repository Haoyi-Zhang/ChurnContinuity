# Proof arguments for continuity certificates

This file states the mathematical claims implemented or exercised by the
artifact.  It is written proof, not a proof-assistant development.  The
executable checks cover finite domains and selected crash boundaries; they do
not replace the general arguments below.

## 1. Objects and assumptions

Let `F` be a prime field and let the recommendation state be a vector
`x in F^m`.  A three-component replicated additive sharing is

```
x = z_0 + z_1 + z_2.
```

Physical server `S_i` stores the two components `z_j` with `j != i`.  Thus each
component has two physical holders, while any one server sees two uniformly
random components.  The artifact instantiates `F = F_1019`; the exact privacy
oracle uses `F_5`.

A vector Pedersen commitment has the form

```
Com(z; rho) = h^rho * product_i g_i^(z[i]).
```

The general claims assume a prime-order group, independently derived
generators with unknown discrete-log relations, computational binding, and
perfect hiding.  The code uses the tiny safe-prime group `(p,q)=(2039,1019)` so
that structural checks are inexpensive.  That group is not a production
security parameter and the artifact does not infer cryptographic security from
its finite executions.

An old certified generation supplies commitments
`C_i = Com(z_i; rho_i)` and an authenticated context containing the service,
epoch, exact cut root, ordered old and new membership, replaced slot, session,
generation, vector dimension, and arithmetic domain.  The control plane is
assumed to authorize the ordered memberships and to activate at most one
certificate per epoch.  Stable request identifiers and the cut root are handled
by the durable admission ledger in `src/churn/model.py`.

The protocol replaces exactly one physical slot at a time.  Let the replaced
slot be `k`, and let `a=(k+1) mod 3` and `b=(k+2) mod 3`.  Survivor `S_a` stores
`z_k,z_b`; survivor `S_b` stores `z_k,z_a`.

Honest-server rules are:

1. Persist a session's random mask and signed outbox entry before first send.
2. On retry, reuse the same session-bound mask and signed statement.
3. Verify each received opening against its signed commitment and full context.
4. Persist a component opening before signing a `PERSIST_RECEIPT`.
5. Never sign two different roots for the same statement context.

The safety theorem tolerates at most one Byzantine or unavailable server in the
new three-server committee.  Liveness additionally requires both survivors and
the replacement eventually to execute their steps; silence in a fully
asynchronous execution is not publicly blameable.

## 2. One-slot resharing protocol

Survivor `S_b` samples a uniform vector `delta_a` and scalar `tau_a`, commits

```
D_a = Com(delta_a; tau_a),
```

and survivor `S_a` independently samples `delta_b,tau_b` and commits
`D_b = Com(delta_b;tau_b)`.  The refreshed components and openings are

```
z'_a   = z_a + delta_a,      rho'_a = rho_a + tau_a,
z'_b   = z_b + delta_b,      rho'_b = rho_b + tau_b,
z'_k   = z_k-delta_a-delta_b,rho'_k = rho_k-tau_a-tau_b.
```

There are four authenticated private envelopes.  Survivor `S_b` sends
`(delta_a,tau_a)` to `S_a`, and `S_a` sends `(delta_b,tau_b)` to `S_b`, so both
survivors can derive the common component `z'_k`.  Each survivor also sends the
replacement a distinct envelope that binds its random-mask opening to the
corresponding refreshed component opening: `S_b` delivers `(delta_a,tau_a,
 z'_a,rho'_a)`, and `S_a` delivers `(delta_b,tau_b,z'_b,rho'_b)`.  The receiver
checks the full context, signer, recipient, target component, mask commitment,
component commitment, and both openings before persistence.  Thus the
replacement obtains `z'_a,z'_b` only through authenticated protocol messages,
not from a fixture or an unauthenticated side channel.  The survivors retain
`z'_a,z'_k` and `z'_b,z'_k`, respectively, so the new physical layout remains
“server `i` stores every component except `i`.”  No protocol message gives one
server all three components.

The public continuity equations are

```
C'_a = C_a * D_a,
C'_b = C_b * D_b,
C'_k = C_k / (D_a * D_b).
```

A continuity certificate contains the full context, the three old and three new
commitments, the two mask commitments, two survivor signatures on the mask
commitments, and six persistence receipts: one from each of the two physical
holders of every new component.  The public certificate does not contain the
state vectors or their openings.

## 3. Algebraic continuity

**Lemma 1 (sharing correctness).** The refreshed components reconstruct the
same vector as the old components.

**Proof.** Coordinate-wise in `F`,

```
z'_k+z'_a+z'_b
 = z_k-delta_a-delta_b + z_a+delta_a + z_b+delta_b
 = z_k+z_a+z_b = x.
```

The same cancellation holds for vectors because addition is coordinate-wise.
QED.

**Lemma 2 (commitment equations).** Honest openings satisfy all three public
continuity equations.

**Proof.** Vector Pedersen commitments are additively homomorphic in both the
message vector and blinding scalar.  Hence
`Com(z_a+delta_a;rho_a+tau_a)=C_a D_a`, similarly for `b`, and
`Com(z_k-delta_a-delta_b;rho_k-tau_a-tau_b)=C_k/(D_a D_b)`. QED.

**Theorem 1 (receipt-backed certificate continuity).** Let certified openings of
the old commitment triple sum to `x`.  Suppose a continuity certificate
verifies, at most one new server is Byzantine or unavailable, honest receipts
are issued only after verifying and persisting the named opening, signatures are
unforgeable, and the vector commitment is binding.  Then the openings held by
honest new holders sum to `x`, except with cryptographic failure probability.

**Proof.** Verification fixes one full context, authenticates the two mask
commitments, and checks all three equations.  Multiplying the equations cancels
the masks and gives `C'_0 C'_1 C'_2 = C_0 C_1 C_2`.  Every new component has
receipts from both physical holders.  At most one server can be faulty, so at
least one receipt for each component is honest and supplies a verified durable
opening `(z'_i,rho'_i)` of `C'_i`.  Let `x'=z'_0+z'_1+z'_2`.  The common product
commitment has an old opening to `x` and a new opening to `x'`.  If `x' != x`,
this violates binding. QED.

The public equations alone prove only a product-commitment relation.  The
semantic state theorem additionally uses certified old openings and the honest
persist-after-verify receipt premise.  It does not show that an arbitrary base
triple encodes the correct application state; the base generation must be tied
to the sealed admission cut.

## 4. Durable availability after activation

**Lemma 3 (two-holder coverage).** In a valid certificate, each component index
appears in exactly two authenticated persistence receipts, signed by the two
new physical servers whose slot is different from that component index.

**Proof.** The verifier constructs the six-element expected set from the
ordered membership and rejects missing, duplicate, foreign, wrong-component,
wrong-commitment, wrong-generation, or invalidly signed entries. QED.

**Theorem 2 (one-fault post-activation availability).** Suppose honest servers
sign a receipt only after durably storing a verified opening, and at most one
new server is Byzantine or unavailable after activation.  Every new component
has at least one available correct opening bound to the certificate.

**Proof.** By Lemma 3 each component has two distinct holders.  Removing at most
one physical server leaves at least one holder of each component.  If that
remaining holder is honest, its receipt implies durable storage and local
opening verification.  If the removed holder is honest, the other holder must
be the sole possibly Byzantine server; but then the honest removed server was
unavailable, contradicting the premise that at most one server is Byzantine or
unavailable in total.  Thus at least one available honest holder remains for
each component.  Commitment binding connects its opening to the certified
component. QED.

A single receipt per component cannot establish this property: the sole signer
may be the one unavailable server.  The artifact retains this as the
`single-receipt-per-component` ablation.  If two servers issue false receipts,
the theorem's one-fault premise is violated; public signatures alone do not
make dishonest storage durable.

## 5. Static one-server privacy

The privacy statement concerns only the sharing and continuity layer.  It does
not remove leakage from recommendation outputs, rating counts, timing, public
membership, epoch identifiers, activation decisions, or the application-level
cut root.

For a fixed secret vector `x`, sample `z_0,z_1` uniformly and set
`z_2=x-z_0-z_1`.  Any pair of components is uniform over `F^(2m)` and therefore
independent of `x`.

**Lemma 4 (survivor views).** The algebraic view of either survivor in one
replacement is independent of `x`.

**Proof.** A survivor initially holds a pair of components, which is uniform and
independent of `x`.  It additionally sees the two independent uniform masks,
its refreshed pair, and deterministic functions of these values.  The complete
view is therefore an efficiently computable function of variables whose joint
distribution is independent of `x`. QED.

**Lemma 5 (replacement view).** The algebraic view of the replacement is
independent of `x`.

**Proof.** The replacement sees `(z'_a,z'_b)` and the two masks needed to verify
its incoming openings.  The map

```
(z_a,z_b,delta_a,delta_b)
  <-> (z'_a,z'_b,delta_a,delta_b)
```

is a bijection.  Since `(z_a,z_b)` is a uniform pair independent of `x` and the
masks are independent uniform vectors, the replacement view is also independent
of `x`. QED.

**Theorem 3 (static one-server privacy, hybrid form).** Assume authenticated
private channels, perfectly hiding vector commitments, and signature security.
Fix one corrupted server identity.  For one transfer, or a bounded serial chain
with exact membership handoff, permanent identity-to-slot binding, fresh
contexts/sessions/generations, no identity re-entry, and no later honest state
delivered to a removed identity, the protocol view is simulatable from the
declared public leakage and the corrupted identity's current two-component
view.  For a fresh initial sharing, that view is independent of `x`.

**Proof.** For each transition in which the corrupted identity participates,
Lemmas 4 or 5 give an `x`-independent algebraic transition.  The simulator
samples the same independent masks, computes all deterministic local values,
and replaces commitments by commitments to zero using perfect hiding.  It uses
the standard signature-hybrid argument for honest statements.  Exact handoff
keeps one serial history, slot binding prevents the fixed identity from
accumulating views from different replicated roles, and no-reentry prevents a
removed identity from receiving later state.  Induction over the bounded chain
completes the simulation. QED.

The theorem explicitly excludes mobile corruptions that move to new identities
and accumulate erased state.  It also excludes collusion of two current
servers.  The executable `privacy_views.csv` enumerates all `5^4` algebraic
randomness assignments for every secret and each of the three server roles; it
checks equality of the exact view histograms.  That finite oracle validates the
small-domain algebra but does not prove the commitment or signature assumptions.

## 6. Exactly-once inclusion through churn

The durable admission ledger maps a stable request identifier `(client,seq)` to
one commitment and one receipt index.  Repeating the same identifier and
commitment returns the original receipt; changing the commitment is rejected.
A sealed epoch stores an immutable snapshot of all admitted bindings up to its
cut.  New seals have strictly increasing epoch numbers and nondecreasing cuts.

**Lemma 6 (stable admission).** Each stable identifier occurs at most once in a
sealed epoch snapshot, and retries cannot change its commitment.

**Proof.** The ledger dictionary has one entry per identifier.  The admission
transition either returns the existing receipt after equality checking or
inserts one new entry.  Sealing copies the dictionary into an immutable sorted
tuple. QED.

**Lemma 7 (monotone snapshots).** If epoch `e'` is sealed after epoch `e`, then
the identifier/commitment set in `e` is a subset of that in `e'`.

**Proof.** Admission only adds entries and cannot alter existing entries.  A
later seal copies the resulting dictionary. QED.

**Theorem 4 (exactly-once continuity).** Assume the initial certified sharing of
epoch `e` encodes exactly the state obtained from its sealed stable-ID snapshot.
Every bounded sequence of valid continuity certificates with exact commitment
and membership handoff, invariant service/epoch/cut/dimension/domain, and fresh
context/session/generation identifiers preserves that state, and therefore
preserves exactly-once inclusion for all identifiers in the cut.

**Proof.** Lemma 6 establishes exactly-once membership in the base snapshot.
The base-generation assumption ties the initial committed vector to that
snapshot.  Theorem 1 preserves the committed vector across one replacement.
Induction over the certificate chain preserves it across any bounded number of
replacements. QED.

This theorem does not claim that a recommender's entire training algorithm is
verified.  It protects the epoch state vector whose construction is bound to
the sealed cut; application-specific computation still needs its own proof or
trusted implementation boundary.

## 7. Crash-safe retries and activation

A session identifier is part of every signed statement and commitment context.
An honest sender persists its sampled mask and signed outbox before first send.
An honest recipient first authenticates and verifies its private envelope,
then persists the verified component opening before issuing its receipt.  The
reference `DurableServer.issue_receipt` operation refuses to sign unless the
matching durable opening already exists.  Re-executing a persisted transition
is idempotent; a conflicting
value for the same durable key is rejected.  Activation accepts one full
certificate and does not select “latest” local state.

**Theorem 5 (crash safety).** Under crash-stop failures that preserve the
modeled durable dictionaries, any execution that activates a full certificate
has the same committed state as a failure-free execution.  A finite replay of
all durable session messages completes the protocol once all three new servers
resume.

**Proof.** A crash removes only volatile state.  Persisted sender masks and
outboxes fix every retried proposal and opening.  Persisted component slots are
immutable.  A receipt can exist only after its component slot exists, so an
activated certificate names six durable copies.  Replays either reproduce the
same entry or are rejected as conflicts; they cannot create a second value for
one context key.  The public equations then give continuity by Theorem 1.  If
all servers resume, replay visits the finite list of missing idempotent steps and
produces all receipts. QED.

The theorem is not a hardware `fsync` measurement, a consensus proof, or a
bound on asynchronous completion time.  Durable media loss is a different
fault.  A permanently silent required participant prevents completion.

The artifact executes 20 crash boundaries covering two persisted survivor
masks, six signed sender-outbox records, six verified component copies, and six
individual receipt records.  Fresh server objects begin with none of these
facts.  Each nonempty prefix is crashed and replayed from durable state.  These
checks exercise every persistence boundary in the fixed step list; they are not
exhaustive over arbitrary network schedules.

## 8. Positive accountability and its boundary

A signed mask commitment names the full transfer context and target component.
A signed private mask opening names the same context, intended recipient,
vector, blinding, and commitment.

**Proposition 1 (invalid-opening evidence).** Under signature unforgeability and
authentic authorization, a valid signature on a mask opening that fails the
public commitment equation proves that the named signer emitted a statement
violating the opening contract, or a cryptographic premise failed.

**Proof.** The verifier first authenticates the exact encoded statement under
an independently supplied authorized key.  It then recomputes the commitment.
If the equation fails, the signed vector/blinding pair is not an opening of the
signed root.  Injective encoding prevents interpreting the same signature as a
different permitted statement. QED.

The disclosed object is a uniformly random resharing mask, not an application
state component.  One such witness is independent of `x`.  Repeated evidence
under mobile corruptions or implementation-dependent auxiliary leakage is not
analyzed.

**Proposition 2 (equivocation evidence).** Two valid signatures by one signer on
different mask roots for the same full context and target component prove a
violation of the single-root signing rule, or a signature/authorization premise
failed.

**Proof.** The two roots produce distinct canonical messages.  If both
signatures are authentic, either the signer emitted both messages or one is a
forgery.  Context equality rules out legitimate retries or different sessions.
QED.

**Proposition 3 (silence impossibility).** In a fully asynchronous network, no
finite public transcript can both always blame a nonresponding participant and
never blame an honest participant whose message is merely delayed.

**Proof.** Consider a finite prefix with no response.  One execution has a
silent faulty participant; an indistinguishable execution has an honest
response delivered after the prefix.  Any detector makes the same decision on
both prefixes. QED.

Consequently, the protocol offers positive evidence for malformed signed
openings and equivocation, not complete attribution for omission faults.

## 9. Mixed-generation necessity and negative controls

The earlier algebraic study is retained because activation must bind every
component to one generation.  For a linear decoder `L` and two valid encodings
`u` and `v` of the same state, a selector `P` that mixes coordinates reconstructs
correctly exactly when

```
L(Pu + (I-P)v) = x,
```

or equivalently `L P (u-v)=0`.  Equality of logical content does not imply this
kernel condition.  In minimal three-component additive sharing over a field, a
fixed non-homogeneous selector has a uniformly distributed reconstruction
error.  Over a cyclic ring the error is uniform on the image ideal of the
relevant coefficient.  A decomposable encoding can admit non-homogeneous
cancellation, so universal “all linear schemes require one generation” is
false; the exact kernel criterion is the general statement.

The artifact retains three continuity ablations:

1. **No algebraic link.** All statements can be freshly signed around a changed
   commitment vector.  A verifier that skips the three homomorphic equations
   accepts; the full verifier rejects.
2. **No receipt-generation check.** Authenticated receipts carrying another
   generation label become reusable; the full verifier rejects them.
3. **One receipt per component.** A weak availability certificate can lose its
   only holder; the full two-holder certificate rejects the reduced set.

These are controlled counterexamples to weakened verifiers, not attacks on an
external system.

## 10. Certificate size

For fixed three-server membership and a fixed signature/commitment scheme, the
public certificate contains eight group elements (three old commitments, three
new commitments, and two mask commitments) and eight signatures (two proposals
and six receipts), plus bounded context labels.  Its asymptotic size is
`O(lambda + |context|)` and is independent of the number `m` of state scalars.
Private openings and durable component storage are `Theta(m)`.

The JSON reference encoding measures 3,708--3,717 bytes for dimensions
1, 8, 32, and 64.  The variation is decimal/JSON representation noise, not an
asymptotic trend.  The combined four authenticated private envelopes grow from
1,630 bytes at dimension 1 to 3,130 bytes at dimension 64.  The two
replacement-directed envelopes contain both a mask opening and a refreshed
component opening; the two peer-survivor envelopes contain only a mask opening.
These are encoding
measurements, not network throughput or production latency results.

## 11. Composition boundary

The completed construction is a continuity layer for prime-field replicated
sharing.  It is not a drop-in implementation of Nudge's arithmetic over
`Z_(2^b)`.  Applying the same design to that ring requires a hiding, binding,
linearly homomorphic commitment or proof system for the ring relation and a new
security argument.  The artifact does not claim such an instantiation.

The construction also assumes an authenticated activation service, authorized
membership changes, private channels, durable honest signing state, and a
certified base generation.  It does not implement Byzantine consensus,
recommendation training, erasure against mobile corruption, two-server privacy,
or liveness with a silent survivor.  These are explicit non-claims rather than
implicit guarantees.
