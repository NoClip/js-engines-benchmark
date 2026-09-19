// Benchmark 08: Sieve of Eratosthenes
// -------------------------------------------------------------------------------------
// Source & Attribution: Eratosthenes of Cyrene / Computer Language Benchmarks Game
// Upstream Reference: https://benchmarksgame-team.pages.debian.net/benchmarksgame/
// Author: Classic Algorithm adapted for JS TypedArrays by Benchmark Contributors
// Ported to self-contained ECMAScript with deterministic mathematical checksum validation.
// -------------------------------------------------------------------------------------
// Tests array buffer indexing, branch prediction, and memory-intensive prime sieve computation.

var log = typeof console !== "undefined" && console.log ? console.log : print;
var now = typeof performance !== "undefined" && performance.now ? function() { return performance.now(); } : Date.now;

var LIMIT = 1000000;
var MOD = 100000007;

function runPrimeSieve(limit, mod) {
    var isPrime = new Uint8Array(limit + 1);
    for (var i = 2; i <= limit; i = i + 1) {
        isPrime[i] = 1;
    }

    for (var p = 2; p * p <= limit; p = p + 1) {
        if (isPrime[p] === 1) {
            for (var mult = p * p; mult <= limit; mult = mult + p) {
                isPrime[mult] = 0;
            }
        }
    }

    var count = 0;
    var primeSum = 0;
    for (var j = 2; j <= limit; j = j + 1) {
        if (isPrime[j] === 1) {
            count = count + 1;
            primeSum = (primeSum + j) % mod;
        }
    }
    return primeSum;
}

// In-engine warmup
runPrimeSieve(20000, MOD);

var start = now();
var primeSum = runPrimeSieve(LIMIT, MOD);
var end = now();
var duration = end - start;

log("BENCHMARK_OUTPUT:" + JSON.stringify({
    name: "08_prime_sieve",
    category: "Algorithms & Memory",
    duration_ms: duration,
    checksum: primeSum
}));
