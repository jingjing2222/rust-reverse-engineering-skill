# Rust Reverse Engineering Skill

A shared Rust reverse-engineering workflow packaged for both Claude Code and Codex.

This skill is intended for defensive security work. Reverse-engineering tooling is not inherently harmful; used responsibly, it helps developers inspect what their own compiled artifacts expose, validate hardening assumptions, audit attack surface, and better protect the binaries they ship.

It is designed for **authorized** reverse engineering, malware triage in controlled environments, CTFs, binary auditing, and compatibility/interoperability work. The shared skill body fingerprints Rust builds, demangles symbols, surfaces likely crate boundaries, highlights panic/unwind and FFI edges, and drives a repeatable static/dynamic analysis workflow.

If you publish compiled deliverables, prefer using this skill to understand and defend your own outputs, or binaries you are explicitly permitted to assess.

## What it does

- Fast binary triage: format, architecture, stripped/debug-info status, exported/imported symbols
- Rust fingerprinting: v0/legacy mangling, `core`/`alloc`/`std` artifacts, panic and unwind paths, crate namespace recovery
- Static analysis workflow for Ghidra, IDA, and Binary Ninja
- Dynamic-analysis guidance for `gdb` and `lldb`
- Artifact generation: triage bundles, demangled symbol dumps, import/export snapshots, disassembly, Ghidra pseudocode exports, and summary reports
- Structured reporting: key namespaces, entry points, FFI boundaries, async/state-machine candidates, unresolved questions

## Requirements

Required:

- `file`
- `strings`
- `readelf` or `llvm-readelf` for ELF, or `otool` for Mach-O
- `nm` or `llvm-nm`
- `objdump` or `llvm-objdump`, or `otool` on macOS

Optional but recommended:

- `rustfilt`
- `gdb` or `lldb`
- Ghidra, IDA Pro, or Binary Ninja

To auto-install missing tools when possible:

```bash
bash skills/rust-reverse-engineering/scripts/install-dep.sh rustfilt
bash skills/rust-reverse-engineering/scripts/install-dep.sh ghidra
```

## Installation

### Claude Code

Load the repository directly as a local plugin:

```bash
claude --plugin-dir /absolute/path/to/rust-reverse-engineering-skill
```

Then use the slash command shown under `/help`, typically:

```bash
/rust-reverse-engineering:re-rust /path/to/binary
```

Claude-specific wrapper files live under `.claude-plugin/` and `commands/`.

### Codex

Codex installs reusable workflows as plugins. This repository includes a Codex plugin manifest that bundles the shared Rust reverse-engineering skill.

For **local testing**, follow the plugin install steps in `.codex/INSTALL.md`.

The short version is:

```bash
mkdir -p ~/.codex/plugins
git clone https://github.com/jingjing2222/rust-reverse-engineering-skill.git ~/.codex/plugins/rust-reverse-engineering
mkdir -p ~/.agents/plugins
```

Then add the plugin to your personal marketplace, restart Codex, open `/plugins`, and install `Rust Reverse Engineering`.

For repo-scoped testing, this repository also includes `.agents/plugins/marketplace.json`, which exposes the repo itself as a local Codex plugin source.

For **public distribution**, the current Codex docs say official public plugin publishing is not self-serve yet. The recommended path today is to publish the plugin repo publicly, keep `.codex-plugin/plugin.json` and marketplace metadata ready, and distribute it through repo or personal marketplaces until the official public Plugin Directory submission flow opens.

Codex-specific wrapper files live under `.agents/plugins/`, `.codex/`, `.codex-plugin/`, and `skills/rust-reverse-engineering/agents/`.

## Usage

### Natural language

The shared skill should trigger on requests like:

- "Reverse engineer this Rust binary"
- "Analyze this Rust executable"
- "Demangle Rust symbols"
- "Map crates and entry points in this binary"
- "Find the FFI boundary in this Rust library"
- "Trace panic and unwind paths"

### Manual scripts

Run the bundled scripts from the repository checkout:

