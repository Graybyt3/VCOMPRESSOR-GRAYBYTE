import os
import subprocess
import time
from datetime import timedelta
from pathlib import Path
from colorama import init, Fore, Style
from tqdm import tqdm
import logging
import random
import re

# Graybyt3 - Ex-Blackhat | Ex Super Mod of Team_CC.
# Now securing systems as a Senior Security Expert.
# I hack servers for fun, patch them to torture you.
#
# "My life is a lie, and i'm living in this only truth.- Graybyt3"
#
# WARNING: This code is for educational and ethical purposes only.
# I am not responsible for any misuse or illegal activities.
#
# WARNING: Steal my code, and I'll call you Pappu — there's no worse shame in this world than being called Pappu.
#FuCk_Pappu

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

RAINBOW = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]

def colored_ascii(text):
    colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA, Fore.BLUE]
    return "".join(random.choice(colors) + c for c in text if c != " ")

ASCII_BANNER = colored_ascii(
"\n\n\n█▀▀ █▀█ ▄▀█ █▄█ █▄▄ █▄█ ▀█▀ █▀▀   █░█ █ █▀▄ ▄▄ █▀▀ █▀█ █▀▄▀█ █▀█ █▀█ █▀▀ █▀ █▀ █▀█ █▀█\n"
"█▄█ █▀▄ █▀█ ░█░ █▄█ ░█░ ░█░ ██▄   ▀▄▀ █ █▄▀ ░░ █▄▄ █▄█ █░▀░█ █▀▀ █▀▄ ██▄ ▄█ ▄█ █▄█ █▀▄\n\n\n"
)

EXPLANATION = f"""
{Fore.YELLOW}This Script Compresses All .mp4 Videos In The Folder
It Makes The Files Smaller Using The H.265 Codec But Keeps The Quality Good
You Will See Real-time Progress, Elapsed/remaining Time, And How Much Space Is Saved
Tweak -crf,-preset For More Quality Options
Change Cpu Limit For Faster Performance
Higher Limits Make It Faster But Use More Cpu
{Style.RESET_ALL}
"""

PLAIN_BANNER = """
█▀▀ █▀█ ▄▀█ █▄█ █▄▄ █▄█ ▀█▀ █▀▀ █░█ █ █▀▄ ▄▄ █▀▀ █▀█ █▀▄▀█ █▀█ █▀█ █▀▀ █▀ █▀ █▀█ █▀█
█▄█ █▀▄ █▀█ ░█░ █▄█ ░█░ ░█░ ██▄ ▀▄▀ █ █▄▀ ░░ █▄▄ █▄█ █░▀░█ █▀▀ █▀▄ ██▄ ▄█ ▄█ █▄█ █▀▄
"""

EXPLANATIONL = f"{Fore.GREEN}Multi-format H.265 Video Compressor | Resumable | Color Enhancement → {Style.RESET_ALL}\n"

PLAIN_EXPLANATION = "Multi-format H.265 Video Compressor | Resumable | Color Enhancement"

def strip_ansi(text):
    return re.sub(r'\x1b\[[0-9;]*m', '', text)

def log_only(text=""):
    if text:
        EXECUTION_LOG.open("a", encoding="utf-8").write(strip_ansi(text).rstrip() + "\n")

def log_and_print(text=""):
    if text:
        print(text)
        log_only(text)

class RainbowBar(tqdm):
    def update(self, n=1):
        super().update(n)
        displayed = int(self.n)
        bar = ""
        for i in range(self.total):
            if i < displayed:
                bar += RAINBOW[i % len(RAINBOW)] + "█"
            else:
                bar += "░"
        self.container.components[0].text = f"\t{bar} {displayed:3.0f}%"

def load_processed():
    if not PROCESSED_LOG.exists():
        return set()
    return {line.strip() for line in PROCESSED_LOG.open("r", encoding="utf-8") if line.strip()}

def mark_processed(filepath):
    PROCESSED_LOG.open("a", encoding="utf-8").write(str(filepath) + "\n")

print(ASCII_BANNER)
print(EXPLANATION)
print(EXPLANATIONL)
print()
log_and_print(f"{Fore.GREEN}{'='*100}{Style.RESET_ALL}\n")
cpu_input = input(f"{Fore.RED}$ ENTER CPU LIMIT (Press Enter For Default {DEFAULT_CPU_LIMIT}): {Style.RESET_ALL}").strip()
CPU_LIMIT = int(cpu_input) if cpu_input.isdigit() and 1 <= int(cpu_input) <= 1600 else DEFAULT_CPU_LIMIT

