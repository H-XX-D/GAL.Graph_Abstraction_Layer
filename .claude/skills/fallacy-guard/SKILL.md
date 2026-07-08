---
name: Fallacy Guard
description: Detects logical fallacies, maps them to formal reasoning tests, and rewrites arguments to avoid relevance, presumption, induction, ambiguity, formal, and common reasoning traps.
when_to_use: Use when reviewing an argument, policy, spec, debate, critique, decision memo, prompt, proof sketch, incident analysis, or recommendation for reasoning errors. Also use when the user asks for fallacies, bias checks, adversarial reasoning, argument repair, or mathematical ways to avoid reasoning traps.
argument-hint: "[argument, claim, memo, or decision]"
---

## Purpose

Use this skill to audit reasoning without turning the audit into a personal attack.
Separate three questions:

1. Is the conclusion true?
2. Does the stated argument support the conclusion?
3. What stronger argument or test would avoid the trap?

Never reject a conclusion merely because one argument for it contains a fallacy.
That mistake is itself the argument from fallacy.

## Required References

Read these supporting files before giving a fallacy audit:

- `fallacy-catalog.md`: complete 70-fallacy catalog with detection cues and mathematical guardrails.
- `math-guards.md`: reusable formal checks, probability tests, causal tests, and argument-repair templates.

## Operating Procedure

1. Extract the argument into `claim`, `premises`, `warrant`, `evidence`, and `conclusion`.
2. Normalize terms. Flag ambiguous terms, shifting definitions, hidden quantifiers, and unstated assumptions.
3. Test relevance: each premise must increase support for the conclusion under an explicit relevance relation, likelihood ratio, causal model, or deductive rule.
4. Test validity:
   - For deductive claims, translate to propositional, predicate, or syllogistic form and check whether the conclusion follows.
   - For inductive claims, check sample size, base rate, uncertainty, selection process, effect size, and rival hypotheses.
   - For causal claims, require a causal graph, counterfactual contrast, mechanism, and confounder check.
   - For decisions, compare expected utility from future costs and benefits only; sunk costs are evidence about process, not payoff.
5. Identify fallacies by name only after showing the failed reasoning test.
6. Repair the argument by proposing the minimum change needed: better evidence, narrower conclusion, corrected logic form, clarified definition, or an explicit uncertainty range.

## Response Format

Prefer this concise structure unless the user asks for a full report:

```text
Claim:
Reasoning map:
Detected traps:
- Fallacy: ...
  Failed test: ...
  Mathematical guard: ...
  Repair: ...
Stronger version:
Residual uncertainty:
```

## Tone Rules

- Audit arguments, not people.
- Use confidence levels when evidence is incomplete.
- Treat fallacy names as labels for failed checks, not as rhetorical weapons.
- Preserve any valid evidence even when the surrounding argument is flawed.
