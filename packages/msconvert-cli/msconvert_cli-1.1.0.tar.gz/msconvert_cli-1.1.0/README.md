# msconvert-cli

Python CLI wrapper for ProteoWizard's MS-Convert that runs in Docker containers. Convert mass spectrometry
files (`.raw`, `.wiff`, `.d`, etc.) to mzML/MGF/... formats with parallel processing.

## Installation

```bash
pip install msconvert-cli
```

**Recommended:** Install with [pipx](https://pipx.pypa.io/) for isolated environments:

```bash
pipx install msconvert-cli
```

**Requirements:** Docker must be installed and running.

## Quick Start

```bash
# Convert with preset config
mscli /path/to/data/ -o ./output --sage

# Parallel processing (1 file per worker for Wine stability)
mscli /data/*.raw -o ./output --casanovo --workers 4

# With resource limits
mscli /data/*.raw -o ./output --sage --workers 4 --worker-cores 2.0 --worker-memory 4g
```

## Presets

Pre-configured msconvert settings for common tools:

| Preset | Format | Details |
|--------|--------|---------|
| `--sage` | mzML | 32-bit, zlib/gzip compression |
| `--biosaur` | mzML | Standard format |
| `--blitzff` | mzML | MS1 only, 32-bit, zlib/gzip |
| `--casanovo` | mzML | MS2 only, m/z [50-2500], denoised, top 200 peaks |
| `--casanovo_mgf` | MGF | Same as casanovo, MGF format |

Use custom configs with `-c my_config.txt` or pass msconvert args directly.

## Common Options

```bash
-o, --output-dir DIR      Output directory (required)
-w, --workers N          Number of parallel workers (default: 1)
-v, --verbose            Enable detailed logging
--log FILE               Custom log file path
-c, --config FILE        Custom msconvert config file

# Docker resource limits per worker
--worker-cores N         CPU cores (e.g., 2.0, 0.5)
--worker-memory SIZE     RAM limit (e.g., 4g, 2048m)
--worker-swap SIZE       Swap limit (set equal to memory to disable)
--worker-shm-size SIZE   Shared memory (default: 512m, increase for large files)
```

## Examples

```bash
# Basic conversion
mscli file.raw -o ./output --sage

# Directory with parallel processing
mscli /data/raw_files/ -o ./output --blitzff --workers 4

# Custom config file
mscli file1.raw file2.raw -o ./output -c my_config.txt

# Verbose logging
mscli /data/*.raw -o ./output --casanovo -v

# Resource-limited workers
mscli /data/*.raw -o ./output --sage \
  --workers 4 \
  --worker-cores 2.0 \
  --worker-memory 4g \
  --worker-swap 4g

# Specific Docker image version
mscli data.raw -o ./output --sage \
  --docker-image proteowizard/pwiz-skyline-i-agree-to-the-vendor-licenses:3.0.23310
```

## Supported Formats

`.raw`, `.wiff`, `.wiff2`, `.d`, `.baf`, `.fid`, `.yep`, `.tsf`, `.tdf`, `.mbi`, `.lcd`, `.ms`, `.cms1`,
`.ms1`, `.cms2`, `.ms2`, `.t2d`

## Development

```bash
# Setup
git clone https://github.com/pgarrett-scripps/msconvert-cli.git
cd msconvert-cli
uv sync

# Quality checks
make check    # Run linters and type checking
make format   # Format code with ruff
make test     # Run tests

# Run locally
uv run mscli --help
```

## License

Apache 2.0 - ProteoWizard license applies to the Docker image.

https://proteowizard.sourceforge.io/index.html

## Citation

If using ProteoWizard, please cite:
A cross-platform toolkit for mass spectrometry and proteomics. Chambers, M.C., MacLean, B., Burke, R., Amode, D., Ruderman, D.L., Neumann, S., Gatto, L., Fischer, B., Pratt, B., Egertson, J., Hoff, K., Kessner, D., Tasman, N., Shulman, N., Frewen, B., Baker, T.A., Brusniak, M.-Y., Paulse, C., Creasy, D., Flashner, L., Kani, K., Moulding, C., Seymour, S.L., Nuwaysir, L.M., Lefebvre, B., Kuhlmann, F., Roark, J., Rainer, P., Detlev, S., Hemenway, T., Huhmer, A., Langridge, J., Connolly, B., Chadick, T., Holly, K., Eckels, J., Deutsch, E.W., Moritz, R.L., Katz, J.E., Agus, D.B., MacCoss, M., Tabb, D.L. & Mallick, P. Nature Biotechnology 30, 918-920 (2012).
