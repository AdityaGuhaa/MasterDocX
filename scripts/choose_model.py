#!/usr/bin/env python3
# Copyright (c) 2026 Aditya Guha
# SPDX-License-Identifier: MIT

"""Pick the LLM that llama-server should load. Used by start.sh.

Asks the user whether they already have a model, offers the GGUF models it
finds on this computer (LM Studio, Ollama, llama.cpp / Hugging Face caches,
~/models, ~/Downloads, ...), or lets them type a path. Downloads are only
offered as an option and need an explicit "yes" first.

Prompts go to stderr; the answer is printed to stdout as one line:
    m <path to .gguf>         load a local file
    hf <user/repo[:quant]>    download from Hugging Face (user agreed)
    none                      start without an LLM

Usage: choose_model.py --config FILE [--reconfigure]
"""
import argparse
import json
import os
import sys
from pathlib import Path

DOWNLOADS = [
    ("Llama 3.1 8B Instruct (recommended, best answers)", "bartowski/Meta-Llama-3.1-8B-Instruct-GGUF:Q4_K_M", "4.9 GB"),
    ("Llama 3.2 3B Instruct (lighter, for 8 GB RAM machines)", "bartowski/Llama-3.2-3B-Instruct-GGUF:Q4_K_M", "2.0 GB"),
]

MIN_MODEL_BYTES = 50 * 1024 * 1024  # skip tokenizer/vocab test files


def say(msg=""):
    print(msg, file=sys.stderr, flush=True)


def ask(prompt):
    sys.stderr.write(prompt)
    sys.stderr.flush()
    line = sys.stdin.readline()
    if not line:  # EOF (e.g. Ctrl+D)
        return ""
    return line.strip()


def ask_yes_no(prompt, default):
    hint = "[Y/n]" if default else "[y/N]"
    while True:
        answer = ask(f"{prompt} {hint} ").lower()
        if not answer:
            return default
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        say("Please answer y or n.")


def human_size(num_bytes):
    return f"{num_bytes / 1e9:.1f} GB"


def is_model_file(path):
    name = path.name.lower()
    return (
        name.endswith(".gguf")
        and "mmproj" not in name  # vision projector, not a language model
        and not name.startswith("ggml-vocab")
    )


def search_dirs():
    home = Path.home()
    dirs = [
        home / ".lmstudio" / "models",
        home / ".cache" / "lm-studio" / "models",
        home / "Library" / "Caches" / "llama.cpp",
        home / ".cache" / "llama.cpp",
        home / ".cache" / "huggingface" / "hub",
        home / "Library" / "Application Support" / "nomic.ai" / "GPT4All",
        home / "jan" / "models",
        home / "models",
        home / "Models",
        home / "llama.cpp" / "models",
        home / "Downloads",
    ]
    if os.environ.get("HF_HOME"):
        dirs.append(Path(os.environ["HF_HOME"]) / "hub")
    if os.environ.get("LLAMA_CACHE"):
        dirs.append(Path(os.environ["LLAMA_CACHE"]))
    return dirs


def find_gguf_files():
    found = []
    for base in search_dirs():
        if not base.is_dir():
            continue
        for root, dirnames, filenames in os.walk(base):
            # don't descend too deep into unrelated folders like Downloads
            if len(Path(root).relative_to(base).parts) >= 6:
                dirnames[:] = []
            dirnames[:] = [d for d in dirnames if not d.startswith(".") and d != "node_modules"]
            for filename in filenames:
                path = Path(root) / filename
                if not is_model_file(path):
                    continue
                try:
                    size = path.stat().st_size
                except OSError:
                    continue
                if size >= MIN_MODEL_BYTES:
                    found.append((path.name, str(path), size))
    return found


def find_ollama_models():
    """Ollama stores GGUF weights as blobs; llama-server can load them directly."""
    root = Path(os.environ.get("OLLAMA_MODELS", Path.home() / ".ollama" / "models"))
    manifests = root / "manifests"
    found = []
    if not manifests.is_dir():
        return found
    for manifest in manifests.rglob("*"):
        if not manifest.is_file():
            continue
        try:
            data = json.loads(manifest.read_text())
        except (OSError, ValueError):
            continue
        for layer in data.get("layers", []):
            if layer.get("mediaType") != "application/vnd.ollama.image.model":
                continue
            blob = root / "blobs" / layer["digest"].replace(":", "-")
            if blob.is_file():
                rel = manifest.relative_to(manifests).parts
                name = f"{rel[-2]}:{rel[-1]}" if len(rel) >= 2 else manifest.name
                found.append((f"{name} (from Ollama)", str(blob), blob.stat().st_size))
    return found