input_path = input(f"{Fore.RED}$ ENTER PATH OF VIDEO FILES (Press Enter For Current Directory): {Style.RESET_ALL}").strip()
input_dir = Path(input_path) if input_path else Path.cwd()

if not input_dir.exists() or not input_dir.is_dir():
    print(f"{Fore.RED}Invalid path! Using current directory.{Style.RESET_ALL}")
    input_dir = Path.cwd()

folder_name = input_dir.name
output_dir = input_dir.parent / f"{folder_name}-ENCODED"
output_dir.mkdir(exist_ok=True)

print(f"{Fore.GREEN}$ OUTPUT DIRECTORY : {output_dir}{Style.RESET_ALL}\n")

if EXECUTION_LOG.exists():
    EXECUTION_LOG.unlink()

log_only(PLAIN_BANNER)
log_only(PLAIN_EXPLANATION)
log_only(f"Logs stored in: {CONFIG_DIR}")
log_only(f"CPU LIMIT: {CPU_LIMIT}% | INPUT: {input_dir} | OUTPUT: {output_dir}\n")

processed_files = load_processed()

# ==================== START VISUAL ENHANCEMENT CONFIG ====================
ENHANCE_BRIGHTNESS = None
ENHANCE_CONTRAST = None
ENHANCE_SATURATION = 1.20
ENHANCE_SHARPNESS = None
# ==================== END VISUAL ENHANCEMENT CONFIG ====================

def build_vf_chain():
    filters = []
    if ENHANCE_BRIGHTNESS is not None:
        filters.append(f"brightness={ENHANCE_BRIGHTNESS}")
    if ENHANCE_CONTRAST is not None:
        filters.append(f"contrast={ENHANCE_CONTRAST}")
    if ENHANCE_SATURATION is not None:
        filters.append(f"saturation={ENHANCE_SATURATION}")
    if ENHANCE_SHARPNESS is not None:
        filters.append(f"unsharp=5:5:{ENHANCE_SHARPNESS:.2f}")
    if not filters:
        return None
    eq_part = ":".join([f for f in filters if not f.startswith("unsharp")])
    unsharp_part = [f for f in filters if f.startswith("unsharp")]
    vf = "eq=" + eq_part if eq_part else ""
    if unsharp_part:
        vf += "," if vf else ""
        vf += unsharp_part[0]
    return vf if vf else None

VF_CHAIN = build_vf_chain()

if VF_CHAIN:
    log_only(f"VISUAL ENHANCEMENT ACTIVE: -vf \"{VF_CHAIN}\"")
    print(f"{Fore.GREEN}VISUAL ENHANCEMENT ACTIVE | -vf \"{VF_CHAIN}\"{Style.RESET_ALL}\n")
else:
    log_only("VISUAL ENHANCEMENT DISABLED")

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
    # Remove everything except letters, numbers, spaces, and dots (for extension)
    # First: replace "-" with space
    name = name.replace("-", " ")
    # Remove all special characters including _, (), [], etc.
    name = re.sub(r'[^a-zA-Z0-9.\s]', '', name)
    # Clean up multiple spaces
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def get_new_filename(original_path):
    stem = original_path.stem
    stem = stem.replace("-compressed", "").replace("~EncodeD", "")
    cleaned_stem = clean_filename(stem)
    ext = original_path.suffix.lower()
    return output_dir / f"{cleaned_stem}{ext}"

