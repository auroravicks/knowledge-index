# grep-knowledge

A local, grep-first knowledge layer for private study materials. It extracts searchable text and generates a catalog without copying source materials into this repository.

```powershell
.\run.ps1
.\.venv\Scripts\grep-knowledge.exe search "logistic regression" --subject "Machine Learning Paradigms"
```

Private source files, extracted text, index state, and the generated catalog stay under the configured `Resources` directory.

Each indexing run sends its own Google Chat summary with counts and names of added, updated, and removed documents. Store the webhook only in the ignored `.env`; notification behavior remains in `config.yml`.

Subjects that should remain outside the active course index can be listed by their exact directory names:

```yaml
unenrolled_subjects:
  - 1.6 Introduction to Financial Analytics
```

Indexing and unscoped searches skip these subjects. Their private source files are left untouched.