```bash
# Check required and optional tooling
bash skills/rust-reverse-engineering/scripts/check-deps.sh

# Install one missing dependency
bash skills/rust-reverse-engineering/scripts/install-dep.sh ghidra

# Generate a reusable artifact bundle on disk
bash skills/rust-reverse-engineering/scripts/collect-artifacts.sh ./target.bin

# Export only the Ghidra headless pseudocode bundle
bash skills/rust-reverse-engineering/scripts/export-ghidra-pseudocode.sh ./target.bin ./target-reverse-output/decompiled/ghidra

# Override the automatically selected Mach-O slice when needed
bash skills/rust-reverse-engineering/scripts/collect-artifacts.sh --macho-arch x86_64 ./target.bin

# For very long runs in your own shell, you can also launch a detached job
bash skills/rust-reverse-engineering/scripts/ghidra-job.sh start --max-functions 500 ./target.bin ./target-reverse-output/decompiled/ghidra
bash skills/rust-reverse-engineering/scripts/ghidra-job.sh status ./target-reverse-output/decompiled/ghidra

# Dump and demangle symbols (best effort)
bash skills/rust-reverse-engineering/scripts/demangle-symbols.sh ./target.bin

# Search the generated artifacts for runtime / async / panic / FFI / network buckets
bash skills/rust-reverse-engineering/scripts/find-rust-patterns.sh ./target-reverse-output
```

`collect-artifacts.sh` now creates a source-like decompiler bundle under `decompiled/ghidra/` when `analyzeHeadless` is available. The exported `.c` files are Ghidra pseudocode, not original Rust source, but they provide the same kind of on-disk deliverable that APK-focused reverse-engineering workflows produce.

Universal Mach-O inputs are now thinned automatically before triage, disassembly, and Ghidra import. On Apple Silicon hosts, the default analysis slice is `arm64`; use `--macho-arch x86_64` only when you explicitly want the Intel slice. The chosen slice is recorded in `input/analysis-target.txt` and `decompiled/ghidra/analysis-target.txt`.

Treat the export as final only when `decompiled/ghidra/status.txt` says `STATE: completed` or `decompiled/ghidra/complete.marker` exists. The script now updates `status.txt` and `summary.txt` while the export is still running, and the foreground wrapper prints periodic `PROGRESS:` heartbeats so long-running jobs do not look stalled.

Inside Codex, keep the foreground export session alive until it reaches `STATE: completed`. Do not interrupt a long-running headless export unless the user explicitly asks to stop it. In particular, do not stop because “enough signal was gathered”, “the remaining analysis value seems low”, or “it is taking too long”. If the process is still alive, it is still running.

Use `decompiled/ghidra/runner-status.txt` to distinguish “slow but alive” from “actually stopped”. That file is updated by the shell wrapper every heartbeat interval even during the long auto-analysis phase, before the Java exporter starts updating decompilation counters. A fresh heartbeat together with `PROCESS_ALIVE: yes` means the export is still running. `ghidra-job.sh status` now also prints `RUNNER_HEARTBEAT_AGE_SECONDS`, `RUNNER_HEARTBEAT_STALE`, and `LIVENESS_HINT` so detached jobs do not depend on `status.txt` alone. `decompiled/ghidra/warning-summary.txt` summarizes headless `pcode error` / `Unable to resolve constructor` warnings so you can spot whether a handful of toxic functions are dominating the decompile noise.

## Repository structure

```text
rust-reverse-engineering-skill/
├── .agents/
│   └── plugins/
│       └── marketplace.json
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
        ├── agents/
        │   └── openai.yaml
        ├── references/
        │   ├── setup-guide.md
        │   ├── triage-and-fingerprinting.md
        │   ├── rust-patterns.md
        │   ├── static-analysis-workflow.md
        │   └── dynamic-analysis-notes.md
        ├── scripts/
        │   ├── check-deps.sh
        │   ├── collect-artifacts.sh
        │   ├── export-ghidra-pseudocode.sh
        │   ├── ghidra-job.sh
        │   ├── install-dep.sh
        │   ├── macho-slice.sh
        │   ├── triage.sh
        │   ├── demangle-symbols.sh
        │   └── find-rust-patterns.sh
        └── SKILL.md
```
