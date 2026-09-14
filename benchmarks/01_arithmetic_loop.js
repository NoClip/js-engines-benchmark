// Benchmark 01: Arithmetic & Loop Throughput
// Tests JIT loop optimization, bitwise logic, and integer math throughput.

var log = typeof console !== "undefined" && console.log ? console.log : print;
var now = typeof performance !== "undefined" && performance.now ? function() { return performance.now(); } : Date.now;

var ITERATIONS = 1000000;
var MOD = 100000007;

var start = now();
var sum = 0;
for (var i = 0; i < ITERATIONS; i = i + 1) {
    sum = (sum + ((i ^ 3) * 2)) % MOD;
}
var end = now();
var duration = Math.max(1, end - start);

log("BENCHMARK_OUTPUT:" + JSON.stringify({
    name: "01_arithmetic_loop",
    category: "Compute & JIT",
    duration_ms: duration,
    checksum: sum
}));
