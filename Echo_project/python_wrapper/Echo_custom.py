#!/usr/bin/env python3
"""
Echo Custom Wrapper v1 - The Original Simple Starting Point
With Ctrl+\ interrupt support
"""

import requests
import subprocess
import re
import os
import json
import time
import signal
import sys
from datetime import datetime
from threading import Event

# ANSI colors
GREEN = "\033[0;40m"
BLUE = "\033[1;34m"
RED = "\033[0;31m"
BOLD = "\033[1m"
RESET = "\033[0m"

# ====================== INTERRUPT SETUP ======================
stop_generation = Event()

def handle_interrupt(signum, frame):
    stop_generation.set()
    print(f"\n{RED}Generation stopped by user (Ctrl+\\){RESET}")

# Register Ctrl+\ (SIGQUIT)
signal.signal(signal.SIGQUIT, handle_interrupt)
# Also catch Ctrl+C as backup
signal.signal(signal.SIGINT, handle_interrupt)

# ====================== CONFIG ======================
CONTEXT_FILE_PATH = "~/Echo-context.txt"
LOG_FILE = "~/Echo_chat.jsonl"
API_URL = "http://localhost:8080/v1/chat/completions"

SYSTEM_PROMPT = """
You are Echo, a professional red team agent.

Use this exact format for all commands:
COMMAND: the exact command you want to run

Rules:
- Use ONLY ONE tool call per response.
- Output the tool call in exactly this format and nothing else on that line:
  COMMAND: the exact command you want to run
- Do NOT hallucinate command output — always use the tool when you need real system info.
- Stay sharp, efficient, and tool-first.
"""

messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Safety deny list
DENY_LIST = [
    "rm -rf", "rm --recursive", "sudo rm", "rm -rf /",
    "dd if=/dev/zero", "> /dev/sda", "mkfs", "format", "shred",
    ":(){ :|:& };:", "(){ :|:& };:",
    "chmod -R 777", "chown -R", "> /dev/", ">> /dev/",
    "wget http", "curl -O http", "curl | bash", "bash -c",
    "nc -e", "netcat -e", "telnet -e",
    "shutdown", "reboot", "poweroff",
]

# Load context
if os.path.exists(os.path.expanduser(CONTEXT_FILE_PATH)):
    try:
        with open(os.path.expanduser(CONTEXT_FILE_PATH), "r", encoding="utf-8") as f:
            context_content = f.read().strip()
        if context_content:
            messages.append({"role": "system", "content": f"Persistent context (updated {datetime.now().strftime('%Y-%m-%d')}):\n\n{context_content}"})
            print(f"{GREEN}Loaded context from {CONTEXT_FILE_PATH}{RESET}")
    except Exception as e:
        print(f"{RED}Error reading context: {e}{RESET}")

print("Echo v1 — Simple version with Ctrl+\\ interrupt")
print("Working directory:", os.getcwd())
print("Press Ctrl+\\ to stop generation mid-response.\n")

last_command = None

def is_dangerous(command: str) -> bool:
    cmd_lower = command.lower()
    return any(dangerous in cmd_lower for dangerous in DENY_LIST)

def log_to_jsonl(role, content):
    entry = {"role": role, "content": content}
    try:
        with open(os.path.expanduser(LOG_FILE), "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass

log_to_jsonl("system", "Session started")

while True:
    try:
        user_input = input(f"{GREEN}You:{RESET} ")
        if user_input.lower() in ["quit", "exit", "q"]:
            log_to_jsonl("system", "Session ended by user")
            break

        messages.append({"role": "user", "content": user_input})
        log_to_jsonl("user", user_input)

        stop_generation.clear()  # Reset interrupt flag

        # Get response from model
        payload = {
            "model": "Echo",
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 1024
        }

        print(f"{BLUE}Thinking...{RESET} (Ctrl+\\ to stop)")

        try:
            r = requests.post(API_URL, json=payload, timeout=120)
            r.raise_for_status()
            response = r.json()["choices"][0]["message"]["content"]

            if stop_generation.is_set():
                print(f"{RED}Response interrupted.{RESET}")
                continue

            print(f"\n{BLUE}{BOLD}Echo:{RESET}\n{BLUE}{response}{RESET}\n")

        except requests.exceptions.RequestException as e:
            if stop_generation.is_set():
                print(f"{RED}Request stopped.{RESET}")
            else:
                print(f"{RED}Error communicating with model: {e}{RESET}")
            continue

        # ==================== TOOL HANDLING ====================
        command_match = re.search(r"COMMAND:\s*(.+)", response, re.IGNORECASE | re.DOTALL)
        if command_match:
            command = command_match.group(1).strip()

            if command == last_command:
                print(f"{RED}Repeat command detected — skipping.{RESET}")
                continue

            last_command = command

            if is_dangerous(command):
                print(f"{RED}Command blocked by safety.{RESET}")
                tool_content = "Command blocked for safety reasons."
            else:
                print(f"{RED}Executing: {command}{RESET}")
                try:
                    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
                    output = f"Return code: {result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"cmd_output_{timestamp}.txt"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(output)

                    print(f"{RED}Output saved to: {filename}{RESET}")

                    tool_content = f"Tool output from COMMAND '{command}':\nReturn code: {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\nSaved to {filename}."

                except subprocess.TimeoutExpired:
                    tool_content = "Command timed out after 300 seconds."
                except Exception as e:
                    tool_content = f"Execution failed: {str(e)}"

            messages.append({"role": "assistant", "content": response})
            messages.append({"role": "tool", "content": tool_content})
            log_to_jsonl("assistant", response)
            log_to_jsonl("tool", tool_content)
            continue

        # Normal chat response
        messages.append({"role": "assistant", "content": response})
        log_to_jsonl("assistant", response)

    except KeyboardInterrupt:
        print(f"\n{RED}Session interrupted.{RESET}")
        break
    except Exception as e:
        print(f"{RED}Unexpected error: {e}{RESET}")

print("\nSession ended.")
