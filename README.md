# Echo - Local Red Team AI Agent

**A fast, local AI sidekick that executes shell commands safely via `COMMAND: your command` lines from a custom LLM.**

Current recommended version: **Rust** (much faster and cleaner than the original Python version).

### Quick Answers
- **What does it do?**  
  You chat with your local LLM. When it wants to run a command, it outputs `COMMAND: nmap -sV 192.168.1.1`. Echo detects it, runs the command safely, and feeds the output back to the model.

- **How do I try it?**  
  Go to the [Rust version](https://github.com/charlesericwilson-portfolio/Echo_agent/blob/main/Echo_project/echo_rust_wrapper/README.md) — build and run in under 2 minutes.

- **Does it work?**  
  Yes — the Rust COMMAND executor is stable and working daily. The older complex Python proxy was experimental and is no longer the main focus.

### Repository Structure
- `python_wrapper/` — Original simple Python implementation
- `echo_rust_wrapper/` — **Recommended**: Fast Rust port (active development)
- `docs/` — Progress logs and journey notes

See the full journey in [docs/progress_rust.md](https://github.com/charlesericwilson-portfolio/Echo_agent/blob/main/Echo_project/Docs/progress_rust.md).

---

Built locally with a custom 14B model. Safety deny list included.  
For red teaming and learning purposes only.

Ongoing builds are [Echo Agent Proxy](https://github.com/charlesericwilson-portfolio/Echo_agent_proxy)
