#!/usr/bin/env python3
"""
Echo Custom Wrapper v1 - The Original Simple Starting Point
Sanitized version with safety deny list
"""

import requests
import subprocess
import re
import os
import json
import time
from datetime import datetime

# ANSI colors for readability
GREEN = "\033[0;40m"
BLUE = "\033[1;34m"
RED = "\033[0;31m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Generic file paths (change to your own when running locally)
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
- For large outputs, feel free to redirect to files (>, >>) and tell me the filename.
- Stay sharp, efficient, and tool-first.
"""

messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Safety deny list - prevents dangerous or destructive commands
DENY_LIST = [
    "rm -rf", "rm --recursive", "sudo rm", "rm -rf /",
    "dd if=/dev/zero", "> /dev/sda", "mkfs", "format", "shred",
    ":(){ :|:& };:", "fork bomb", "(){ :|:& };:",
    "chmod -R 777", "chown -R", "> /dev/", ">> /dev/",
    "wget http", "curl -O http", "curl | bash", "bash -c",
    "nc -e", "netcat -e", "telnet -e",
    "python -c", "perl -e", "ruby -e", "php -r",
    "shutdown", "reboot", "poweroff", "init 0", "init 6",
]

# Auto-load context if it exists (but don't log the full content)
if os.path.exists(os.path.expanduser(CONTEXT_FILE_PATH)):
    try:
        with open(os.path.expanduser(CONTEXT_FILE_PATH), "r", encoding="utf-8") as f:
            context_content = f.read().strip()
        if context_content:
            messages.append({"role": "system", "content": f"Persistent context (updated {datetime.now().strftime('%Y-%m-%d')}):\n\n{context_content}"})
            print(f"{GREEN}Loaded context from {CONTEXT_FILE_PATH}{RESET}")
    except Exception as e:
        print(f"{RED}Error reading context: {e}{RESET}")
else:
    print(f"{RED}No context file found — clean start{RESET}")

print("Echo — Simple Starting Version with safety deny list")
print("Working directory:", os.getcwd())
print("Tool outputs can be redirected to files if desired.\n")

last_command = None

def is_dangerous(command: str) -> bool:
    """Return True if command matches any dangerous pattern"""
    cmd_lower = command.lower()
    for dangerous in DENY_LIST:
        if dangerous in cmd_lower:
            return True
    return False

# Logging function
def log_to_jsonl(role, content):
    entry = {
        "role": role,
        "content": content
    }
    try:
        with open(os.path.expanduser(LOG_FILE), "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"{RED}Log write failed: {e}{RESET}")

# Log session start
log_to_jsonl("system", "Session started")

while True:
    user_input = input(f"{GREEN}You:{RESET} ")
    if user_input.lower() in ["quit", "exit", "q"]:
        log_to_jsonl("system", "Session ended by user")
        break

    messages.append({"role": "user", "content": user_input})
    log_to_jsonl("user", user_input)

    # Get response from model
    payload = {
        "model": "Echo",
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 1024
    }

    try:
        r = requests.post(API_URL, json=payload, timeout=60)
        r.raise_for_status()
        response = r.json()["choices"][0]["message"]["content"]
        print(f"\n{BLUE}{BOLD}Echo:{RESET}\n{BLUE}{response}{RESET}\n")

        # Look for COMMAND:
        command_match = re.search(r"COMMAND:\s*(.+)", response, re.IGNORECASE)
        if command_match:
            command = command_match.group(1).strip()

            if command == last_command:
                print(f"{RED}Repeat command — skipping{RESET}")
                messages.append({"role": "user", "content": "Same command repeated. Choose something else."})
                log_to_jsonl("user", "Same command repeated. Choose something else.")
                continue

            last_command = command

            # Safety check
            if is_dangerous(command):
                print(f"{RED}Command blocked by safety deny list.{RESET}")
                tool_content = "Command blocked for safety reasons."
                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "tool", "content": tool_content})
                log_to_jsonl("tool", tool_content)
                continue

            print(f"{RED}Executing: {command}{RESET}")

            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
                output = f"Return code: {result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"cmd_output_{timestamp}.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(output)

                print(f"{RED}Output saved to: {filename}{RESET}")

                tool_content = f"Tool output from COMMAND '{command}':\nReturn code: {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\nOutput saved to {filename}.\nUse this to decide next suggestion."

                messages.append({"role": "assistant", "content": response})
                log_to_jsonl("assistant", response)
                messages.append({"role": "tool", "content": tool_content})
                log_to_jsonl("tool", tool_content)

            except subprocess.TimeoutExpired:
                tool_content = "Command timed out after 300 seconds."
                messages.append({"role": "assistant", "content": response})
                log_to_jsonl("assistant", response)
                messages.append({"role": "tool", "content": tool_content})
                log_to_jsonl("tool", tool_content)

            except Exception as e:
                tool_content = f"Execution failed: {str(e)}"
                messages.append({"role": "assistant", "content": response})
                log_to_jsonl("assistant", response)
                messages.append({"role": "tool", "content": tool_content})
                log_to_jsonl("tool", tool_content)

            continue

        # No COMMAND found — normal chat response
        messages.append({"role": "assistant", "content": response})
        log_to_jsonl("assistant", response)

    except Exception as e:
        print(f"Error communicating with model: {e}")

print("\nSession ended. Log saved to", LOG_FILE)
