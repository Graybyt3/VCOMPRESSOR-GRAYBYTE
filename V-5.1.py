import os
import subprocess
import time
from datetime import timedelta
from pathlib import Path
import logging
import random
import re
from colorama import init, Fore, Style
from tqdm import tqdm

init(autoreset=True)

# ==================== DEFAULT CONFIGS & PATHS ====================
DEFAULT_CPU_LIMIT = 600
VIDEO_EXTENSIONS = (".mp4", ".mkv", ".mpeg", ".mpg", ".ts", ".mov", ".avi", ".webm", ".flv", ".m4v", ".wmv", ".vob", ".ogv")
CONFIG_DIR = Path.cwd() / "VCOM-CONFIG"
CONFIG_DIR.mkdir(exist_ok=True)
PROCESSED_LOG = CONFIG_DIR / "processed_files.log"
EXECUTION_LOG = CONFIG_DIR / "execution_log.txt"
ERROR_LOG = CONFIG_DIR / "compression_errors.log"

logging.basicConfig(filename=ERROR_LOG, level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def colored_ascii(text):
    colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA, Fore.BLUE]
    return "".join(random.choice(colors) + c for c in text if c != " ")

ASCII_BANNER = colored_ascii(
"\n\n\n█▀▀ █▀█ ▄▀█ █▄█ █▄▄ █▄█ ▀█▀ █▀▀   █░█ █ █▀▄ ▄▄ █▀▀ █▀█ █▀▄▀█ █▀█ █▀█ █▀▀ █▀ █▀ █▀█ █▀█\n"
"█▄█ █▀▄ █▀█ ░█░ █▄█ ░█░ ░█░ ██▄   ▀▄▀ █ █▄▀ ░░ █▄▄ █▄█ █░▀░█ █▀▀ █▀▄ ██▄ ▄█ ▄█ █▄█ █▀▄\n\n\n"
)

EXPLANATION = f"""
{Fore.YELLOW}🚀 This Script Compresses All Supported Videos In The Folder
💾 Makes Files Smaller With H.265 (HEVC) While Keeping Excellent Quality
📊 Real-time Progress • Elapsed/Remaining Time • Space Savings Displayed
⚙️ Tweak CRF & Preset For Your Perfect Quality/Speed Balance
🖥️ CPU Limit Keeps Your System Happy
{Style.RESET_ALL}
"""

EXPLANATIONL = f"{Fore.GREEN}🎬 Multi-format H.265 Video Compressor | Resumable | Enhanced Visuals 🔥{Style.RESET_ALL}\n"

def strip_ansi(text):
    return re.sub(r'\x1b\[[0-9;]*m', '', text)

def log_only(text=""):
    if text:
        with EXECUTION_LOG.open("a", encoding="utf-8") as f:
            f.write(strip_ansi(text).rstrip() + "\n")

def log_and_print(text=""):
    if text:
        print(text)
        log_only(text)

# Fixed rainbow bar: use ASCII 2588 (full block) with direct ANSI codes, no colorama prefixes
RAINBOW_BLOCK = "".join([
    "\033[31m█\033[33m█\033[32m█\033[36m█\033[34m█\033[35m█"  # RED YELLOW GREEN CYAN BLUE MAGENTA
] * 14)[:80] + "\033[0m"  # reset at the end (safe)

class RainbowBar(tqdm):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('ncols', 80)
        kwargs.setdefault('leave', False)
        kwargs.setdefault('ascii', RAINBOW_BLOCK)
        kwargs.setdefault('bar_format', '{l_bar}{bar}{r_bar}')
        super().__init__(*args, **kwargs)

