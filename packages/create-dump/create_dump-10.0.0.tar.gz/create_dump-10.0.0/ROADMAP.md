## 🗺️ Feature Roadmap

### 🟩 Basic: Quality-of-Life & Usability Enhancements ✨

These are low-effort, high-value additions that extend our existing framework.

1.  **`TODO` / `FIXME` Scanner:**
    
    * **What:** Create a new `TodoScanner` middleware (just like `SecretScanner`). It would scan files for keywords like `TODO:`, `FIXME:`, `HACK:`, or `TECH_DEBT:` and append a summary of all found items to the bottom of the Markdown dump.
    * **Why:** This turns a simple code dump into an actionable **technical debt report**, which is incredibly valuable for SREs and managers during audits or sprint planning.

2.  **Per-Project Config Discovery (`batch` mode):**
    
    * **What:** Enhance `run_batch` logic. When it enters a subdirectory (e.g., `./services/api`), it should check for a `services/api/create_dump.toml` or `services/api/pyproject.toml` file and use *that* configuration for the `run_single` call.
    * **Why:** This is a true monorepo feature. It allows a service (`api`) to have different `include`/`exclude` patterns or secret scanning rules than another service (`web`), making the `batch` command far more powerful and flexible.

3.  **Simple Push Notifications (`ntfy.sh`):**
    
    * **What:** Add a `--notify-topic <topic>` flag. When a dump (especially a `watch` or `batch` run) completes, it sends a simple HTTP POST to `ntfy.sh/YourTopic`.
    * **Why:** This provides a dead-simple, zero-dependency notification system for long-running tasks, which is perfect for SREs monitoring a CI job or a local file watch.

4.  **Configuration Profiles:**
    
    * **Why:** A developer's local run (`--watch`) and a CI run (`--scan-secrets --archive`) have very different needs. Profiles let us define these sets of flags in `pyproject.toml`.
    * **Implementation:** Add a `--profile <name>` flag. The `load_config` function would merge `[tool.create-dump]` with `[tool.create-dump.profile.<name>]` if specified.

5.  **Dump Header Statistics:**
    
    * **Why:** Adds immediate, high-level context. "Is this a big project or a small one?"
    * **Implementation:** In `workflow/single.py`, after collection and filtering (but before processing), add a small utility to calculate `total_lines_of_code` and `total_files` from the `files_list`. Pass this to the `MarkdownWriter` / `JsonWriter`.

6.  **Custom Secret Scanning Rules:**
    
    * **Why:** A project might have internal tokens (e.g., `MYAPP_...`) that `detect-secrets` doesn't know about.
    * **Implementation:** Add a `config.custom_secret_patterns` list. In `scanning.py`, this list would be used to build a simple regex scanner that runs *in addition* to the main `detect-secrets` scan.

---

### 🟨 Moderate: CI/CD & SRE Integrations 🚀

These features focus on integrating `create-dump` into automated, production-level SRE and DevOps pipelines.

1.  **Cloud Storage Uploads (S3 / GCS / Azure Blob):**
    
    * **What:** Add a `--upload-s3 <bucket/path>` (or GCS/Azure) flag. After the `.md` and `.sha256` (and/or `.zip`) are created, the tool securely uploads them to the specified cloud bucket using `boto3`, `google-cloud-storage`, etc.
    * **Why:** This is the **most important "enterprise" feature.** Dumps are for forensics, compliance, and sharing. They *must* live in a durable, centralized, and secure location, not just on a local disk. This makes the tool 10x more useful for teams.

2.  **Database Dump Integration:**
    
    * **What:** Add a `--pg-dump <connection_string>` or `--mysql-dump` flag. The tool would securely execute `pg_dump` / `mysqldump`, capture the SQL output, and include it as `_db_dump.sql` inside the generated archive.
    * **Why:** This transforms the tool from a "code dump" to a true **application snapshot**. For debugging, a snapshot of *both* the code and the data (from a dev/staging DB) is the gold standard.

3.  **ChatOps Notifications (Slack / Discord / Telegram):**
    
    * **What:** Add a `--notify-slack <webhook_url>` flag. On success or failure, send a formatted JSON payload to the webhook with the dump name, file size, and status.
    * **Why:** This is the next level of integration. It allows `create-dump` to plug directly into a team's CI/CD or SRE alerting workflows.

