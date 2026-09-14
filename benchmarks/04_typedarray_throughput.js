// Benchmark 04: TypedArray Throughput
// Tests Int32Array contiguous buffer allocation, indexed stores, and indexed loads.

var log = typeof console !== "undefined" && console.log ? console.log : print;
var now = typeof performance !== "undefined" && performance.now ? function() { return performance.now(); } : Date.now;

var SIZE = 50000;
var MOD = 100000007;

var start = now();
var ta = new Int32Array(SIZE);
for (var i = 0; i < SIZE; i = i + 1) {
    ta[i] = (i * 7) & 0xffff;
}

var sum = 0;
for (var j = 0; j < SIZE; j = j + 1) {
    sum = (sum + ta[j]) % MOD;
}
var end = now();
var duration = Math.max(1, end - start);

log("BENCHMARK_OUTPUT:" + JSON.stringify({
    name: "04_typedarray_throughput",
    category: "Memory & TypedArrays",
    duration_ms: duration,
    checksum: sum
}));
