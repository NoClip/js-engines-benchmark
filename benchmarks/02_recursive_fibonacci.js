// Benchmark 02: Recursive Fibonacci
// Tests call stack allocation, function frame prologue/epilogue, and recursion throughput.

var log = typeof console !== "undefined" && console.log ? console.log : print;
var now = typeof performance !== "undefined" && performance.now ? function() { return performance.now(); } : Date.now;

function fib(n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}

var start = now();
var result = fib(28);
var end = now();
var duration = Math.max(1, end - start);

log("BENCHMARK_OUTPUT:" + JSON.stringify({
    name: "02_recursive_fibonacci",
    category: "Call Stack & Recursion",
    duration_ms: duration,
    checksum: result
}));
