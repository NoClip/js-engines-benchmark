#!/usr/bin/env python3
"""
Automated Engine Provisioner & Installer for js-engines-benchmarks.

Supports zero-permission local installation into .engines/ for:
- R8 (via local cargo build or GitHub Release prebuilts)
- Bun (via official GitHub Release zip)
- Google V8 standalone d8 (via Chrome Labs canary/release archive)
- QuickJS (via prebuilt static binaries)
- Deno (via official GitHub Release zip)
"""

import os
import sys
import platform
import shutil
import subprocess
import urllib.request
import zipfile
import tarfile
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
ENGINES_DIR = BASE_DIR / ".engines"

def detect_platform():
    """Detect current OS and CPU architecture."""
    system = platform.system().lower()
    if system.startswith("win"):
        os_name = "windows"
    elif system.startswith("darwin"):
        os_name = "darwin"
    else:
        os_name = "linux"

    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64", "x64"):
        arch = "x64"
    elif machine in ("arm64", "aarch64"):
        arch = "arm64"
    else:
        arch = machine

    return os_name, arch, f"{os_name}_{arch}"

def get_installed_path(engine):
    """Check if the engine executable exists in .engines/<id>/."""
    os_name, _, _ = detect_platform()
    install_meta = engine.get("install", {})
    binary_names = install_meta.get("binary_name", {})
    binary_name = binary_names.get(os_name, engine.get("command"))
    if os_name == "windows" and not binary_name.endswith(".exe"):
        binary_name += ".exe"

    target_path = ENGINES_DIR / engine["id"] / binary_name
    if target_path.exists() and target_path.is_file():
        return target_path
    return None

