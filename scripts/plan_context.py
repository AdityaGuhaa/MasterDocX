#!/usr/bin/env python3
# Copyright (c) 2026 Aditya Guha
# SPDX-License-Identifier: MIT

"""Work out the context size llama-server should use on this machine. Used by start.sh.

The context (KV cache) gets the memory left over after loading the model:
  1. Ask llama.cpp how much memory each GPU has free (on Apple Silicon this is the
     unified memory macOS lets the GPU use). With no GPU, use free system RAM.
  2. Keep 25% of that free for the rest of the computer.
  3. Let llama.cpp's own fitting (llama-fit-params) compute the largest context
     that fits next to the model, using the model's real architecture.
  4. Cap it at LLAMA_CTX_MAX (default 65536) and at the model's trained maximum.

Prints "<context> <fit-target MiB list>" to stdout and a short explanation to stderr.
Usage: plan_context.py <llama.cpp model args, e.g. -m model.gguf or -hf user/repo:Q4_K_M>
"""
import os
import re
import subprocess
import sys

KEEP_FREE_SHARE = 0.25  # fraction of free memory left for the OS, browser and backend
MIN_MARGIN_MIB = 512
DEFAULT_CAP = 65536
FALLBACK_CTX = 8192
DEVICE_LINE = re.compile(r"^\s*(\S+):\s*(.+?)\s*\((\d+) MiB,\s*(\d+) MiB free\)")


def say(msg):
    print(msg, file=sys.stderr, flush=True)


def gpu_devices():
    """GPUs llama.cpp can use, as (name, free MiB), in llama.cpp's device order."""
    try:
        out = subprocess.run(
            ["llama-server", "--list-devices"], capture_output=True, text=True, timeout=60
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    devices = []
    for line in (out.stdout + out.stderr).splitlines():
        match = DEVICE_LINE.match(line)
        if match and int(match.group(4)) > 0:  # skip memory-less backends such as BLAS
            devices.append((match.group(2), int(match.group(4))))
    return devices


def free_ram_mib():
    """Free (available) system RAM in MiB, or None if it can't be read."""
    try:
        with open("/proc/meminfo") as meminfo:  # Linux
            for line in meminfo:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) // 1024
    except OSError:
        pass
    try:  # macOS
        out = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=10).stdout
        page = int(re.search(r"page size of (\d+) bytes", out).group(1))
        pages = sum(
            int(re.search(rf"{name}:\s+(\d+)", out).group(1))
            for name in ("Pages free", "Pages inactive", "Pages speculative")
        )
        return pages * page // (1024 * 1024)
    except (OSError, AttributeError, ValueError, subprocess.TimeoutExpired):
        return None


def margin_for(free_mib):
    return max(MIN_MARGIN_MIB, int(free_mib * KEEP_FREE_SHARE))


def gib(mib):
    return f"{mib / 1024:.1f} GB"


def main():
    model_args = sys.argv[1:]
    if not model_args:
        sys.exit("usage: plan_context.py -m model.gguf | -hf user/repo[:quant]")

    try:
        cap = int(os.environ.get("LLAMA_CTX_MAX", DEFAULT_CAP))
    except ValueError:
        cap = DEFAULT_CAP

    devices = gpu_devices()
    if devices:
        margins = [margin_for(free) for _, free in devices]
        memory_note = ", ".join(f"{name}: {gib(free)} free" for name, free in devices)
    else:
        free = free_ram_mib()
        margins = [margin_for(free) if free else 1024]
        memory_note = f"no GPU found, {gib(free)} of RAM free" if free else "no GPU found"
    fit_target = ",".join(str(m) for m in margins)

    if "-hf" in model_args:
        say("(If the model isn't downloaded yet, it is downloaded now; this can take a while.)")
    try:
        out = subprocess.run(
            ["llama-fit-params", *model_args, "--fit-target", fit_target, "-np", "1"],
            capture_output=True,
            text=True,
        )
        fitted = int(re.search(r"(?:^|\s)-c\s+(\d+)", out.stdout).group(1))
    except (OSError, AttributeError, ValueError):
        say(f"Couldn't measure how much context fits; using {FALLBACK_CTX:,} tokens.")
        print(f"{FALLBACK_CTX} {fit_target}")
        return

    ctx = min(fitted, cap)
    reason = f"capped at {cap:,}; {fitted:,} would fit" if fitted > cap else "the most that fits in memory"
    say(
        f"Context: {ctx:,} tokens ({reason}). "
        f"Memory: {memory_note}; keeping {', '.join(gib(m) for m in margins)} free."
    )
    print(f"{ctx} {fit_target}")


if __name__ == "__main__":
    main()
