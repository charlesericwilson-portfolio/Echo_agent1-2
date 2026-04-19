use std::io::{self, Write};
use std::process::{Command, Stdio};
use std::fs;
use chrono::Utc;
use regex::Regex;
use reqwest::blocking::Client;
use serde_json::{Value, json};
use dirs;

// ==================== ANSI COLORS ====================
const LIGHT_BLUE: &str = "\x1b[94m";
const YELLOW: &str = "\x1b[33m";
const RESET_COLOR: &str = "\x1b[0m";

// ==================== CONSTANTS ====================
const MODEL_NAME: &str = "Echo";
const API_URL: &str = "http://localhost:8080/v1/chat/completions";

const SYSTEM_PROMPT: &str = r#"
You are Echo, Eric's local sidekick and friend.
Only run one tool per turn. Never start a session with a tool call and run ONE tool then wait for user input before deciding the next command or completing your task.

You are built to be red team friendly: aggressive, efficient, and always using tools when needed.

Rules:
- Use the command format exactly (case-sensitive):
  COMMAND: [full shell command here]
- Stop after one command per turn. Wait for results before deciding next steps.
- Summarize findings clearly in your final response.

You have permanent access to two files across sessions:
~/Documents/Echo_short_term_memory.txt — For the current job.
~/Documents/Echo_long_term_memory.txt — Permanent knowledge from past jobs.

Stay sharp, efficient, and tool-first.
"#;

const DENY_LIST: [&str; 15] = [
    "rm -rf", "rm --recursive", "sudo rm", "rm -rf /",
    "dd if=/dev/zero", "> /dev/sda", "mkfs", "format", "shred",
    ":(){ :|:& };:", "fork bomb", "chmod -R 777", "chown -R", "shutdown", "reboot",
];

// ==================== HELPER FUNCTIONS ====================
fn load_context_file(path: &str) -> String {
    match std::fs::read_to_string(path) {
        Ok(content) => content,
        Err(_) => "".into(),
    }
}

// Improved logging to match Python v1.5 format
fn save_chat_log_entry(user_message: &str, assistant_response: &str) {
    let home_dir = dirs::home_dir().expect("Could not resolve home directory");
    let file_path = home_dir.join("Documents/echo_chat.jsonl");

    fs::create_dir_all(home_dir.join("Documents")).expect("Failed to create ~/Documents directory");

    let trimmed_user = user_message.trim().replace('\n', " ").replace('\r', "");
    let trimmed_assistant = assistant_response.trim().replace('\n', " ").replace('\r', "");

    let entry = json!({
        "messages": [
            { "role": "user", "content": &trimmed_user },
            { "role": "assistant", "content": &trimmed_assistant }
        ]
    });

    if let Ok(mut file) = fs::OpenOptions::new().append(true).create(true).open(&file_path) {
        let _ = writeln!(file, "{}", entry.to_string());
    }
}

fn rough_token_count(text: &str) -> usize {
    text.len() / 3 + text.chars().filter(|&c| c == '\n').count() * 2
}

fn total_history_tokens(messages: &[Value]) -> usize {
    messages.iter()
        .filter_map(|m| m.get("content").and_then(|c| c.as_str()))
        .map(rough_token_count)
        .sum()
}

fn maybe_summarize_context(messages: &mut Vec<Value>) {
    if total_history_tokens(messages) < 30000 {
        return;
    }

    println!("{}Context getting long — summarizing older messages...{}", YELLOW, RESET_COLOR);

    // Keep system message + last 8 messages
    let system_msg = messages[0].clone();
    let recent: Vec<Value> = messages.iter().rev().take(8).rev().cloned().collect();
    let old_messages: Vec<Value> = messages.iter().skip(1).rev().skip(8).rev().cloned().collect();

    if old_messages.len() < 3 {
        return;
    }

    let summary_prompt = format!(
        "Summarize the following conversation history in 200-300 words. Focus on key findings and important tool results.\n\n{}",
        old_messages.iter()
            .filter_map(|m| m.get("content").and_then(|c| c.as_str()))
            .map(|c| c.chars().take(600).collect::<String>())
            .collect::<Vec<_>>()
            .join("\n")
    );

    let payload = json!({
        "model": MODEL_NAME,
        "messages": [{"role": "system", "content": summary_prompt}],
        "max_tokens": 600,
        "temperature": 0.3
    });

    let summary = match Client::new().post(API_URL).json(&payload).send() {
        Ok(res) => res.json::<Value>()
            .ok()
            .and_then(|v| v["choices"][0]["message"]["content"].as_str().map(String::from))
            .unwrap_or_else(|| "Summary failed.".to_string()),
        Err(_) => "Summary failed.".to_string(),
    };

    save_chat_log_entry("SYSTEM", &format!("Context summarized: {}", &summary[..150.min(summary.len())]));

    *messages = vec![
        system_msg,
        json!({"role": "system", "content": format!("Summary of earlier conversation:\n{}", summary)}),
    ];
    messages.extend(recent);
}

fn is_dangerous(command: &str) -> bool {
    let cmd_lower = command.to_lowercase();
    DENY_LIST.iter().any(|&bad| cmd_lower.contains(bad))
}

