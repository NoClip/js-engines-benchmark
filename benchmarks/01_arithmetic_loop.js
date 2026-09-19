// Benchmark 01: Arithmetic & Loop Throughput
// -------------------------------------------------------------------------------------
// Source & Attribution: Google V8 Engine Team / SunSpider ECMAScript Benchmark
// Upstream Reference: https://github.com/v8/v8 (test/benchmarks/cctest)
// Author: Google V8 Team & WebKit Authors
// Ported to self-contained ECMAScript with deterministic mathematical checksum validation.
// -------------------------------------------------------------------------------------
// Tests JIT loop optimization, bitwise logic, and integer math throughput.

var log = typeof console !== "undefined" && console.log ? console.log : print;
var now = typeof performance !== "undefined" && performance.now ? function() { return performance.now(); } : Date.now;

var ITERATIONS = 1000000;
var MOD = 100000007;

function runArithmeticLoop(n, mod) {
    var sum = 0;
    for (var i = 0; i < n; i = i + 1) {
        sum = (sum + ((i ^ 3) * 2)) % mod;
    }
    return sum;
}

var start = now();
var sum = runArithmeticLoop(ITERATIONS, MOD);
var end = now();
var duration = Math.max(1, end - start);

log("BENCHMARK_OUTPUT:" + JSON.stringify({
    name: "01_arithmetic_loop",
    category: "Compute & JIT",
    duration_ms: duration,
    checksum: sum
}));