4.  **Cloud Storage Uploader:**
    
    * **Why:** Dumps created in CI are useless if they're lost when the runner is terminated. We need to persist them. This was a stated limitation in the `README.md`.
    * **Implementation:** Add a new `uploader.py` module with `S3Uploader` / `GCSUploader` classes (using `boto3`/`google-cloud-storage`). In `workflow/single.py`, after the checksum is written, check for new CLI flags like `--upload-s3-bucket <name>`. This would run in `anyio.to_thread.run_sync`.

5.  **"Diff-Only" Dump Format:**
    
    * **Why:** When using `--diff-since`, we're currently dumping the *entire file* that changed, not the *diff itself*. For LLM analysis, a clean `.diff` or `.patch` format is often far more useful and concise.
    * **Implementation:** Add `--format=diff`. In `GitDiffCollector`, instead of just getting file names, also run `git diff <ref> -- {file_path}` for each file. The `MarkdownWriter` would then wrap this output in a ````diff` block.

6.  **File Hashing & Caching:**
    
    * **Why:** In a large monorepo, `--watch` mode is inefficient. It re-processes all files even if only one changed.
    * **Implementation:** Create a cache file (e.g., `.create_dump_cache.json`) storing `{ "path": "sha256_hash_of_content" }`. In `FileProcessor.process_file`, hash the raw content. If the hash matches the cache, skip processing and reuse the previous result. This would make `--watch` mode instantaneous on large projects.

---

### 🟥 Advanced: Platform & Scalability Architecture 🧠

These features represent a significant architectural evolution, moving the tool from a CLI to a true platform component for massive-scale operations.

1.  **Official GitHub Action (`create-dump-action`):**
    
    * **What:** Create a new repository for a dedicated GitHub Action. This action would run `create-dump` (likely using `--diff-since ${{ github.event.before }}`) to generate a dump of *only the files changed in the PR*. It would then (ideally) upload this as a build artifact.
    * **Why:** This provides a powerful code review tool. A reviewer can download a single, self-contained file with all PR changes, checksums, and secret-scan results, rather than browsing the GitHub UI.

2.  **Interactive TUI Explorer:**
    
    * **What:** A new command, `create-dump explore <dump_file.md>`. This would open a Terminal UI (using **`textual`**) that parses the dump file and presents a browsable, searchable file tree, allowing you to read the code *inside* the dump without rehydrating it.
    * **Why:** This enhances the `rollback` workflow. Instead of rehydrating 500 files just to read one, you can instantly explore the snapshot from your terminal.

3.  **Persistent Server Mode:**
    
    * **What:** Add a `create-dump serve` command. This would launch a lightweight **FastAPI** server that exposes the Prometheus metrics (as it already does) and also provides a simple REST API to:
        * Trigger a new dump (e.g., `POST /dump`) via a webhook.
        * List all available dumps (from the `dest` directory).
        * Download a specific dump file.
    * **Why:** This turns `create-dump` from a CLI tool into a lightweight, persistent service, allowing it to be integrated into any CI/CD system (GitLab, Jenkins, etc.) that can call a webhook.

4.  **Direct-to-Archive Streaming:**
    
    * **Why:** The current flow (`read file -> write tempfile -> read tempfile -> write .md -> read .md -> write .zip`) is durable but has high disk I/O. For a 1GB dump, this is very slow.
    * **Implementation:** Create a new `StreamingMarkdownWriter` that writes directly to a `tarfile.TarFile` object (which can be streamed). `FileProcessor` would `yield` file content, which the writer would format as a markdown chunk and write *immediately* into the tar stream, bypassing the large intermediate `.md` file entirely.

5.  **Remote/Centralized Configuration:**
    
    * **Why:** In a large organization, you don't want 100 teams defining their own (potentially insecure) dump rules. An SRE team needs to enforce a central policy (e.g., "all dumps *must* scan for secrets").
    * **Implementation:** In `core.py`, update `load_config` to check for an environment variable like `CREATE_DUMP_CONFIG_URI`. If set (e.g., `s3://my-org-config/create-dump.toml`), the tool would fetch and use that config instead of local files.

6.  **GitHub App / PR Commenting Bot:**
    
    * **Why:** This is the ultimate CI integration. A developer pushes a commit, and a bot automatically runs `create-dump --diff-since main` and posts the result as a PR comment.
    * **Implementation:** This would be a separate (but related) project. Create a new `cli/github.py` command `create-dump post-pr --file <dump.md> --pr-url <url>`. This command would use the GitHub API to post the file's content as a comment.
    
---
