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
    """Install or build the specified engine."""
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

    # Strategy 1: R8 source build or release download
    if strategy == "r8_source_or_release":
        # First attempt: Check sibling source directories for cargo build
        candidates = [
            BASE_DIR.parent / "r8",
            BASE_DIR.parent / "Chromium-Rust"
        ]
        built = False
        cargo_found = shutil.which("cargo")

        if cargo_found:
            for repo_path in candidates:
                cargo_toml = repo_path / "Cargo.toml"
                if cargo_toml.exists():
                    print(f"    [r8] Found local source at {repo_path}. Building via cargo...")
                    try:
                        res = subprocess.run(
                            ["cargo", "build", "--release", "--bin", "r8"],
                            cwd=str(repo_path),
                            capture_output=True,
                            text=True,
                            timeout=600
                        )
                        built_bin = repo_path / "target" / "release" / binary_name
                        if res.returncode == 0 and built_bin.exists():
                            shutil.copy2(built_bin, final_bin_path)
                            print(f"    [r8] Build succeeded -> {final_bin_path}")
                            built = True
                            break
                    except Exception as e:
                        print(f"    [r8] Local build warning: {e}")

        if not built:
            # Fallback to GitHub Release prebuilt download
            downloads = install_meta.get("downloads", {})
            download_url = downloads.get(platform_key)
            if download_url:
                print(f"    [r8] Downloading prebuilt binary from GitHub Releases: {download_url}")
                try:
                    tmp_archive = engine_dir / f"r8_download.zip"
                    download_file(download_url, tmp_archive)
                    extract_archive(tmp_archive, engine_dir)
                    if tmp_archive.exists():
                        tmp_archive.unlink()
                except Exception as e:
                    print(f"    [r8] Notice: Prebuilt download not yet published on GitHub ({e}).")

    # Strategy 2: Direct binary download
    elif strategy == "direct_binary":
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

    # Strategy 3: Download archive (zip / tar.gz) and extract
    elif strategy in ("archive", "v8_archive"):
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
    engines_file = BASE_DIR / "engines.json"
    if not engines_file.exists():
        print(f"engines.json not found at {engines_file}")
        sys.exit(1)

    with open(engines_file, "r") as f:
        data = json.load(f)

    target_engine = sys.argv[1] if len(sys.argv) > 1 else "r8"
    for eng in data.get("engines", []):
        if eng["id"] == target_engine or target_engine == "all":
            install_engine(eng)
