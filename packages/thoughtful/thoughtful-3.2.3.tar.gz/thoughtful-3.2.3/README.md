**thoughtful** is a collection of open-source libraries and tools for Robot Process
Automation (RPA) development. The goal of this project is to provide a set of
for supervising bot execution, and enabling these bots to do more.

[![PyPi version](https://badgen.net/pypi/v/thoughtful/)](https://pypi.org/project/thoughtful/)
[![Supported Versions](https://img.shields.io/pypi/pyversions/thoughtful.svg)](https://pypi.org/project/thoughtful)
[![Downloads](https://pepy.tech/badge/thoughtful/month)](https://pepy.tech/project/thoughtful)

[//]: # "[![GitHub release](https://img.shields.io/github/release/Thoughtful-Automation/supervisor.svg)](https://GitHub.com/Naereen/StrapDown.js/releases/)"

This project is:

- Open-source: [GitHub][url:gh]
- Owned by [thoughtful][url:ta]
- Licensed under the [Apache License 2.0][url:al]

Links:

- [Homepage][url:gh]
- [Documentation][url:docs]
- [PyPI][url:pypi]

**thoughtful** is available on [PyPI][url:pypi] and can be installed using pip:

```sh
pip install thoughtful
```

---

**thoughtful** officially supports Python 3.10+.

---

# Libraries

## Supervisor

Supervisor is a Workflow Engine for Digital Workers that constructs
and broadcasts a detailed and structured telemetric log, called the Run Report.

### Detailed documentation

Detailed documentation on how to utilize Supervisor can be found [here][url:supervisor_docs].

### Usage

```python
from thoughtful.supervisor import step, step_scope, supervise, set_step_status


# using the step decorator
@step("2")
def step_2(name: str) -> bool:
    print(f'Hello {name}')
    return True  # some condition

def main() -> None:
    # using the step_scope context manager
    with step_scope('1') as step_context:
        try:
            print("Getting credentials")
            # ...
        except Exception as e:
            # set step status using method
            step_context.set_status("warning")

    if not step_2():
        # set step status using function
        set_step_status("2", "fail")

if __name__ == '__main__':
    with supervise():
        main()
```

## Telemetry & Observability

The Supervisor automatically provides comprehensive observability for your bot workflows with **zero code changes** required. Simply use the `supervise()` context manager and your workflows are automatically instrumented with distributed tracing, metrics, and structured logging.

### 🚀 Seamless Integration

**No code changes needed** - telemetry is automatically enabled when you use the supervisor:

```python
from thoughtful.supervisor import supervise
from t_vault import bw_login_from_env

# Login to Bitwarden first
bw_login_from_env()

# That's it! Telemetry starts automatically
with supervise(manifest="manifest.yaml"):
    main()
```

### 🔧 Automatic Configuration

The supervisor automatically configures telemetry using your existing Bitwarden
`otl-info` item which we configure to retain our up to date Endpoint/Auth info:

- **Endpoint**: Retrieved from `bw_get_item("otl-info")["username"]`
- **Authentication**: Retrieved from `bw_get_item("otl-info")["password"]`
- **Zero configuration**: Works out-of-the-box with your existing vault setup

### 🔌 Endpoint Usage & Exporter Selection

The telemetry system uses intelligent endpoint resolution and exporter selection:

#### **Bitwarden Endpoints (Automatic)**
When using Bitwarden configuration, the system automatically:
- **Uses gRPC exporter** for all telemetry types
- **Assumes port 4317** (standard gRPC port)
- **No path segments needed** (gRPC handles this internally)

#### **Custom Endpoints (Port-Based Detection)**
When providing custom endpoints, the system determines the exporter based on the port:

| Port | Protocol | Exporter | Path Handling |
|------|----------|----------|---------------|
| `4317` | gRPC | `GRPCOTLP*Exporter` | No path segments |
| `4318` | HTTP | `HTTPOTLP*Exporter` | Adds `/v1/{telemetry_type}` |
| No port | HTTP | `HTTPOTLP*Exporter` | Adds `/v1/{telemetry_type}` |

#### **Example Endpoint Resolution**
```python
# Bitwarden endpoint (always gRPC)
"otel-collector.obs.thoughtful.ai:4317" → GRPCOTLPMetricExporter

# Custom gRPC endpoint
"https://custom.example.com:4317" → GRPCOTLPMetricExporter

# Custom HTTP endpoint
"https://custom.example.com:4318" → HTTPOTLPMetricExporter + /v1/metrics

# Custom HTTP endpoint (no port)
"https://custom.example.com" → HTTPOTLPMetricExporter + /v1/metrics
```

### 📊 What You Get Automatically

- **📈 Distributed Tracing**: Complete workflow execution traces with step-by-step timing
  - All timing and performance data is available in traces for dashboard creation
- **📝 Structured Logs**: Contextual logging with automatic trace correlation
- **🌐 HTTP Monitoring**: Automatic tracing of external API calls and responses

### 📋 Manifest Standards for Telemetry

To ensure optimal telemetry performance, follow these standards when creating your `manifest.yaml`:

#### **Fields with Length Limits**
- **`uid`**: Maximum 5 characters (e.g., `"PAR3"`, `"AOC2"`)
  - Used as root span name and `service.name` resource attribute
  - Automatically truncated with warning if exceeded
  - Must be unique across your agent

- **`step_id`**: Maximum 8 characters (e.g., `"1.1"`, `"auth"`)
  - Used in span names (`step.{step_id}`)
  - Step duration and execution information is available in trace spans
  - You can add larger description to describe it using `description` field, but
    shorten the `step_id` field to 8 characters max
  - Critical for telemetry compliance

> **Note**: Length limits ensure span names remain within reasonable bounds and maintain consistency across the observability platform. The `uid` limit applies to span names and resource attributes, while `step_id` limits apply to span names.

#### **Environment Detection**
The supervisor automatically detects the deployment environment and includes it in all telemetry data:

- **Production**: Set `THOUGHTFUL_PRODUCTION` environment variable to any value
  - Results in `deployment.environment = "supervisor.prod"`
- **Development**: Leave `THOUGHTFUL_PRODUCTION` unset or empty
  - Results in `deployment.environment = "supervisor.dev"`

This allows you to filter and analyze telemetry data by environment in your observability platform.

### 🎯 Benefits

- **🔍 Debug Faster**: See exactly where workflows fail and how long each step takes
- **📈 Monitor Performance**: Extract execution times and duration statistics from traces
- **🚨 Proactive Alerts**: Get notified of issues before they impact users
- **📊 Business Insights**: Understand workflow patterns and optimization opportunities through trace analysis

### 🔧 Optional: Custom Configuration

For advanced use cases, you can provide custom telemetry configuration:

```python
with supervise(
    manifest="manifest.yaml",
    otlp_config={
        "tracing_endpoint": "http://localhost:4317",  # gRPC (port 4317)
        "metrics_endpoint": "http://localhost:4318",  # HTTP (port 4318)
        "auth_headers": {"Authorization": "Bearer your-token"}
    }
):
    main()
```

#### **Fine-Tune Telemetry Processors**

You can customize batch processing behavior directly in your `manifest.yaml` to optimize for throughput, latency, or resource constraints:

```yaml
uid: MYAPP
name: My Application
# ... other fields ...

telemetry:
  # Configure logging batch processor
  log_processor:
    max_queue_size: 4096              # Queue size (default: 2048)
    schedule_delay_millis: 10000      # Export delay in ms (default: 5000)
    export_timeout_millis: 60000      # Export timeout in ms (default: 30000)
    max_export_batch_size: 1024       # Batch size (default: 512)

  # Metrics are disabled - using traces for dashboards instead
  # metric_reader:
  #   export_interval_millis: 15000     # Export interval in ms (default: 10000)
  #   export_timeout_millis: 7500       # Export timeout in ms (default: 5000)

  # Configure tracing batch processor
  span_processor:
    max_queue_size: 8192              # Queue size (default: 2048)
    schedule_delay_millis: 2500       # Export delay in ms (default: 5000)
    export_timeout_millis: 45000      # Export timeout in ms (default: 30000)
    max_export_batch_size: 2048       # Batch size (default: 512)
```

**Use Cases:**
- **High-throughput**: Increase queue and batch sizes for heavy workloads
- **Low-latency**: Decrease delays for faster telemetry export
- **Resource-constrained**: Reduce queue sizes to save memory

All fields are optional - specify only what you need to customize.

### Telemetry & Observability

Supervisor includes robust telemetry capabilities with **fail-safe async batch exporters** that ensure your applications never hang due to telemetry issues:

#### **🛡️ Fail-Safe Behavior**
- **Non-blocking**: Telemetry runs in background threads, never blocks main execution
- **Automatic fallback**: Falls back to console output when OTLP collector is unavailable
- **Self-healing**: Automatically recovers when connectivity is restored
- **Queue management**: Preserves recent data during outages (up to 2048 items)
- **Smart data handling**: When queue fills up, removes oldest data to preserve newest telemetry

#### **🔄 Failure & Recovery Timeline**
```
T+0s:   OTLP collector goes down
T+5s:   First retry attempt fails (background)
T+10s:  Second retry attempt fails
...     Continues retrying every 5 seconds
T+60s:  Collector comes back online
T+65s:  Next retry succeeds automatically
T+70s:  Queued data starts exporting
T+75s:  Normal operation resumed
```

#### **📊 What This Means**
- **No agent hangs** - main thread never waits for telemetry
- **Graceful degradation** - console output when collector is down
- **Automatic recovery** - no restart needed when collector returns
- **Data preservation** - recent telemetry data protected during outages


### 📚 Observability Platform

Your telemetry data is automatically sent to Thoughtful's observability platform, where you can:

- **View workflow traces** in real-time
- **Monitor performance metrics** with custom dashboards
- **Set up alerts** for failures or performance degradation
- **Analyze trends** across your bot fleet

### 🔗 Learn More

- [Thoughtful Observability Platform](https://hyperdx.obs.thoughtful.ai/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- Join #Observability for any questions!

### 📝 Abbreviations & Naming Conventions

The supervisor uses specific abbreviations and shortening logic for telemetry metrics and identifiers to ensure consistency and readability:

#### **Telemetry Data Sources**
- **Traces**: All performance and timing data is available in distributed traces
  - Step durations are recorded in span attributes
  - Execution information can be extracted from traces for dashboard creation
  - No separate metrics are collected - traces provide all observability data

#### **Endpoint Abbreviations**
External service endpoints are automatically shortened using predefined abbreviations:

| Service | Full Name | Abbreviation | Example |
|---------|-----------|-------------|---------|
| JSONPlaceholder | `placeholder` | `ph` | `jsonplaceholder.typicode.com` → `jsonph.typicode.com` |
| Typicode | `typicode` | `tc` | `api.typicode.com` → `api.tc.com` |
| GitHub | `github` | `gh` | `api.github.com` → `api.gh.com` |
| HTTPBin | `httpbin` | `hb` | `httpbin.org` → `hb.org` |
| Google APIs | `googleapis` | `gapi` | `www.googleapis.com` → `www.gapi.com` |
| Amazon AWS | `amazonaws` | `aws` | `api.amazonaws.com` → `api.aws.com` |
| Microsoft | `microsoft` | `ms` | `graph.microsoft.com` → `graph.ms.com` |
| Cloudflare | `cloudflare` | `cf` | `api.cloudflare.com` → `api.cf.com` |
| OpenAI | `openai` | `oai` | `api.openai.com` → `api.oai.com` |
| Anthropic | `anthropic` | `ant` | `api.anthropic.com` → `api.ant.com` |
| Claude | `claude` | `cl` | `claude.ai` → `cl.ai` |
| GPT | `gpt` | `gpt` | `gpt.openai.com` → `gpt.oai.com` |
| Gemini | `gemini` | `gem` | `gemini.google.com` → `gem.google.com` |

## Screen Recorder

The ScreenRecorder library facilitates the recording of screen activity from a
programmatic browser session and generates a video file of the recorded session.

### Detailed documentation

Detailed documentation on how to utilize Screen Recorder can be found [here][url:screen_recorder_docs].

### Prerequisites

Ensure you have already downloaded `FFmpeg` as it is utilized to create the video recording.

https://www.ffmpeg.org/download.html

### Installation

Install the optional `screen-recorder` extras

#### Poetry

```shell
poetry install -E screen-recorder
```

#### Pip

```shell
pip install thoughtful[screen-recorder]
```

### Usage

**WARNING: It is essential that you call `end_recording` at the end of a recording.**

**If you do not call `end_recording`, the recording threads will continue to run until your program ends and a
video will not be created.**

```python
from thoughtful.screen_recorder import ScreenRecorder, BrowserManager
from RPA.Browser.Selenium import Selenium # This dependency must be installed separately

class YoutubeScraper(ScreenRecorder):
    def __init__(self) -> None:
        self._selenium_instance = Selenium()
        super().__init__(browser_manager=BrowserManager(instance=self._selenium_instance))

youtube_scraper = YoutubeScraper()
try:
    # ... Perform actions here ...
finally:
    if youtube_scraper:
        # We recommend calling `end_recording` in a `finally` block to ensure that
        # video processing occurs and all recording threads are terminated even if the Process fails
        youtube_scraper.end_recording()
```

## Contributing

Contributions to **thoughtful** are welcome!

To get started, see the [contributing guide](CONTRIBUTING.md).

---

Made with ❤️ by

[![Thoughtful](https://user-images.githubusercontent.com/1096881/141985289-317c2e72-3c2d-4e6b-800a-0def1a05f599.png)][url:ta]

---

This project is open-source and licensed under the terms of the [Apache License 2.0][url:al].

<!--  Link References -->

[url:ta]: https://www.thoughtful.ai/
[url:gh]: https://github.com/Thoughtful-Automation/supervisor
[url:pypi]: https://pypi.org/project/thoughtful/
[git:issues]: https://github.com/Thoughtful-Automation/supervisor/issues
[url:docs]: https://www.notion.so/thoughtfulautomation/Thoughtful-Library-c0333f67989d4044aa0a595eaf8fd07b
[url:al]: http://www.apache.org/licenses/LICENSE-2.0
[url:supervisor_docs]: https://www.notion.so/thoughtfulautomation/How-to-develop-with-Supervisor-4247b8d2a5a747b6bff1d232ad395e9c
[url:screen_recorder_docs]: https://www.notion.so/thoughtfulautomation/ScreenRecorder-67380d38b18345f9bac039ff0ef38b0a
