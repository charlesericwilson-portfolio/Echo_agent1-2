# Echo - Local Red Team AI Agent tool

**A fast, local AI tool wrapper that executes shell commands safely via `COMMAND: your command` lines from a custom LLM.**

Current recommended version: **Rust** (much faster and cleaner than the original Python version).

### Quick Answers
- **What does it do?**  
  You chat with your local LLM. When it wants to run a command, it outputs `COMMAND: nmap -sV 192.168.1.1`. Echo detects it, runs the command safely, and feeds the output back to the model.

- **How do I try it?**  
  Go to the [Rust version](https://github.com/charlesericwilson-portfolio/Echo_agent/blob/main/Echo_project/echo_rust_wrapper/README.md) — build and run in under 2 minutes.

  Option 2 download the [python_wrapper](https://github.com/charlesericwilson-portfolio/Echo_agent1-2/blob/main/Echo_project/python_wrapper/Echo_custom.py) read the [README.md](https://github.com/charlesericwilson-portfolio/Echo_agent1-2/blob/main/Echo_project/python_wrapper/README.md) takes just a minute.

- **Does it work?**  
  Yes — the Rust COMMAND executor is newer stable and working daily. The older Python wrapper works and is stable as well but is no longer the main focus. Can be ran on remote device connected to the server over vpn and tools execute on the remote device.

### Repository Structure
- `python_wrapper/` — Original simple Python implementation
- `echo_rust_wrapper/` — **Recommended**: Fast Rust port (active development)
- `docs/` — Progress logs and journey notes

See the full journey and screenshots in [progress_python.md](https://github.com/charlesericwilson-portfolio/Echo_agent/blob/main/Echo_project/Docs/progress_python.md) and [progress_rust.md](https://github.com/charlesericwilson-portfolio/Echo_agent/blob/main/Echo_project/Docs/progress_rust.md).

---

Built locally with a custom 14B model. Safety deny list included.  
For chat, red teaming, and learning purposes only.

Builds in testing [Echo_tmux](https://github.com/charlesericwilson-portfolio/Echo_tmux/blob/main/README.md)
Builds in development [Echo Agent Proxy](https://github.com/charlesericwilson-portfolio/Echo_agent_proxy), [Echo rust agent proxyv5](https://github.com/charlesericwilson-portfolio/Echo_rust_agent_proxyv5/tree/main)

