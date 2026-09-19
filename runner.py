#!/usr/bin/env python3
"""
Multi-Engine JavaScript Benchmark Runner
Automated High-Precision Performance & Mathematical Parity Suite
"""

import os
import sys
import json
import time
import shutil
import argparse
import subprocess
import statistics
from pathlib import Path
from installer import get_installed_path, install_engine

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).parent.resolve()
BENCHMARKS_DIR = BASE_DIR / "benchmarks"
TEMPLATES_DIR = BASE_DIR / "templates"
RESULTS_DIR = BASE_DIR / "results"
ENGINES_CONFIG = BASE_DIR / "engines.json"

PREFIX = "BENCHMARK_OUTPUT:"

def load_engine_registry():
    if not ENGINES_CONFIG.exists():
        print(f"[ERROR] Engine configuration not found: {ENGINES_CONFIG}")
        sys.exit(1)

    with open(ENGINES_CONFIG, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("engines", [])

def check_engine_availability(engine, auto_install=False, prefer_prebuilt=False):
    # 0. If prebuilt explicitly requested and engine has install metadata, provision directly
    if prefer_prebuilt and engine.get("install"):
        newly_installed = install_engine(engine, force=True, prefer_prebuilt=True)
        if newly_installed and newly_installed.is_file():
            engine["command"] = str(newly_installed)
            return True

    # 1. Check if engine is already provisioned in local .engines/<id>/
    installed = get_installed_path(engine)
    if installed and installed.is_file():
        engine["command"] = str(installed)
        return True

    # 2. If auto_install requested and engine has install metadata, provision it now
    if auto_install and engine.get("install"):
        newly_installed = install_engine(engine, prefer_prebuilt=prefer_prebuilt)
        if newly_installed and newly_installed.is_file():
            engine["command"] = str(newly_installed)
            return True

    cmd_raw = engine.get("command", "")
    cmd_path = Path(cmd_raw)

    # 3. Check if direct executable path exists
    if cmd_path.exists() and cmd_path.is_file():
        return True

    # 4. Check if relative to BASE_DIR
    rel_path = (BASE_DIR / cmd_raw).resolve()
    if rel_path.exists() and rel_path.is_file():
        engine["command"] = str(rel_path)
        return True

    # 5. For R8, search common relative sibling directories and environment variables
    if engine.get("id") == "r8":
        r8_env = os.environ.get("R8_PATH") or os.environ.get("R8_BIN")
        if r8_env and Path(r8_env).is_file():
            engine["command"] = str(Path(r8_env).resolve())
            return True

        candidates = [
            BASE_DIR.parent / "r8" / "target" / "release" / "r8.exe",
            BASE_DIR.parent / "r8" / "target" / "release" / "r8",
            BASE_DIR / "bin" / "r8.exe",
            BASE_DIR / "bin" / "r8",
        ]
        for cand in candidates:
            if cand.exists() and cand.is_file():
                engine["command"] = str(cand.resolve())
                return True

    if engine.get("id") == "bun":
        bun_home = Path.home() / ".bun" / "bin" / ("bun.exe" if os.name == "nt" else "bun")
        if bun_home.exists() and bun_home.is_file():
            engine["command"] = str(bun_home.resolve())
            return True

    # 6. Check if executable is available on system PATH
    found = shutil.which(cmd_raw)
    if found:
        return True

    if engine.get("id") == "r8":
        found_r8 = shutil.which("r8")
        if found_r8:
            engine["command"] = found_r8
            return True

    # 5. Check version args test
    version_args = engine.get("version_args", [])
    if version_args:
        try:
            cmd = [cmd_raw] + version_args
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=3)
            if res.returncode == 0:
                return True
        except Exception:
            pass

    return False

def discover_benchmarks(filter_names=None):
    if not BENCHMARKS_DIR.exists():
        print(f"[ERROR] Benchmarks directory not found: {BENCHMARKS_DIR}")
        sys.exit(1)

    benchmarks = sorted(list(BENCHMARKS_DIR.glob("*.js")))
    if filter_names:
        filter_set = set(filter_names)
        benchmarks = [b for b in benchmarks if b.stem in filter_set or b.name in filter_set]

    return benchmarks

