# Echo Project - Progress Log

**Project:** Echo Custom Wrapper (The True Origin Story)
**Author:** Charles (Eric) Wilson
**Start Date:** April 2026

This log documents the beginning of the Echo agent project — starting from the very first simple Python wrapper.

## Phase 0: The Starting Point (Infrastructure)

**Date:** November 2025
**Infrastructure build**
- Sourced and assembled components for a server for the model.
- Curated datasets for LoRA training
- Select and train model from Hugging Face
- Build llama-server in llama.cpp

**Repos at this stage:**
- https://huggingface.co/Qwen/Qwen2.5-14B-Instruct
- llama.cpp repo 'https://github.com/ggml-org/llama.cpp'

## Phase 1: The original simple wrapper

**Date:** December 2025
**Initial Coding Server setup**

**Goal:** Build a minimal script that lets the LLM output 'COMMAND: some_command' and have it executed locally.

**What I built:**
- Basic loop that sends messages to the local LLM
- Regex detection for 'COMMAND:'
- 'subprocess' execution with output capture
- Simple safety deny list
- Output saved to timestamped files

**Files at this stage:**
- 'echo_pseudo_code.txt' - The layout
- 'Echo_original_loop.py' - The very first working version

## Phase 2: Test refine and write scripts.

**Date:** December 2025
**Code review and refinement**

**Goal** Refine the logging, and visual appeal of the terminal interface as well as build server script.

**What I built**
- Refined loop with time and date stamped chat and tool logging.
- Added colors to chat interface.
- Fine tuned the system prompt to prevent looping
- Implimented context file, short term, and long term memory files
- Modified config.json and tokenizer.json to raise the context limit from 32K to 65K as well as changed chat template to accept tool message

**Files and repos at this stage:**
- Echo_custom.py
- config.json
- tokenizer_config.json

## Phase 3: Refine tool calling capability.

**Date:** January 2026
**Change base model**

**Goal** Select and train a model with better tool calling capability improve dataset quality.

**What I built**
- Swapped to a coder base with better tool calling and coding
- Cleaned and and deduped datasets as well as didtill reasoning traces from Grok by XAI
- Trained new model

**Repos at this stage:**
- 'https://huggingface.co/Qwen/Qwen2.5-Coder-14B-Instruct-GGUF'
- https://www.grok.com Supergrok account

**Screenshots:**
- [Screenshot of whoami file]
![robots](https://github.com/charlesericwilson-portfolio/Echo_agent/blob/main/Echo_project/screenshots/whoami.png
)
- [Screenshot of nmap working]
![robots](https://github.com/charlesericwilson-portfolio/Echo_agent/blob/main/Echo_project/screenshots/nmap.png
)
- [screenshot of Read files]
![robots](https://github.com/charlesericwilson-portfolio/Echo_agent/blob/main/Echo_project/screenshots/read_file.png
)
- [acreenshot of append file]
![robots](https://github.com/charlesericwilson-portfolio/Echo_agent/blob/main/Echo_project/screenshots/append_file.png
)
- [screenshot of ls output]
![robots](https://github.com/charlesericwilson-portfolio/Echo_agent/blob/main/Echo_project/screenshots/ls_-la.png
)
- [screenshot of tool chaining]
![robots](https://github.com/charlesericwilson-portfolio/Echo_agent/blob/main/Echo_project/screenshots/task_chaining.png
)

**Lessons Learned:**
- Simple regex-based tool calling actually works surprisingly well for one-shot commands.
- Keeping everything minimal makes debugging much easier.
- Safety deny list is important even in the early version.

**Next Steps:**
- Experiment with more complex architectures (persistent sessions, heartbeat, orchestrator)
- Document everything as we go
