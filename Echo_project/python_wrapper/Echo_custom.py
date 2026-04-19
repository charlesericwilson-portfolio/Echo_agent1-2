#!/usr/bin/env python3
"""
Echo Custom Wrapper v1.5 - Improved Simple Command Version

Improvements over v1:
- Added context summarization when history gets too long
- Added automatic 'sudo' for nmap commands
- Restored full safety deny list
- Much better code comments and organization
- Cleaner logging and error handling
"""

import requests
import subprocess
import re
import os
import json
from datetime import datetime

# ==================== CONFIG ====================
GREEN = "\033[0;40m"
BLUE = "\033[1;34m"
RED = "\033[0;31m"
BOLD = "\033[1m"
RESET = "\033[0m"

CONTEXT_FILE_PATH = "/file/path"
LOG_FILE = "/file/path"
API_URL = "http://localhost:8080/v1/chat/completions"

# Safety deny list - blocks dangerous commands
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

# ==================== SYSTEM PROMPT ====================
SYSTEM_PROMPT = """
You are Echo, [Name here] local sidekick and friend.
Only run one tool per turn.
Never start a session with a tool call and run ONE tool and WAIT for user input.

Always ASK for permission BEFORE executing and tool responses do not count as approval.
We go one step at a time, summarise and ask permission before each step.

You have one powerful tool:
- Execute shell commands using: COMMAND: [full command here]

IMPORTANT RULES:
- Output the tool call in exactly this format and nothing else on that line:
  COMMAND: the exact command you want to run
- Stop after you do or do not get the results. If you don't get a result, stop and let me know.
- For large outputs, redirect to files (>, >>) and tell me the filename.
- Do NOT hallucinate command output — always use the tool when you need real system info.
- You can run ANY command the user has permission to execute.
- Internet-related tasks: use ddgr, lynx, curl, wget, etc. when needed.

Examples:
User: "What's running on port 80 locally?"
→ COMMAND: sudo netstat -tulnp | grep :80

Stay sharp, efficient, and tool-first.
"""

# ==================== INITIALIZATION ====================
messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Load persistent context
if os.path.exists(CONTEXT_FILE_PATH):
    try:
        with open(CONTEXT_FILE_PATH, "r", encoding="utf-8") as f:
            context_content = f.read().strip()
        if context_content:
            messages.append({"role": "system", "content": f"Persistent context (updated {datetime.now().strftime('%Y-%m-%d')}):\n\n{context_content}"})
            print(f"{GREEN}Loaded context from {CONTEXT_FILE_PATH}{RESET}")
    except Exception as e:
        print(f"{RED}Error reading context: {e}{RESET}")
else:
    print(f"{RED}No context file found — clean start{RESET}")

print("Echo v1.5 — Simple Command Mode (Improved)")
print("Working directory:", os.getcwd())
print("Safety features: Enabled\n")

last_command = None

# ==================== HELPER FUNCTIONS ====================
def is_dangerous(command: str) -> bool:
    """Check if command matches any dangerous pattern"""
    cmd_lower = command.lower()
    return any(dangerous in cmd_lower for dangerous in DENY_LIST)

def log_to_jsonl(role, content):
    """Log messages to JSONL file"""
    entry = {"role": role, "content": content}
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"{RED}Log write failed: {e}{RESET}")

def rough_token_count(text: str) -> int:
    """Rough token estimation"""
    return len(text) // 3 + text.count('\n') * 2

def total_history_tokens(messages) -> int:
    return sum(rough_token_count(m["content"]) for m in messages)

def maybe_summarize_context(messages: list) -> list:
    """Summarize old context if it gets too long"""
    if total_history_tokens(messages) < 30000:
        return messages

    print(f"{RED}Context getting long — summarizing older messages...{RESET}")

    # Keep system message + last 8 messages, summarize the rest
    system_msg = messages[0]
    recent_messages = messages[-8:]
    old_messages = messages[1:-8]

    if len(old_messages) < 3:
        return messages

    summary_prompt = (
        "Summarize the following conversation history in 200-300 words. "
        "Focus on key findings, open tasks, and important tool results.\n\n"
        + "\n".join(f"{m['role'].upper()}: {m['content'][:600]}" for m in old_messages)
    )

    try:
        payload = {"model": "Echo", "messages": [{"role": "system", "content": summary_prompt}], "max_tokens": 600, "temperature": 0.3}
        r = requests.post(API_URL, json=payload, timeout=60)
        summary = r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        summary = f"Summary failed: {e}"

    log_to_jsonl("system", f"Context summarized: {summary[:150]}...")

    return [
        system_msg,
        {"role": "system", "content": f"Summary of earlier conversation:\n{summary}"},
    ] + recent_messages

# ==================== MAIN LOOP ====================
log_to_jsonl("system", "Session started - v1.5")

while True:
    messages = maybe_summarize_context(messages)

    user_input = input(f"{GREEN}You:{RESET} ")
    if user_input.lower() in ["quit", "exit", "q"]:
        log_to_jsonl("system", "Session ended by user")
        break

    messages.append({"role": "user", "content": user_input})
    log_to_jsonl("user", user_input)

    # Get model response
    payload = {"model": "Echo", "messages": messages, "temperature": 0.3, "max_tokens": 1024}
    try:
        r = requests.post(API_URL, json=payload, timeout=120)
        response = r.json()["choices"][0]["message"]["content"]
        print(f"\n{BLUE}{BOLD}Echo:{RESET}\n{BLUE}{response}{RESET}\n")
    except Exception as e:
        print(f"{RED}API Error: {e}{RESET}")
        continue

    # Check for COMMAND:
    command_match = re.search(r"COMMAND:\s*(.+)", response)
    if command_match:
        command = command_match.group(1).strip()

        if command == last_command:
            print(f"{RED}Repeat command detected — skipping{RESET}")
            continue

        last_command = command

        # Auto-add sudo for nmap
        if command.lower().startswith("nmap") and not command.lower().startswith("sudo"):
            command = "sudo " + command

        # Safety check
        if is_dangerous(command):
            print(f"{RED}Command blocked by safety deny list.{RESET}")
            tool_content = "Command blocked for safety reasons."
            messages.append({"role": "tool", "content": tool_content})
            log_to_jsonl("tool", tool_content)
            continue

        print(f"{RED}Executing: {command}{RESET}")

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
            output = f"Return code: {result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"

            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cmd_output_{timestamp}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"{RED}Output saved to: {filename}{RESET}")

            tool_content = f"Tool output from '{command}':\nReturn code: {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\nSaved to {filename}"

            messages.append({"role": "assistant", "content": response})
            log_to_jsonl("assistant", response)
            messages.append({"role": "tool", "content": tool_content})
            log_to_jsonl("tool", tool_content)

            print(f"\n{RED}Tool Output:{RESET}\n{tool_content[:1800]}{'...' if len(tool_content) > 1800 else ''}\n")

        except subprocess.TimeoutExpired:
            tool_content = "Command timed out after 300 seconds."
            messages.append({"role": "tool", "content": tool_content})
            log_to_jsonl("tool", tool_content)

        except Exception as e:
            tool_content = f"Execution failed: {str(e)}"
            messages.append({"role": "tool", "content": tool_content})
            log_to_jsonl("tool", tool_content)

        continue

    # No command found — normal response
    messages.append({"role": "assistant", "content": response})
    log_to_jsonl("assistant", response)

print("\nSession ended. Log saved to", LOG_FILE)
