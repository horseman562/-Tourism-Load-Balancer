# Moving this work to another PC

Two separate things have to move. The project files are already on GitHub; the
Claude Code session history is not, and is in `claude-session-transfer.zip`.

---

## The one thing that will break it

Claude Code stores conversations in a folder named after the project's **full path**:

```
C:\Users\death\.claude\projects\D--2025-project-portfolio-dosm\
                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                 = D:\2025_project_portfolio\dosm
```

**On the new PC the project must sit at exactly `D:\2025_project_portfolio\dosm`.**
Put it anywhere else and Claude Code will look for a folder with a different name,
find nothing, and start with no history.

If the new machine has no D: drive, rename the folder inside the zip to match
whatever the new path is — replace `:` and `\` with `-`. For example
`C:\work\dosm` becomes `C--work-dosm`.

---

## Step 1 — the project files

```bash
cd /d
mkdir 2025_project_portfolio
cd 2025_project_portfolio
git clone https://github.com/horseman562/-Tourism-Load-Balancer.git dosm
```

Raw source files are optional — grab `dosm-raw-data.zip` from the repo's Releases
page and unpack it to `data/raw/` only if you need the original PDFs. The dashboard
does not need them.

Rebuild the environment:

```bash
cd D:\2025_project_portfolio\dosm
python -m venv dashboard\.venv
dashboard\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Step 2 — the Claude Code history

Unzip `claude-session-transfer.zip`. It contains a `claude/` folder mirroring the
structure of `C:\Users\<you>\.claude\`. Copy its contents there, merging with what
is already present:

```
claude/projects/D--2025-project-portfolio-dosm/   -> conversations + memory
claude/skills/                                    -> installed skills
claude/settings.json                              -> permissions and config
```

⚠️ **Do not overwrite an existing `settings.json` blindly** if the new machine is
already set up — open both and merge. The other files are additive and safe.

## Step 3 — resume

```bash
cd D:\2025_project_portfolio\dosm
claude --resume
```

Pick the longest session from the list — the 32 MB one is this conversation.

---

## What is in the zip

| | |
|---|---|
| `02e466bb-….jsonl` | **31 MB — this conversation.** Full transcript including every tool call |
| `68f1a68c-….jsonl` | 2.5 MB — the data-acquisition session |
| `0286694c-….jsonl` | 0.3 MB + tool results — an earlier session |
| `memory/` | 3 files: the panel-defence project note, the explain-plainly preference, and `MEMORY.md` |
| `skills/` | `color-palette`, `dashboard-designer`, `jimat-vps-deploy` |
| `settings.json` | Claude Code configuration |

## What is NOT in the zip, and does not need to be

- **Project files** — on GitHub, clone them
- **Raw DOSM downloads** — 321 MB, on the repo's Releases page
- **`.venv`** — rebuild with pip, never copy a virtualenv between machines
- **`dosm-raw-data.zip`** — already published as a release asset

---

## If resume does not find the history

Check the folder name matches the project path exactly. Run this on the new PC:

```bash
ls "$HOME/.claude/projects/"
```

The folder name must be the project's full path with `:` and `\` replaced by `-`.
Rename it to match and resume again.
