# GRAYBYTE VCOMPRESSOR

![Preview](https://raw.githubusercontent.com/Graybyt3/VCOMPRESSOR-GRAYBYTE/refs/heads/main/VCOMPRESS-GRAYBYTE.png)

## Overview

This Python script compresses all `.mp4` videos in a folder using the **H.265 (HEVC)** codec.  
It makes video files smaller without losing much quality.  

The script helps save storage space and makes it easier to share videos online.

---

## Features

- Compress all `.mp4` videos in a folder automatically.  
- Reduces file sizes while keeping good video quality.  
- Saves compressed videos to a `COMPRESSED` folder.  
- Records any errors in a log file (`compression_errors.log`).  

---

## Requirements

- Python 3.13+  
- **ffmpeg** (`sudo pacman -S ffmpeg`)  
- **cpulimit** (`sudo pacman -S cpulimit`)  
- Python packages:
  ```bash
  pip install colorama tqdm
