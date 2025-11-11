# Vention Communication

A thin, FastAPI-powered RPC layer for machine-apps that exposes Connect-compatible request-response and server-streaming endpoints — plus .proto generation from Python decorators, allowing typed SDKs to be generated separately via Buf.

## Table of Contents

- [✨ Features](#-features)
- [🧠 Concepts & Overview](#-concepts--overview)
- [⚙️ Installation & Setup](#️-installation--setup)
- [🚀 Quickstart Tutorial](#-quickstart-tutorial)
- [🛠 How-to Guides](#-how-to-guides)
- [📖 API Reference](#-api-reference)
- [🔍 Troubleshooting & FAQ](#-troubleshooting--faq)

## ✨ Features

- **Zero boilerplate RPCs**: Expose any async Python function as a network API with a single decorator.
- **Strong typing**: Request and response models derived directly from Python annotations.
- **Built-in schema emission**: Generates a .proto file at runtime, ready for SDK code generation.
- **Single service surface**: All methods exposed under `/rpc/<package.Service>/<Method>`.
- **Connect-compatible transport**: Works seamlessly with `@connectrpc/connect-web` and `connectrpc-python`.

## 🧠 Concepts & Overview

### The Problem

Machine-app developers write Python daily but shouldn’t need to know REST, gRPC, or frontend networking.
They just need a way to say “this function should be callable from anywhere.”

### The Solution

vention-communication bridges that gap by turning annotated Python functions into typed RPC endpoints automatically.

`@action()` → defines a one-request / one-response method.

`@stream()` → defines a live telemetry or event stream that other services can subscribe to.

`VentionApp.finalize()` → scans for decorators, builds a Connect router, and emits a .proto schema.

Once the .proto exists, SDKs for TypeScript, Python, or Go can be generated using Buf.
The result: your frontend gets auto-completed methods for every RPC, no HTTP or JSON code required.

### Core Concepts

- **Actions (Request-Response)** — send a request, get a response back. Input and output types are inferred from function annotations. If either is missing, `google.protobuf.Empty` is used.
- **Streams (Server streaming)** — continuous updates broadcast to all subscribers. Each stream can optionally replay the last value when someone subscribes. Queues default to size-1 to always show the latest value.
- **Service Surface** — all actions and streams belong to one service, e.g. `vention.app.v1.<YourAppName>Service`, with routes mounted under `/rpc`.
- **Proto Generation** — `VentionApp.finalize()` writes a .proto to disk, capturing all decorated RPCs, inferred models, and scalar wrappers. SDK generation (via Buf) is handled externally.


## ⚙️ Installation & Setup

**Requirements:**

- Python 3.10+
- FastAPI
- Uvicorn (for serving)

**Install:**

```bash
pip install vention-communication
```

**Optional client libraries:**

- TypeScript: `@connectrpc/connect-web`
- Python: `connectrpc` with `httpx.AsyncClient`

## 🚀 Quickstart Tutorial
A complete "hello world" in three steps.

### 1. Define your RPCs

```python
from pydantic import BaseModel
from vention_communication import VentionApp, action, stream
import time, random

class PingRequest(BaseModel):
    message: str

class PingResponse(BaseModel):
    message: str

class Heartbeat(BaseModel):
    value: str
    timestamp: int

app = VentionApp(name="DemoApp", emit_proto=True)

@action()
async def ping(req: PingRequest) -> PingResponse:
    return PingResponse(message=f"Pong: {req.message}")

@stream(name="heartbeat", payload=Heartbeat, replay=True)
async def heartbeat():
    """Broadcast a live heartbeat value to all subscribers."""
    return Heartbeat(value=f"{random.uniform(0,100):.2f}", timestamp=int(time.time()))

app.finalize()

```

**Run:**

```bash
uvicorn demo.main:app --reload
```

Endpoints are automatically registered under `/rpc/vention.app.v1.DemoAppService.`

### 2. Generated .proto

After startup, `proto/app.proto` is emitted automatically.

You can now use Buf or protoc to generate client SDKs:

```bash
buf generate --template buf.gen.ts.yaml
buf generate --template buf.gen.python.yaml
```

SDK generation is external to vention-communication — allowing you to control versions and plugins.

### 3. Example TypeScript Client

```typescript
import { createClient } from "@connectrpc/connect";
import { createConnectTransport } from "@connectrpc/connect-web";
import { DemoAppService } from "./gen/connect/proto/app_connect";

const transport = createConnectTransport({
  baseUrl: "http://localhost:8000/rpc",
  useBinaryFormat: false,
});

const client = createClient(DemoAppService, transport);

const res = await client.ping({ message: "Hello" });
console.log(res.message);

for await (const hb of client.heartbeat({})) {
  console.log("Heartbeat", hb.value, hb.timestamp);
}
```

## 🛠 How-to Guides

### Add a new request-response endpoint

```python
@action()
async def get_status() -> dict:
    return {"ok": True}
```

### Add a new stream

```python
@stream(name="Status", payload=dict)
async def publish_status() -> dict:
    return {"ok": True}
```

### Emit proto to a custom path

```python
app = VentionApp(name="MyService", emit_proto=True, proto_path="out/myservice.proto")
app.finalize()
```

## 📖 API Reference

### VentionApp

```python
VentionApp(
  name: str = "VentionApp",
  *,
  emit_proto: bool = False,
  proto_path: str = "proto/app.proto",
  **fastapi_kwargs
)
```

**Methods:**

- `.register_rpc_plugin(bundle: RpcBundle)` — merges external action/stream definitions (e.g., from state-machine or storage).
- `.finalize()` — registers routes, emits .proto, and makes publishers available.

**Attributes:**

- `connect_router`: internal FastAPI router for Connect RPCs.
- `proto_path`: location of the emitted .proto.

### Decorators

```python
@action(name: Optional[str] = None)
# → Registers a request-response handler

@stream(
    name: str,
    payload: type,
    replay: bool = True,
    queue_maxsize: int = 1,
    policy: Literal["latest", "fifo"] = "latest"
)
# → Registers a server-streaming RPC and publisher
```

**Stream Parameters:**

- `name`: Unique name for the stream
- `payload`: Type of data to stream (Pydantic model or JSON-serializable type)
- `replay`: Whether new subscribers receive the last value (default: `True`)
- `queue_maxsize`: Maximum items per subscriber queue (default: `1`)
- `policy`: Delivery policy when queue is full - `"latest"` drops old items, `"fifo"` waits for space (default: `"latest"`)

### Stream Configuration Options

When creating a stream with `@stream()`, you can configure how updates are delivered to subscribers:

#### `replay` (default: `True`)

Controls whether new subscribers receive the last published value immediately when they subscribe.

- **`replay=True`**: New subscribers instantly receive the most recent value (if one exists). Useful for state streams where clients need the current state immediately upon connection.
- **`replay=False`**: New subscribers only receive values published after they subscribe. Useful for event streams where you only want to see new events.


#### `queue_maxsize` (default: `1`)

The maximum number of items that can be queued for each subscriber before the delivery policy kicks in.

- **`queue_maxsize=1`**: Only the latest value is kept. Perfect for state streams where you only care about the current state.
- **`queue_maxsize=N`** (N > 1): Allows buffering up to N items. Useful when subscribers might process items slower than they're published, but you still want to limit memory usage.

```python
# Only keep latest temperature reading
@stream(name="Temperature", payload=Temperature, queue_maxsize=1)

# Buffer up to 10 sensor readings
@stream(name="SensorData", payload=SensorReading, queue_maxsize=10)
```

#### `policy` (default: `"latest"`)

Defines what happens when a subscriber’s queue is full and a new value is published.

Each subscriber maintains its own in-memory queue of pending messages.
When you publish faster than a client can consume, the queue eventually fills — the policy determines what happens next.

`policy="latest"` — “drop oldest, never block”

- The publisher never waits.
- If a subscriber’s queue is full, the oldest item is dropped and the new one is inserted immediately.
- Fast subscribers receive every message; slow subscribers skip intermediate values but always see the most recent state.

✅ Pros
- Zero backpressure — publisher performance unaffected by slow clients.
- Keeps UI dashboards and telemetry feeds current (“latest value always wins”).
- Ideal for high-frequency data (positions, sensor readings, machine state).

⚠️ Cons
- Drops messages for slow clients (they may miss intermediate updates).
- Subscribers can diverge — one may receive more updates than another.

Example:
```python
@stream(name="Temperature", payload=TempReading,
        policy="latest", queue_maxsize=1)
# → publisher never blocks; subscribers always see the most recent temperature
```
`policy="fifo"` — “deliver all, may block”

- The publisher awaits until there’s space in every subscriber’s queue.
- Guarantees that all messages are delivered in order to every subscriber.
- A slow subscriber can stall the entire stream, because the distributor
waits for that subscriber’s queue to make room before continuing.

✅ Pros
- Preserves every event and strict ordering.
- Reliable for command sequences, audit logs, and event-driven logic.

⚠️ Cons
- One slow or paused subscriber can block all others.
- Publishing rate is limited by the slowest client.
- In extreme cases, a throttled browser or dropped connection can cause the
distributor to stall until the queue frees or the subscriber is removed.

Example:
```python
@stream(name="Events", payload=MachineEvent,
        policy="fifo", queue_maxsize=100)
# → guarantees ordered delivery but can back-pressure the publisher
```

**Common Combinations:**

- **State monitoring** (default): `replay=True`, `queue_maxsize=1`, `policy="latest"` — subscribers get current state immediately and always see the latest value.
- **Event streaming**: `replay=False`, `queue_maxsize=100`, `policy="fifo"` — subscribers only see new events and process them in order.


## 🔍 Troubleshooting & FAQ

**Q: Can I disable proto generation at runtime?**

Yes — set `emit_proto=False` in `VentionApp(...)`.

**Q: Publishing raises `KeyError: Unknown stream`.**

Ensure `app.finalize()` has been called before publishing or subscribing.

**Q: How do I integrate this with other libraries (state machine, storage, etc.)?**

Use `app.register_rpc_plugin()` to merge additional RPC definitions before calling `.finalize()`.
