// Benchmark 10: PostgreSQL Binary Row Tuple Decoder
// -------------------------------------------------------------------------------------
// Source & Attribution: Bun Benchmark Suite (https://github.com/oven-sh/bun/tree/main/bench)
// Upstream Reference: bench/postgres
// Author: Jarred Sumner (@Jarred-Sumner) and the Oven team (oven-sh)
// Ported to self-contained ECMAScript with deterministic mathematical checksum validation.
// -------------------------------------------------------------------------------------
// Tests binary wire protocol parsing: DataView big-endian integer decoding, column tuple extraction, and record projection.

var log = typeof console !== "undefined" && console.log ? console.log : print;
var now = typeof performance !== "undefined" && performance.now ? function() { return performance.now(); } : Date.now;

var ROWS_PER_QUERY = 100;
var QUERIES = 2000;
var BYTES_PER_ROW = 37;
var MOD = 100000007;

function writeRow(view, u8, offset, r) {
    u8[offset] = 68; // 'D'
    view.setInt32(offset + 1, 23);
    view.setInt16(offset + 5, 4);
    view.setInt32(offset + 7, 4);
    view.setInt32(offset + 11, r + 1);
    view.setInt32(offset + 15, 4);
    view.setInt32(offset + 19, (r * 17) & 0xffff);
    view.setInt32(offset + 23, 4);
    view.setInt32(offset + 27, (r * 1337) % 50000);
    view.setInt32(offset + 31, 2);
    view.setInt16(offset + 35, r & 7);
    return offset + 37;
}

function buildPostgresWireBuffer(rowCount) {
    var totalBytes = rowCount * BYTES_PER_ROW;
    var u8 = new Uint8Array(totalBytes);
    var view = new DataView(u8.buffer);
    var offset = 0;

    for (var r = 0; r < rowCount; r = r + 1) {
        offset = writeRow(view, u8, offset, r);
    }

    return view;
}

function decodePostgresRowHash(view, offset) {
    var id = view.getInt32(offset + 11);
    var userId = view.getInt32(offset + 19);
    var amount = view.getInt32(offset + 27);
    var status = view.getInt16(offset + 35);
    return ((id * 31 + userId) ^ (amount + status)) | 0;
}

function parsePostgresQuery(view, rowCount, currentChecksum, mod) {
    var offset = 0;
    var csum = currentChecksum;

    for (var r = 0; r < rowCount; r = r + 1) {
        var rowHash = decodePostgresRowHash(view, offset);
        csum = (csum + rowHash) % mod;
        offset = offset + 37;
    }

    return csum;
}

function runPostgresBenchmark(queries, rowCount, mod) {
    var view = buildPostgresWireBuffer(rowCount);
    var checksum = 0;

    for (var q = 0; q < queries; q = q + 1) {
        checksum = parsePostgresQuery(view, rowCount, checksum, mod);
    }

    return checksum;
}

// In-engine warmup
runPostgresBenchmark(20, ROWS_PER_QUERY, MOD);

var start = now();
var checksum = runPostgresBenchmark(QUERIES, ROWS_PER_QUERY, MOD);
var end = now();
var duration = end - start;

log("BENCHMARK_OUTPUT:" + JSON.stringify({
    name: "10_postgres_row_decode",
    category: "Database & Protocol",
    duration_ms: duration,
    checksum: checksum
}));
