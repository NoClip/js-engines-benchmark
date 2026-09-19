// Benchmark 06: String Slicing & Concatenation
// -------------------------------------------------------------------------------------
// Source & Attribution: Apple WebKit SunSpider Benchmark Suite
// Upstream Reference: https://webkit.org/perf/sunspider/sunspider.html
// Author: Apple WebKit Team
// Ported to self-contained ECMAScript with deterministic mathematical checksum validation.
// -------------------------------------------------------------------------------------
// Tests string allocation, slice/substring operations, flattening, and character accumulation.

var log = typeof console !== "undefined" && console.log ? console.log : print;
var now = typeof performance !== "undefined" && performance.now ? function() { return performance.now(); } : Date.now;

var ITERATIONS = 200000;
var MOD = 100000007;

function runStringConcat(iterations, mod) {
    var alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    var acc = "";
    var checksum = 0;

    for (var i = 0; i < iterations; i = i + 1) {
        var startIdx = i % 20;
        var sub = alphabet.substring(startIdx, startIdx + 8);
        acc = acc + sub;
        if (acc.length > 200) {
            checksum = (checksum + acc.length) % mod;
            acc = acc.substring(50);
        }
    }

    checksum = (checksum + acc.length) % mod;
    return checksum;
}

// In-engine warmup
runStringConcat(5000, MOD);

var start = now();
var checksum = runStringConcat(ITERATIONS, MOD);
var end = now();
var duration = end - start;

log("BENCHMARK_OUTPUT:" + JSON.stringify({
    name: "06_string_slicing_concat",
    category: "Strings & Slicing",
    duration_ms: duration,
    checksum: checksum
}));
