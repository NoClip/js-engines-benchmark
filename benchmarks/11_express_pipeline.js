// Benchmark 11: Express HTTP Request & Middleware Pipeline
// -------------------------------------------------------------------------------------
// Adapted from the Bun Benchmark Suite (https://github.com/oven-sh/bun/tree/main/bench)
// Originally designed & created by Jarred Sumner and the Oven team (oven-sh/bun).
// Ported to self-contained ECMAScript with deterministic mathematical checksum validation.
// -------------------------------------------------------------------------------------
// Tests HTTP header parsing, query extraction, middleware closure chaining, route dispatch, and response formatting.

var log = typeof console !== "undefined" && console.log ? console.log : print;
var now = typeof performance !== "undefined" && performance.now ? function() { return performance.now(); } : Date.now;

var REQUESTS = 2500;
var MOD = 100000007;

var RAW_HTTP_REQUEST = "GET /api/v1/users/42?format=json&cached=true HTTP/1.1\r\n" +
    "Host: localhost:3000\r\n" +
    "User-Agent: Bombardier/1.2.5\r\n" +
    "Accept: application/json\r\n" +
    "Authorization: Bearer secret_token_xyz\r\n\r\n";

function parseHttpRequest(raw) {
    var lines = raw.split("\r\n");
    var reqLine = lines[0].split(" ");
    var method = reqLine[0];
    var fullUrl = reqLine[1];

    var pathAndQuery = fullUrl.split("?");
    var pathname = pathAndQuery[0];
    var queryString = pathAndQuery.length > 1 ? pathAndQuery[1] : "";

    var headers = {};
    for (var i = 1; i < lines.length; i = i + 1) {
        var line = lines[i];
        if (line.length === 0) {
            break;
        }
        var colonIdx = line.indexOf(":");
        if (colonIdx > 0) {
            var key = line.substring(0, colonIdx).toLowerCase();
            var val = line.substring(colonIdx + 2);
            headers[key] = val;
        }
    }

    return {
        method: method,
        url: pathname,
        query: queryString,
        headers: headers,
        params: {}
    };
}

function processPipeline(req, reqIndex) {
    var res = {
        statusCode: 200,
        headers: { "content-type": "application/json" },
        body: ""
    };

    // Middleware 1: CORS
    res.headers["access-control-allow-origin"] = "*";

    // Middleware 2: Auth Check
    if (!req.headers["authorization"]) {
        res.statusCode = 401;
        res.body = '{"error":"Unauthorized"}';
        return res;
    }

    // Middleware 3: Route Matcher (/api/v1/users/:id)
    var parts = req.url.split("/");
    if (parts.length >= 5 && parts[1] === "api" && parts[2] === "v1" && parts[3] === "users") {
        req.params.id = parts[4];
        // Route Controller: Hello World User JSON
        res.statusCode = 200;
        res.body = '{"id":' + req.params.id + ',"req":' + reqIndex + ',"status":"ok"}';
    } else {
        res.statusCode = 404;
        res.body = '{"error":"Not Found"}';
    }

    return res;
}

function formatHttpResponse(res) {
    return "HTTP/1.1 " + res.statusCode + " OK\r\nContent-Length: " + res.body.length + "\r\n\r\n" + res.body;
}

function runExpressBenchmark(requests, mod) {
    var checksum = 0;

    for (var i = 0; i < requests; i = i + 1) {
        var req = parseHttpRequest(RAW_HTTP_REQUEST);
        var res = processPipeline(req, i);
        var httpText = formatHttpResponse(res);

        // Fold status code and response text length into checksum
        var hash = (res.statusCode * 31 + httpText.length + (i & 0xff)) | 0;
        checksum = (checksum + hash) % mod;
    }

    return checksum;
}

var start = now();
var checksum = runExpressBenchmark(REQUESTS, MOD);
var end = now();
var duration = Math.max(1, end - start);

log("BENCHMARK_OUTPUT:" + JSON.stringify({
    name: "11_express_pipeline",
    category: "HTTP & Routing",
    duration_ms: duration,
    checksum: checksum
}));