def process_video(file):
    try:
        full_path = str(file.resolve())
        if full_path in processed_files:
            msg = f"{Fore.MAGENTA}RESUMED | ALREADY EXECUTED : {file.name}{Style.RESET_ALL}"
            log_and_print(msg)
            return True

        out_file = get_new_filename(file)
        if out_file.exists():
            msg = f"{Fore.MAGENTA}SKIPPING | OUTPUT EXISTS : {out_file.name}{Style.RESET_ALL}"
            log_and_print(msg)
            mark_processed(full_path)
            return True

        original_size = get_size(file)
        duration = get_duration(file) or 0
        duration_str = timedelta(seconds=int(duration)) if duration else "Unknown"

        log_and_print(f"{Fore.GREEN}{'='*100}{Style.RESET_ALL}\n")
        log_and_print(f"\n{Fore.YELLOW}FILE-NAME :{Style.RESET_ALL} {Fore.WHITE}{file.name}{Style.RESET_ALL}\n")
        log_and_print(f"INPUT-SIZE: {Fore.YELLOW}{original_size:.2f} MB{Style.RESET_ALL} | DURATION: {Fore.GREEN}{duration_str} MIN{Style.RESET_ALL}\n")

        start_time = time.time()
        cmd = [
            "cpulimit", "-l", str(CPU_LIMIT), "--", "ffmpeg",
            "-i", str(file),
            "-c:v", "libx265", "-crf", "30", "-preset", "superfast",
            "-c:a", "copy", "-threads", "4",
            "-progress", "pipe:1", "-nostats"
        ]
        if VF_CHAIN:
            cmd.extend(["-vf", VF_CHAIN])
        cmd.append(str(out_file))

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        current_seconds = 0

        with RainbowBar(total=100, bar_format="{l_bar}{bar}", ncols=80, leave=False) as bar:
            bar.set_description(f"{Fore.YELLOW}ELAPSED: {Style.RESET_ALL}{Fore.GREEN}0:00:00{Style.RESET_ALL} | REMAINNING: {Fore.YELLOW}{duration_str}{Style.RESET_ALL}")
            while process.poll() is None:
                line = process.stdout.readline()
                if line.startswith("out_time_ms="):
                    val = line.split("=")[1]
                    if val != "N/A":
                        current_seconds = int(val) / 1_000_000
                if duration > 0:
                    progress = min(int((current_seconds / duration) * 100), 100)
                    bar.n = progress
                    elapsed = timedelta(seconds=int(time.time() - start_time))
                    remaining = max(int(duration - current_seconds), 0)
                    bar.set_description(f"ELAPSED: {Fore.GREEN}{elapsed}{Style.RESET_ALL} | REM: {Fore.YELLOW}{timedelta(seconds=remaining)}{Style.RESET_ALL}")
                time.sleep(0.1)

        elapsed = timedelta(seconds=int(time.time() - start_time))
        new_size = get_size(out_file) if out_file.exists() else 0
        space_saved = original_size - new_size

        if process.returncode == 0 and out_file.exists():
            success_msg = f"{Fore.GREEN}SUCCESS → {out_file.name}{Style.RESET_ALL}\n"
            savings_msg = f"{Fore.YELLOW}TIME TAKEN: {elapsed}{Style.RESET_ALL} | {Fore.RED}OLD-SIZE: {original_size:.2f} MB{Style.RESET_ALL} → {Fore.GREEN}NEW SIZE: {new_size:.2f} MB{Style.RESET_ALL} | SPACE SAVED: {Fore.GREEN}{space_saved:.2f} MB{Style.RESET_ALL}\n"
            log_and_print(success_msg)
            log_and_print(savings_msg)
            log_and_print(f"{Fore.GREEN}{'='*100}{Style.RESET_ALL}")
            mark_processed(full_path)
            return True
        else:
            error = process.stderr.read()
            logging.error(f"Failed {file}: {error}")
            fail_msg = f"{Fore.RED}FAILED | {file.name} → {out_file.name} | See {ERROR_LOG}{Style.RESET_ALL}\n"
            log_and_print(fail_msg)
            log_and_print(f"{Fore.GREEN}{'='*100}{Style.RESET_ALL}")
            if out_file.exists():
                out_file.unlink()
            return False

    except Exception as e:
        err = f"{Fore.RED}EXCEPTION | {file.name}: {e}{Style.RESET_ALL}\n"
        log_and_print(err)
        logging.error(f"Exception: {file} | {e}")
        return False

def main():
    video_files = [f for f in input_dir.iterdir() if f.suffix.lower() in VIDEO_EXTENSIONS and f.is_file()]
    to_process = [f for f in video_files if str(f.resolve()) not in processed_files]

    summary = f"{Fore.RED}$ TOTAL: {len(video_files)} VIDEO FOUND | {len(processed_files)} :  EXECUTED | {len(to_process)} : REMAINING{Style.RESET_ALL}"
    log_and_print(summary)
    success = len(processed_files)
    failed = 0

    for file in to_process:
        if process_video(file):
            success += 1
        else:
            failed += 1

    final = f"\n{Fore.CYAN}COMPRESSION COMPLETE | {Fore.GREEN}{success} SUCCEEDED{Style.RESET_ALL}, | {Fore.RED}{failed} FAILED{Style.RESET_ALL}"
    log_and_print(final)
    log_and_print(f"{Fore.MAGENTA}ENCODED FILES ARE STORED AT : {output_dir}{Style.RESET_ALL}\n")
    log_and_print(f"\n{Fore.YELLOW}{'='*100}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
