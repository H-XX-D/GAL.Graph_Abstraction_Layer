# Changelog

All notable project changes are summarized here. The repository is still in
draft status, so versions describe working release candidates rather than a
published package release.

## 0.1.0 - 2026-07-08

### Added

- Defined the GAL:netlist syntax profile for graph runtime interchange.
- Added the initial Python package and `gal` CLI.
- Implemented parsing, canonical formatting, semantic round-trip verification,
  and structured parse diagnostics.
- Added the draft GAL dialect family:
  AAL, AUDAL, CAL, DAL, EAL, FAL, GOVAL, HAL, IAL, KAL, LAL, MAL, OAL, PAL,
  QAL, RAL, ReAL, RISKAL, SAL, TAL, VAL, and WAL.
- Added dialect vocabulary validation for node kinds, fields, relations,
  signals, net operations, standing operations, and threads.
- Added JSON, DOT, YAML, Cypher, and JSON-to-GAL conversion support.
- Added in-memory loader modes: `verify`, `plan`, `replay`, and `merge`.
- Added the component registry for reusable net and standing operations.
- Added batch verification with `gal verify-all`.
- Added machine-readable JSON reports for verification, batch verification,
  components, dialects, doctor diagnostics, init, examples, AST, and runtime
  payloads.
- Added `gal schemas` and published static JSON Schema files under
  `docs/schemas/`.
- Added `gal doctor` for local and adapter diagnostics.
- Added `gal init` for starter graph generation.
- Added bundled dialect specs and examples so installed wheels work outside a
  source checkout.
- Added `gal examples` with JSON output, named example printing, export to a
  directory, overwrite control, and dialect filtering.
- Added GitHub Actions CI for tests, package build verification, installed-wheel
  smoke tests, example verification, and CLI smoke coverage.
- Added GitHub Pages documentation, schema catalog, dialect pages, blog draft
  index, and generated blog image assets.
- Refined HAL with research inspirations, loader rules, cross-dialect handoffs,
  and a richer hardware substrate example.

### Changed

- README now describes the implemented CLI surface, quickstart flow, bundled
  assets, and draft blog posts.
- HAL examples now model firmware, adapters, capabilities, sensors, interrupts,
  DMA paths, and capability mapping.
- Static schema publishing is checked against the in-code registry in tests.
- Package metadata now uses SPDX license syntax and verifies source distribution
  and wheel builds in CI.

### Validation

- The release gate runs the test suite, package build, Twine artifact checks,
  installed-wheel smoke tests, and CLI smoke tests.
- CI verifies package builds, package metadata, bundled examples, and the
  installed wheel outside the checkout.
- GitHub Pages deployment is active for project docs and schema artifacts.
