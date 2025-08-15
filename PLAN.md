# Developer-Friendly Output Implementation Plan

## Overview
Transform azpype output to be more developer-friendly using Rich for beautiful terminal output and loguru for better logging, while integrating the existing stdout parser.

## Approved Improvements

### 1. Integrate stdout_parser into Copy.execute() ✅ COMPLETED
- **Current**: Returns `(exit_code, raw_stdout)`
- **Target**: Return parsed object with accessible attributes
- **Implementation**:
  ```python
  from .stdout_parser import AzCopyStdoutParser
  
  def execute(self):
      exit_code, stdout = super().execute(args, self.options)
      parsed = AzCopyStdoutParser(stdout)
      parsed.exit_code = exit_code
      parsed.raw_stdout = stdout  # Keep raw available
      return parsed
  ```

### 2. Improve Console Logging Format (Keep Timestamps) ✅ COMPLETED
- **Current**: `2025-08-15 18:12:27,190 - copy - INFO - Run name: 18-12-27--lively-haze-7339`
- **Target**: `2025-08-15 18:12:27 [COPY] Run: lively-haze-7339`
- **Implementation**: Update logging formatter in `logging_config.py`

### 3. Add Rich-based Summary Method ✅ COMPLETED
- **Target**: Add `summary()` method to `AzCopyStdoutParser` using Rich
- **Features**:
  - Status indicators with colors/icons
  - Formatted tables for transfer stats
  - Progress-style output for bytes transferred

### 4. Integrate Rich for Pretty Output ✅ COMPLETED
- **Add** Rich console for structured output
- **Features**:
  - Formatted panels for command output
  - Syntax highlighting for commands
  - Status-based colors and icons

## New Improvements (Phase 2)

### 5. Remove Redundant Command Output
- **Issue**: Command and output appear twice (in logs and Rich panels)
- **Target**: Show Rich panels only, keep detailed logging in files only
- **Implementation**: Modify base_command.py to separate console vs file logging

### 6. Improve Flag Config Display
- **Issue**: Flag config shows null values and isn't Rich-formatted
- **Target**: Rich-formatted config display with only non-null values
- **Implementation**: Create Rich panel for config, filter nulls

### 7. Improve Command Display Readability
- **Issue**: Command shown as one long line with full binary path
- **Target**: Multi-line format with 'azcopy' + named arguments
- **Implementation**: 
  ```
  azcopy copy \
    source: ./payload \
    destination: https://storage.../sandbox \
    --overwrite=ifSourceNewer \
    --recursive=True
  ```

## Implementation Plan

### Phase 1: Dependencies
- Add to `requirements.txt`:
  ```
  rich>=13.0.0
  loguru>=0.7.0
  ```

### Phase 2: Enhanced Stdout Parser with Rich
- **File**: `azpype/commands/stdout_parser.py`
- **Changes**:
  ```python
  from rich.console import Console
  from rich.table import Table
  from rich.panel import Panel
  
  class AzCopyStdoutParser:
      def summary(self) -> str:
          """Return Rich-formatted summary"""
          console = Console()
          
          # Status with icon
          status_icon = "✅" if "Completed" in self.final_job_status else "⚠️"
          
          # Create summary table
          table = Table(title=f"{status_icon} Transfer Summary")
          table.add_column("Metric", style="cyan")
          table.add_column("Value", style="magenta")
          
          table.add_row("Status", self.final_job_status)
          table.add_row("Files Transferred", str(self.number_of_file_transfers_completed))
          table.add_row("Files Skipped", str(self.number_of_file_transfers_skipped))
          table.add_row("Files Failed", str(self.number_of_file_transfers_failed))
          table.add_row("Elapsed Time", f"{self.elapsed_time} minutes")
          table.add_row("Bytes Transferred", f"{self.total_bytes_transferred:,} bytes")
          table.add_row("Job ID", self.job_id)
          
          return console.render_str(table)
  ```

