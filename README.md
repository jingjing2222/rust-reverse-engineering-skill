# Rust Reverse Engineering Skill

Shared Rust reverse-engineering skill for Claude Code and Codex.

This project is for defensive security work. Reverse-engineering tooling is not inherently harmful; used responsibly, it helps developers understand what their own compiled artifacts expose, audit attack surface, and protect the binaries they ship.

Use it for binaries you own or are explicitly authorized to assess.

## What It Helps With

- Fingerprinting Rust binaries and libraries
- Recovering likely crate boundaries and entry points
- Surfacing panic, unwind, async, and FFI edges
- Producing reviewable artifacts such as demangled symbols, disassembly, and Ghidra pseudocode bundles
- Driving a repeatable static and dynamic analysis workflow

## Who This Is For

- Developers auditing their own release binaries
- Security engineers reviewing compiled Rust deliverables
- Authorized interoperability, compatibility, malware-triage, or CTF work

## Requirements

Required:

- `file`
- `strings`
- `nm` or `llvm-nm`
- `objdump` or `llvm-objdump`, or `otool` on macOS
- `readelf` or `llvm-readelf` for ELF, or `otool` for Mach-O

Recommended:

- `rustfilt`
- `gdb` or `lldb`
- Ghidra, IDA Pro, or Binary Ninja

## Install

### Claude Code

For a public GitHub repository, the recommended install path is the marketplace flow:

```bash
claude plugin marketplace add jingjing2222/rust-reverse-engineering-skill
claude plugin install rust-reverse-engineering@jingjing2222-plugins
```

This flow was validated against the public repo.

For local development, you can still load the repository directly:

```bash
claude --plugin-dir /absolute/path/to/rust-reverse-engineering-skill
```

### Codex

Codex can install this plugin from local or repo-scoped marketplaces, but public self-serve publishing to the official Codex Plugin Directory is not open yet. For now, use one of the local marketplace flows below.

Option A: install from this repo directly when you have the repo open in Codex.

1. Open this repository in Codex.
2. Restart Codex if needed.
3. Run `/plugins`.
4. Open the `Rust Reverse Engineering Local` marketplace exposed by `.agents/plugins/marketplace.json`.
5. Install `Rust Reverse Engineering`.

Option B: install as a reusable local plugin.

```bash
mkdir -p ~/.codex/plugins
git clone https://github.com/jingjing2222/rust-reverse-engineering-skill.git ~/.codex/plugins/rust-reverse-engineering
```

Add an entry to `~/.agents/plugins/marketplace.json` that points at the cloned path:

```json
{
  "name": "personal-local-plugins",
  "interface": {
    "displayName": "Personal Local Plugins"
  },
  "plugins": [
    {
      "name": "rust-reverse-engineering",
      "source": {
        "source": "local",
        "path": "./.codex/plugins/rust-reverse-engineering"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Coding"
    }
  ]
}
```

Then restart Codex, run `/plugins`, open your marketplace, and install `Rust Reverse Engineering`.

You can also copy or symlink this repo into another local directory and point the marketplace entry there instead of cloning.

## Typical Output

The skill is built around artifact generation, not just chat answers. A normal run can produce:

- Binary triage summaries
- Demangled symbol inventories
- Import and export snapshots
- Pattern hits for runtime, panic, async, FFI, and network-adjacent code
- Ghidra pseudocode exports when headless Ghidra is available

Important: Ghidra output is pseudocode, not recovered original Rust source.

## Key Behavior

- Universal Mach-O inputs are thinned automatically to one analysis slice
- Long-running Ghidra exports keep live progress markers on disk
- `runner-status.txt` is the fast liveness signal for "still running" vs "actually stopped"

## Repository Layout

- `skills/rust-reverse-engineering/SKILL.md`: full skill instructions and analysis workflow
- `commands/re-rust.md`: Claude slash-command entry point
- `skills/rust-reverse-engineering/scripts/`: helper scripts for triage, symbol recovery, artifact collection, and Ghidra export
- `.claude-plugin/`: Claude plugin and marketplace manifests
- `.codex-plugin/` and `.agents/plugins/`: Codex plugin and marketplace manifests

## Repository Structure

```text
rust-reverse-engineering-skill/
├── .agents/
│   └── plugins/marketplace.json
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── .codex/
│   └── INSTALL.md
├── .codex-plugin/
│   └── plugin.json
├── commands/
│   └── re-rust.md
└── skills/
    └── rust-reverse-engineering/
        ├── agents/openai.yaml
        ├── references/
        ├── scripts/
        │   ├── check-deps.sh
        │   ├── collect-artifacts.sh
        │   ├── demangle-symbols.sh
        │   ├── export-ghidra-pseudocode.sh
        │   ├── find-rust-patterns.sh
        │   ├── ghidra-job.sh
        │   ├── install-dep.sh
        │   ├── macho-slice.sh
        │   └── triage.sh
        └── SKILL.md
```

## Where To Start

- Want to install in Claude Code: use the marketplace commands above
- Want to install in Codex: follow the install steps above
- Want the full analysis workflow: read [skills/rust-reverse-engineering/SKILL.md](skills/rust-reverse-engineering/SKILL.md)
- Want the Claude command entry point: read [commands/re-rust.md](commands/re-rust.md)
