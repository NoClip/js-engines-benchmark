# Multi-Engine JavaScript Benchmark Suite

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Standard%20Library%20Only-brightgreen.svg)]()
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

An automated, high-precision performance benchmarking and mathematical checksum validation suite for JavaScript and WebAssembly runtimes.

Built to compare **R8 (Rust V8)**, **Google V8 (TurboFan Full JIT & Jitless)**, **Bun (JavaScriptCore)**, **Deno**, **QuickJS**, **SpiderMonkey**, and custom JavaScript engines with **zero code modifications**.

---

## 📑 Table of Contents

- [⚡ Quickstart](#-quickstart)
- [📖 Complete Usage Guide](#-complete-usage-guide)
  - [1. Basic Execution (All Engines & Benchmarks)](#1-basic-execution)
  - [2. Filtering Specific Engines](#2-filtering-specific-engines)
  - [3. Filtering Specific Benchmarks](#3-filtering-specific-benchmarks)
  - [4. Custom Warmup & Measurement Iterations](#4-custom-warmup--measurement-iterations)
  - [5. Headless / CI Mode & Custom Output Directory](#5-headless--ci-mode--custom-output-directory)
  - [6. Viewing Reports & Outputs](#6-viewing-reports--outputs)
  - [7. Complete CLI Reference Table](#7-complete-cli-reference-table)
- [🛠️ Engine Installation Guide](#%EF%B8%8F-engine-installation-guide)
  - [1. R8 (Rust V8)](#1-r8-rust-v8)
  - [2. Google V8 (TurboFan & Jitless)](#2-google-v8-turbofan--jitless)
  - [3. Bun (JavaScriptCore)](#3-bun-javascriptcore)
  - [4. Deno (V8 Runtime)](#4-deno-v8-runtime)
  - [5. QuickJS](#5-quickjs)
  - [6. Universal Engine Installer (`jsvu`)](#6-universal-engine-installer-jsvu)
- [📊 Included Benchmarks & Latest Results](#-included-benchmarks--latest-results)
- [➕ Adding Custom Benchmarks](#-adding-custom-benchmarks)
- [⚙️ Adding New Engines (`engines.json`)](#%EF%B8%8F-adding-new-engines-enginesjson)
- [📄 License](#-license)

---

## ⚡ Quickstart

### Prerequisites
- **Python 3.8+** (Zero external pip packages needed; uses Python standard library only).
- At least one JavaScript engine installed or built (e.g. Node.js for Google V8, or R8).

```bash
# 1. Clone the benchmark suite
git clone https://github.com/NoClip/js-engines-benchmark.git
cd js-engines-benchmark

# 2. Run the benchmarks (auto-detects all available engines on your machine)
python runner.py
```

> **Note**: Any engine not installed on your system is automatically detected and skipped with a polite notice. You do **not** need to install every engine to use this tool!

---

## 📖 Complete Usage Guide

### 1. Basic Execution
Run all 8 benchmarks across all detected JavaScript engines on your system with default settings (2 warmups, 5 iterations):
```bash
python runner.py
```

### 2. Filtering Specific Engines
Use `--engines` to specify one or more engine IDs defined in `engines.json`:
```bash
# Compare R8 against Google V8 TurboFan
python runner.py --engines r8 v8_turbofan

# Compare R8 against both Google V8 TurboFan and Google V8 Jitless
python runner.py --engines r8 v8_turbofan v8_jitless

# Compare all available engines including Bun and Deno
python runner.py --engines r8 v8_turbofan bun deno quickjs
```

### 3. Filtering Specific Benchmarks
Use `--benchmarks` to specify one or more benchmark script names (stem or full filename):
```bash
# Run only recursive fibonacci
python runner.py --benchmarks 02_recursive_fibonacci

# Run arithmetic loop and prime sieve
python runner.py --benchmarks 01_arithmetic_loop 08_prime_sieve
```

### 4. Custom Warmup & Measurement Iterations
Customize the statistical rigor using `--warmup` and `--iterations`:
```bash
# Quick test (0 warmups, 1 measurement run)
python runner.py --warmup 0 --iterations 1

# High-precision statistical run (5 warmups, 20 measurement runs)
python runner.py --warmup 5 --iterations 20
```

### 5. Headless / CI Mode & Custom Output Directory
For automated testing in CI/CD pipelines:
```bash
# Skip HTML report generation and output results to custom folder
python runner.py --no-html --output-dir ./ci-artifacts
```

### 6. Viewing Reports & Outputs
After running the benchmark suite, the tool generates multiple report formats:

1. **Terminal Summary Table**: Real-time mean execution time, standard deviation ($\pm\sigma$), speedup vs baseline, and checksum parity status (`PASS` / `FAIL`).
2. **Interactive HTML5 Dashboard (`report.html`)**:
   - Open in your browser:
     - **Windows**: `start report.html`
     - **macOS**: `open report.html`
     - **Linux**: `xdg-open report.html`
   - Features dynamic Bar Charts, Speedup Multipliers, and Category Breakdowns powered by Chart.js.
3. **Machine-Readable JSON (`results/latest.json`)**: Full execution metadata, raw timing samples, median, min, max, stddev, and checksums for automated analysis.
4. **Markdown Table (`results/summary.md`)**: GitHub-flavored markdown table ready for copy-pasting into pull requests or READMEs.

### 7. Complete CLI Reference Table

| Argument | Flag | Type | Default | Description |
|:---|:---|:---:|:---:|:---|
| Filter Engines | `--engines` | `str...` | *All detected* | Space-separated engine IDs to benchmark (`r8`, `v8_turbofan`, `v8_jitless`, `bun`, `deno`, `quickjs`). |
| Filter Benchmarks | `--benchmarks` | `str...` | *All (01-08)* | Space-separated benchmark names (e.g. `01_arithmetic_loop 02_recursive_fibonacci`). |
| Measurement Iterations | `--iterations` | `int` | `5` | Number of timed measurement runs per benchmark per engine. |
| Warmup Passes | `--warmup` | `int` | `2` | Number of untimed warmup passes executed before measurement to prime JIT compilation and caches. |
| Skip HTML Generation | `--no-html` | `flag` | `False` | Disables rendering the interactive `report.html` dashboard. |
| Output Directory | `--output-dir` | `str` | `results` | Path to directory where JSON, Markdown, and HTML reports are written. |
| Help | `-h`, `--help` | `flag` | - | Displays usage syntax, available flags, and exits. |

---

## 🛠️ Engine Installation Guide

The benchmark runner auto-detects whichever engines are installed on your machine. Follow the instructions below for any engines you wish to include in your benchmark runs:

---

### 1. R8 (Rust V8)
[R8](https://github.com/NoClip/r8) is Google V8 reimplemented in 100% Pure Safe Rust with zero C++ and zero external dependencies.

#### How to Build:
```bash
# Clone R8 repository next to js-engines-benchmark
git clone https://github.com/NoClip/r8.git
cd r8

# Build the release binary
cargo build --release
```
- **Binary Output**: `target/release/d8.exe` (Windows) or `target/release/d8` (Linux/macOS).
- **Auto-Discovery**: The benchmark runner automatically searches for R8 in:
  1. Sibling directories: `../r8/target/release/d8` (or `.exe`)
  2. Sibling directories: `../Chromium-Rust/target/release/d8` (or `.exe`)
  3. Environment variable `R8_PATH` (e.g. `export R8_PATH=/path/to/d8`)
  4. System `PATH` (`d8`)

---

### 2. Google V8 (TurboFan & Jitless)
Google V8 can be benchmarked directly through Node.js (which embeds official Google V8) or as a standalone `d8` binary.

#### Via Node.js (Recommended):
- **Windows**:
  ```powershell
  winget install OpenJS.NodeJS
  # Or with Chocolatey:
  choco install nodejs
  ```
- **macOS**:
  ```bash
  brew install node
  ```
- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt update && sudo apt install nodejs
  ```
*Node.js enables benchmarking both **Google V8 TurboFan** (full JIT) and **Google V8 Jitless** (`node --jitless`) out of the box.*

---

### 3. Bun (JavaScriptCore)
[Bun](https://bun.sh/) is a high-performance JavaScript runtime built on WebKit's JavaScriptCore (JSC) engine.

- **Windows**:
  ```powershell
  powershell -c "irm bun.sh/install.ps1 | iex"
  ```
- **macOS & Linux**:
  ```bash
  curl -fsSL https://bun.sh/install | bash
  ```

---

### 4. Deno (V8 Runtime)
[Deno](https://deno.land/) is a modern TypeScript/JavaScript runtime powered by Google V8 and Rust.

- **Windows**:
  ```powershell
  winget install DenoLand.Deno
  # Or PowerShell:
  irm https://deno.land/install.ps1 | iex
  ```
- **macOS**:
  ```bash
  brew install deno
  ```
- **Linux**:
  ```bash
  curl -fsSL https://deno.land/install.sh | sh
  ```

---

### 5. QuickJS
[QuickJS](https://bellard.org/quickjs/) is Fabrice Bellard's ultra-lightweight, embeddable C JavaScript engine.

- **Windows**:
  ```powershell
  # Via MSYS2:
  pacman -S mingw-w64-x86_64-quickjs
  # Or Scoop:
  scoop install quickjs
  ```
- **macOS**:
  ```bash
  brew install quickjs
  ```
- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt update && sudo apt install quickjs
  # Or compile from source:
  git clone https://github.com/bellard/quickjs.git
  cd quickjs && make && sudo make install
  ```

---

### 6. Universal Engine Installer: `jsvu`
[`jsvu`](https://github.com/GoogleChromeLabs/jsvu) (JavaScript Virtual Machine Universal installer) is an official Google tool to install standalone CLI developer shells for all major JS engines:

```bash
# 1. Install jsvu globally
npm install -g jsvu

# 2. Run jsvu and select engines (v8, spidermonkey, javascriptcore, quickjs, hermes)
jsvu

# 3. Add ~/.jsvu/bin (or %USERPROFILE%\.jsvu\bin on Windows) to your PATH
```
Once installed, standalone engine binaries (`v8`, `jsc`, `sm`, `qjs`) can be benchmarked directly.

---

## 📊 Included Benchmarks & Latest Results

| ID | Benchmark Name | Category | Workload Description |
|:---|:---|:---|:---|
| **01** | `01_arithmetic_loop` | Compute & JIT | 1,000,000 iterations of bitwise XOR, multiplications, and modulo arithmetic. |
| **02** | `02_recursive_fibonacci` | Call Stack & Recursion | Deep call stack stress test via recursive `fib(28)` calculating 317,811. |
| **03** | `03_object_shape_transitions` | Objects & Shapes | 30,000 object allocations, Hidden Class (Map) property transitions, and Inline Cache (IC) lookups. |
| **04** | `04_typedarray_throughput` | Memory & TypedArrays | 50,000 Int32Array contiguous buffer allocations, indexed writes, and reduction passes. |
| **05** | `05_array_dynamic_ops` | Arrays & Collections | 50,000 dynamic array push operations, buffer reallocations, and element traversals. |
| **06** | `06_string_slicing_concat` | Strings & Slicing | 10,000 iterations of substring extractions, string concatenation, and buffer truncations. |
| **07** | `07_crypto_hash` | Cryptography & Bitwise | 100,000 iterations of 32-bit FNV-1a cryptographic hashing and bitwise permutations. |
| **08** | `08_prime_sieve` | Algorithms & Memory | Sieve of Eratosthenes calculating primes up to 150,000 using Uint8Array memory buffers. |
| **09** | `09_websocket_broadcast` | WebSockets & I/O | RFC 6455 4-byte rotating XOR frame masking/unmasking and 32-client broadcast distribution loop (inspired by Bun's WebSocket benchmark). |
| **10** | `10_postgres_row_decode` | Database & Protocol | PostgreSQL Frontend/Backend Protocol 3.0 binary row tuple parsing and DataView big-endian decoding (inspired by Bun's Postgres benchmark). |
| **11** | `11_express_pipeline` | HTTP & Routing | HTTP/1.1 request line and header tokenization, query extraction, middleware closure chaining, and response formatting (inspired by Bun's Express benchmark). |
| **12** | `12_package_resolver` | Graphs & Resolution | DAG dependency graph building, SemVer range matching, deduplication, and topological sort (inspired by Bun's package install benchmark). |

### Latest Head-to-Head Benchmark Results
> Verified with 100% bit-for-bit mathematical checksum parity across all engines.

| Benchmark | Workload | R8 (Rust V8) | Google V8 (TurboFan) | Parity Checksum | Status |
|:---|:---|:---:|:---:|:---:|:---:|
| `01_arithmetic_loop` | Compute & JIT | **5.62 ms** | 6.11 ms | `98930007` | **PASS (100% Parity) ✓** |
| `02_recursive_fibonacci` | Recursion | **2.30 ms** | 4.96 ms | `317811` | **PASS (100% Parity) ✓** |
| `03_object_shape_transitions` | Hidden Classes | **1.00 ms** | 3.24 ms | `49954909` | **PASS (100% Parity) ✓** |
| `04_typedarray_throughput` | TypedArrays | **1.00 ms** | 2.33 ms | `69504127` | **PASS (100% Parity) ✓** |
| `05_array_dynamic_ops` | Dynamic Arrays | **1.00 ms** | 3.26 ms | `91342198` | **PASS (100% Parity) ✓** |
| `06_string_slicing_concat` | Strings & Slicing | **1.00 ms** | 3.34 ms | `327380` | **PASS (100% Parity) ✓** |
| `07_crypto_hash` | Cryptography & Bitwise | **4.06 ms** | 7.97 ms | `62024169` | **PASS (100% Parity) ✓** |
| `08_prime_sieve` | Algorithms & Memory | **1.00 ms** | 8.11 ms | `86017384` | **PASS (100% Parity) ✓** |
| `09_websocket_broadcast` | WebSockets & I/O | 68.36 ms | **3.23 ms** | `32663040` | **PASS (100% Parity) ✓** |
| `10_postgres_row_decode` | Database & Protocol | 22.64 ms | **1.91 ms** | `54979172` | **PASS (100% Parity) ✓** |
| `11_express_pipeline` | HTTP & Routing | 87.79 ms | **13.03 ms** | `15994260` | **PASS (100% Parity) ✓** |
| `12_package_resolver` | Graphs & Resolution | 61.64 ms | **8.18 ms** | `6465229` | **PASS (100% Parity) ✓** |
| **Total Suite Parity** | **All 12 Benchmarks** | **257.41 ms** | **64.43 ms** | **100% Bit-for-Bit Parity** | **12 / 12 PASS** 🏆 |

---

## ➕ Adding Custom Benchmarks

To add a new benchmark, place a `.js` file in the `benchmarks/` directory (e.g. `benchmarks/09_my_custom_workload.js`).

Each script must output a single line prefixed with `BENCHMARK_OUTPUT:` containing a JSON payload:

```javascript
// Cross-engine console/print and high-resolution timer
var log = typeof console !== "undefined" && console.log ? console.log : print;
var now = typeof performance !== "undefined" && performance.now ? function() { return performance.now(); } : Date.now;

var start = now();

// --- Execute Your Workload Here ---
var checksum = 0;
for (var i = 0; i < 500000; i++) {
    checksum = (checksum + (i ^ 42)) | 0;
}

var end = now();
var duration = Math.max(1, end - start);

// Print standardized JSON output
log("BENCHMARK_OUTPUT:" + JSON.stringify({
    name: "09_my_custom_workload",
    category: "Compute & JIT",
    duration_ms: duration,
    checksum: checksum
}));
```

The runner will automatically discover the file on its next execution!

---

## ⚙️ Adding New Engines (`engines.json`)

To benchmark any other JavaScript runtime (e.g. SpiderMonkey, Hermes, or an experimental engine), simply add an entry to [`engines.json`](engines.json):

```json
{
  "id": "spidermonkey",
  "name": "Mozilla SpiderMonkey",
  "command": "sm",
  "args": ["-f", "{file}"],
  "enabled": "auto",
  "version_args": ["--version"],
  "description": "Mozilla Firefox SpiderMonkey JavaScript engine",
  "color": "#ff7139"
}
```

- `command`: Binary executable name (on `PATH`) or relative/absolute path.
- `args`: Command-line arguments. `{file}` is automatically substituted with the path to the benchmark script.
- `enabled`: `"auto"` (probes system for presence), `true` (always run), or `false` (disabled).

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