### Phase 3: Loguru Integration
- **File**: `azpype/logging_config.py`
- **Changes**:
  ```python
  from loguru import logger
  from rich.console import Console
  
  class CopyLogger:
      def __init__(self, name, ...):
          # Configure loguru with Rich
          logger.remove()  # Remove default handler
          
          # File logging (detailed)
          logger.add(
              str(self.run_log_directory / 'azpype.log'),
              format="{time} | {level} | {name} | {message}",
              level="DEBUG"
          )
          
          # Console logging (pretty)
          logger.add(
              sys.stderr,
              format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> <level>[{level}]</level> <cyan>{extra[prefix]}</cyan> {message}",
              level="INFO"
          )
          
          self.logger = logger.bind(prefix="COPY")
  ```

### Phase 4: Rich Command Output
- **File**: `azpype/commands/base_command.py`
- **Changes**:
  ```python
  from rich.console import Console
  from rich.panel import Panel
  from rich.syntax import Syntax
  
  def execute(self, args, options):
      console = Console()
      command = self.build_command(args, options)
      
      # Pretty command display
      cmd_text = ' '.join(command)
      syntax = Syntax(cmd_text, "bash", theme="monokai", word_wrap=True)
      console.print(Panel(syntax, title="🚀 Executing Command", border_style="blue"))
      
      try:
          result = subprocess.run(...)
          # Pretty output display
          if result.stdout:
              console.print(Panel(result.stdout, title="📋 Output", border_style="green"))
          return result.returncode, result.stdout
      except subprocess.CalledProcessError as e:
          # Pretty error display
          console.print(Panel(f"[red]{e.stderr}[/red]", title="❌ Error", border_style="red"))
          return e.returncode, e.stdout
  ```

### Phase 5: Update Copy Command
- **File**: `azpype/commands/copy.py`
- **Changes**:
  ```python
  from .stdout_parser import AzCopyStdoutParser
  from rich.console import Console
  
  def execute(self):
      console = Console()
      
      # Execute with pretty output
      exit_code, stdout = super().execute(args, self.options)
      
      # Parse and enhance
      parsed = AzCopyStdoutParser(stdout)
      parsed.exit_code = exit_code
      parsed.raw_stdout = stdout
      
      # Show pretty summary
      console.print(parsed.summary())
      
      return parsed
  ```

## File Changes Summary
1. `requirements.txt` - Add rich, loguru
2. `azpype/commands/stdout_parser.py` - Add Rich summary method
3. `azpype/logging_config.py` - Replace logging with loguru+Rich
4. `azpype/commands/base_command.py` - Add Rich command/output display
5. `azpype/commands/copy.py` - Return parsed object, show summary

## Example Expected Output
```
2025-08-15 18:12:27 [INFO] [COPY] Run: lively-haze-7339

╭─────────────── 🚀 Executing Command ───────────────╮
│ azcopy copy ./payload https://storage.../sandbox   │
│ --overwrite=ifSourceNewer --recursive=True         │
╰─────────────────────────────────────────────────────╯

╭─────────────────── 📋 Output ───────────────────────╮
│ INFO: SPN Auth via secret succeeded.               │
│ INFO: Authenticating to destination using Azure AD │
│ Job 870b6071-0463-6549-4677-117cbc7498e9 started   │
╰─────────────────────────────────────────────────────╯

      ✅ Transfer Summary
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric          ┃ Value                 ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ Status          │ CompletedWithSkipped  │
│ Files Transferred│ 0                     │
│ Files Skipped   │ 1                     │
│ Elapsed Time    │ 0.0333 minutes        │
│ Job ID          │ 870b6071-0463-6549... │
└─────────────────┴───────────────────────┘
```

## Testing
- Update `copy_sanity_test.py` to work with new return type
- Ensure backward compatibility where possible
- Test Rich output in different terminal environments