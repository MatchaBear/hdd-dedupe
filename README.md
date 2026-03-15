# hdd-dedupe

Find and review duplicate files across external HDDs on Linux.

## Requirements
```bash
sudo apt install jdupes python3
```

## Usage
```bash
# Dry run first (no files moved)
python3 dedupe.py "/path/to/drive/" --dry-run

# Run for real
python3 dedupe.py "/path/to/drive/"
```

## What it does
- Scans a drive recursively for duplicate files (by content, not filename)
- Keeps the first occurrence in place
- Moves all duplicates to `DUPLICATES_FOR_REVIEW/` on the same drive
- Renames duplicates to show where the kept original lives

## Credits
- **[MatchaBear](https://github.com/MatchaBear)** — project owner
- **[Claude](https://claude.ai) (Anthropic)** — developed via pair programming through Claude.ai web interface