def download_file(url, dest_path, progress_callback=None):
    """Download a file via HTTP/HTTPS with progress reporting."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "js-engines-benchmark/1.0"})

    with urllib.request.urlopen(req) as response, open(dest_path, "wb") as out_file:
        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0
        chunk_size = 64 * 1024

        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            out_file.write(chunk)
            downloaded += len(chunk)
            if progress_callback and total_size > 0:
                progress_callback(downloaded, total_size)

def extract_archive(archive_path, extract_dir):
    """Extract zip, tar.gz, or tar.xz archives."""
    extract_dir.mkdir(parents=True, exist_ok=True)
    suffix = archive_path.name.lower()

    if suffix.endswith(".zip"):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    elif suffix.endswith(".tar.gz") or suffix.endswith(".tgz") or suffix.endswith(".tar.xz"):
        with tarfile.open(archive_path, 'r:*') as tar_ref:
            tar_ref.extractall(extract_dir)
    else:
        # Direct binary file
        shutil.copy2(archive_path, extract_dir)

def install_engine(engine, force=False):
    """Install the specified engine from official prebuilt binaries."""
    os_name, arch, platform_key = detect_platform()
    install_meta = engine.get("install")
    if not install_meta:
        return None

    binary_names = install_meta.get("binary_name", {})
    binary_name = binary_names.get(os_name, engine.get("command"))
    if os_name == "windows" and not binary_name.endswith(".exe"):
        binary_name += ".exe"

    engine_dir = ENGINES_DIR / engine["id"]
    final_bin_path = engine_dir / binary_name

    if final_bin_path.exists() and not force:
        return final_bin_path

    strategy = install_meta.get("strategy")
    engine_dir.mkdir(parents=True, exist_ok=True)

    print(f"[+] Provisioning engine '{engine['name']}'...")

    # Strategy 1: Direct binary download
    if strategy == "direct_binary":
        downloads = install_meta.get("downloads", {})
        download_url = downloads.get(platform_key)
        if not download_url:
            print(f"    [-] No prebuilt download available for platform '{platform_key}'")
            return None

        print(f"    [download] Fetching {download_url}...")
        try:
            def print_progress(cur, total):
                pct = int(cur / total * 100)
                sys.stdout.write(f"\r    [download] {pct}% ({cur // 1024} KB / {total // 1024} KB)")
                sys.stdout.flush()

            download_file(download_url, final_bin_path, progress_callback=print_progress)
            print()
            if os_name != "windows" and final_bin_path.exists():
                os.chmod(final_bin_path, 0o755)
        except Exception as e:
            print(f"    [!] Failed to download direct binary: {e}")
            return None

    # Strategy 3: Google V8 Standalone (dynamic canary version resolution)
    elif strategy == "v8_archive":
        v8_os_map = {
            "windows_x64": "win64",
            "linux_x64": "linux64",
            "darwin_arm64": "mac-arm64",
            "darwin_x64": "mac64"
        }
        v8_platform = v8_os_map.get(platform_key, "win64")
        version_json_url = f"https://storage.googleapis.com/chromium-v8/official/canary/v8-{v8_platform}-rel-latest.json"
        print(f"    [v8] Resolving latest canary version from {version_json_url}...")
        try:
            import json as json_lib
            req = urllib.request.Request(version_json_url, headers={"User-Agent": "js-engines-benchmark/1.0"})
            with urllib.request.urlopen(req) as resp:
                v_data = json_lib.loads(resp.read().decode("utf-8"))
                latest_v8_ver = v_data.get("version")
            download_url = f"https://storage.googleapis.com/chromium-v8/official/canary/v8-{v8_platform}-rel-{latest_v8_ver}.zip"
            print(f"    [v8] Canary version: {latest_v8_ver} -> {download_url}")
            tmp_archive = engine_dir / "download.zip"

            def print_progress(cur, total):
                pct = int(cur / total * 100)
                sys.stdout.write(f"\r    [download] {pct}% ({cur // 1024} KB / {total // 1024} KB)")
                sys.stdout.flush()

            download_file(download_url, tmp_archive, progress_callback=print_progress)
            print("\n    [extract] Unpacking V8 archive (d8, snapshot_blob, icudtl)...")
            extract_archive(tmp_archive, engine_dir)
            if tmp_archive.exists():
                tmp_archive.unlink()

            if not final_bin_path.exists():
                for found_file in engine_dir.rglob(binary_name):
                    if found_file.is_file():
                        shutil.move(str(found_file), str(final_bin_path))
                        break

            if os_name != "windows" and final_bin_path.exists():
                os.chmod(final_bin_path, 0o755)

        except Exception as e:
            print(f"    [!] Failed to download/install official V8: {e}")
            return None

    # Strategy 4: Mozilla SpiderMonkey (jsshell prebuilt archive)
    elif strategy == "spidermonkey_archive":
        sm_os_map = {
            "windows_x64": "win64",
            "linux_x64": "linux-x86_64",
            "darwin_arm64": "mac",
            "darwin_x64": "mac"
        }
        sm_platform = sm_os_map.get(platform_key, "win64")
        sm_version = "136.0"
        download_url = f"https://archive.mozilla.org/pub/firefox/releases/{sm_version}/jsshell/jsshell-{sm_platform}.zip"
        print(f"    [spidermonkey] Fetching Mozilla jsshell ({sm_version}) from {download_url}...")
        try:
            tmp_archive = engine_dir / "download.zip"

            def print_progress(cur, total):
                pct = int(cur / total * 100)
                sys.stdout.write(f"\r    [download] {pct}% ({cur // 1024} KB / {total // 1024} KB)")
                sys.stdout.flush()

            download_file(download_url, tmp_archive, progress_callback=print_progress)
            print("\n    [extract] Unpacking SpiderMonkey archive...")
            extract_archive(tmp_archive, engine_dir)
            if tmp_archive.exists():
                tmp_archive.unlink()

            # Locate js.exe or js and ensure final_bin_path exists
            for cand in ["js.exe", "js", binary_name]:
                found = list(engine_dir.rglob(cand))
                if found and found[0].is_file():
                    target_file = found[0]
                    if target_file != final_bin_path:
                        shutil.copy2(str(target_file), str(final_bin_path))
                    break

            if os_name != "windows" and final_bin_path.exists():
                os.chmod(final_bin_path, 0o755)

        except Exception as e:
            print(f"    [!] Failed to download/install SpiderMonkey: {e}")
            return None

    # Strategy 5: Generic archive download (zip / tar.gz) and extract
    elif strategy == "archive":
        downloads = install_meta.get("downloads", {})
        download_url = downloads.get(platform_key)
        if not download_url:
            print(f"    [-] No prebuilt download available for platform '{platform_key}'")
            return None

        print(f"    [download] Fetching {download_url}...")
        try:
            archive_ext = ".zip" if "zip" in download_url else ".tar.gz"
            tmp_archive = engine_dir / f"download{archive_ext}"
            
            def print_progress(cur, total):
                pct = int(cur / total * 100)
                sys.stdout.write(f"\r    [download] {pct}% ({cur // 1024} KB / {total // 1024} KB)")
                sys.stdout.flush()

            download_file(download_url, tmp_archive, progress_callback=print_progress)
            print("\n    [extract] Unpacking archive...")
            
            extract_archive(tmp_archive, engine_dir)
            if tmp_archive.exists():
                tmp_archive.unlink()

            # Find executable if nested in subdirectories
            if not final_bin_path.exists():
                for found_file in engine_dir.rglob(binary_name):
                    if found_file.is_file():
                        shutil.move(str(found_file), str(final_bin_path))
                        break

            # Ensure executable permissions on POSIX
            if os_name != "windows" and final_bin_path.exists():
                os.chmod(final_bin_path, 0o755)

        except Exception as e:
            print(f"    [!] Failed to download/install: {e}")
            return None

    if final_bin_path.exists():
        print(f"    [OK] Successfully installed to: {final_bin_path}")
        return final_bin_path
    else:
        print(f"    [!] Installation failed: binary {binary_name} not found.")
        return None

if __name__ == "__main__":
    import json
    import argparse

    engines_file = BASE_DIR / "engines.json"
    if not engines_file.exists():
        print(f"engines.json not found at {engines_file}")
        sys.exit(1)

    with open(engines_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    parser = argparse.ArgumentParser(description="js-engines-benchmarks engine installer (official prebuilt binaries)")
    parser.add_argument("engine", nargs="?", default="r8", help="Engine ID to install (e.g. r8, v8_standalone, sm, bun, deno, quickjs, or 'all')")
    parser.add_argument("--force", action="store_true", help="Force reinstall even if already installed")
    cli_args = parser.parse_args()

    for eng in data.get("engines", []):
        if eng["id"] == cli_args.engine or cli_args.engine == "all":
            install_engine(eng, force=cli_args.force)
