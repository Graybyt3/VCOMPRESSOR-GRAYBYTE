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
#
# Graybyt3 - Ex-Blackhat 🖤 | Ex Super Mod of Team_CC.
# Now securing systems as a Senior Security Expert 🛡️.
# I hack servers for fun, patch them to torture you.
#
# "My life is a lie, and i'm living in this only truth.- Graybyt3"
#
# WARNING: Steal my code, and I'll call you Pappu
# There's no worse shame in this world than being called Pappu.
# FuCk_Pappu
#
# ======================== ENCODING PARAMETER EXPLANATIONS ======================
# PRESETS (libx265):
#   superfast / veryfast / faster / fast  → Very fast encoding, slightly larger file size
#   medium                                 → Balanced speed/quality (FFmpeg default)
#   slow / slower / veryslow               → Slower encoding, best compression, smallest file size
#
# CRF (Constant Rate Factor) - Range 27-31 (recommended for H.265):
#   27 → Highest quality, largest file size (almost lossless)
#   28 → Excellent quality/size balance (default & recommended for most users)
#   29 → Very good quality, noticeably smaller file
#   30 → Good quality, significant size reduction
#   31 → Smaller files with acceptable quality (visible quality loss starts here)
#   Lower CRF = better quality + bigger file | Higher CRF = smaller file + lower quality
#
# CPU LIMIT (700-1000%):
#   700-800%  → Balanced speed with lower system load (recommended for daily use)
#   850-900%  → Faster encoding, moderate CPU usage
#   950-1000% → Maximum encoding speed (uses almost all CPU cores, higher heat & power usage)
#
# THREADS (4-8):
#   4 → Good balance between speed and system responsiveness
#   5-6 → Faster encoding on 6-12 core CPUs
#   7-8 → Maximum speed on high-core CPUs (may increase system temperature)
# ===============================================================================

# =========================== DEFAULT CONFIGS & PATHS ===========================
DEFAULT_CPU_LIMIT = 600
VIDEO_EXTENSIONS = (".mp4", ".mkv", ".mpeg", ".mpg", ".ts", ".mov", ".avi", ".webm", ".flv", ".m4v", ".wmv", ".vob", ".ogv")
CONFIG_DIR = Path.cwd() / "VCOM-CONFIG"
CONFIG_DIR.mkdir(exist_ok=True)
PROCESSED_LOG = CONFIG_DIR / "processed_files.log"
EXECUTION_LOG = CONFIG_DIR / "execution_log.txt"
ERROR_LOG = CONFIG_DIR / "compression_errors.log"
logging.basicConfig(
    filename=ERROR_LOG,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
def colored_ascii(text):
    colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA, Fore.BLUE]
    return "".join(random.choice(colors) + c for c in text if c != " ")