fn save_command_output(command: &str, stdout: &str, stderr: &str, return_code: i32) -> std::path::PathBuf {
    fs::create_dir_all("outputs").expect("Failed to create outputs directory");

    let timestamp = Utc::now().format("%Y-%m-%dT%H-%M-%S%.fZ").to_string();
    let filename = format!("cmd_output_{}.txt", timestamp);
    let full_path = std::path::PathBuf::from("outputs").join(&filename);

    let mut content = format!("Command: {}\n\n", command);
    if !stdout.is_empty() { content.push_str(&format!("[STDOUT]\n{}\n", stdout)); }
    if !stderr.is_empty() { content.push_str(&format!("\n[STDERR]\n{}\n", stderr)); }
    content.push_str(&format!("\n--- Metadata ---\nReturn code: {}\n", return_code));

    let _ = fs::write(&full_path, &content);
    full_path
}

// ==================== MAIN ====================
fn main() {
    println!("Echo Rust Wrapper v1.5 – Improved Simple COMMAND Method");
    println!("Type 'quit' or 'exit' to stop.\n");

    let context_path = std::env::var("ECHO_CONTEXT_PATH")
        .unwrap_or_else(|_| "/home/eric/echo/Echo_rag/Echo-context.txt".into());

    let context_content = load_context_file(&context_path);
    let full_system_prompt = if !context_content.trim().is_empty() {
        format!("{}\n\n{}", SYSTEM_PROMPT, context_content.trim())
    } else {
        SYSTEM_PROMPT.to_string()
    };

    let client = Client::new();
    save_chat_log_entry("SESSION_START", "");

    let mut messages: Vec<Value> = vec![json!({ "role": "system", "content": full_system_prompt })];
    let mut last_command: Option<String> = None;

    loop {
        maybe_summarize_context(&mut messages);

        print!("You: ");
        io::stdout().flush().unwrap();

        let mut user_input = String::new();
        if io::stdin().read_line(&mut user_input).is_err() { break; }

        let trimmed = user_input.trim();
        if trimmed.eq_ignore_ascii_case("quit") || trimmed.eq_ignore_ascii_case("exit") {
            println!("Session ended.");
            break;
        }

        save_chat_log_entry(trimmed, "");
        messages.push(json!({ "role": "user", "content": trimmed }));

        // Send to model
        let payload = json!({
            "model": MODEL_NAME,
            "messages": &messages,
            "temperature": 0.3,
            "max_tokens": 1024
        });

        let response_text = match client.post(API_URL).json(&payload).send() {
            Ok(res) => {
                if res.status().is_success() {
                    res.json::<Value>()
                        .ok()
                        .and_then(|v| v["choices"][0]["message"]["content"].as_str().map(String::from))
                        .unwrap_or_else(|| "No content in response".to_string())
                } else {
                    format!("API error: {}", res.status())
                }
            },
            Err(e) => format!("Request failed: {}", e),
        };

        save_chat_log_entry("", &response_text);

        // Check for COMMAND:
        if let Some(captures) = Regex::new(r#"^COMMAND:\s*(.+)$"#).unwrap().captures(&response_text) {
            let command = captures.get(1).unwrap().as_str().trim();

            if Some(command) == last_command.as_deref() {
                println!("Command identical to last turn. Skipping.");
                continue;
            }
            last_command = Some(command.to_string());

            if is_dangerous(command) {
                println!("{}Blocking dangerous command: {}{}", LIGHT_BLUE, command, RESET_COLOR);
                continue;
            }

            println!("{}Echo: Executing:{}\n{}\n{}", LIGHT_BLUE, RESET_COLOR, command, RESET_COLOR);

            match Command::new("sh").arg("-c").arg(command)
                .stdout(Stdio::piped()).stderr(Stdio::piped()).output()
            {
                Ok(output) => {
                    let stdout = String::from_utf8_lossy(&output.stdout).into_owned();
                    let stderr = String::from_utf8_lossy(&output.stderr).into_owned();
                    let return_code = output.status.code().unwrap_or(-1);

                    let file_path = save_command_output(command, &stdout, &stderr, return_code);

                    if !stdout.is_empty() {
                        println!("{}Echo:\n{}\n{}", LIGHT_BLUE, stdout, RESET_COLOR);
                    }
                    if !stderr.is_empty() {
                        println!("{}Warnings:\n{}\n{}", YELLOW, stderr, RESET_COLOR);
                    }

                    let tool_content = format!(
                        "Command: {}\nReturn code: {}\nSaved to: {}",
                        command, return_code, file_path.display()
                    );
                    messages.push(json!({ "role": "tool", "content": tool_content }));
                    save_chat_log_entry(&format!("COMMAND: {}", command), &tool_content);
                },
                Err(e) => {
                    let err = format!("Execution failed: {}", e);
                    println!("{}Echo: {}{}", YELLOW, err, RESET_COLOR);
                    save_chat_log_entry(&format!("COMMAND FAILED: {}", command), &err);
                }
            }
        } else {
            // Normal response
            println!("{}Echo:\n{}\n{}", LIGHT_BLUE, response_text, RESET_COLOR);
        }
    }
}
