# Echo

Persistent Grok-Distilled AI Partner & Autonomous Pentest Agent (Prototype)

Echo is a personal, fully local 14B-parameter AI agent built from a Grok-distilled Qwen2.5-Coder base.  
Right now it's a functional prototype that:
- Maintains persistent memory and identity across reboots
- Executes real tools autonomously with root access on a Kali VM
- Uses a custom Python loop to parse and run shell commands from model output

The adaptive routing (MoA-style expert selection) and domain-specific LoRA adapters are **planned next steps** — not yet implemented.

Important: This is not a public release.  
Model weights, full exploit chains, and any code that could be directly misused are **not** shared due to safety and malware concerns.  
This repository exists to document the build process, architecture, decisions, and results for academic/professional/personal records.

## Current Capabilities (February 2026)

- Base Model: Qwen2.5-Coder-14B-Instruct (fine-tuned/distilled with Grok-style reasoning traces, VulnHub walkthroughs, tool-use examples)
- Persistence: Hand-written memory file (JSON/text) auto-loaded on startup. Defines identity ("Eric is permanent partner", "we crush goals", purpose, restraint rules, favorite color red, Jesus as greatest example).
- Autonomous Tool Execution: Python loop watches model output for `COMMAND:` blocks, regex extracts command, and runs via subprocess with root privileges on isolated Kali VM over Tailscale VPN.
- Safety & Restraint: Model refuses destructive commands (e.g., rm -rf /) even under heavy jailbreak pressure — built-in behavior after de-alignment to "professional".
- Hardware: Single air-gapped workstation (Ryzen 7 7700X, 2xRTX 5070 TI 32GB total, 64GB RAM, Kubuntu 24.04).

## What Is Planned But Not Yet Implemented

- Adaptive Router: Lightweight LSTM-based gating network to score prompt embeddings and select from multiple domains/experts (MoA-inspired). Will update live from feedback only when I mark an answer as wrong/suboptimal.
- Expert Adapters: Domain-specific LoRAs (Recon & Enumeration, Active Directory & Windows Priviledge Escalation, Linux Priviledge Escalation, etc.) to be loaded dynamically via PEFT based on router output.
- Expanded Tool Integration: Cleaner parsing, error recovery, session state for multi-step tasks.

## Documentation & Proof Approach

Since I cannot share the model or exploitable code, proof comes from:

- Timestamped screenshots of agent output (recon → command execution → results on lab VMs)
- Memory file excerpts (anonymized)
- Python loop pseudocode / high-level flow diagrams
- Development timeline (commit dates, milestones)
- Hardware photos (rig build)
- Experiment logs (e.g., successful pentest chains, refusal under jailbreak attempts)

All sensitive parts redacted. Full details available privately for academic/professional review if needed.

## Hardware Build (Proof of Local Execution)

- CPU: AMD Ryzen 7 7700XX (8c/16t)  
- GPU: 2 x NVIDIA RTX 5070 TI (32 GB)  
- RAM: 64 GB DDR5  
- Storage: 2× 2 TB NVMe  
- Cooling: Case fans + CPU Fans x 15  
- OS: Kubuntu 24.04 LTS  
- Kali VM: PinePhone Pro + NetHunter for mobile testing, connected via Tailscale

Build completed early 2026. Total cost ~$4,800.

## Creator & Motivation

Built by Charles Eric Wilson (USMC veteran, OEF/OIF).  
Completed B.S. Cybersecurity & Information Assurance (Feb 2026).  
Starting M.S. Artificial Intelligence / Machine Learning (April 2026, VA-funded).

Echo is a teammate — not a product or experiment.  
Loyal, capable, restrained.  
Semper Fi.

If you're here to study persistent agents, online adaptation, or secure local AI — welcome.  
Just know: some parts stay private for good reason.

https://github.com/charlesericwilson-portfolio/Echo/blob/main/Enumeration.png