ascii_art = (
    f"\n\n{Fore.RED}░█▀▀█ {Fore.GREEN}░█▀▀█ {Fore.YELLOW}─█▀▀█ {Fore.GREEN}░█──░█ {Fore.RED}░█──░█ {Fore.CYAN}▀█▀ {Fore.RED}░█▀▀▄ {Fore.GREEN}── {Fore.YELLOW}░█▀▀█ {Fore.GREEN}░█▀▀▀█ {Fore.RED}░█▀▄▀█ {Style.RESET_ALL}\n"
    f"{Fore.RED}░█─▄▄ {Fore.GREEN}░█▄▄▀ {Fore.YELLOW}░█▄▄█ {Fore.GREEN}░█▄▄▄█ {Fore.RED}─░█░█─ {Fore.CYAN}░█─ {Fore.RED}░█─░█ {Fore.GREEN}▀▀ {Fore.YELLOW}░█─── {Fore.GREEN}░█──░█ {Fore.RED}░█░█░█ {Style.RESET_ALL}\n"
    f"{Fore.RED}░█▄▄█ {Fore.GREEN}░█─░█ {Fore.YELLOW}░█─░█ {Fore.GREEN}──░█── {Fore.RED}──▀▄▀─ {Fore.CYAN}▄█▄ {Fore.RED}░█▄▄▀ {Fore.GREEN}── {Fore.YELLOW}░█▄▄█ {Fore.GREEN}░█▄▄▄█ {Fore.RED}░█──░█ {Style.RESET_ALL}\n\n"
)
print(ascii_art)
EXPLANATION = f"""
{Fore.YELLOW}🚀 THIS SCRIPT COMPRESSES ALL SUPPORTED VIDEOS IN THE FOLDER
💾 MAKES FILES SMALLER WITH H.265 (HEVC) WHILE KEEPING EXCELLENT QUALITY
📊 REAL-TIME PROGRESS • ELAPSED/REMAINING TIME • SPACE SAVINGS DISPLAYED
⚙️ TWEAK CRF & PRESET FOR YOUR PERFECT QUALITY/SPEED BALANCE
🖥️ CUSTOM CPU LIMITS {Style.RESET_ALL}
"""
EXPLANATIONL = f"{Fore.GREEN}🎬 MULTI-FORMAT H.265 VIDEO COMPRESSOR | RESUMABLE | ENHANCED VISUALS 🔥{Style.RESET_ALL}\n"
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
RAINBOW_BLOCK = "".join(["\033[31m█\033[33m█\033[32m█\033[36m█\033[34m█\033[35m█"] * 14)[:80] + "\033[0m"
class RainbowBar(tqdm):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('ncols', 80)
        kwargs.setdefault('leave', False)
        kwargs.setdefault('ascii', RAINBOW_BLOCK)
        kwargs.setdefault('bar_format', '{desc}')
        super().__init__(*args, **kwargs)
