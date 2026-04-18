#!/usr/bin/env python3

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPO_SLUG = "jingjing2222/rust-reverse-engineering-skill"


def fail(message: str) -> None:
    raise SystemExit(message)


def load_json(path: Path) -> dict:
    if not path.is_file():
        fail(f"Missing JSON file: {path.relative_to(ROOT)}")
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        fail(f"JSON root must be an object: {path.relative_to(ROOT)}")
    return data


def require(value: bool, message: str) -> None:
    if not value:
        fail(message)


def relative_path(path: Path) -> str:
    return str(path.relative_to(ROOT))


def main() -> None:
    claude_marketplace_path = ROOT / ".claude-plugin" / "marketplace.json"
    claude_plugin_path = ROOT / ".claude-plugin" / "plugin.json"
    codex_plugin_path = ROOT / ".codex-plugin" / "plugin.json"
    codex_marketplace_path = ROOT / ".agents" / "plugins" / "marketplace.json"

    claude_marketplace = load_json(claude_marketplace_path)
    claude_plugin = load_json(claude_plugin_path)
    codex_plugin = load_json(codex_plugin_path)
    codex_marketplace = load_json(codex_marketplace_path)

    require(bool(claude_marketplace.get("name")), "Claude marketplace name is required")
    require(bool(claude_marketplace.get("owner", {}).get("name")), "Claude marketplace owner.name is required")
    require(bool(claude_marketplace.get("owner", {}).get("email")), "Claude marketplace owner.email is required")

    claude_marketplace_plugins = claude_marketplace.get("plugins")
    require(isinstance(claude_marketplace_plugins, list) and claude_marketplace_plugins, "Claude marketplace must list at least one plugin")

    claude_plugin_name = claude_plugin.get("name")
    require(claude_plugin_name == "rust-reverse-engineering", "Claude plugin name must stay 'rust-reverse-engineering'")
    require(bool(claude_plugin.get("version")), "Claude plugin version is required")
    require(claude_plugin.get("repository") == f"https://github.com/{REPO_SLUG}", "Claude plugin repository URL must match the public repo")

    matching_claude_entries = [plugin for plugin in claude_marketplace_plugins if plugin.get("name") == claude_plugin_name]
    require(matching_claude_entries, "Claude marketplace must contain the rust-reverse-engineering plugin entry")
    for plugin in matching_claude_entries:
        require(plugin.get("source") == "./", "Claude marketplace plugin source must remain './' for repo installs")
        require(plugin.get("version") == claude_plugin.get("version"), "Claude marketplace plugin version must match .claude-plugin/plugin.json")

    require(codex_plugin.get("name") == "rust-reverse-engineering", "Codex plugin name must stay 'rust-reverse-engineering'")
    require(bool(codex_plugin.get("version")), "Codex plugin version is required")
    require(codex_plugin.get("repository") == f"https://github.com/{REPO_SLUG}", "Codex plugin repository URL must match the public repo")

    codex_interface = codex_plugin.get("interface")
    require(isinstance(codex_interface, dict), "Codex plugin interface block is required")
    require(bool(codex_interface.get("displayName")), "Codex plugin interface.displayName is required")
    require(bool(codex_interface.get("shortDescription")), "Codex plugin interface.shortDescription is required")
    require(bool(codex_interface.get("developerName")), "Codex plugin interface.developerName is required")
    require(isinstance(codex_interface.get("capabilities"), list) and codex_interface["capabilities"], "Codex plugin interface.capabilities must be a non-empty array")
    require(isinstance(codex_interface.get("defaultPrompt"), list) and codex_interface["defaultPrompt"], "Codex plugin interface.defaultPrompt must be a non-empty array")

    skills_value = codex_plugin.get("skills")
    require(isinstance(skills_value, str) and skills_value, "Codex plugin skills path is required")
    skills_root = (ROOT / skills_value).resolve()
    require(skills_root.is_dir(), f"Codex skills path does not exist: {skills_value}")

    skill_files = sorted(skills_root.glob("*/SKILL.md"))
    require(skill_files, "Codex skills path must contain at least one skill directory with SKILL.md")

    rust_skill_dir = skills_root / "rust-reverse-engineering"
    require((rust_skill_dir / "SKILL.md").is_file(), f"Missing skill entrypoint: {relative_path(rust_skill_dir / 'SKILL.md')}")
    require((rust_skill_dir / "agents" / "openai.yaml").is_file(), f"Missing skill agent config: {relative_path(rust_skill_dir / 'agents' / 'openai.yaml')}")

    expected_scripts = {
        "check-deps.sh",
        "collect-artifacts.sh",
        "demangle-symbols.sh",
        "export-ghidra-pseudocode.sh",
        "find-rust-patterns.sh",
        "ghidra-job.sh",
        "install-dep.sh",
        "macho-slice.sh",
        "triage.sh",
    }
    scripts_dir = rust_skill_dir / "scripts"
    require(scripts_dir.is_dir(), f"Missing scripts directory: {relative_path(scripts_dir)}")
    actual_scripts = {path.name for path in scripts_dir.glob("*.sh")}
    missing_scripts = sorted(expected_scripts - actual_scripts)
    require(not missing_scripts, f"Missing expected scripts: {', '.join(missing_scripts)}")
    require((scripts_dir / "ghidra" / "ExportRustPseudocode.java").is_file(), "Missing Ghidra export helper: skills/rust-reverse-engineering/scripts/ghidra/ExportRustPseudocode.java")

    codex_marketplace_plugins = codex_marketplace.get("plugins")
    require(isinstance(codex_marketplace_plugins, list) and codex_marketplace_plugins, "Codex marketplace must list at least one plugin")

    matching_codex_entries = [plugin for plugin in codex_marketplace_plugins if plugin.get("name") == codex_plugin.get("name")]
    require(matching_codex_entries, "Codex marketplace must contain the rust-reverse-engineering plugin entry")

    repo_entry = matching_codex_entries[0]
    source = repo_entry.get("source", {})
    policy = repo_entry.get("policy", {})
    require(source.get("source") == "local", "Repo-scoped Codex marketplace entry must use local source")
    require(source.get("path") == "./", "Repo-scoped Codex marketplace entry must keep local path './'")
    require(policy.get("installation") == "AVAILABLE", "Codex marketplace installation policy must remain AVAILABLE")
    require(policy.get("authentication") == "ON_INSTALL", "Codex marketplace authentication policy must remain ON_INSTALL")

    required_docs = [
        ROOT / "README.md",
        ROOT / ".codex" / "INSTALL.md",
        ROOT / "commands" / "re-rust.md",
        rust_skill_dir / "SKILL.md",
    ]
    for path in required_docs:
        require(path.is_file(), f"Missing required documentation file: {relative_path(path)}")

    print("Repository validation passed.")


if __name__ == "__main__":
    main()
