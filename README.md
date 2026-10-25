# grep-knowledge

A cross-platform, grep-first knowledge layer for private study materials. It extracts searchable text from transcripts, PDF files, Word documents, PowerPoint presentations, notebooks, Markdown, and source files without copying the originals into this repository.

Private sources, extracted text, index state, and the generated catalog remain under the configured resources directory. The repository contains only indexing and search tooling.

## Requirements

- Python 3.11+
- `ripgrep` (`rg`) for searching
- A sibling or otherwise accessible resources directory

## Quick start

### Linux and macOS (`sh`, `bash`, or `zsh`)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
cp .env.example .env
cp config.example.yml config.yml

sh run.sh
grep-knowledge search "logistic regression" --subject "Example Subject"
```

The runner is POSIX-shell compatible: use `sh run.sh`, `bash run.sh`, or `zsh run.sh`.

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
Copy-Item config.example.yml config.yml

.\run.ps1
grep-knowledge search "logistic regression" --subject "Example Subject"
```

## Resource layout

The indexer discovers supported files below each subject's `Transcripts` and `Notes` directories:

```text
Resources/
  Example Subject/
    Transcripts/
      Lecture 01.txt
    Notes/
      slides.pdf
      notebook.ipynb
  .knowledge/
    searchable/
    state.json
  CATALOG.md
```

Configure a relative or absolute `resources_dir` in the ignored `config.yml`. Subjects listed in `unenrolled_subjects` are skipped without modifying their files.

Run logs use size-based rotation under `Resources/.knowledge/logs` by default. The level, directory, maximum file size, and retained backup count are configurable in `config.yml`.

## Indexing and searching

```bash
grep-knowledge index
grep-knowledge search "regularization"
grep-knowledge search "regularization" --subject "Example Subject"
grep-knowledge search "regularization" --kind Notes --context 8
```

Changed files are extracted incrementally. Removed sources have their generated searchable copies removed. Original resources are never edited.

See `AGENTS.md`, `CITATION_RULES.md`, and `STUDY_WORKFLOWS.md` for a Codex-oriented study workflow based on catalog inspection and `rg` rather than a vector database.

## Notifications

Google Chat summaries are optional. When enabled in `config.yml`, put `GOOGLE_CHAT_WEBHOOK_URL` only in the ignored `.env`. Each index run reports added, updated, removed, unchanged, and failed documents.

Set `notifications.google_chat.enabled: false` for a completely local workflow.

## Orchestration

The runner is a finite process and does not require a resident shell.

For a collector-first pipeline, keep the orchestrator outside both repositories and rely on normal process exit codes:

```bash
#!/usr/bin/env sh
set -eu
/bin/sh /absolute/path/to/moodle-lms-automation/run.sh
/bin/sh /absolute/path/to/grep-knowledge/run.sh
```

The second command runs only after the collector succeeds.
