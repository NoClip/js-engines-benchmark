// Benchmark 02: Recursive Fibonacci
// -------------------------------------------------------------------------------------
// Source & Attribution: The Computer Language Benchmarks Game (CLBG)
// Upstream Reference: https://benchmarksgame-team.pages.debian.net/benchmarksgame/
// Author: Computer Language Benchmarks Game Contributors & Classic Algorithm
// Ported to self-contained ECMAScript with deterministic mathematical checksum validation.
// -------------------------------------------------------------------------------------
// Tests call stack allocation, function frame prologue/epilogue, and recursion throughput.

var log = typeof console !== "undefined" && console.log ? console.log : print;
var now = typeof performance !== "undefined" && performance.now ? function() { return performance.now(); } : Date.now;

function fib(n) {
    if (n < 2) return n;
    var a = fib(n - 1);
    var b = fib(n - 2);
    return a + b;
}

// In-engine warmup
fib(15);

var start = now();
var result = fib(29);
var end = now();
var duration = end - start;

log("BENCHMARK_OUTPUT:" + JSON.stringify({
    name: "02_recursive_fibonacci",
    category: "Call Stack & Recursion",
    duration_ms: duration,
    checksum: result
}));
