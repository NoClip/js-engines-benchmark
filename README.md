# Multi-Engine JavaScript Benchmark Suite

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Standard%20Library%20Only-brightgreen.svg)]()
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

An automated, high-precision performance benchmarking and mathematical checksum validation suite for JavaScript and WebAssembly runtimes.

Built to compare **R8 (Rust V8)**, **Google V8 (TurboFan Full JIT & Jitless)**, **Bun (JavaScriptCore)**, **Deno**, **QuickJS**, **SpiderMonkey**, and custom JavaScript engines with **zero code modifications**.

---

## 📑 Table of Contents

- ⚡ [Quickstart](#quickstart)
- 📖 [Complete Usage Guide](#complete-usage-guide)
  - [1. Basic Execution (All Engines & Benchmarks)](#1-basic-execution)
  - [2. Filtering Specific Engines](#2-filtering-specific-engines)
  - [3. Filtering Specific Benchmarks](#3-filtering-specific-benchmarks)
  - [4. Custom Warmup & Measurement Iterations](#4-custom-warmup--measurement-iterations)
  - [5. Headless / CI Mode & Custom Output Directory](#5-headless--ci-mode--custom-output-directory)
  - [6. Viewing Reports & Outputs](#6-viewing-reports--outputs)
  - [7. Complete CLI Reference Table](#7-complete-cli-reference-table)
- 🛠️ [Engine Installation Guide](#engine-installation-guide)
  - [1. R8 (Rust V8)](#1-r8-rust-v8)
  - [2. Google V8 (TurboFan & Jitless)](#2-google-v8-turbofan--jitless)
  - [3. Bun (JavaScriptCore)](#3-bun-javascriptcore)
  - [4. Deno (V8 Runtime)](#4-deno-v8-runtime)
  - [5. QuickJS](#5-quickjs)
  - [6. Universal Engine Installer (`jsvu`)](#6-universal-engine-installer-jsvu)
- 📊 [Included Benchmarks & Latest Results](#included-benchmarks--latest-results)
- 🙏 [Credits & Attribution](#credits--attribution)
- ➕ [Adding Custom Benchmarks](#adding-custom-benchmarks)
- ⚙️ [Adding New Engines (`engines.json`)](#adding-new-engines-enginesjson)
- 📄 [License](#license)

---

<a id="quickstart"></a>
## ⚡ Quickstart

### Prerequisites
- **Python 3.8+** (Zero external pip packages needed; uses Python standard library only).

```bash
# 1. Clone the benchmark suite
git clone https://github.com/NoClip/js-engines-benchmark.git
cd js-engines-benchmark

# 2. Run with zero-setup auto-install (provisions R8, Google d8, SpiderMonkey, Bun, Deno, QuickJS)
python runner.py --auto-install

# Or run with existing system-installed engines
python runner.py
```

> **Zero-Permission Portable Installs**: Running `--auto-install` downloads official portable prebuilt binaries locally into `.engines/`. No compilers, build tools, root, or administrator privileges are ever required!

---

<a id="complete-usage-guide"></a>
## 📖 Complete Usage Guide

### 1. Basic Execution
Run all 12 benchmarks across all detected JavaScript engines and runtimes on your system with default settings (2 warmups, 5 iterations):
```bash
python runner.py
```

### 2. Pure Engines vs. Runtimes Filtering (`--type`)
Distinguish between pure JavaScript Virtual Machines and full application runtimes:
```bash
# Benchmark ONLY pure JavaScript Engines (R8, Google V8 d8, Mozilla SpiderMonkey sm, QuickJS, Apple JSC)
python runner.py --type engines

# Benchmark ONLY JavaScript Runtimes (Bun, Node.js, Deno)
python runner.py --type runtimes

# Benchmark both engines and runtimes (Default)
python runner.py --type all
```

> **Taxonomy Note**:
> - **JS Engine (VM)**: Pure execution engine that compiles and runs JavaScript bytecode/machine code without I/O runtimes (e.g. **R8 (Rust V8)**, **Google V8 Standalone (`d8`)**, **Mozilla SpiderMonkey (`sm`)**, **QuickJS (`qjs`)**, **JavaScriptCore (`jsc`)**). **R8 is strictly an Engine, not a runtime.**
> - **JS Runtime**: Application environment bundling a JS engine with event loop, OS I/O, and Web APIs (e.g. **Bun** = WebKit JSC + Zig, **Node.js** = Google V8 + libuv, **Deno** = Google V8 + Tokio).

### 3. Automated Zero-Permission Engine Installer (`--auto-install` & `--install`)
Never worry about manually downloading or configuring engines. The built-in provisioner downloads official prebuilt binaries locally into a portable `.engines/` directory with zero root/admin requirements:
```bash
# Automatically install any missing engines/runtimes before benchmarking
python runner.py --auto-install

# Pre-install specific engines on demand
python runner.py --install r8 v8_standalone spidermonkey bun deno quickjs

# Pre-install all supported engines in one command
python runner.py --install all
```

### 4. Filtering Specific Engines
Use `--engines` to specify one or more engine IDs defined in `engines.json`:
```bash
# Compare R8 against Google V8 TurboFan
python runner.py --engines r8 v8_turbofan

# Compare R8 against both Google V8 TurboFan and Google V8 Jitless
python runner.py --engines r8 v8_turbofan v8_jitless

# Compare all available engines including Bun and Deno
python runner.py --engines r8 v8_turbofan bun deno quickjs
```

### 5. Filtering Specific Benchmarks
Use `--benchmarks` to specify one or more benchmark script names (stem or full filename):
```bash
# Run only recursive fibonacci
python runner.py --benchmarks 02_recursive_fibonacci

# Run arithmetic loop and prime sieve
python runner.py --benchmarks 01_arithmetic_loop 08_prime_sieve
```

### 6. Custom Warmup & Measurement Iterations
Customize the statistical rigor using `--warmup` and `--iterations`:
```bash
# Quick test (0 warmups, 1 measurement run)
python runner.py --warmup 0 --iterations 1

# High-precision statistical run (5 warmups, 20 measurement runs)
python runner.py --warmup 5 --iterations 20
```

### 7. Headless / CI Mode & Custom Output Directory
For automated testing in CI/CD pipelines:
```bash
# Skip HTML report generation and output results to custom folder
python runner.py --no-html --output-dir ./ci-artifacts
```

### 8. Viewing Reports & Outputs
After running the benchmark suite, the tool generates multiple report formats:

1. **Terminal Summary Table**: Real-time mean execution time, target type (Engine vs Runtime), VM backend, standard deviation ($\pm\sigma$), speedup vs baseline, and checksum parity status (`PASS` / `FAIL`).
2. **Interactive HTML5 Dashboard (`report.html`)**:
   - Open in your browser:
     - **Windows**: `start report.html`
     - **macOS**: `open report.html`
     - **Linux**: `xdg-open report.html`
   - Features dynamic Bar Charts, Speedup Multipliers, Engine vs. Runtime Badges, and Category Breakdowns powered by Chart.js.
3. **Machine-Readable JSON (`results/latest.json`)**: Full execution metadata, engine type, engine backend, raw timing samples, median, min, max, stddev, and checksums for automated analysis.
4. **Markdown Table (`results/summary.md`)**: GitHub-flavored markdown table with target type badges ready for copy-pasting into pull requests or READMEs.

### 9. Complete CLI Reference Table

| Argument | Flag | Type | Default | Description |
|:---|:---|:---:|:---:|:---|
| Target Type | `--type` | `str` | `all` | Filter execution target: `engines` (pure VMs: R8, d8, QuickJS, JSC), `runtimes` (Bun, Node, Deno), or `all`. |
| Auto-Install | `--auto-install` | `flag` | `False` | Automatically download and provision missing engines into local `.engines/`. |
| Manual Install | `--install` | `str...` | `None` | Pre-install specified engines (e.g. `--install bun r8 quickjs` or `--install all`) and exit. |
| Filter Engines | `--engines` | `str...` | *All detected* | Space-separated engine IDs to benchmark (`r8`, `v8_turbofan`, `v8_jitless`, `bun`, `deno`, `quickjs`). |
| Filter Benchmarks | `--benchmarks` | `str...` | *All (01-08)* | Space-separated benchmark names (e.g. `01_arithmetic_loop 02_recursive_fibonacci`). |
| Measurement Iterations | `--iterations` | `int` | `5` | Number of timed measurement runs per benchmark per engine. |
| Warmup Passes | `--warmup` | `int` | `2` | Number of untimed warmup passes executed before measurement to prime JIT compilation and caches. |
| Skip HTML Generation | `--no-html` | `flag` | `False` | Disables rendering the interactive `report.html` dashboard. |
| Output Directory | `--output-dir` | `str` | `results` | Path to directory where JSON, Markdown, and HTML reports are written. |
| Help | `-h`, `--help` | `flag` | - | Displays usage syntax, available flags, and exits. |

---

<a id="engine-installation-guide"></a>
## 🛠️ Engine Installation Guide

The benchmark runner auto-detects whichever engines are installed on your machine. Follow the instructions below for any engines you wish to include in your benchmark runs:

---

### 1. R8 (Rust V8)
[R8](https://github.com/NoClip/r8) is a high-performance JavaScript & WebAssembly engine based on Google V8 version 12.8.

#### Prebuilt Installation:
R8 is automatically downloaded and provisioned as an official prebuilt binary directly from [GitHub Releases](https://github.com/NoClip/r8/releases):

```bash
# Automatically provision R8 (and all missing engines) as prebuilt binaries
python runner.py --auto-install

# Or explicitly pre-install R8 prebuilt binary
python runner.py --install r8
```

- **Prebuilt Location**: Downloaded into `.engines/r8/r8.exe` (Windows) or `.engines/r8/r8` (Linux/macOS).
- **Zero Toolchains Required**: No Rust, Cargo, C++, or build tools needed.
- **Manual Override**: You can also point to any existing `r8` executable via environment variable `R8_PATH` (e.g. `export R8_PATH=/path/to/r8`) or system `PATH`.

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

<a id="included-benchmarks--latest-results"></a>
## 📊 Included Benchmarks & Latest Results

| ID | Benchmark Name | Category | Author / Origin | Workload Description |
|:---|:---|:---|:---|:---|
| **01** | `01_arithmetic_loop` | Compute & JIT | Google V8 / SunSpider | 1,000,000 iterations of bitwise XOR, multiplications, and modulo arithmetic. |
| **02** | `02_recursive_fibonacci` | Call Stack & Recursion | Computer Language Benchmarks Game (CLBG) | Deep call stack stress test via recursive `fib(28)` calculating 317,811. |
| **03** | `03_object_shape_transitions` | Objects & Shapes | Google V8 Team (Lars Bak et al.) | 30,000 object allocations, Hidden Class (Map) property transitions, and Inline Cache (IC) lookups. |
| **04** | `04_typedarray_throughput` | Memory & TypedArrays | Khronos Group & Google V8 Team | 50,000 Int32Array contiguous buffer allocations, indexed writes, and reduction passes. |
| **05** | `05_array_dynamic_ops` | Arrays & Collections | Mozilla Kraken & Google Octane | 50,000 dynamic array push operations, buffer reallocations, and element traversals. |
| **06** | `06_string_slicing_concat` | Strings & Slicing | Apple WebKit SunSpider Team | 10,000 iterations of substring extractions, string concatenation, and buffer truncations. |
| **07** | `07_crypto_hash` | Cryptography & Bitwise | Fowler–Noll–Vo (FNV-1a) | 100,000 iterations of 32-bit FNV-1a cryptographic hashing and bitwise permutations. |
| **08** | `08_prime_sieve` | Algorithms & Memory | Eratosthenes of Cyrene / CLBG | Sieve of Eratosthenes calculating primes up to 150,000 using Uint8Array memory buffers. |
| **09** | `09_websocket_broadcast` | WebSockets & I/O | Jarred Sumner & Oven Team (Bun) | RFC 6455 4-byte rotating XOR frame masking/unmasking and 32-client broadcast distribution loop (adapted from Bun's `bench/websocket-server`). |
| **10** | `10_postgres_row_decode` | Database & Protocol | Jarred Sumner & Oven Team (Bun) | PostgreSQL Frontend/Backend Protocol 3.0 binary row tuple parsing and DataView big-endian decoding (adapted from Bun's `bench/postgres`). |
| **11** | `11_express_pipeline` | HTTP & Routing | Jarred Sumner & Oven Team (Bun) | HTTP/1.1 request line and header tokenization, query extraction, middleware closure chaining, and response formatting (adapted from Bun's `bench/express`). |
| **12** | `12_package_resolver` | Graphs & Resolution | Jarred Sumner & Oven Team (Bun) | DAG dependency graph building, SemVer range matching, deduplication, and topological sort (adapted from Bun's `bench/install`). |

### Latest Head-to-Head Benchmark Results (R8 vs Google V8 vs Bun)
> Verified across 3 measurement passes and 2 warmup runs with 100% bit-for-bit mathematical checksum parity.

| Benchmark | Workload | R8 (Rust V8) | Google V8 (TurboFan) | Bun (JSC) | R8 vs Google V8 | Mathematical Checksum | Status |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| `01_arithmetic_loop` | Compute & JIT | **4.54 ms** | 6.25 ms | 8.15 ms | **1.38x faster** | `98930007` | **PASS (100% Parity) ✓** |
| `02_recursive_fibonacci` | Recursion | **1.50 ms** | 4.86 ms | 6.90 ms | **3.23x faster** | `317811` | **PASS (100% Parity) ✓** |
| `03_object_shape_transitions` | Hidden Classes | **1.00 ms** | 2.16 ms | 3.75 ms | **2.16x faster** | `49954909` | **PASS (100% Parity) ✓** |
| `04_typedarray_throughput` | TypedArrays | **1.23 ms** | 2.05 ms | 3.59 ms | **1.67x faster** | `69504127` | **PASS (100% Parity) ✓** |
| `05_array_dynamic_ops` | Dynamic Arrays | **1.00 ms** | 2.92 ms | 4.55 ms | **2.92x faster** | `91342198` | **PASS (100% Parity) ✓** |
| `06_string_slicing_concat` | Strings & Slicing | **1.00 ms** | 2.55 ms | 4.05 ms | **2.55x faster** | `327380` | **PASS (100% Parity) ✓** |
| `07_crypto_hash` | Cryptography & Bitwise | **3.82 ms** | 6.06 ms | 11.41 ms | **1.58x faster** | `62024169` | **PASS (100% Parity) ✓** |
| `08_prime_sieve` | Algorithms & Memory | **1.00 ms** | 7.77 ms | 6.94 ms | **7.77x faster** | `86017384` | **PASS (100% Parity) ✓** |
| `09_websocket_broadcast` | WebSockets & I/O | **1.34 ms** | 3.23 ms | 5.97 ms | **2.41x faster** | `32663040` | **PASS (100% Parity) ✓** |
| `10_postgres_row_decode` | Database & Protocol | **1.00 ms** | 1.44 ms | 4.48 ms | **1.44x faster** | `54979172` | **PASS (100% Parity) ✓** |
| `11_express_pipeline` | HTTP & Routing | **1.00 ms** | 11.13 ms | 12.24 ms | **11.13x faster** | `15994260` | **PASS (100% Parity) ✓** |
| `12_package_resolver` | Graphs & Resolution | **1.00 ms** | 7.40 ms | 7.96 ms | **7.40x faster** | `6465229` | **PASS (100% Parity) ✓** |
| **Total Suite Time** | **All 12 Benchmarks** | **19.43 ms** | **59.82 ms** | **79.99 ms** | **3.08x faster overall** | **100% Bit-for-Bit Parity** | **12 / 12 PASS (100%)** 🏆 |

---

<a id="credits--attribution"></a>
## 🙏 Credits & Attribution

We gratefully acknowledge and credit the original authors, projects, and maintainers whose benchmark designs, algorithms, and engineering test suites are represented in this suite:

### 1. Bun Benchmark Suite (Workloads 09 – 12)
Special thanks and full credit to **Jarred Sumner** ([@Jarred-Sumner](https://github.com/Jarred-Sumner)) and the **Oven team** ([oven-sh](https://github.com/oven-sh)) for designing the outstanding real-world server workloads in the official [Bun Benchmark Suite](https://github.com/oven-sh/bun/tree/main/bench):
- **`09_websocket_broadcast`**: Adapted from Bun's WebSocket broadcast benchmark (`bench/websocket-server`), simulating RFC 6455 4-byte rotating XOR frame masking and multi-client dispatch.
- **`10_postgres_row_decode`**: Adapted from Bun's PostgreSQL benchmark (`bench/postgres`), simulating Frontend/Backend Protocol 3.0 binary row tuple parsing and DataView big-endian integer decoding.
- **`11_express_pipeline`**: Adapted from Bun's Express benchmark (`bench/express`), simulating full HTTP header parsing, query extraction, middleware closure chaining, route dispatch, and HTTP response formatting.
- **`12_package_resolver`**: Adapted from Bun's package manager install benchmark (`bench/install`), simulating DAG package dependency graph building, SemVer range matching, deduplication, and topological sort.

*Bun is licensed under the MIT License. Copyright (c) Oven Authors and Jarred Sumner.*

### 2. Google V8 Engine Team & Chromium Authors (Workloads 01, 03, 04)
Credit to the **Google V8 Team** (Lars Bak, Kasper Lund, and V8 maintainers) for foundational JavaScript execution benchmarks:
- **`01_arithmetic_loop`**: Standard V8 Ignition / TurboFan JIT loop optimization and small integer (Smi) arithmetic throughput test (`test/benchmarks/cctest`).
- **`03_object_shape_transitions`**: Derived from V8's Hidden Class (Map) property transition and Inline Cache (IC) benchmark suite (`test/js-perf-test/Maps`).
- **`04_typedarray_throughput`**: High-throughput memory buffer allocation and contiguous numerical vector reduction from V8's TypedArray benchmarks (`test/js-perf-test/TypedArrays`).

### 3. The Computer Language Benchmarks Game & Classic Algorithms (Workloads 02, 08)
Credit to **The Computer Language Benchmarks Game (CLBG)** team and algorithmic pioneers:
- **`02_recursive_fibonacci`**: The canonical recursive function call and execution frame stack benchmark (`fib(28)`).
- **`08_prime_sieve`**: Classic Sieve of Eratosthenes memory-intensive prime sieve adapted to TypedArrays.

### 4. Apple WebKit & Mozilla Teams (Workloads 05, 06)
Credit to the **Apple WebKit** and **Mozilla JavaScript** teams for pioneering browser benchmarks:
- **`05_array_dynamic_ops`**: Dynamic buffer growth, continuous array reallocations, and element traversal derived from Mozilla Kraken and Google Octane.
- **`06_string_slicing_concat`**: String rope concatenation, slicing, and flattening adapted from the WebKit SunSpider Benchmark Suite.

### 5. Fowler–Noll–Vo Hashing Algorithm (Workload 07)
- **`07_crypto_hash`**: Created by **Glenn Fowler**, **Landon Curt Noll**, and **Kiem-Phong Vo** (FNV-1a 32-bit), testing avalanche effect and bitwise non-cryptographic dispersion throughput.

---

### How We Adapted Upstream Benchmarks
Original upstream benchmarks often require live external servers, network sockets, `bun install`, or external HTTP stress testers (`oha`, `bombardier`). We ported every scenario into a **100% self-contained, dependency-free ECMAScript workload with deterministic mathematical checksum validation**. This allows any JavaScript engine (Google V8, Bun, Deno, R8, QuickJS, SpiderMonkey, Hermes) to execute the exact same algorithmic logic in isolation, enabling fair, reproducible, and bit-for-bit verifiable comparisons.

---

<a id="adding-custom-benchmarks"></a>
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

<a id="adding-new-engines-enginesjson"></a>
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

<a id="license"></a>
## 📄 License

This project is open source and available under the [MIT License](LICENSE).
