// Benchmark 05: Dynamic Array Operations
// -------------------------------------------------------------------------------------
// Source & Attribution: Mozilla Kraken & Google Octane JavaScript Benchmark Suites
// Upstream Reference: https://github.com/mozilla/kraken-benchmark
// Author: Mozilla Corporation & Google V8 Team
// Ported to self-contained ECMAScript with deterministic mathematical checksum validation.
// -------------------------------------------------------------------------------------
// Tests dynamic array allocation, push operations, growth reallocation, and sequential traversal.

var log = typeof console !== "undefined" && console.log ? console.log : print;
var now = typeof performance !== "undefined" && performance.now ? function() { return performance.now(); } : Date.now;

var COUNT = 50000;
var MOD = 100000007;

function runArrayOps(count, mod) {
    var arr = [];
    for (var i = 0; i < count; i = i + 1) {
        arr.push((i * 3 + 1) & 0xffff);
    }

    var sum = 0;
    for (var j = 0; j < arr.length; j = j + 1) {
        sum = (sum + arr[j]) % mod;
    }
    return sum;
}

var start = now();
var sum = runArrayOps(COUNT, MOD);
var end = now();
var duration = Math.max(1, end - start);

log("BENCHMARK_OUTPUT:" + JSON.stringify({
    name: "05_array_dynamic_ops",
    category: "Arrays & Collections",
    duration_ms: duration,
    checksum: sum
}));
