# Installing Rust Reverse Engineering for Codex

Install this repository as a local Codex plugin.

This document covers local installation and testing. For public distribution, publish the repository and have users add it to a repo or personal marketplace until official public Codex plugin publishing opens.

## Installation

1. Clone the repository:

```bash
mkdir -p ~/.codex/plugins
git clone https://github.com/jingjing2222/rust-reverse-engineering-skill.git ~/.codex/plugins/rust-reverse-engineering
```

2. Create or update your personal marketplace file at `~/.agents/plugins/marketplace.json`:

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

3. Restart Codex.

4. Open the plugin directory:

```text
/plugins
```

5. Choose your personal marketplace and install `Rust Reverse Engineering`.

## Verify

```bash
ls -la ~/.codex/plugins/rust-reverse-engineering
```

You should see the plugin checkout, including `.codex-plugin/plugin.json`.

## Updating

```bash
cd ~/.codex/plugins/rust-reverse-engineering
git pull
```

Restart Codex after updating the plugin files so the local install picks up changes.

## Repo-scoped testing

This repository includes `.agents/plugins/marketplace.json`, which exposes the repo root as a local plugin source with `source.path` set to `./`.

If you open this repository itself in Codex:

1. Restart Codex after cloning or pulling changes.
2. Open `/plugins`.
3. Select the `Rust Reverse Engineering Local` marketplace.
4. Install the plugin from that repo-scoped marketplace.

## Uninstalling

```bash
rm -rf ~/.codex/plugins/rust-reverse-engineering
```

If you added it to a personal marketplace, remove that plugin entry from `~/.agents/plugins/marketplace.json` and restart Codex.
