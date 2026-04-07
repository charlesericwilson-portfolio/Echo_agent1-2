 # Echo Rust - Simple COMMAND Executor (Recommended)

This is the **current recommended version** — a clean, fast Rust port of the original Echo COMMAND method.

### What it does
Detects lines like `COMMAND: nmap -sV 192.168.1.50` from your local LLM, runs them safely with a built-in deny list, saves the output, and feeds the result back to the model and logs chat to jsonl.

### Why Rust?
- Much faster than the Python version
- Lower memory and CPU usage
- Compiles to a single standalone binary
- Better performance with large context

### Quick Start

1. Make sure your llama.cpp server is running on port 8080.

2. Build and run the Rust version:

```bash
cd [build directory]
cargo build --release
./target/release/echo_rust_wrapper
```

Build direction is moving toward this https://github.com/charlesericwilson-portfolio/Echo_agent_proxy
