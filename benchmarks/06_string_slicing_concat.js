// Benchmark 06: String Slicing & Concatenation
// Tests string allocation, slice/substring operations, flattening, and character accumulation.

var log = typeof console !== "undefined" && console.log ? console.log : print;
var now = typeof performance !== "undefined" && performance.now ? function() { return performance.now(); } : Date.now;

var ITERATIONS = 10000;
var MOD = 100000007;

function runStringConcat() {
    var alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    var acc = "";
    var checksum = 0;

    for (var i = 0; i < ITERATIONS; i = i + 1) {
        var startIdx = i % 20;
        var sub = alphabet.substring(startIdx, startIdx + 8);
        acc = acc + sub;
        if (acc.length > 200) {
            checksum = (checksum + acc.length) % MOD;
            acc = acc.substring(50);
        }
    }

    checksum = (checksum + acc.length) % MOD;
    return checksum;
}

var start = now();
var checksum = runStringConcat();
var end = now();
var duration = Math.max(1, end - start);

log("BENCHMARK_OUTPUT:" + JSON.stringify({
    name: "06_string_slicing_concat",
    category: "Strings & Slicing",
    duration_ms: duration,
    checksum: checksum
}));
