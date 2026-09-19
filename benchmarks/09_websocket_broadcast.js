// Benchmark 09: WebSocket Broadcast & Framing
// -------------------------------------------------------------------------------------
// Source & Attribution: Bun Benchmark Suite (https://github.com/oven-sh/bun/tree/main/bench)
// Upstream Reference: bench/websocket-server
// Author: Jarred Sumner (@Jarred-Sumner) and the Oven team (oven-sh)
// Ported to self-contained ECMAScript with deterministic mathematical checksum validation.
// -------------------------------------------------------------------------------------
// Tests RFC 6455 frame masking/unmasking (4-byte XOR over Uint8Array) and multi-client broadcast dispatch.

var log = typeof console !== "undefined" && console.log ? console.log : print;
var now = typeof performance !== "undefined" && performance.now ? function() { return performance.now(); } : Date.now;

var CLIENT_COUNT = 32;
var BROADCASTS = 1500;
var PAYLOAD_SIZE = 128;
var MOD = 100000007;

function unmaskWebSocketPayload(serverPayload, maskedFrame, maskKey) {
    for (var u = 0; u < PAYLOAD_SIZE; u = u + 1) {
        serverPayload[u] = maskedFrame[u] ^ maskKey[u & 3];
    }
}

function dispatchToClients(b, serverPayload, clientBuffers, currentChecksum, mod) {
    var csum = currentChecksum;
    for (var i = 0; i < CLIENT_COUNT; i = i + 1) {
        var buf = clientBuffers[i];
        for (var j = 0; j < PAYLOAD_SIZE; j = j + 8) {
            buf[j] = (serverPayload[j] + b + i) & 0xff;
            csum = (csum + buf[j]) % mod;
        }
    }
    return csum;
}

function runWebSocketBroadcast(broadcasts, mod) {
    var clientBuffers = [];
    for (var c = 0; c < CLIENT_COUNT; c = c + 1) {
        clientBuffers.push(new Uint8Array(PAYLOAD_SIZE));
    }

    var rawPayload = new Uint8Array(PAYLOAD_SIZE);
    for (var p = 0; p < PAYLOAD_SIZE; p = p + 1) {
        rawPayload[p] = (p * 13 + 7) & 0xff;
    }
    var maskKey = [0x7f, 0x3b, 0xa1, 0x5e];

    var maskedClientFrame = new Uint8Array(PAYLOAD_SIZE);
    for (var m = 0; m < PAYLOAD_SIZE; m = m + 1) {
        maskedClientFrame[m] = rawPayload[m] ^ maskKey[m & 3];
    }

    var serverPayload = new Uint8Array(PAYLOAD_SIZE);
    var checksum = 0;

    for (var b = 0; b < broadcasts; b = b + 1) {
        unmaskWebSocketPayload(serverPayload, maskedClientFrame, maskKey);
        checksum = dispatchToClients(b, serverPayload, clientBuffers, checksum, mod);
    }

    return checksum;
}

// In-engine warmup
runWebSocketBroadcast(50, MOD);

var start = now();
var checksum = runWebSocketBroadcast(BROADCASTS, MOD);
var end = now();
var duration = end - start;

log("BENCHMARK_OUTPUT:" + JSON.stringify({
    name: "09_websocket_broadcast",
    category: "WebSockets & I/O",
    duration_ms: duration,
    checksum: checksum
}));
