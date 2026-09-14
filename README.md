# Multi-Engine JavaScript Benchmark Suite

An automated, high-precision performance benchmarking and mathematical checksum validation suite for JavaScript and WebAssembly runtimes.

Built to compare **Google V8**, **R8 (Rust V8)**, **Bun (JavaScriptCore)**, **Deno**, **QuickJS**, and any future JavaScript engines with zero code modifications.

---

## Key Features

- 🚀 **Dynamic Pluggability**: Add any new JavaScript engine in seconds by adding a JSON entry to `engines.json`. No runner changes required.
- 🎯 **Mathematical Parity Verification**: Every benchmark computes a deterministic checksum. The runner automatically validates bit-for-bit equality across all engines to ensure correct semantics alongside speed.
- 📊 **Statistical Rigor**: Configurable warmup passes (default: 2) and measurement passes (default: 5). Computes Mean, Median, Min, Max, and Standard Deviation (StdDev).
- 📈 **Interactive Visual Reports**: Generates an interactive, responsive HTML5 dashboard powered by Chart.js (`report.html`) featuring execution time comparisons, relative speedup multipliers, and category breakdowns.
- 💾 **Machine-Readable Outputs**: Generates JSON exports (`results/latest.json`) and Markdown summaries (`results/summary.md`) for CI/CD pipelines.

---

## Included Benchmarks

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

---

## Quickstart

### Prerequisites
- Python 3.8+
- Node.js (for Google V8 TurboFan & Jitless)
- R8 executable (`d8.exe` built in release mode)
- Optional: Bun, Deno, QuickJS (auto-detected if present on PATH)

### Running Benchmarks
Run the full suite across all available engines:
```bash
python runner.py
```

### Filtering Engines
Benchmark only specific engines (e.g. R8 vs Google V8 TurboFan):
```bash
python runner.py --engines r8 v8_turbofan
```

### Filtering Benchmarks
Run a subset of benchmarks:
```bash
python runner.py --benchmarks 01_arithmetic_loop 02_recursive_fibonacci
```

### Custom Warmups and Iterations
```bash
python runner.py --warmup 3 --iterations 10
```

---

## How to Add a New Engine

To add a new JavaScript engine (e.g., SpiderMonkey `js`, Hermes, or custom build), simply add an entry to `engines.json`:

```json
{
  "id": "spidermonkey",
  "name": "Mozilla SpiderMonkey",
  "command": "js",
  "args": ["-f", "{file}"],
  "enabled": "auto",
  "version_args": ["--version"],
  "description": "Mozilla SpiderMonkey JavaScript engine",
  "color": "#ff7139"
}
```

The runner automatically:
1. Probes the binary's presence on your system.
2. Invokes the engine with the provided arguments (`{file}` is replaced with the benchmark script path).
3. Parses the standard output protocol and compares it against all other engines.

---

## Benchmark Script Protocol

All benchmark scripts are standalone `.js` files placed in `benchmarks/`. Each script must output a single line starting with `BENCHMARK_OUTPUT:` containing a JSON payload:

```javascript
var log = typeof console !== "undefined" && console.log ? console.log : print;
var now = typeof performance !== "undefined" && performance.now ? function() { return performance.now(); } : Date.now;

var start = now();
// ... execute workload ...
var end = now();
var duration = Math.max(1, end - start);

log("BENCHMARK_OUTPUT:" + JSON.stringify({
    name: "my_benchmark_name",
    category: "My Category",
    duration_ms: duration,
    checksum: computedChecksum
}));
```

---

## License

This project is open source and available under the [MIT License](LICENSE).
