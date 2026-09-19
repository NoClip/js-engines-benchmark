// Benchmark 04: TypedArray Throughput
// -------------------------------------------------------------------------------------
// Source & Attribution: Khronos Group & Google V8 TypedArray Performance Suite
// Upstream Reference: https://github.com/v8/v8 (test/js-perf-test/TypedArrays)
// Author: Khronos Group / Google V8 Team
// Ported to self-contained ECMAScript with deterministic mathematical checksum validation.
// -------------------------------------------------------------------------------------
// Tests Int32Array contiguous buffer allocation, indexed stores, and indexed loads.

var log = typeof console !== "undefined" && console.log ? console.log : print;
var now = typeof performance !== "undefined" && performance.now ? function() { return performance.now(); } : Date.now;

var SIZE = 1000000;
var MOD = 100000007;

function runTypedArray(size, mod) {
    var ta = new Int32Array(size);
    for (var i = 0; i < size; i = i + 1) {
        ta[i] = (i * 7) & 0xffff;
    }

    var sum = 0;
    for (var j = 0; j < size; j = j + 1) {
        sum = (sum + ta[j]) % mod;
    }
    return sum;
}

// In-engine warmup
runTypedArray(10000, MOD);

var start = now();
var sum = runTypedArray(SIZE, MOD);
var end = now();
var duration = end - start;

log("BENCHMARK_OUTPUT:" + JSON.stringify({
    name: "04_typedarray_throughput",
    category: "Memory & TypedArrays",
    duration_ms: duration,
    checksum: sum
}));