def load_processed():
    if not PROCESSED_LOG.exists():
        return set()
    with PROCESSED_LOG.open("r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}
def mark_processed(filepath):
    with PROCESSED_LOG.open("a", encoding="utf-8") as f:
        f.write(str(filepath) + "\n")
print(EXPLANATION)
print(EXPLANATIONL)
print()
CONFIG_FILE = Path(__file__).resolve().parent / "config.txt"


def load_config():
    config = {}
    if not CONFIG_FILE.exists():
        return config
    with CONFIG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue
            key, value = line.split(":", 1)
            config[key.strip().upper()] = value.strip()
    return config


config = load_config()

if config:
    CPU_LIMIT = int(re.sub(r"[^0-9]", "", config.get("CPULIMIT", str(DEFAULT_CPU_LIMIT))) or DEFAULT_CPU_LIMIT)
    CRF = int(re.sub(r"[^0-9]", "", config.get("CRF", "28")) or 28)
    PRESET = config.get("PRESET", "faster").strip().lower()
    THREADS = int(re.sub(r"[^0-9]", "", config.get("THREADS", "4")) or 4)
    VIDEO_CODEC = config.get("VIDEO CODEC", "libx265 (HEVC)").strip()
    AUDIO = config.get("AUDIO", "copy (no re-encoding)").strip()
    DELETE_ORIGINAL = config.get("DELETE_ORIGINAL", "n").strip().lower() in ("y", "yes")

    if CPU_LIMIT > 1000:
        CPU_LIMIT = 1000
    if CPU_LIMIT < 1:
        CPU_LIMIT = DEFAULT_CPU_LIMIT
    if not 27 <= CRF <= 31:
        CRF = 28
    if not 4 <= THREADS <= 8:
        THREADS = 4
    delete_input = input(f"{Fore.RED}⚠️⚠️ DELETE ORIGINAL FILE AFTER SUCCESS CONVERSION? (y/n|ENTER=n): {Style.RESET_ALL}").strip().lower()
    DELETE_ORIGINAL = delete_input in ("y", "yes")

    input_dir = Path.cwd()
    folder_name = input_dir.name
    output_dir = input_dir / f"{folder_name}-ENCODED"
    output_dir.mkdir(exist_ok=True)
    SMALL_SIZE_DIR = input_dir / "SMALL-SIZE"
    SMALL_SIZE_DIR.mkdir(exist_ok=True)
    SMALL_SIZE_LIMIT_MB = 20

    print(f"{Fore.GREEN}🏠︎ OUTPUT WILL BE SAVED TO: {output_dir}{Style.RESET_ALL}\n")
    print(f"{Fore.GREEN}ENCODING SETTINGS THAT WILL BE USED:{Style.RESET_ALL}")
    print(f"{Fore.RED} • VIDEO CODEC : {VIDEO_CODEC}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA} • CPULIMIT : {CPU_LIMIT}%{Style.RESET_ALL}")
    print(f"{Fore.GREEN} • PRESET   : {PRESET}{Style.RESET_ALL}")
    print(f"{Fore.RED} • CRF      : {CRF}{Style.RESET_ALL}")
    print(f"{Fore.GREEN} • AUDIO    : {AUDIO}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW} • THREADS  : {THREADS}{Style.RESET_ALL}\n")
    print(f"{Fore.RED} • ORIGINAL FILE  : WILL BE DELETED{Style.RESET_ALL}\n")
    confirm = input(f"{Fore.GREEN}📝 IF CONFIG SATISFIED THEN PRESS y/YES (or n/NO) ❓: {Style.RESET_ALL}").strip().lower()
    if confirm not in ['y', 'yes']:
        print(f"{Fore.YELLOW}⏹️ ENCODING CANCELLED → EDIT CONFIG.TXT AND RUN AGAIN{Style.RESET_ALL}")
        raise SystemExit(0)
    print(f"{Fore.GREEN}▶️ STARTING COMPRESSION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓{Style.RESET_ALL}\n")
else:
    while True:
        print(f"{Fore.CYAN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓{Style.RESET_ALL}")
        print(f"{Fore.CYAN} COMPRESSION SETTINGS CONFIGURATION{Style.RESET_ALL}")
        print(f"{Fore.CYAN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{Style.RESET_ALL}\n")
        cpu_input = input(f"{Fore.GREEN}❇️ CPU LIMIT % (ENTER={DEFAULT_CPU_LIMIT}): {Style.RESET_ALL}").strip()
        CPU_LIMIT = int(cpu_input) if cpu_input.isdigit() and 1 <= int(cpu_input) <= 1600 else DEFAULT_CPU_LIMIT
        if CPU_LIMIT > 1000:
            print(f"{Fore.RED}⚠️ CAPPED AT 1000% FOR SYSTEM STABILITY ⚠️{Style.RESET_ALL}")
            CPU_LIMIT = 1000
        crf_input = input(f"{Fore.GREEN}❇️ CRF VALUE (27-31|ENTER=28): {Style.RESET_ALL}").strip()
        CRF = int(crf_input) if crf_input.isdigit() and 27 <= int(crf_input) <= 31 else 28
        preset_input = input(f"{Fore.GREEN}❇️ PRESET |(SUPERFAST/FASTER/ETC ENTER=FASTER): {Style.RESET_ALL}").strip().lower()
        PRESET = preset_input if preset_input else "faster"
        threads_input = input(f"{Fore.GREEN}❇️ THREADS (4-8|ENTER=4): {Style.RESET_ALL}").strip()
        THREADS = int(threads_input) if threads_input.isdigit() and 4 <= int(threads_input) <= 8 else 4
        delete_input = input(f"{Fore.RED}⚠️⚠️ DELETE ORIGINAL FILE AFTER CONVERSION? (y/n|ENTER=n): {Style.RESET_ALL}").strip().lower()
        DELETE_ORIGINAL = delete_input in ("y", "yes")
        input_path = input(f"{Fore.GREEN}🗃  VIDEO FOLDER PATH (ENTER=CWD): {Style.RESET_ALL}").strip()
        input_dir = Path(input_path) if input_path else Path.cwd()
        if not input_dir.exists() or not input_dir.is_dir():
            print(f"{Fore.RED}❌ INVALID PATH → FALLING BACK TO CURRENT DIRECTORY{Style.RESET_ALL}")
            input_dir = Path.cwd()
        folder_name = input_dir.name
        output_dir = input_dir / f"{folder_name}-ENCODED"
        output_dir.mkdir(exist_ok=True)
        SMALL_SIZE_DIR = input_dir / "SMALL-SIZE"
        SMALL_SIZE_DIR.mkdir(exist_ok=True)
        SMALL_SIZE_LIMIT_MB = 20
        print(f"{Fore.GREEN}🏠︎ OUTPUT WILL BE SAVED TO: {output_dir}{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓{Style.RESET_ALL}")
        print(f"{Fore.RED} INITIAL INPUT SUMMARY {Style.RESET_ALL}")
        print(f"{Fore.YELLOW}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{Style.RESET_ALL}")
        print(f"{Fore.GREEN}❇️ CPU LIMIT  : {CPU_LIMIT}%{' ' * (35 - len(str(CPU_LIMIT)) - 7)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}❇️ CRF        : {CRF}{' ' * (35 - len(str(CRF)) - 7)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}❇️ PRESET     : {PRESET}{' ' * (35 - len(PRESET) - 7)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}❇️ THREADS    : {THREADS}{' ' * (35 - len(str(THREADS)) - 7)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}❇️ INPUT FOLDER : {input_dir}{' ' * (35 - len(str(input_dir)) - 7)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}❇️ OUTPUT FOLDER : {output_dir}{' ' * (35 - len(str(output_dir)) - 7)}{Style.RESET_ALL}")
        print(f"{Fore.RED}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{Style.RESET_ALL}\n")
        print(f"{Fore.GREEN}ENCODING SETTINGS THAT WILL BE USED:{Style.RESET_ALL}")
        print(f"{Fore.RED} • VIDEO CODEC : libx265 (HEVC){Style.RESET_ALL}")
        print(f"{Fore.MAGENTA} • CPULIMIT : {CPU_LIMIT}%{Style.RESET_ALL}")
        print(f"{Fore.GREEN} • PRESET   : {PRESET}{Style.RESET_ALL}")
        print(f"{Fore.RED} • CRF      : {CRF}{Style.RESET_ALL}")
        print(f"{Fore.GREEN} • AUDIO    : copy (no re-encoding){Style.RESET_ALL}")
        print(f"{Fore.YELLOW} • THREADS  : {THREADS}{Style.RESET_ALL}\n")
        print(f"{Fore.RED} • ORIGINAL FILE  : WILL BE DELETED{Style.RESET_ALL}\n")
        confirm = input(f"{Fore.GREEN}📝 IF CONFIG SATISFIED THEN PRESS y/YES (or n/NO) ❓: {Style.RESET_ALL}").strip().lower()
        if confirm in ['y', 'yes']:
            print(f"{Fore.GREEN}▶️ STARTING COMPRESSION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓{Style.RESET_ALL}\n")
            with CONFIG_FILE.open("w", encoding="utf-8") as f:
                f.write(f"• • • • • • • • • • • • • • • • • • •• • • • •     DEFAULT ENCODING SETTINGS      • • • • •• • • • • • • • • • • • • • \n\n\n")
                f.write(f"CPULIMIT: {CPU_LIMIT}\n")
                f.write(f"CRF: {CRF}\n")
                f.write(f"PRESET: {PRESET}\n")
                f.write(f"THREADS: {THREADS}\n")
                f.write(f"VIDEO CODEC: libx265 (HEVC)\n")
                f.write(f"AUDIO: copy (no re-encoding)\n")
                f.write(f"DELETE_ORIGINAL: {'y' if DELETE_ORIGINAL else 'n'}\n")
        
            break
        else:
            print(f"{Fore.YELLOW}⏹️ RESTARTING CONFIGURATION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓{Style.RESET_ALL}\n")

if EXECUTION_LOG.exists():
    EXECUTION_LOG.unlink()
log_only("H.265 Video Compressor Run")
log_only(f"CPU LIMIT: {CPU_LIMIT}% | CRF: {CRF} | PRESET: {PRESET} | THREADS: {THREADS} | INPUT: {input_dir} | OUTPUT: {output_dir}\n")
processed_files = load_processed()
VF_CHAIN = None
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
    name = name.replace("xHamster", "").replace("Taboofantazy", "").replace("EPORNER", "").replace("SpankBang", "")
    name = re.sub(r'[_-]+', ' ', name)
    name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name.upper()
def get_new_filename(original_path):
    cleaned_stem = clean_filename(original_path.stem)
    ext = original_path.suffix.lower()
    return output_dir / f"{cleaned_stem} __ENC-L-{CRF}__{ext}"
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

def move_small_file(file):
    try:
        size_mb = get_size(file)

        if size_mb < SMALL_SIZE_LIMIT_MB:
            SMALL_SIZE_DIR.mkdir(exist_ok=True)

            destination = SMALL_SIZE_DIR / file.name

            if destination.exists():
                stem = destination.stem
                suffix = destination.suffix
                counter = 1

                while destination.exists():
                    destination = SMALL_SIZE_DIR / f"{stem}_{counter}{suffix}"
                    counter += 1

            file.rename(destination)

            msg = (
                f"{Fore.GREEN}📦 SMALL FILE → {file.name} | "
                f"{size_mb:.2f} MB < {SMALL_SIZE_LIMIT_MB} MB → "
                f"MOVED TO SMALL-SIZE{Style.RESET_ALL}"
            )

            log_and_print(msg)
            mark_processed(str(file.resolve()))
            return True

        return False

    except Exception as e:
        logging.error(f"Failed moving small file {file}: {e}")

        msg = (
            f"{Fore.RED}❌ SMALL-FILE MOVE FAILED → "
            f"{file.name} | {e}{Style.RESET_ALL}"
        )

        log_and_print(msg)
        return False

def process_video(file):
    try:
        full_path = str(file.resolve())

        if get_size(file) <= SMALL_SIZE_LIMIT_MB:
            move_small_file(file)
            return True

        if full_path in processed_files:
            msg = f"{Fore.MAGENTA}⏭️ ALREADY PROCESSED → SKIPPINg {file.name}{Style.RESET_ALL}"
            log_and_print(msg)
            return True

        out_file = get_new_filename(file)
        if out_file.exists():
            msg = f"{Fore.MAGENTA}⏭️ OUTPUT ALREADY EXISTS → SKIPPING {out_file.name}{Style.RESET_ALL}"
            log_and_print(msg)
            mark_processed(full_path)
            return True

        original_size = get_size(file)
        duration = get_duration(file) or 0
        duration_str = str(timedelta(seconds=int(duration))) if duration else "❌ UNKNOWN ❌ "
        log_and_print(f"{Fore.RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓{Style.RESET_ALL}\n")
        log_and_print(f"{Fore.YELLOW}🔀 PROCESSING → {file.name}{Style.RESET_ALL}")
        log_and_print(f"⚠️ ORIGINAL SIZE: {Fore.YELLOW}{original_size:.2f} MB{Style.RESET_ALL} DURATION: {Fore.GREEN}{duration_str}{Style.RESET_ALL}\n")
        start_time = time.time()
        cmd = [
            "cpulimit", "-l", str(CPU_LIMIT), "--", "ffmpeg",
            "-i", str(file),
            "-c:v", "libx265", "-crf", str(CRF), "-preset", PRESET,
            "-c:a", "copy",
            "-threads", str(THREADS),
            "-progress", "pipe:1", "-nostats"
        ]
        if VF_CHAIN:
            cmd.extend(["-vf", VF_CHAIN])
        cmd.append(str(out_file))
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        current_seconds = 0
        bar = RainbowBar(total=100, desc="", ncols=80, leave=False, dynamic_ncols=False)
        bar.set_description(f"{Fore.YELLOW}⏳ ELAPSED: {Style.RESET_ALL}{Fore.GREEN}0:00:00{Style.RESET_ALL} | ⏱ REMAINING: {Fore.YELLOW}{duration_str}")
        while process.poll() is None:
            line = process.stdout.readline()
            if not line:
                continue
            parsed = parse_progress_time(line)
            if parsed is not None:
                current_seconds = parsed
            if duration > 0 and current_seconds > 3:
                progress = min(int((current_seconds / duration) * 100), 100)
                bar.n = progress
                elapsed_sec = max(time.time() - start_time, 0.1)
                elapsed = timedelta(seconds=int(elapsed_sec))

                speed = current_seconds / elapsed_sec
                remaining_video = max(duration - current_seconds, 0)
                remaining_sec = int(remaining_video / speed) if speed > 0.05 else int(remaining_video)
                remaining_str = str(timedelta(seconds=remaining_sec))

                bar.set_description(
                    f"⏳{Fore.GREEN} ELAPSED: {elapsed} | "
                    f"⏱️ REM: {Fore.YELLOW}{remaining_str}"
                )
                bar.refresh()
            time.sleep(1.0)
        bar.close()
        elapsed = timedelta(seconds=int(time.time() - start_time))
        new_size = get_size(out_file) if out_file.exists() else 0
        space_saved = original_size - new_size
        if process.returncode == 0 and out_file.exists() and new_size > 0:
            success_msg = f"{Fore.GREEN}✅ SUCCESS → {out_file.name}{Style.RESET_ALL}"
            terminal_line = (
                f"⏱️ TIME TAKEN: {elapsed} | "
                f"{Fore.RED}OLD: {original_size:.2f} MB{Style.RESET_ALL} → "
                f"{Fore.GREEN}NEW: {new_size:.2f} MB{Style.RESET_ALL} | "
                f"SAVED-SPACE: {Fore.GREEN if space_saved >= 0 else Fore.RED}{space_saved:+.2f} MB{Style.RESET_ALL}"
            )
            log_and_print(success_msg)
            log_and_print(terminal_line)
            mark_processed(full_path)

            if DELETE_ORIGINAL:
                try:
                    file.unlink()
                    log_and_print(f"{Fore.RED}🗑️ ORIGINAL FILE DELETED → {file.name}{Style.RESET_ALL}")
                except Exception as e:
                    log_and_print(f"{Fore.YELLOW}⚠️ COULD NOT DELETE ORIGINAL FILE → {file.name} | {e}{Style.RESET_ALL}")

            return True
        else:
            error = process.stderr.read()
            logging.error(f"Failed {file}: {error}")
            fail_msg = f"{Fore.RED}❌ FAILED → {file.name} | CHECK {ERROR_LOG}{Style.RESET_ALL}\n"
            log_and_print(fail_msg)
            log_and_print(f"{Fore.GREEN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{Style.RESET_ALL}\n")
            if out_file.exists():
                out_file.unlink()
            return False
    except Exception as e:
        if 'bar' in locals():
            bar.close()
        err = f"{Fore.RED}💥 EXCEPTION | {file.name}: {e}{Style.RESET_ALL}\n"
        log_and_print(err)
        logging.error(f"Exception: {file} | {e}")
        return False
def main():
    video_files = [f for f in input_dir.iterdir() if f.suffix.lower() in VIDEO_EXTENSIONS and f.is_file()]
    to_process = [f for f in video_files if str(f.resolve()) not in processed_files]
    totalinput_count = len(video_files)
    summary = f"{Fore.WHITE}🎬 TOTAL VIDEOS: {len(video_files)} | ✅ ALREADY DONE: {len(processed_files)} | ⏳ TO PROCESS: {len(to_process)}{Style.RESET_ALL}"
    log_and_print(summary)
    success = len(processed_files)
    failed = 0
    for file in to_process:
        if process_video(file):
            success += 1
        else:
            failed += 1
        processed_count = success + failed
        remaining = totalinput_count - processed_count
        print(f"{Fore.GREEN}\n🎯 STATUS → {Style.RESET_ALL}"
              f"📥 TOTAL-FILE: {totalinput_count} {Fore.WHITE} | {Style.RESET_ALL} "
              f"✅ PROCESSED: {Fore.GREEN}{processed_count} {Style.RESET_ALL}{Fore.WHITE} | {Style.RESET_ALL}"
              f"{Fore.YELLOW}⏩ REMAINING: {remaining}{Style.RESET_ALL} 🎯\n")
    final = f"{Fore.GREEN}🎉 COMPRESSION COMPLETE → {Fore.GREEN}{success} SUCCESS{Style.RESET_ALL} | {Fore.RED}{failed} FAILED{Style.RESET_ALL}"
    log_and_print(final)
    log_and_print(f"{Fore.GREEN}💿 ENCODED FILES LOCATION → {output_dir}{Style.RESET_ALL}\n")
    log_and_print(f"{Fore.MAGENTA}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{Style.RESET_ALL}\n")
if __name__ == "__main__":
    main()
