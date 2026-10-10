# VCOMPRESSOR-GRAYBYTE

![Preview](https://raw.githubusercontent.com/Graybyt3/VCOMPRESSOR-GRAYBYTE/refs/heads/main/vCompress-Graybyte.png)

**Multi-format H.265 (HEVC) Video Compressor**  
Batch compress videos with real-time progress, resumable processing, CPU limiting, and optional original-file cleanup.

**Main script:** `vCompress-Graybyte_v10.py`

---

## Features

- **H.265 / HEVC encoding** via `libx265` (excellent quality-to-size ratio)
- **Batch processing** of all supported videos in a folder
- **Resumable** – already processed files are skipped (logged in `VCOM-CONFIG/processed_files.log`)
- **Real-time progress bar** with elapsed time + estimated remaining time (speed-based)
- **CPU limiting** via `cpulimit` (prevents system overload)
- **Configurable** CRF, preset, threads
- **Small-file handling** – files under 20 MB are moved to a `SMALL-SIZE` folder
- **Optional delete original** after successful compression (configurable)
- **Clean output filenames** (removes common site tags, uppercases, etc.)
- **Colored terminal UI** + rainbow progress bar
- **Logging** – execution log + error log
- **Config persistence** – settings saved to `config.txt` for next runs

---

## Supported Formats

`.mp4` `.mkv` `.mpeg` `.mpg` `.ts` `.mov` `.avi` `.webm` `.flv` `.m4v` `.wmv` `.vob` `.ogv`

---

## Requirements

| Dependency | Purpose |
|------------|---------|
| **Python 3.8+** | Runtime |
| **FFmpeg** + **ffprobe** | Encoding & duration detection |
| **cpulimit** | CPU usage limiting |
| **colorama** | Colored terminal output |
| **tqdm** | Progress bar |

### Install dependencies

```bash
# Debian / Ubuntu / Garuda / Arch
sudo pacman -S ffmpeg cpulimit python-pip   # or apt install ffmpeg cpulimit
pip install colorama tqdm
```

---

## Quick Start

```bash
python vCompress-Graybyte_v10.py
```

1. First run → interactive configuration (CPU limit, CRF, preset, threads, delete-original, input folder)
2. Settings are saved to `config.txt`
3. Subsequent runs load `config.txt` and ask for confirmation
4. Compressed files are written to `<folder-name>-ENCODED/`

---

## Configuration

### Interactive (first run / no config.txt)

| Setting | Default | Range / Options |
|---------|---------|-----------------|
| CPU Limit | 600% | 1–1000 (capped) |
| CRF | 28 | 27–31 |
| Preset | faster | superfast / veryfast / faster / fast / medium / slow / … |
| Threads | 4 | 4–8 |
| Delete Original | n | y / n |
| Input Folder | Current working directory | Any valid path |

### config.txt example

```text
CPULIMIT: 600
CRF: 28
PRESET: faster
THREADS: 4
VIDEO CODEC: libx265 (HEVC)
AUDIO: copy (no re-encoding)
DELETE_ORIGINAL: n
```

---

## Output Structure

```
your-video-folder/
├── video1.mp4
├── video2.mkv
├── your-video-folder-ENCODED/
│   ├── VIDEO1 __ENC-L-28__.mp4
│   └── VIDEO2 __ENC-L-28__.mkv
├── SMALL-SIZE/                  # files < 20 MB moved here
└── VCOM-CONFIG/
    ├── processed_files.log
    ├── execution_log.txt
    └── compression_errors.log
```

---

## Encoding Parameters Explained

### CRF (Constant Rate Factor)
- **27** → Highest quality, larger files
- **28** → Recommended balance (default)
- **29–30** → Smaller files, still good quality
- **31** → Maximum compression (visible quality loss starts)

### Presets
- `superfast` / `veryfast` / `faster` → Speed priority
- `medium` → Balanced
- `slow` / `slower` / `veryslow` → Best compression

### CPU Limit
- 600–800% → Safe daily use
- 850–1000% → Faster encoding (higher heat / power)

---

## Important Notes

- **Delete Original** only runs **after** a confirmed successful encode.
- Already-processed files and existing output files are skipped automatically.
- The script is designed for **owned / authorized media only**.
- Requires `cpulimit` – without it the process will fail.

```