def run_single_benchmark(engine, script_path):
    cmd_template = [engine["command"]] + engine.get("args", ["{file}"])
    resolved_cmd = [str(script_path.resolve()) if arg == "{file}" else arg for arg in cmd_template]

    start_wall = time.perf_counter()
    try:
        proc = subprocess.run(
            resolved_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
            cwd=str(BASE_DIR)
        )
        end_wall = time.perf_counter()
        wall_duration_ms = (end_wall - start_wall) * 1000.0

        if proc.returncode != 0:
            return {
                "success": False,
                "error": proc.stderr.strip() or f"Exited with code {proc.returncode}",
                "duration_ms": wall_duration_ms,
                "checksum": None
            }

        # Parse BENCHMARK_OUTPUT line
        for line in proc.stdout.splitlines():
            if line.startswith(PREFIX):
                json_part = line[len(PREFIX):].strip()
                try:
                    payload = json.loads(json_part)
                    return {
                        "success": True,
                        "duration_ms": float(payload.get("duration_ms", wall_duration_ms)),
                        "checksum": payload.get("checksum"),
                        "category": payload.get("category", "General"),
                        "error": None
                    }
                except Exception as e:
                    pass

        # Fallback if no BENCHMARK_OUTPUT line
        return {
            "success": True,
            "duration_ms": wall_duration_ms,
            "checksum": None,
            "category": "General",
            "error": None
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Timeout after 30s",
            "duration_ms": 30000.0,
            "checksum": None
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "duration_ms": 0.0,
            "checksum": None
        }

