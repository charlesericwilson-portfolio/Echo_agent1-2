# Echo - Local Red Team AI Agent tool

**A fast, local AI tool wrapper that executes shell commands safely via `COMMAND: your command` lines from a custom LLM.**

Current recommended version: **Rust** (much faster and cleaner than the original Python version).

### Quick Answers
- **What does it do?**  
  You chat with your local LLM. When it wants to run a command, it outputs `COMMAND: nmap -sV 192.168.1.1`. Echo detects it, runs the command safely, and feeds the output back to the model.

- **How do I try it?**
   Download the [python_wrapper](https://github.com/charlesericwilson-portfolio/Echo_agent1-2/blob/main/Echo_project/python_wrapper/Echo_custom.py) edit your file paths and api endpoint and run with python.
   ```
   bash
   python3 Echo_custom.py
   ```
    
- **Does it work?**  
  Yes — the Python COMMAND executor is stable and working daily. The newer Rust wrapper works and is stable as well but is no longer the main focus.

### Repository Structure
- `python_wrapper/` — Original simple Python implementation
- `echo_rust_wrapper/` — **Recommended**: Fast Rust port (active development)
- `docs/` — Progress logs and journey notes

See the full journey in [progress_python.md](https://github.com/charlesericwilson-portfolio/Echo_agent/blob/main/Echo_project/Docs/progress_python.md) and [progress_rust.md](https://github.com/charlesericwilson-portfolio/Echo_agent/blob/main/Echo_project/Docs/progress_rust.md).

---

Built locally with a custom 14B model. Safety deny list included.  
For chat, red teaming, and learning purposes only.

Next step is a port to rust check it out here [Echo rust](https://github.com/charlesericwilson-portfolio/Echo_agent/blob/main/Echo_project/echo_rust_wrapper/README.md)

Builds in testing [Echo_tmux](https://github.com/charlesericwilson-portfolio/Echo_tmux/blob/main/README.md)

Builds in development [Echo Agent Proxy](https://github.com/charlesericwilson-portfolio/Echo_agent_proxy) 
