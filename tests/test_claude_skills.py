from pathlib import Path
import importlib.util
import re


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".claude" / "skills" / "fallacy-guard"
COMMAND_PATH = ROOT / ".claude" / "commands" / "fallacy-guard.md"
INSTALLER_PATH = ROOT / "scripts" / "install_claude_fallacy_guard.py"


EXPECTED_FALLACIES = [
    "Ad Hominem",
    "Straw Man",
    "Red Herring",
    "Appeal to Pity",
    "Appeal to Force",
    "Appeal to Emotion",
    "Appeal to Popularity",
    "Appeal to Tradition",
    "Appeal to Novelty",
    "Genetic Fallacy",
    "Guilt by Association",
    "Tu Quoque",
    "Poisoning the Well",
    "Moral Equivalence",
    "Begging the Question",
    "Circular Reasoning",
    "False Dilemma",
    "Complex Question",
    "Slippery Slope",
    "Appeal to Ignorance",
    "Burden of Proof",
    "No True Scotsman",
    "Suppressed Evidence",
    "Argument from Incredulity",
    "Hasty Generalization",
    "Anecdotal Evidence",
    "Appeal to Authority",
    "False Cause",
    "Weak Analogy",
    "Gambler's Fallacy",
    "Sunk Cost Fallacy",
    "Texas Sharpshooter",
    "Argument from Silence",
    "Moving the Goalposts",
    "Equivocation",
    "Amphiboly",
    "Composition",
    "Division",
    "Accent",
    "Quoting Out of Context",
    "Reification",
    "Kettle Logic",
    "Affirming the Consequent",
    "Denying the Antecedent",
    "Undistributed Middle",
    "Illicit Major",
    "Illicit Minor",
    "Affirming a Disjunct",
    "Argument from Fallacy",
    "Ad Hoc Rescue",
    "Appeal to Nature",
    "Appeal to Money",
    "Appeal to Poverty",
    "Appeal to Flattery",
    "Appeal to Ridicule",
    "Chronological Snobbery",
    "Etymological Fallacy",
    "Single Cause Fallacy",
    "False Attribution",
    "Historian's Fallacy",
    "Ipse Dixit",
    "Middle Ground",
    "Nirvana Fallacy",
    "Package Deal",
    "Proof by Verbosity",
    "Style Over Substance",
    "Thought-Terminating Cliche",
    "Two Wrongs Make a Right",
    "Wishful Thinking",
    "Is-Ought Fallacy",
]


def test_fallacy_guard_skill_has_claude_frontmatter():
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    assert text.startswith("---\n")
    frontmatter = text.split("---", 2)[1]
    assert "description:" in frontmatter
    assert "when_to_use:" in frontmatter
    assert "fallacy-catalog.md" in text
    assert "math-guards.md" in text


def test_fallacy_guard_legacy_command_wrapper_points_to_skill():
    text = COMMAND_PATH.read_text(encoding="utf-8")

    assert text.startswith("---\n")
    assert "description:" in text.split("---", 2)[1]
    assert "$ARGUMENTS" in text
    assert ".claude/skills/fallacy-guard/SKILL.md" in text
    assert ".claude/skills/fallacy-guard/fallacy-catalog.md" in text
    assert ".claude/skills/fallacy-guard/math-guards.md" in text


def test_fallacy_guard_installer_copies_personal_files(tmp_path, capsys):
    installer = _load_installer()

    assert installer.install(tmp_path) == 0

    for source, destination in installer.FILES:
        assert (tmp_path / destination).read_text(encoding="utf-8") == (ROOT / source).read_text(encoding="utf-8")
    assert "fallacy guard installed" in capsys.readouterr().out


def test_fallacy_guard_installer_check_detects_missing_files(tmp_path):
    installer = _load_installer()

    assert installer.install(tmp_path, check=True) == 1


def test_fallacy_guard_installer_refuses_to_overwrite_different_file(tmp_path):
    installer = _load_installer()
    destination = tmp_path / "commands" / "fallacy-guard.md"
    destination.parent.mkdir(parents=True)
    destination.write_text("local custom command\n", encoding="utf-8")

    try:
        installer.install(tmp_path)
    except installer.InstallError as error:
        assert "--force" in str(error)
        assert str(destination) in str(error)
    else:
        raise AssertionError("expected differing installed file to require --force")


def test_fallacy_guard_installer_force_overwrites_different_file(tmp_path):
    installer = _load_installer()
    destination = tmp_path / "commands" / "fallacy-guard.md"
    destination.parent.mkdir(parents=True)
    destination.write_text("local custom command\n", encoding="utf-8")

    assert installer.install(tmp_path, force=True) == 0
    assert destination.read_text(encoding="utf-8") == COMMAND_PATH.read_text(encoding="utf-8")


def test_fallacy_catalog_covers_requested_fallacies_in_order():
    text = (SKILL_DIR / "fallacy-catalog.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\| (\d+) \| ([^|]+) \|", text, flags=re.MULTILINE)

    assert [int(number) for number, _ in rows] == list(range(1, 71))
    assert [name.strip() for _, name in rows] == EXPECTED_FALLACIES


def test_fallacy_catalog_has_mathematical_guard_for_each_entry():
    text = (SKILL_DIR / "fallacy-catalog.md").read_text(encoding="utf-8")
    guards = [_catalog_cells(line)[4] for line in text.splitlines() if re.match(r"^\| \d+ \|", line)]

    assert len(guards) == 70
    assert all(len(guard.strip()) >= 30 for guard in guards)
    assert any("P(evidence \\| claim)" in guard for guard in guards)
    assert any("truth-table" in guard.lower() for guard in guards)
    assert any("expected future utility" in guard for guard in guards)


def test_math_guards_cover_core_formalisms():
    text = (SKILL_DIR / "math-guards.md").read_text(encoding="utf-8")

    for phrase in (
        "Math Used To Support Or Refute Reasoning",
        "Deductive Validity",
        "Bayesian Relevance",
        "Statistical Induction",
        "Causal Reasoning",
        "Decision Theory",
        "Consistency And Coherence",
    ):
        assert phrase in text


def test_math_guards_cover_reasoning_toolbox_entries():
    text = (SKILL_DIR / "math-guards.md").read_text(encoding="utf-8")

    for phrase in (
        "Propositional logic",
        "First-order logic",
        "Rules of inference",
        "Truth tables",
        "Proof by contradiction",
        "Counterexamples",
        "Set theory",
        "Model theory",
        "Proof theory",
        "Computability theory",
        "Category theory",
    ):
        assert phrase in text


def test_source_distribution_includes_project_skill_files():
    text = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")

    assert "recursive-include .claude/skills/fallacy-guard *.md" in text
    assert "recursive-include .claude/commands *.md" in text
    assert "include scripts/install_claude_fallacy_guard.py" in text


def test_readme_documents_fallacy_guard_installer():
    text = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "scripts/install_claude_fallacy_guard.py" in text
    assert "python3 scripts/install_claude_fallacy_guard.py --check" in text


def _catalog_cells(line: str) -> list[str]:
    return line.strip().removeprefix("| ").removesuffix(" |").split(" | ")


def _load_installer():
    spec = importlib.util.spec_from_file_location("install_claude_fallacy_guard", INSTALLER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
