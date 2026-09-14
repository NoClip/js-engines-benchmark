// Benchmark 08: Sieve of Eratosthenes
// Tests array buffer indexing, branch prediction, and memory-intensive prime sieve computation.

var log = typeof console !== "undefined" && console.log ? console.log : print;
var now = typeof performance !== "undefined" && performance.now ? function() { return performance.now(); } : Date.now;

var LIMIT = 150000;

var start = now();
var isPrime = new Uint8Array(LIMIT + 1);
for (var i = 2; i <= LIMIT; i = i + 1) {
    isPrime[i] = 1;
}

for (var p = 2; p * p <= LIMIT; p = p + 1) {
    if (isPrime[p] === 1) {
        for (var mult = p * p; mult <= LIMIT; mult = mult + p) {
            isPrime[mult] = 0;
        }
    }
}

var count = 0;
var primeSum = 0;
var MOD = 100000007;
for (var j = 2; j <= LIMIT; j = j + 1) {
    if (isPrime[j] === 1) {
        count = count + 1;
        primeSum = (primeSum + j) % MOD;
    }
}
var end = now();
var duration = Math.max(1, end - start);

log("BENCHMARK_OUTPUT:" + JSON.stringify({
    name: "08_prime_sieve",
    category: "Algorithms & Memory",
    duration_ms: duration,
    checksum: primeSum
}));
