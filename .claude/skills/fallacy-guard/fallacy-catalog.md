# Logical Fallacy Catalog

Each guard is a compact mathematical or formal reasoning test to run before accepting the argument.

| # | Fallacy | Class | Reasoning trap | Mathematical guard |
|---:|---|---|---|---|
| 1 | Ad Hominem | Relevance | Attacks the person instead of the claim. | Define support as `P(evidence \| claim) / P(evidence \| not claim)`; personal traits are irrelevant unless they change reliability of the specific evidence. |
| 2 | Straw Man | Relevance | Attacks a weaker substitute for the real claim. | Require semantic equivalence: compare original claim `C` and attacked claim `C'`; reject if `C'` is not entailed by `C`. |
| 3 | Red Herring | Relevance | Introduces a distracting issue. | Maintain a claim-premise graph; every premise must have a path to the target conclusion through an explicit warrant. |
| 4 | Appeal to Pity | Relevance | Uses compassion as proof. | Separate utility from truth: suffering may affect action value `U(a)`, not truth probability `P(C)`, unless it supplies evidence. |
| 5 | Appeal to Force | Relevance | Uses threats instead of evidence. | Model threat as payoff pressure, not epistemic support; `threat -> cost`, not `threat -> truth`. |
| 6 | Appeal to Emotion | Relevance | Lets feeling replace evidence. | Require an evidential likelihood ratio; affective intensity is not support unless tied to measured outcomes. |
| 7 | Appeal to Popularity | Relevance | Treats consensus or popularity as proof. | Use independence-adjusted testimony: update only for independent, competent, non-correlated observers. |
| 8 | Appeal to Tradition | Relevance | Treats age or custom as truth. | Distinguish survival evidence from correctness; ask whether historical persistence predicts the target property after confounders. |
| 9 | Appeal to Novelty | Relevance | Treats newness as truth or superiority. | Compare measured performance distributions; novelty is a feature, not a proof of dominance. |
| 10 | Genetic Fallacy | Relevance | Judges a claim only by its origin. | Condition on source reliability only as evidence quality; still evaluate the claim's direct evidence. |
| 11 | Guilt by Association | Relevance | Transfers guilt through links. | Require causal or evidential dependency; association alone is not transitive guilt. |
| 12 | Tu Quoque | Relevance | Deflects criticism by alleging hypocrisy. | Test whether hypocrisy changes the proposition's truth value; usually it only affects speaker credibility. |
| 13 | Poisoning the Well | Relevance | Discredits a source before hearing the claim. | Use prior reliability as a weight, then evaluate evidence content; do not set evidence weight to zero without proof of unreliability. |
| 14 | Moral Equivalence | Relevance | Equates trivial and grave wrongs. | Compare harm magnitude, intent, scope, reversibility, and probability; require proportional metrics. |
| 15 | Begging the Question | Presumption | Hides the conclusion in a premise. | Build a dependency graph; reject cycles where conclusion `C` is required to justify a premise supporting `C`. |
| 16 | Circular Reasoning | Presumption | Loops back to itself as support. | Detect directed cycles with no independent evidence node. |
| 17 | False Dilemma | Presumption | Presents only two options when more exist. | Model option space `S`; require proof that `S = {A, B}` before using binary elimination. |
| 18 | Complex Question | Presumption | Embeds an accusation in a question. | Decompose into atomic propositions; answer only after each presupposition is independently established. |
| 19 | Slippery Slope | Presumption | Claims one step guarantees collapse. | Require transition probabilities `P(S_i -> S_{i+1})` and cumulative probability product across the chain. |
| 20 | Appeal to Ignorance | Presumption | Treats absence of disproof as proof. | Absence updates probability only by search power: `P(no detection \| claim)` versus `P(no detection \| not claim)`. |
| 21 | Burden of Proof | Presumption | Shifts proof unfairly to the skeptic. | Assign burden to the party making the positive, costly, or policy-changing claim; require evidence proportional to risk. |
| 22 | No True Scotsman | Presumption | Redefines a group to protect a claim. | Freeze definitions before testing; reject post hoc predicate changes that exclude counterexamples. |
| 23 | Suppressed Evidence | Presumption | Shows only favorable facts. | Require a complete evidence table with included, excluded, and unknown data plus selection criteria. |
| 24 | Argument from Incredulity | Presumption | Treats inability to imagine as impossibility. | Convert incredulity to a knowledge-state variable; personal model failure is not probability zero. |
| 25 | Hasty Generalization | Weak Induction | Infers too much from too little data. | Check sample size, sampling method, confidence interval, and population match before generalizing. |
| 26 | Anecdotal Evidence | Weak Induction | Lets stories replace statistics. | Treat anecdotes as hypothesis generators; require representative data for prevalence or effect claims. |
| 27 | Appeal to Authority | Weak Induction | Lets authority decide truth without fit. | Weight testimony by domain expertise, independence, track record, conflict of interest, and evidence transparency. |
| 28 | False Cause | Weak Induction | Confuses timing or correlation with cause. | Use causal DAGs, counterfactuals, controls, and confounder checks; correlation is not causation. |
| 29 | Weak Analogy | Weak Induction | Treats unlike things as meaningfully alike. | List shared and differing predicates; accept analogy only if shared predicates causally determine the inferred property. |
| 30 | Gambler's Fallacy | Weak Induction | Thinks independent random events self-correct. | Check independence: for independent trials, `P(next outcome \| history) = P(next outcome)`. |
| 31 | Sunk Cost Fallacy | Weak Induction | Lets past costs trap future decisions. | Optimize expected future utility; exclude irrecoverable costs from `E[U(next action)]`. |
| 32 | Texas Sharpshooter | Weak Induction | Draws the target after seeing the data. | Penalize post hoc pattern search with multiple-comparison correction or held-out validation. |
| 33 | Argument from Silence | Weak Induction | Treats lack of mention as proof. | Estimate detection probability; silence matters only if a reliable record would probably contain the fact. |
| 34 | Moving the Goalposts | Weak Induction | Changes standards after evidence appears. | Pre-register acceptance criteria; compare new criteria against the original decision rule. |
| 35 | Equivocation | Ambiguity | Shifts a word's meaning mid-argument. | Assign each key term a stable symbol; reject proofs where one symbol maps to multiple meanings. |
| 36 | Amphiboly | Ambiguity | Uses grammar that permits misleading parses. | Parse the sentence into possible syntactic forms; do not infer from an ambiguous parse without disambiguation. |
| 37 | Composition | Ambiguity | Assigns part properties to the whole. | Test whether the property is additive, compositional, or emergent before aggregating. |
| 38 | Division | Ambiguity | Assigns whole properties to each part. | Test whether the property distributes from set/system to members; many predicates are non-distributive. |
| 39 | Accent | Ambiguity | Alters meaning through emphasis. | Represent emphasized tokens explicitly and compare proposition changes under different stress patterns. |
| 40 | Quoting Out of Context | Ambiguity | Uses fragments to distort intent. | Compare quoted proposition with surrounding source proposition; require contextual entailment. |
| 41 | Reification | Ambiguity | Treats abstractions like concrete agents. | Map abstract nouns to measurable variables or agents; reject causal claims with no actor or mechanism. |
| 42 | Kettle Logic | Ambiguity | Uses mutually inconsistent excuses. | Check consistency: the defense set must be jointly satisfiable. |
| 43 | Affirming the Consequent | Formal | Infers `A` from `A -> B` and `B`. | Truth-table the conditional; valid forms are modus ponens and modus tollens, not `B -> A`. |
| 44 | Denying the Antecedent | Formal | Infers `not B` from `A -> B` and `not A`. | Check whether other sufficient causes for `B` exist; `A -> B` does not imply `not A -> not B`. |
| 45 | Undistributed Middle | Formal | Treats shared traits as identity. | In syllogisms, the middle term must be distributed in at least one premise. |
| 46 | Illicit Major | Formal | Overextends the major term in the conclusion. | A term distributed in the conclusion must be distributed in its premise. |
| 47 | Illicit Minor | Formal | Overextends the minor term in the conclusion. | Apply the same distribution rule to the minor term: no broader conclusion than the premise supports. |
| 48 | Affirming a Disjunct | Formal | Treats inclusive `A or B` as exclusive. | Specify inclusive `or` versus exclusive `xor`; `A` implies `not B` only under XOR. |
| 49 | Argument from Fallacy | Formal | Treats a bad argument as proving the conclusion false. | Separate validity of argument `G` from truth of conclusion `C`; `invalid(G)` does not entail `not C`. |
| 50 | Ad Hoc Rescue | Other Common | Adds excuses only to protect a failed claim. | Penalize unfalsifiable auxiliary assumptions; require new predictions or independent evidence. |
| 51 | Appeal to Nature | Other Common | Treats natural as good or right. | Separate descriptive predicate `natural(x)` from normative value `good(x)`; require a value premise. |
| 52 | Appeal to Money | Other Common | Treats wealth or price as truth. | Money may proxy incentives or resources; require direct reliability evidence before epistemic weighting. |
| 53 | Appeal to Poverty | Other Common | Treats poverty as virtue or truth. | Socioeconomic status is not a truth-maker; require independent moral or factual premises. |
| 54 | Appeal to Flattery | Other Common | Uses praise to lower scrutiny. | Strip social reward from premise set; evaluate the claim with praise removed. |
| 55 | Appeal to Ridicule | Other Common | Uses mockery instead of logic. | Replace ridicule with explicit premises; if none remain, support is zero. |
| 56 | Chronological Snobbery | Other Common | Treats era as decisive. | Model time as context, not proof; require evidence that the era predicts truth or value. |
| 57 | Etymological Fallacy | Other Common | Treats word origin as current meaning. | Use current usage distribution and context; etymology is historical evidence, not semantic authority. |
| 58 | Single Cause Fallacy | Other Common | Explains a complex outcome with one cause. | Use multivariable models or causal graphs; check omitted variables and interaction effects. |
| 59 | False Attribution | Other Common | Misplaces credit or source. | Trace provenance to primary evidence; confidence decays with citation-chain uncertainty. |
| 60 | Historian's Fallacy | Other Common | Judges past choices as if present knowledge was available. | Condition analysis on information available at time `t`, not later observations. |
| 61 | Ipse Dixit | Other Common | Treats assertion alone as proof. | Assertion has evidential weight only through calibrated reliability; unsupported fiat is not a premise. |
| 62 | Middle Ground | Other Common | Treats compromise as truth. | Truth is not the midpoint of claims; compare each claim's evidence likelihood independently. |
| 63 | Nirvana Fallacy | Other Common | Rejects realistic options because they are imperfect. | Compare feasible alternatives by expected utility, not against an unattainable ideal. |
| 64 | Package Deal | Other Common | Fuses unrelated ideas into one bundle. | Factor claims into independent propositions; require covariance or entailment before bundling. |
| 65 | Proof by Verbosity | Other Common | Uses length or complexity as strength. | Score arguments by independent valid supports, not token count; remove duplicate premises. |
| 66 | Style Over Substance | Other Common | Lets presentation hide weakness. | Separate rhetorical quality from evidential weight; evaluate premises in plain form. |
| 67 | Thought-Terminating Cliche | Other Common | Uses slogans to stop analysis. | Expand slogan into propositions; require testable premises and a conclusion. |
| 68 | Two Wrongs Make a Right | Other Common | Uses others' wrongs to excuse this wrong. | Compare moral propositions independently; another violation does not negate this obligation. |
| 69 | Wishful Thinking | Other Common | Treats desire as evidence. | Remove utility term from belief update; wanting `C` does not increase `P(C)` unless it changes action. |
| 70 | Is-Ought Fallacy | Other Common | Derives moral duty from facts alone. | Require an explicit normative bridge premise; descriptive `is` statements do not entail `ought` alone. |
