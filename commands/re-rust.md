---
allowed-tools: Bash, Read, Glob, Grep
description: Triage and reverse engineer a Rust binary or library
user-invocable: true
argument-hint: path to ELF, Mach-O, PE/COFF, .so, .dylib, .dll, .a, .rlib, or object file
---

# /re-rust

Start the Rust reverse engineering workflow.

## Instructions

### Step 1: Get the target file

If the user passed a path, use it.

Otherwise, ask for the path to the binary, library, archive, or object file they want to analyze.

### Step 2: Check and install dependencies

Run:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/rust-reverse-engineering/scripts/check-deps.sh
```

Parse the output looking for:

- `INSTALL_REQUIRED:`
- `INSTALL_OPTIONAL:`

If required tooling is missing, install it one dependency at a time:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/rust-reverse-engineering/scripts/install-dep.sh <dependency>
```

The install script auto-detects the OS and package manager. If automatic installation is not possible, it prints exact manual instructions and exits with code 2. Show those instructions to the user and stop.

For optional dependencies, ask the user if they want to install them. Recommend at least:

- `rustfilt`
- one debugger: `gdb` or `lldb`
- `ghidra`

After any installation attempts, re-run `check-deps.sh`. Do not proceed until all required dependencies pass.

### Step 3: Triage the target

Run:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/rust-reverse-engineering/scripts/collect-artifacts.sh <target>
```

If the target is a universal Mach-O, the scripts now thin it automatically before analysis. Override only when you intentionally want another slice:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/rust-reverse-engineering/scripts/collect-artifacts.sh --macho-arch x86_64 <target>
```

If you are running this manually in your own shell and expect a very long Ghidra export, you can use the detached helper:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/rust-reverse-engineering/scripts/ghidra-job.sh start --max-functions 500 <target> <output-dir>/decompiled/ghidra
bash ${CLAUDE_PLUGIN_ROOT}/skills/rust-reverse-engineering/scripts/ghidra-job.sh status <output-dir>/decompiled/ghidra
```

Inside Codex itself, keep the foreground export alive and wait for the periodic `PROGRESS:` heartbeats until `decompiled/ghidra/status.txt` reaches `STATE: completed`.
Never stop the export because “enough signal was gathered” or because the remaining runtime looks expensive. Only stop on explicit user request or when the process has actually died.

Tell the user where the output directory was written, then inspect:

- `input/analysis-target.txt`
- `decompiled/ghidra/analysis-target.txt`
- `decompiled/ghidra/runner-status.txt`
- `decompiled/ghidra/status.txt`
- `reports/summary.md`
- `reports/pattern-hits.txt`
- `symbols/demangled.txt`
- `symbols/imports.txt`
- `symbols/exports.txt`
- `decompiled/ghidra/warning-summary.txt`
- `decompiled/ghidra/summary.txt`
- `decompiled/ghidra/functions.tsv`
- `decompiled/ghidra/decompile-errors.tsv`
- `decompiled/ghidra/functions/*.c`

Do not summarize the Ghidra export as final until `decompiled/ghidra/status.txt` says `STATE: completed` or `decompiled/ghidra/complete.marker` exists.
Treat a fresh `decompiled/ghidra/runner-status.txt` heartbeat together with `PROCESS_ALIVE: yes` as the source of truth for “still running”, even if `status.txt` counters are quiet for a while. For detached jobs, `ghidra-job.sh status` now surfaces `RUNNER_HEARTBEAT_AGE_SECONDS`, `RUNNER_HEARTBEAT_STALE`, and `LIVENESS_HINT`.

### Step 4: Recover symbols

If you need a targeted follow-up sweep, run:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/rust-reverse-engineering/scripts/find-rust-patterns.sh <output-dir>
```

Use the generated artifacts to separate:

- runtime crates
- likely app crates
- likely third-party crates
- exported FFI boundaries

### Step 5: Report next steps

Offer concrete next moves:

- **Static analysis**: load into Ghidra / IDA / Binary Ninja and start from entry points, strings, imports, or FFI boundaries
- **Dynamic analysis**: attach `gdb` / `lldb`, break on exports or panic paths, and trace one feature path
- **Subsystem focus**: networking, filesystem, crypto, config, async executor, or plugin API

Refer to `${CLAUDE_PLUGIN_ROOT}/skills/rust-reverse-engineering/SKILL.md` for the full workflow.
