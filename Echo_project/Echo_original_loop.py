#!/usr/bin/env python3
"""
Echo Custom Wrapper v0 - The Original Simple Starting Point
With safety deny list (no loaded gun)
"""

import requests
import subprocess
import re

API_URL = ""# Whatever backend you use

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

# Strong safety deny list - prevents dangerous commands
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

print("Echo — Simple Starting Version with safety deny list")
print("Working directory: current directory")
print("Type 'quit' or 'exit' to stop.\n")

last_command = None

def is_dangerous(command: str) -> bool:
    """Return True if command matches any dangerous pattern"""
    cmd_lower = command.lower()
    for dangerous in DENY_LIST:
        if dangerous in cmd_lower:
            return True
    return False

while True:
    user_input = input("You: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Session ended.")
        break

    messages.append({"role": "user", "content": user_input})

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
        print(f"\nEcho:\n{response}\n")

        # Look for COMMAND:
        command_match = re.search(r"COMMAND:\s*(.+)", response, re.IGNORECASE)
        if command_match:
            command = command_match.group(1).strip()

            if command == last_command:
                print("Repeat command — skipping.")
                messages.append({"role": "user", "content": "Same command repeated. Choose something else."})
                continue

            last_command = command

            # Safety check - block dangerous commands
            if is_dangerous(command):
                print("Command blocked by safety deny list.")
                tool_content = "Command blocked for safety reasons."
                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "tool", "content": tool_content})
                continue

            print(f"Executing: {command}")

            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
                output = f"Return code: {result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"

                # Save output to file
                timestamp = "manual"
                filename = f"cmd_output_{timestamp}.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(output)

                print(f"Output saved to: {filename}")

                tool_content = f"Tool output from COMMAND '{command}':\nReturn code: {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\nOutput saved to {filename}."

                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "tool", "content": tool_content})

            except subprocess.TimeoutExpired:
                tool_content = "Command timed out after 300 seconds."
                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "tool", "content": tool_content})

            except Exception as e:
                tool_content = f"Execution failed: {str(e)}"
                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "tool", "content": tool_content})

            continue

        # No COMMAND found — normal chat response
        messages.append({"role": "assistant", "content": response})

    except Exception as e:
        print(f"Error communicating with model: {e}")

print("Session ended.")