def find_local_models():
    models, seen = [], set()
    for label, path, size in find_ollama_models() + find_gguf_files():
        real = os.path.realpath(path)
        if real not in seen:
            seen.add(real)
            models.append((label, path, size))
    return sorted(models, key=lambda m: m[0].lower())


def ask_for_path():
    while True:
        raw = ask("Path to your .gguf model file (leave empty to go back): ")
        if not raw:
            return None
        path = Path(os.path.expanduser(raw.strip("'\""))).resolve()
        if not path.is_file():
            say(f"  No file found at {path}")
            continue
        if path.suffix.lower() != ".gguf" and not ask_yes_no(
            "  llama.cpp needs a GGUF model and this isn't a .gguf file. Use it anyway?", False
        ):
            continue
        return f"m {path}"


def choose_existing():
    say("Looking for models on this computer...")
    models = find_local_models()
    if not models:
        say("  No GGUF models found in the usual places (LM Studio, Ollama, Hugging Face/llama.cpp caches, ~/models, ~/Downloads).")
        return ask_for_path()

    say(f"Found {len(models)} model(s):")
    for i, (label, path, size) in enumerate(models, 1):
        say(f"  {i}) {label}  [{human_size(size)}]")
        say(f"       {path}")
    say(f"  {len(models) + 1}) Enter a path myself")
    while True:
        answer = ask(f"Choose 1-{len(models) + 1} (leave empty to go back): ")
        if not answer:
            return None
        if answer.isdigit() and 1 <= int(answer) <= len(models) + 1:
            if int(answer) == len(models) + 1:
                return ask_for_path()
            return f"m {models[int(answer) - 1][1]}"
        say("Please enter one of the numbers shown.")


def choose_download():
    say("Options:")
    for i, (label, repo, size) in enumerate(DOWNLOADS, 1):
        say(f"  {i}) Download {label}, about {size}")
    custom = len(DOWNLOADS) + 1
    skip = len(DOWNLOADS) + 2
    say(f"  {custom}) Download another model from Hugging Face (you enter its name)")
    say(f"  {skip}) Don't download anything; start without AI features")
    while True:
        answer = ask(f"Choose 1-{skip}: ")
        if not answer.isdigit() or not 1 <= int(answer) <= skip:
            say("Please enter one of the numbers shown.")
            continue
        choice = int(answer)
        if choice == skip:
            return "none"
        if choice == custom:
            repo = ask("Hugging Face GGUF repo, e.g. bartowski/Qwen2.5-7B-Instruct-GGUF:Q4_K_M: ")
            if not repo or "/" not in repo:
                say("  That doesn't look like user/repo; let's try again.")
                continue
            size = "an unknown amount"
        else:
            _, repo, size = DOWNLOADS[choice - 1]
        if ask_yes_no(f"This downloads {repo} ({size}) into llama.cpp's cache. Start the download?", False):
            return f"hf {repo}"


def interactive_choice():
    say("")
    say("=== Choose the AI model (LLM) for MasterDocX ===")
    say("MasterDocX runs the model locally with llama.cpp and needs a model in GGUF format.")
    while True:
        if ask_yes_no("Do you already have an LLM model on this computer?", True):
            choice = choose_existing()
        else:
            choice = choose_download()
        if choice:
            return choice


def load_saved(config):
    try:
        line = config.read_text().strip()
    except OSError:
        return None
    kind, _, value = line.partition(" ")
    if kind == "m" and Path(value).is_file():
        return line
    if kind == "hf" and value:
        return line
    if kind == "m":
        say(f"Saved model not found anymore: {value}")
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="file that remembers the choice")
    parser.add_argument("--reconfigure", action="store_true", help="ignore the saved choice and ask again")
    args = parser.parse_args()
    config = Path(args.config)

    if not args.reconfigure:
        saved = load_saved(config)
        if saved:
            print(saved)
            return

    if not sys.stdin.isatty():
        say("No model chosen and no terminal to ask in; starting without AI features.")
        say("Run ./start.sh in a terminal, or set LLAMA_MODEL_PATH=/path/to/model.gguf.")
        print("none")
        return

    try:
        choice = interactive_choice()
    except KeyboardInterrupt:
        say("")
        print("none")
        return

    if choice != "none" and ask_yes_no("Remember this choice for next time?", True):
        config.write_text(choice + "\n")
        say(f"Saved to {config.name}. Run ./start.sh --choose-model to change it.")
    print(choice)


if __name__ == "__main__":
    main()