def calculate_stats(samples):
    if not samples:
        return {"mean": 0.0, "median": 0.0, "std_dev": 0.0, "min": 0.0, "max": 0.0}
    mean = statistics.mean(samples)
    median = statistics.median(samples)
    std_dev = statistics.stdev(samples) if len(samples) > 1 else 0.0
    return {
        "mean": mean,
        "median": median,
        "std_dev": std_dev,
        "min": min(samples),
        "max": max(samples)
    }

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="Multi-Engine JavaScript Benchmark Runner")
    parser.add_argument("--engines", nargs="+", help="Filter engines by ID (e.g. r8 v8_turbofan bun)")
    parser.add_argument("--type", choices=["all", "engines", "runtimes", "engine", "runtime"], default="all",
                        help="Filter execution target: 'engines' (pure VMs: R8, d8, QuickJS, JSC) or 'runtimes' (Bun, Node, Deno), or 'all' (default)")
    parser.add_argument("--benchmarks", nargs="+", help="Filter benchmarks by name (e.g. 01_arithmetic_loop)")
    parser.add_argument("--iterations", type=int, default=5, help="Number of measurement runs (default: 5)")
    parser.add_argument("--warmup", type=int, default=2, help="Number of warmup runs (default: 2)")
    parser.add_argument("--auto-install", action="store_true", help="Automatically install missing engines/runtimes into local .engines/ directory")
    parser.add_argument("--install", nargs="*", default=None, help="Explicitly install specified engines (e.g. --install bun r8 or --install all) and exit")
    parser.add_argument("--prebuilt", action="store_true", help="Prefer downloading official prebuilt binaries from GitHub Releases")
    parser.add_argument("--no-html", action="store_true", help="Skip generating HTML report")
    parser.add_argument("--output-dir", type=str, default=str(RESULTS_DIR), help="Output directory for reports")
    args = parser.parse_args()

    # Handle explicit --install action
    if args.install is not None:
        print_header("JavaScript Engine Installer")
        all_engines = load_engine_registry()
        targets = []
        if len(args.install) == 0 or "all" in args.install:
            targets = [e for e in all_engines if "install" in e]
        else:
            for tid in args.install:
                found_eng = next((e for e in all_engines if e["id"] == tid), None)
                if found_eng:
                    targets.append(found_eng)
                else:
                    print(f"[-] Unknown engine ID for installation: {tid}")

        if not targets:
            print("[!] No matching installable engines found.")
            sys.exit(1)

        print(f"Installing {len(targets)} target(s)...")
        for e in targets:
            install_engine(e, force=True, prefer_prebuilt=args.prebuilt)
        print("\n[OK] Installation routine complete.")
        sys.exit(0)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print_header("JavaScript Engines Benchmark Runner")
    print(f"Directory:    {BASE_DIR}")
    print(f"Filter Type:  {args.type}")
    print(f"Iterations:   {args.iterations} measurement runs, {args.warmup} warmups")
    if args.auto_install:
        print(f"Auto-install: Enabled (targets installed to {BASE_DIR / '.engines'})")
    if args.prebuilt:
        print(f"Mode:         Prefer official GitHub prebuilt releases")

    # 1. Discover Engines
    all_engines = load_engine_registry()
    active_engines = []

    target_type = None
    if args.type in ("engines", "engine"):
        target_type = "engine"
    elif args.type in ("runtimes", "runtime"):
        target_type = "runtime"

    for eng in all_engines:
        eng_id = eng["id"]
        if target_type and eng.get("type") != target_type:
            continue

        if args.engines and eng_id not in args.engines:
            continue

        enabled = eng.get("enabled", "auto")
        if enabled is True:
            active_engines.append(eng)
        elif enabled == "auto":
            if check_engine_availability(eng, auto_install=args.auto_install, prefer_prebuilt=args.prebuilt):
                active_engines.append(eng)
            else:
                print(f"[-] Engine '{eng['name']}' ({eng_id}) not found on system. Skipping.")
        else:
            print(f"[-] Engine '{eng['name']}' ({eng_id}) disabled in engines.json.")

    if not active_engines:
        print("\n[ERROR] No active JavaScript engines available to benchmark matching the criteria!")
        sys.exit(1)

    print(f"\n[+] Active Engines ({len(active_engines)}):")
    for eng in active_engines:
        e_type = eng.get("type", "engine").upper()
        e_backend = eng.get("engine_backend", "VM")
        print(f"    * {eng['name']:<30} [{e_type}: {e_backend:<22}] [{eng['id']}] -> {eng['command']}")

    # 2. Discover Benchmarks
    benchmark_files = discover_benchmarks(args.benchmarks)
    if not benchmark_files:
        print("\n[ERROR] No benchmark scripts found!")
        sys.exit(1)

    print(f"\n[+] Benchmarks ({len(benchmark_files)}):")
    for b in benchmark_files:
        print(f"    * {b.stem}")

    # 3. Execution Phase
    bench_meta_list = []
    results = {}

    for b_file in benchmark_files:
        b_id = b_file.stem
        print_header(f"Running Benchmark: {b_id}")
        results[b_id] = {}
        category = "General"

        for eng in active_engines:
            eng_id = eng["id"]
            sys.stdout.write(f"  [{eng['name']:<28}] Warming up ({args.warmup})... ")
            sys.stdout.flush()

            # Warmup runs
            for _ in range(args.warmup):
                run_single_benchmark(eng, b_file)

            sys.stdout.write(f"Measuring ({args.iterations})... ")
            sys.stdout.flush()

            durations = []
            checksum = None
            last_err = None

            for _ in range(args.iterations):
                res = run_single_benchmark(eng, b_file)
                if res["success"]:
                    durations.append(res["duration_ms"])
                    checksum = res["checksum"]
                    if res.get("category"):
                        category = res["category"]
                else:
                    last_err = res["error"]

            if durations:
                stats = calculate_stats(durations)
                results[b_id][eng_id] = {
                    "mean": stats["mean"],
                    "median": stats["median"],
                    "std_dev": stats["std_dev"],
                    "min": stats["min"],
                    "max": stats["max"],
                    "checksum": checksum,
                    "samples": durations,
                    "error": None
                }
                print(f"Done: {stats['mean']:6.2f} ms (±{stats['std_dev']:4.2f}) [Checksum: {checksum}]")
            else:
                results[b_id][eng_id] = {
                    "mean": 0.0,
                    "median": 0.0,
                    "std_dev": 0.0,
                    "min": 0.0,
                    "max": 0.0,
                    "checksum": None,
                    "samples": [],
                    "error": last_err
                }
                print(f"FAILED! ({last_err})")

        bench_meta_list.append({
            "id": b_id,
            "name": b_id,
            "category": category
        })

    # 4. Checksum Parity Validation & Results Summary Table
    print_header("Performance Summary & Checksum Validation")
    header_fmt = "{:<24} | {:<26} | {:<8} | {:>10} | {:>10} | {:>9} | {:>14} | {:<12}"
    print(header_fmt.format("Benchmark", "Target", "Type", "Mean (ms)", "Median", "StdDev", "vs Baseline", "Checksum"))
    print("-" * 125)

    summary_md_rows = []

    for b_meta in bench_meta_list:
        b_id = b_meta["id"]
        b_res = results[b_id]
        ref_checksum = None

        # Find baseline reference engine (prefer v8_turbofan, otherwise first active)
        baseline_mean = 1.0
        if "v8_turbofan" in b_res and b_res["v8_turbofan"]["mean"] > 0:
            baseline_mean = b_res["v8_turbofan"]["mean"]
            ref_checksum = b_res["v8_turbofan"]["checksum"]
        else:
            first_id = active_engines[0]["id"]
            if b_res[first_id]["mean"] > 0:
                baseline_mean = b_res[first_id]["mean"]
                ref_checksum = b_res[first_id]["checksum"]

        for eng in active_engines:
            e_id = eng["id"]
            e_type = eng.get("type", "engine").capitalize()
            e_backend = eng.get("engine_backend", "VM")
            data = b_res.get(e_id, {})
            if data.get("error"):
                print(header_fmt.format(b_id, eng["name"][:26], e_type, "ERR", "ERR", "ERR", "N/A", "FAIL"))
                summary_md_rows.append(f"| `{b_id}` | {eng['name']} | **{e_type}** | {e_backend} | ERR | ERR | - | FAIL |")
                continue

            mean = data["mean"]
            median = data["median"]
            std_dev = data["std_dev"]
            csum = data["checksum"]

            speedup = baseline_mean / mean if mean > 0 else 0.0
            if e_id == "v8_turbofan":
                rel_str = "1.00x (Base)"
            elif speedup >= 1.0:
                rel_str = f"{speedup:.2f}x faster"
            else:
                rel_str = f"{(1/speedup):.2f}x slower"

            csum_status = "PASS" if csum == ref_checksum else f"MISMATCH ({csum})"
            print(header_fmt.format(b_id, eng["name"][:26], e_type, f"{mean:.2f}", f"{median:.2f}", f"±{std_dev:.2f}", rel_str, csum_status))
            summary_md_rows.append(f"| `{b_id}` | {eng['name']} | **{e_type}** | {e_backend} | {mean:.2f} ms | {median:.2f} ms | {rel_str} | `{csum}` ({csum_status}) |")

    # 5. Export JSON
    export_payload = {
        "timestamp": time.time() * 1000,
        "config": {
            "iterations": args.iterations,
            "warmup": args.warmup
        },
        "engines": active_engines,
        "benchmarks": bench_meta_list,
        "results": results
    }

    json_path = out_dir / "latest.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(export_payload, f, indent=2)
    print(f"\n[+] Raw results written to: {json_path}")

    # 6. Export Summary Markdown
    summary_md_path = out_dir / "summary.md"
    with open(summary_md_path, "w", encoding="utf-8") as f:
        f.write("# JavaScript Engines Benchmark Summary\n\n")
        f.write(f"Generated on {time.ctime()} with {args.iterations} measurement passes and {args.warmup} warmups.\n\n")
        f.write("| Benchmark | Target | Type | VM Backend | Mean Duration | Median Duration | Relative vs Baseline | Mathematical Checksum |\n")
        f.write("|:---|:---|:---:|:---|:---:|:---:|:---:|:---:|\n")
        for row in summary_md_rows:
            f.write(row + "\n")
    print(f"[+] Summary markdown written to: {summary_md_path}")

    # 7. Generate Interactive HTML Report
    if not args.no_html:
        html_template_path = TEMPLATES_DIR / "report_template.html"
        if html_template_path.exists():
            with open(html_template_path, "r", encoding="utf-8") as f:
                template_str = f.read()

            rendered_html = template_str.replace(
                "/*BENCHMARK_DATA_PLACEHOLDER*/",
                json.dumps(export_payload)
            )

            html_out_path = out_dir / "report.html"
            with open(html_out_path, "w", encoding="utf-8") as f:
                f.write(rendered_html)

            # Also copy to root report.html for convenience
            root_report = BASE_DIR / "report.html"
            with open(root_report, "w", encoding="utf-8") as f:
                f.write(rendered_html)

            print(f"[+] Interactive HTML report generated: {html_out_path}")
            print(f"[+] Root report updated: {root_report}")
        else:
            print(f"[WARN] HTML template not found at {html_template_path}")

    print("\n[SUCCESS] Benchmark run complete!")

if __name__ == "__main__":
    main()
