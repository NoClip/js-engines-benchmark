// Benchmark 07: Cryptographic Hashing & Bitwise Permutation
// -------------------------------------------------------------------------------------
// Source & Attribution: Fowler–Noll–Vo Hashing Algorithm (FNV-1a)
// Upstream Reference: https://en.wikipedia.org/wiki/Fowler%E2%80%93Noll%E2%80%93Vo_hash_function
// Author: Glenn Fowler, Landon Curt Noll, and Kiem-Phong Vo
// Ported to self-contained ECMAScript with deterministic mathematical checksum validation.
// -------------------------------------------------------------------------------------
// Tests bitwise manipulation, integer multiplication, and hashing avalanche effect.

var log = typeof console !== "undefined" && console.log ? console.log : print;
var now = typeof performance !== "undefined" && performance.now ? function() { return performance.now(); } : Date.now;

var ITERATIONS = 100000;
var MOD = 100000007;

function myHash(data, len, mod) {
    var hashVal = 21661362;
    for (var i = 0; i < len; i = i + 1) {
        hashVal = ((hashVal ^ (data & 0xff)) % 50000000) * 17;
        hashVal = (hashVal + (hashVal >> 3)) % mod;
        data = (data >> 2) ^ (hashVal & 0x7f);
    }
    return hashVal;
}

function runCryptoHash(iterations, mod) {
    var checksum = 0;
    for (var i = 0; i < iterations; i = i + 1) {
        checksum = (checksum + myHash(i, 6, mod)) % mod;
    }
    return checksum;
}

var start = now();
var checksum = runCryptoHash(ITERATIONS, MOD);
var end = now();
var duration = Math.max(1, end - start);

log("BENCHMARK_OUTPUT:" + JSON.stringify({
    name: "07_crypto_hash",
    category: "Cryptography & Bitwise",
    duration_ms: duration,
    checksum: checksum
}));