def load_processed():
    if not PROCESSED_LOG.exists():
        return set()
    with PROCESSED_LOG.open("r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}

def mark_processed(filepath):
    with PROCESSED_LOG.open("a", encoding="utf-8") as f:
        f.write(str(filepath) + "\n")

print(ASCII_BANNER)
print(EXPLANATION)
print(EXPLANATIONL)
print()

log_and_print(f"{Fore.CYAN}🔥════════════════════════════════════════════════════════════════════════════════🔥{Style.RESET_ALL}\n")

cpu_input = input(f"{Fore.RED}🔥ENTER CPU LIMIT % (ENTER = DEFAULT {DEFAULT_CPU_LIMIT}): {Style.RESET_ALL}").strip()
CPU_LIMIT = int(cpu_input) if cpu_input.isdigit() and 1 <= int(cpu_input) <= 1600 else DEFAULT_CPU_LIMIT

if CPU_LIMIT > 600:
    print(f"{Fore.YELLOW}⚠️CPU LIMIT CAPPED AT 600% FOR SYSTEM STABILITY.{Style.RESET_ALL}")
    CPU_LIMIT = 600

input_path = input(f"{Fore.RED}📂ENTER VIDEO FOLDER PATH (ENTER = CURRENT DIRECTORY): {Style.RESET_ALL}").strip()
input_dir = Path(input_path) if input_path else Path.cwd()

if not input_dir.exists() or not input_dir.is_dir():
    print(f"{Fore.RED}❌INVALID PATH → FALLING BACK TO CURRENT DIRECTORY.{Style.RESET_ALL}")
    input_dir = Path.cwd()

folder_name = input_dir.name
output_dir = input_dir.with_name(f"{folder_name.upper()}-ENCODED")
output_dir.mkdir(exist_ok=True)

print(f"{Fore.GREEN}💿 OUTPUT DIRECTORY → {output_dir}{Style.RESET_ALL}\n")

if EXECUTION_LOG.exists():
    EXECUTION_LOG.unlink()

log_only("H.265 Video Compressor Run")
log_only(f"CPU LIMIT: {CPU_LIMIT}% | INPUT: {input_dir} | OUTPUT: {output_dir}\n")

processed_files = load_processed()
VF_CHAIN = None  # Visual enhancement disabled

def get_duration(file):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(file)],
            capture_output=True, text=True, check=True
        )
        return float(result.stdout.strip())
    except:
        return None

def get_size(file):
    return os.path.getsize(file) / (1024 * 1024)

def clean_filename(name):
    name = name.replace("-compressed", "").replace("~EncodeD", "").replace("-ENC", "").replace("-enc", "")
    name = re.sub(r'[_-]+', ' ', name)
    name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name.upper()

def get_new_filename(original_path):
    cleaned_stem = clean_filename(original_path.stem)
    ext = original_path.suffix.lower()
    return output_dir / f"{cleaned_stem}__ENC__{ext}"

def parse_progress_time(line):
    line = line.strip()
    if line.startswith("out_time_ms="):
        val = line.split("=", 1)[1]
        if val != "N/A":
            try:
                return int(val) / 1_000_000
            except ValueError:
                pass
    elif line.startswith("out_time="):
        val = line.split("=", 1)[1]
        if val != "N/A":
            try:
                h, m, s_ms = val.split(":")
                s, ms = s_ms.split(".")
                return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000000
            except:
                pass
    return None

