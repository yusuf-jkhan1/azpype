# Azpype 🚀

A Python wrapper for AzCopy that feels native and gets out of your way.

## Why Azpype?

**Performance**: AzCopy, written in Go, significantly outperforms Python's Azure SDK for bulk transfers. Go's goroutines provide true parallelism for file I/O and network operations, while Python's GIL limits concurrency. For large-scale transfers, AzCopy can be 5-10x faster.

**Python Integration**: But switching between Python and bash scripts breaks your workflow. Azpype solves this by wrapping AzCopy in a native Python interface. Now you can:
- Write pure Python scripts with data processing before and after transfers
- Capture and parse output programmatically
- Handle errors with try/except blocks
- Integrate with your existing Python data pipeline

**Additional Benefits**:
- **Zero-configuration setup** - Bundles the right AzCopy binary for your platform
- **Smart defaults** - YAML config for common settings, override with kwargs when needed
- **Rich logging** - Structured logs with loguru, daily rotation, and visual command output
- **Built-in validation** - Checks auth, network, and paths before executing
- **Job management** - List, resume, and recover failed transfers programmatically

## Installation

```bash
pip install azpype
```

That's it. Azpype automatically:
- Downloads the appropriate AzCopy binary (v10.18.1) for your platform
- Creates a config directory at `~/.azpype/`
- Sets up a default configuration file

## Quick Start

### Basic Copy Operation

```python
from azpype.commands.copy import Copy

# Upload a local directory to Azure Blob Storage
Copy(
    source="./data",
    destination="https://myaccount.blob.core.windows.net/mycontainer/"
).execute()

# Download from Azure to local
Copy(
    source="https://myaccount.blob.core.windows.net/mycontainer/data/",
    destination="./downloads"
).execute()
```

### Working with Return Values

The `execute()` method returns a tuple of (exit_code, output):

```python
# Capture and inspect the results
exit_code, output = Copy(
    source="./data",
    destination="https://myaccount.blob.core.windows.net/mycontainer/"
).execute()

if exit_code == 0:
    print("Transfer successful!")
    # Parse the output for job details
    if "Job" in output:
        job_id = output.split("Job ")[1].split(" ")[0]
        print(f"Job ID: {job_id}")
else:
    print(f"Transfer failed with code: {exit_code}")
    
# Use in your data pipeline
def process_and_upload(data_path):
    # Pre-process data
    prepare_data(data_path)
    
    # Upload with error handling
    exit_code, output = Copy(
        source=data_path,
        destination="https://myaccount.blob.core.windows.net/processed/"
    ).execute()
    
    if exit_code != 0:
        raise Exception(f"Upload failed: {output}")
    
    # Continue with post-processing
    cleanup_local_data(data_path)
    return output
```

## Authentication

### Service Principal (Recommended)

Set these environment variables:

```python
import os

os.environ["AZCOPY_TENANT_ID"] = "your-tenant-id"
os.environ["AZCOPY_SPA_APPLICATION_ID"] = "your-app-id"  
os.environ["AZCOPY_SPA_CLIENT_SECRET"] = "your-secret"
os.environ["AZCOPY_AUTO_LOGIN_TYPE"] = "SPN"
```

Or use a `.env` file:

```bash
# .env
AZCOPY_TENANT_ID=your-tenant-id
AZCOPY_SPA_APPLICATION_ID=your-app-id
AZCOPY_SPA_CLIENT_SECRET=your-secret
AZCOPY_AUTO_LOGIN_TYPE=SPN
```

```python
from dotenv import load_dotenv
load_dotenv()

from azpype.commands.copy import Copy
Copy(source, destination).execute()
```

### SAS Token

Pass the token directly (without the leading `?`):

```python
Copy(
    source="./data",
    destination="https://myaccount.blob.core.windows.net/mycontainer/",
    sas_token="sv=2021-12-02&ss=b&srt=sco&sp=rwdlacyx..."
).execute()
```

## Configuration System

Azpype uses a two-level configuration system:

### 1. YAML Config File (Defaults)

