import os
import subprocess
import time
from datetime import timedelta
from pathlib import Path
from colorama import init, Fore, Style
from tqdm import tqdm
import logging
import random

init(autoreset=True)

CPU_LIMIT = 400  # Change to 800 (~50%) or 1600 (~100%) for faster encoding

input_dir = Path("/home/graybyte/Downloads/Video/TEST") # Change to machine path
output_dir = input_dir / "COMPRESSED"
output_dir.mkdir(exist_ok=True)

logging.basicConfig(filename='compression_errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def colored_ascii(text):
    colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA, Fore.BLUE]
    return "".join(random.choice(colors) + c for c in text)

ASCII_HEADER = colored_ascii(
"\n\n\n█▀▀ █▀█ ▄▀█ █▄█ █▄▄ █▄█ ▀█▀ █▀▀   █░█ █ █▀▄ ▄▄ █▀▀ █▀█ █▀▄▀█ █▀█ █▀█ █▀▀ █▀ █▀ █▀█ █▀█\n"
"█▄█ █▀▄ █▀█ ░█░ █▄█ ░█░ ░█░ ██▄   ▀▄▀ █ █▄▀ ░░ █▄▄ █▄█ █░▀░█ █▀▀ █▀▄ ██▄ ▄█ ▄█ █▄█ █▀▄\n"
)

EXPLANATION = f"""
{Fore.YELLOW}This script compresses all .mp4 videos in the folder.
It makes the files smaller using the H.265 codec but keeps the quality good.
You will see real-time progress, elapsed/remaining time, and how much space is saved.{Style.RESET_ALL}
"""

print(ASCII_HEADER)
print(EXPLANATION)
print(f"{Fore.CYAN}CURRENT CPU USAGE LIMIT : {CPU_LIMIT}% (~{CPU_LIMIT//100} cores){Style.RESET_ALL}\n")
print("To change CPU limit for faster performance:")
print("- Edit 'CPU_LIMIT = 400' to 800 (~50%) or 1600 (~100%)")
print("- Higher limits make it faster but use more CPU\n")
print(f"STARTING VIDEO COMPRESSION IN {Fore.YELLOW}{input_dir}{Style.RESET_ALL}\n")

def get_duration(file):
    try:
        result = subprocess.run(
            ["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", str(file)],
            capture_output=True, text=True, check=True
        )
        return float(result.stdout.strip())
    except:
        return None

def get_size(file):
    return os.path.getsize(file)/(1024*1024)

def process_video(file):
    out_file = output_dir / f"{file.stem}-compressed.mp4"
    original_size = get_size(file)
    duration = get_duration(file)

    print(f"\nPROCESSING : {Fore.CYAN}{file.name}{Style.RESET_ALL} | ORIGINAL SIZE : {Fore.YELLOW}{original_size:.2f} MB{Style.RESET_ALL} | VIDEO DURATION : {Fore.GREEN}{timedelta(seconds=int(duration)) if duration else 'Unknown'} MIN{Style.RESET_ALL}\n")

    start_time = time.time()
    cmd = [
        "cpulimit","-l", str(CPU_LIMIT), "--","ffmpeg",
        "-i", str(file), "-c:v","libx265","-crf","30","-preset","veryslow",
        "-c:a","copy","-threads","4","-progress","pipe:1","-nostats", str(out_file)
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

    last_progress = 0
    current_seconds = 0
    tqdm_bar = tqdm(total=100, bar_format='\t{bar} {percentage:3.0f}%', ncols=80, colour='green')

    while process.poll() is None:
        try:
            line = process.stdout.readline()
            if not line:
                time.sleep(0.1)
                continue
            line = line.strip()
            if line.startswith("out_time_ms="):
                val = line.split('=')[1]
                if val != "N/A":
                    current_seconds = int(val)/1_000_000
        except:
            pass

        if duration:
            progress = min(int((current_seconds/duration)*100),100)
            if progress > last_progress:
                elapsed = timedelta(seconds=int(time.time()-start_time))
                remaining = max(int(duration-current_seconds),0)
                tqdm_bar.set_description_str(
                    f"ELAPSED: {Fore.GREEN}{elapsed} MIN{Style.RESET_ALL} | "
                    f"REMAINING: {Fore.YELLOW}{timedelta(seconds=remaining)} MIN{Style.RESET_ALL}"
                )
                tqdm_bar.n = progress
                tqdm_bar.refresh()
                last_progress = progress

        time.sleep(0.1)

    tqdm_bar.n = 100
    tqdm_bar.refresh()
    tqdm_bar.close()
    elapsed = timedelta(seconds=int(time.time()-start_time))
    new_size = get_size(out_file)
    space_saved = original_size - new_size
    if process.returncode == 0:
        print(f"\n{Fore.GREEN}SUCCESS: {out_file.name} CREATED IN {output_dir}{Style.RESET_ALL}\n")
        print(f"TIME TOOK : {elapsed} MIN | SPACE SAVED = {Fore.YELLOW}{original_size:.2f} MB{Style.RESET_ALL} - {Fore.YELLOW}{new_size:.2f} MB{Style.RESET_ALL} = {Fore.RED}{space_saved:.2f} MB{Style.RESET_ALL}\n")
        return True
    else:
        error = process.stderr.read()
        logging.error(f"Failed {file}: {error}")
        print(f"\n{Fore.RED}FAILED: {file.name} | Check compression_errors.log | TIME TOOK : {elapsed} MIN{Style.RESET_ALL}\n")
        return False

def main():
    mp4_files = list(input_dir.glob("*.mp4"))
    print(f"FOUND {Fore.CYAN}{len(mp4_files)}{Style.RESET_ALL} VIDEO FILES FOR PROCESSING\n")
    print("="*85)
    success, failed = 0,0
    for file in mp4_files:
        if process_video(file):
            success +=1
        else:
            failed +=1
        print("="*85)
    print(f"\nCOMPRESSION COMPLETE: {Fore.GREEN}{success} SUCCEEDED{Style.RESET_ALL}, {Fore.RED}{failed} FAILED{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()