def process_video(file):
    try:
        full_path = str(file.resolve())
        if full_path in processed_files:
            msg = f"{Fore.MAGENTA}⏭️RESUMED | ALREADY ENCODED → {file.name}{Style.RESET_ALL}"
            log_and_print(msg)
            return True

        out_file = get_new_filename(file)
        if out_file.exists():
            msg = f"{Fore.MAGENTA}⏭️SKIPPING | OUTPUT EXISTS → {out_file.name}{Style.RESET_ALL}"
            log_and_print(msg)
            mark_processed(full_path)
            return True

        original_size = get_size(file)
        duration = get_duration(file) or 0
        duration_str = str(timedelta(seconds=int(duration))) if duration else "Unknown"

        log_and_print(f"{Fore.CYAN}🔥════════════════════════════════════════════════════════════════════════════════🔥{Style.RESET_ALL}\n")
        log_and_print(f"\n{Fore.YELLOW}🎞️PROCESSING → {Style.RESET_ALL}{Fore.WHITE}{file.name}{Style.RESET_ALL}\n")
        log_and_print(f"📦 ORIGINAL SIZE: {Fore.YELLOW}{original_size:.2f} MB{Style.RESET_ALL} | ⏱️ DURATION: {Fore.GREEN}{duration_str}{Style.RESET_ALL}\n")

        start_time = time.time()
        cmd = [
            "cpulimit", "-l", str(CPU_LIMIT), "--", "ffmpeg",
            "-i", str(file),
            "-c:v", "libx265", "-crf", "28", "-preset", "medium",
            "-c:a", "copy",
            "-threads", "4",
            "-progress", "pipe:1", "-nostats"
        ]
        if VF_CHAIN:
            cmd.extend(["-vf", VF_CHAIN])
        cmd.append(str(out_file))

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

        current_seconds = 0
        bar = RainbowBar(total=100, desc="", ncols=80, leave=False)
        bar.set_description(f"{Fore.YELLOW}⏳ELAPSED: {Style.RESET_ALL}{Fore.GREEN}0:00:00{Style.RESET_ALL} | ⏱️ REMAINING: {Fore.YELLOW}{duration_str}{Style.RESET_ALL}")

        while process.poll() is None:
            line = process.stdout.readline()
            if not line:
                continue
            parsed = parse_progress_time(line)
            if parsed is not None:
                current_seconds = parsed

            if duration > 0:
                progress = min(int((current_seconds / duration) * 100), 100)
                bar.n = progress
                elapsed = timedelta(seconds=int(time.time() - start_time))
                remaining_sec = max(int(duration - current_seconds), 0)
                remaining_str = str(timedelta(seconds=remaining_sec))
                bar.set_description(
                    f"⏳ELAPSED: {Fore.GREEN}{elapsed}{Style.RESET_ALL} | "
                    f"⏱️ REM: {Fore.YELLOW}{remaining_str}{Style.RESET_ALL}"
                )
                bar.refresh()
            time.sleep(0.05)

        bar.close()

        elapsed = timedelta(seconds=int(time.time() - start_time))
        new_size = get_size(out_file) if out_file.exists() else 0
        space_saved = original_size - new_size

        if process.returncode == 0 and out_file.exists() and new_size > 0:
            success_msg = f"{Fore.GREEN}✅ SUCCESS → {out_file.name}{Style.RESET_ALL}\n"
            terminal_line = (
                f"⏱️ TIME TAKEN: {elapsed} | "
                f"{Fore.RED}OLD: {original_size:.2f} MB{Style.RESET_ALL}{Fore.WHITE} → {Style.RESET_ALL}"
                f"{Fore.GREEN}NEW: {new_size:.2f} MB{Style.RESET_ALL} | "
                f"💾 SAVED: {Fore.GREEN if space_saved >= 0 else Fore.RED}"
                f"{space_saved:+.2f} MB"
                f"{Style.RESET_ALL}\n"
            )
            log_and_print(success_msg)
            log_and_print(terminal_line)
            mark_processed(full_path)
            return True
        else:
            error = process.stderr.read()
            logging.error(f"Failed {file}: {error}")
            fail_msg = f"{Fore.RED}❌FAILED → {file.name} | Check {ERROR_LOG}{Style.RESET_ALL}\n"
            log_and_print(fail_msg)
            log_and_print(f"{Fore.CYAN}🔥════════════════════════════════════════════════════════════════════════════════🔥{Style.RESET_ALL}")
            if out_file.exists():
                out_file.unlink()
            return False

    except Exception as e:
        if 'bar' in locals():
            bar.close()
        err = f"{Fore.RED}💥EXCEPTION | {file.name}: {e}{Style.RESET_ALL}\n"
        log_and_print(err)
        logging.error(f"Exception: {file} | {e}")
        return False

def main():
    video_files = [f for f in input_dir.iterdir() if f.suffix.lower() in VIDEO_EXTENSIONS and f.is_file()]
    to_process = [f for f in video_files if str(f.resolve()) not in processed_files]

    summary = f"{Fore.MAGENTA}📊TOTAL VIDEOS: {len(video_files)} | ✅ ALREADY DONE: {len(processed_files)} | ⏳ TO PROCESS: {len(to_process)}{Style.RESET_ALL}"
    log_and_print(summary + "\n")

    success = len(processed_files)
    failed = 0

    for file in to_process:
        if process_video(file):
            success += 1
        else:
            failed += 1

    final = f"\n{Fore.CYAN}🎉COMPRESSION COMPLETE → {Fore.GREEN}{success} SUCCESS{Style.RESET_ALL} | {Fore.RED}{failed} FAILED{Style.RESET_ALL}"
    log_and_print(final)
    log_and_print(f"\n{Fore.MAGENTA}💿ENCODED FILES → {output_dir}{Style.RESET_ALL}\n")
    log_and_print(f"{Fore.YELLOW}🔥════════════════════════════════════════════════════════════════════════════════🔥{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()