Located at `~/.azpype/copy_config.yaml`:

```yaml
# Overwrite strategy at destination
overwrite: 'ifSourceNewer'  # Options: 'true', 'false', 'prompt', 'ifSourceNewer'

# Recursive copy for directories
recursive: true

# Create MD5 hashes during upload
put-md5: true

# Number of parallel transfers
concurrency: 16
```

### 2. Runtime Overrides (kwargs)

Override any config value at runtime:

```python
Copy(
    source="./data",
    destination="https://...",
    overwrite="true",           # Override YAML setting
    concurrency=32,              # Increase parallelism
    dry_run=True,               # Test without copying
    exclude_pattern="*.tmp"     # Add exclusion pattern
).execute()
```

## Common Usage Patterns

### Upload with Patterns

```python
# Upload only Python files
Copy(
    source="./project",
    destination="https://myaccount.blob.core.windows.net/code/",
    include_pattern="*.py",
    recursive=True
).execute()

# Exclude temporary files
Copy(
    source="./data",
    destination="https://myaccount.blob.core.windows.net/backup/",
    exclude_pattern="*.tmp;*.log;*.cache",
    recursive=True
).execute()
```

### Sync with Overwrite Control

```python
# Only upload newer files
Copy(
    source="./local-data",
    destination="https://myaccount.blob.core.windows.net/data/",
    overwrite="ifSourceNewer",
    recursive=True
).execute()

# Never overwrite existing files
Copy(
    source="./archive",
    destination="https://myaccount.blob.core.windows.net/archive/",
    overwrite="false"
).execute()
```

### Dry Run Testing

```python
# See what would be copied without actually transferring
Copy(
    source="./large-dataset",
    destination="https://myaccount.blob.core.windows.net/datasets/",
    dry_run=True
).execute()
```

## Job Management

Resume failed or cancelled transfers:

```python
from azpype.commands.jobs import Jobs

jobs = Jobs()

# List all jobs
exit_code, output = jobs.list()

# Resume a specific job
jobs.resume(job_id="abc123-def456")

# Find and resume the last failed job
job_id = jobs.last_failed()
if job_id:
    jobs.resume(job_id=job_id)

# Auto-recover (find and resume last failed)
jobs.recover_last_failed()
```

## Logging

Azpype provides rich logging with automatic rotation:

- **Location**: `~/.azpype/azpype_YYYY-MM-DD.log`
- **Rotation**: Daily, with 7-day retention and gzip compression
- **Console output**: Color-coded with progress indicators
- **Command details**: Full command, exit codes, and stdout/stderr captured

Example log output:
```
2025-08-15 19:09:29 | INFO | COPY | Starting copy operation
2025-08-15 19:09:29 | INFO | COPY | ========== COMMAND EXECUTION ==========
2025-08-15 19:09:29 | INFO | COPY | Command: azcopy copy ./data https://...
2025-08-15 19:09:29 | INFO | COPY | Exit Code: 0
2025-08-15 19:09:29 | INFO | COPY | STDOUT:
2025-08-15 19:09:29 | INFO | COPY |   Job abc123 has started
2025-08-15 19:09:29 | INFO | COPY |   100.0%, 10 Done, 0 Failed, 0 Pending
```

## Available Options

Common options for the `Copy` command:

| Option | Type | Description |
|--------|------|-------------|
| `overwrite` | str | How to handle existing files: 'true', 'false', 'prompt', 'ifSourceNewer' |
| `recursive` | bool | Include subdirectories |
| `include_pattern` | str | Include only matching files (wildcards supported) |
| `exclude_pattern` | str | Exclude matching files (wildcards supported) |
| `dry_run` | bool | Preview what would be copied without transferring |
| `concurrency` | int | Number of parallel transfers |
| `block_size_mb` | float | Block size for large files (in MiB) |
| `put_md5` | bool | Create MD5 hashes during upload |
| `check_length` | bool | Verify file sizes after transfer |
| `as_subdir` | bool | Place folder sources as subdirectories |

## License
MIT
