// Benchmark 03: Object Shape Transitions & Inline Cache
// Tests object allocation, Map (hidden class) transitions, and inline cache throughput.

var log = typeof console !== "undefined" && console.log ? console.log : print;
var now = typeof performance !== "undefined" && performance.now ? function() { return performance.now(); } : Date.now;

var ITERATIONS = 30000;
var MOD = 100000007;

function runObjectShapes() {
    var total = 0;
    for (var i = 0; i < ITERATIONS; i = i + 1) {
        var obj = { x: i, y: i * 2, sum: 0 };
        obj.sum = obj.x + obj.y;
        total = (total + obj.sum) % MOD;
    }
    return total;
}

var start = now();
var total = runObjectShapes();
var end = now();
var duration = Math.max(1, end - start);

log("BENCHMARK_OUTPUT:" + JSON.stringify({
    name: "03_object_shape_transitions",
    category: "Objects & Shapes",
    duration_ms: duration,
    checksum: total
}));
