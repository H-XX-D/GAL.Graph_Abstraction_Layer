# Mathematical Reasoning Guards

Use these tests to avoid fallacies before naming them.

## Argument Map

Represent an argument as:

```text
P = {p1, p2, ... pn}
W = warrants that connect premises to the conclusion
C = conclusion
E = evidence
U = utility or value considerations
```

An argument is acceptable only if:

```text
all key terms are stable
each premise is relevant to C
the inference rule is valid or probabilistically calibrated
uncertainty is represented honestly
known counterevidence is included
```

## Math Used To Support Or Refute Reasoning

Use this toolbox to choose the right formal check for the argument.

1. Propositional logic

Checks whether statements are true or false. Use it for `and`, `or`, `not`,
and `if...then` claims.

2. First-order logic

Adds variables, predicates, and quantifiers. Use it to express general claims
such as `for all x` or `there exists x`.

3. Rules of inference

Derive conclusions from premises. Core examples include modus ponens, modus
tollens, and hypothetical syllogism.

4. Truth tables

Test whether an argument is valid or a statement is always true. Use them to
check equivalence, contradiction, tautology, and invalid conditional forms.

5. Proof by contradiction

Assume the opposite, then show it leads to impossibility. Use it to support a
claim by eliminating alternatives or exposing inconsistent assumptions.

6. Counterexamples

Find one example that breaks a universal claim. Use counterexamples to refute
overbroad reasoning quickly.

7. Set theory

Reason about groups, membership, subsets, intersections, exclusions, and
relations. Use it for formal definitions and structured arguments about
categories.

8. Model theory

Check whether a statement is true in an interpretation or structure. Use it to
test whether a theory can actually be satisfied.

9. Proof theory

Study formal derivations from axioms. Use it to check what can be proven inside
a system and which rules are being assumed.

10. Computability theory

Study what can or cannot be decided by an algorithm. Use it to show limits of
mechanical reasoning or automated verification.

11. Category theory

Study abstract structure and relationships between structures. Use it for
high-level formal reasoning about mappings, composition, invariants, and
structure-preserving transformations.

## Deductive Validity

Use truth tables, natural deduction, or syllogistic distribution.

Valid forms:

```text
Modus ponens:      A -> B, A, therefore B
Modus tollens:     A -> B, not B, therefore not A
Disjunctive syllogism: A or B, not A, therefore B
```

Invalid common forms:

```text
Affirming the consequent: A -> B, B, therefore A
Denying the antecedent:   A -> B, not A, therefore not B
Inclusive disjunct error: A or B, A, therefore not B
```

Guardrail: if a conclusion is deductive, translate it into symbols before accepting it.

## Predicate And Definition Checks

For quantified claims, write the quantifier explicitly:

```text
all x: P(x) -> Q(x)
some x: P(x) and Q(x)
no x: P(x) and Q(x)
```

Guardrails:

- Do not switch from `some` to `all`.
- Do not distribute a group property to each member unless the predicate is distributive.
- Freeze definitions before evaluating evidence.
- Rename ambiguous terms as `term_1`, `term_2`, and so on until the argument is unambiguous.

## Bayesian Relevance

A premise supports a claim only when it changes the probability of the claim:

```text
support(E, C) = P(E | C) / P(E | not C)
```

Interpretation:

```text
support > 1: E supports C
support = 1: E is irrelevant to C
support < 1: E counts against C
```

Guardrails:

- Popularity, emotion, threats, ridicule, status, and tradition are not evidence unless they change this ratio through a defensible reliability model.
- Expert testimony counts only after adjusting for domain fit, independence, conflict of interest, and track record.
- Absence of evidence counts only when detection probability is high.

## Statistical Induction

For generalizations, require:

```text
population: who or what the conclusion covers
sample: how observations were selected
n: sample size
base rate: prior prevalence
interval: uncertainty range
effect size: magnitude, not just direction
selection rule: whether the pattern was chosen before seeing data
```

Guardrails:

- Anecdotes generate hypotheses; they do not establish prevalence.
- Post hoc patterns need held-out validation or multiple-comparison correction.
- Small samples require wider uncertainty and narrower conclusions.

## Causal Reasoning

For `A causes B`, require:

```text
temporal order: A before B
mechanism: how A changes B
counterfactual: B would differ if A were absent
confounders: C variables that affect both A and B
interventions or controls: data that separates A from rivals
```

A compact DAG check:

```text
C -> A
C -> B
A -> B
```

If `C` is unmeasured, correlation between `A` and `B` may be spurious.

## Decision Theory

For choices, evaluate future consequences:

```text
E[U(action)] = sum over outcomes P(outcome | action) * U(outcome)
```

Guardrails:

- Ignore sunk costs except as evidence about future cost or reliability.
- Compare feasible options, not a real option against a perfect fantasy.
- Treat threats, pity, and flattery as utility pressure, not truth evidence.
- Separate belief updates from preference updates.

## Consistency And Coherence

A defense set must be jointly satisfiable.

Check:

```text
not (A and not A)
not (claim_1 excludes claim_2 while both are asserted)
not (standard_before != standard_after without justification)
```

Guardrails:

- Kettle logic fails consistency.
- Moving the goalposts fails stable decision-rule checking.
- Ad hoc rescue fails when auxiliary assumptions add no independent predictions.

## Repair Templates

Use these replacements when a trap is found:

```text
Instead of attacking the speaker, evaluate this evidence: ...
Instead of a binary choice, the option set appears to be: ...
Instead of "A caused B", the current evidence supports: "A is associated with B, with these rival explanations: ..."
Instead of "everyone believes it", use: "independent qualified sources converge because ..."
Instead of "natural means good", add the missing normative premise: ...
Instead of "we already invested", compare future expected utility from here: ...
```

## Confidence Labels

Use calibrated labels:

```text
High: clear formal error or strong missing evidence
Medium: likely fallacy, but context could repair it
Low: possible issue; ask for clarification
```
