// Benchmark 07: Cryptographic Hashing & Bitwise Permutation
// Tests bitwise manipulation, integer multiplication, and hashing avalanche effect.

var log = typeof console !== "undefined" && console.log ? console.log : print;
var now = typeof performance !== "undefined" && performance.now ? function() { return performance.now(); } : Date.now;

var ITERATIONS = 100000;
var MOD = 100000007;

function myHash(data, len) {
    var hashVal = 21661362;
    for (var i = 0; i < len; i = i + 1) {
        hashVal = ((hashVal ^ (data & 0xff)) % 50000000) * 17;
        hashVal = (hashVal + (hashVal >> 3)) % MOD;
        data = (data >> 2) ^ (hashVal & 0x7f);
    }
    return hashVal;
}

function runCryptoHash() {
    var checksum = 0;
    for (var i = 0; i < ITERATIONS; i = i + 1) {
        checksum = (checksum + myHash(i, 6)) % MOD;
    }
    return checksum;
}

var start = now();
var checksum = runCryptoHash();
var end = now();
var duration = Math.max(1, end - start);

log("BENCHMARK_OUTPUT:" + JSON.stringify({
    name: "07_crypto_hash",
    category: "Cryptography & Bitwise",
    duration_ms: duration,
    checksum: checksum
}));
