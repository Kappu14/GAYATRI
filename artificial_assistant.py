import argparse
import ast
import json
import os
import random
import re
import urllib.error
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer


AI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")


WEB_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Artificial Assistant</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: radial-gradient(circle at top, #1f2d50 0%, #111827 35%, #050816 100%);
            color: #ebf3ff;
            display: grid;
            place-items: center;
            min-height: 100vh;
        }
        .app {
            width: min(980px, 94vw);
            min-height: 760px;
            background: rgba(17, 24, 39, 0.72);
            border: 1px solid rgba(160, 180, 255, 0.18);
            border-radius: 28px;
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(16px);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .header {
            padding: 22px 28px;
            background: rgba(255,255,255,0.04);
            border-bottom: 1px solid rgba(255,255,255,0.08);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            margin: 0;
            font-size: 1.9rem;
            letter-spacing: 0.04em;
        }
        .status {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 0.8rem;
            color: #b4d9ff;
            background: rgba(79, 140, 255, 0.12);
            border: 1px solid rgba(120, 168, 255, 0.24);
            border-radius: 999px;
            padding: 8px 12px;
        }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #4ade80;
            box-shadow: 0 0 12px rgba(74, 222, 128, 0.8);
        }
        .chat-box {
            flex: 1;
            overflow-y: auto;
            padding: 26px 22px 10px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .msg {
            max-width: 78%;
            padding: 14px 16px;
            border-radius: 16px;
            line-height: 1.6;
            box-shadow: 0 10px 18px rgba(0,0,0,0.12);
            white-space: pre-wrap;
        }
        .user {
            align-self: flex-end;
            background: linear-gradient(135deg, #3b82f6, #7c3aed);
            color: white;
            border-bottom-right-radius: 6px;
        }
        .assistant {
            align-self: flex-start;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.08);
            color: #eef6ff;
            border-bottom-left-radius: 6px;
        }
        .composer {
            display: flex;
            gap: 10px;
            padding: 18px 20px 20px;
            border-top: 1px solid rgba(255,255,255,0.08);
            background: rgba(255,255,255,0.03);
        }
        input {
            flex: 1;
            padding: 14px 16px;
            border: 1px solid rgba(160,180,255,0.2);
            border-radius: 14px;
            background: rgba(15, 23, 42, 0.7);
            color: white;
            font-size: 1rem;
            outline: none;
        }
        input:focus {
            border-color: rgba(96,165,250,0.75);
            box-shadow: 0 0 0 3px rgba(96,165,250,0.18);
        }
        .button-row {
            display: flex;
            gap: 10px;
        }
        button {
            border: none;
            border-radius: 14px;
            cursor: pointer;
            transition: transform .15s ease, filter .15s ease;
        }
        button:hover {
            filter: brightness(1.06);
            transform: translateY(-1px);
        }
        .primary {
            padding: 0 18px;
            background: linear-gradient(135deg, #5c9aff, #7c4dff);
            color: white;
            font-weight: 700;
        }
        .secondary {
            padding: 0 16px;
            background: rgba(148, 163, 184, 0.15);
            color: white;
            border: 1px solid rgba(255,255,255,0.12);
        }
        .bottom-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 20px 18px;
            color: #bed7ff;
            font-size: 0.82rem;
        }
        .voice-indicator {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            color: #dbeafe;
        }
        .voice-wave {
            display: inline-flex;
            align-items: end;
            gap: 4px;
            height: 16px;
        }
        .voice-wave span {
            display: block;
            width: 4px;
            border-radius: 10px;
            background: linear-gradient(180deg, #7dd3fc, #60a5fa);
            animation: pulse 1.2s ease-in-out infinite;
        }
        .voice-wave span:nth-child(1){ height: 4px; animation-delay: 0s; }
        .voice-wave span:nth-child(2){ height: 9px; animation-delay: 0.15s; }
        .voice-wave span:nth-child(3){ height: 14px; animation-delay: 0.3s; }
        .voice-wave span:nth-child(4){ height: 9px; animation-delay: 0.45s; }
        .voice-wave span:nth-child(5){ height: 4px; animation-delay: 0.6s; }
        @keyframes pulse {
            0%, 100% { transform: scaleY(0.6); opacity: 0.5; }
            50% { transform: scaleY(1); opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="app">
        <div class="header">
            <h1>Artificial Assistant</h1>
            <div class="status"><span class="status-dot"></span> Online</div>
        </div>
        <div id="chatBox" class="chat-box">
            <div class="msg assistant">Hello! I am your artificial assistant. How can I help you today?</div>
        </div>
        <div class="composer">
            <input id="promptInput" type="text" placeholder="Ask me something..." autocomplete="off" />
            <div class="button-row">
                <button id="voiceBtn" class="secondary" type="button">🎙️ Voice</button>
                <button id="sendBtn" class="primary" type="button">Send</button>
            </div>
        </div>
        <div class="bottom-bar">
            <span>AI-ready assistant</span>
            <span class="voice-indicator">
                <span class="voice-wave"><span></span><span></span><span></span><span></span><span></span></span>
                Voice ready
            </span>
        </div>
    </div>

    <script>
        const chatBox = document.getElementById('chatBox');
        const promptInput = document.getElementById('promptInput');
        const sendBtn = document.getElementById('sendBtn');
        const voiceBtn = document.getElementById('voiceBtn');

        function addMessage(text, sender) {
            const msg = document.createElement('div');
            msg.className = `msg ${sender}`;
            msg.textContent = text;
            chatBox.appendChild(msg);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        async function sendPrompt() {
            const text = promptInput.value.trim();
            if (!text) return;

            addMessage(text, 'user');
            promptInput.value = '';

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: text })
                });
                const data = await response.json();
                addMessage(data.reply || 'I could not understand that.', 'assistant');
                if (window.speechSynthesis && data.reply) {
                    const utterance = new SpeechSynthesisUtterance(data.reply);
                    utterance.rate = 1;
                    utterance.pitch = 1.1;
                    window.speechSynthesis.cancel();
                    window.speechSynthesis.speak(utterance);
                }
            } catch (error) {
                addMessage('Sorry, the assistant is unavailable right now.', 'assistant');
            }
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition = null;

        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.lang = 'en-US';
            recognition.interimResults = false;
            recognition.continuous = false;

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                promptInput.value = transcript;
            };

            recognition.onend = () => {
                voiceBtn.textContent = '🎙️ Voice';
            };
        }

        voiceBtn.addEventListener('click', () => {
            if (!recognition) {
                addMessage('Voice input is not supported in this browser.', 'assistant');
                return;
            }

            voiceBtn.textContent = '🎙️ Listening...';
            recognition.start();
        });

        sendBtn.addEventListener('click', sendPrompt);
        promptInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') sendPrompt();
        });
    </script>
</body>
</html>
"""


def greet_user() -> str:
    hour = datetime.now().hour
    if 5 <= hour < 12:
        period = "Good morning"
    elif 12 <= hour < 18:
        period = "Good afternoon"
    else:
        period = "Good evening"
    return f"{period}! I am your artificial assistant. How can I help you today?"


def extract_numbers(text: str):
    numbers = re.findall(r"-?\d+(?:\.\d+)?", text)
    return [float(n) for n in numbers]


def trigger_any(text: str, *phrases):
    lower = text.lower()
    return any(phrase in lower for phrase in phrases)


def safe_calculate(expression: str):
    allowed_names = {"pi": 3.141592653589793, "e": 2.718281828459045}
    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.Mod,
        ast.FloorDiv,
        ast.USub,
        ast.UAdd,
        ast.Constant,
        ast.Name,
    )
    tree = ast.parse(expression, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            raise ValueError("Unsupported expression")
        if isinstance(node, ast.Name) and node.id not in allowed_names:
            raise ValueError("Unsupported name")
    return eval(compile(tree, "<calc>", "eval"), {"__builtins__": {}}, allowed_names)


def simple_calculator(text: str) -> str:
    cleaned = text.lower().replace("calculate", "").replace("what is", "").replace("equals", "").strip()
    cleaned = cleaned.strip("= ")
    if not cleaned:
        return "I can calculate expressions like 8 + 7 or 10 * 3."
    try:
        result = safe_calculate(cleaned)
        return f"The result is: {result}"
    except Exception:
        return "I can do math if you ask in a simple format like 5 + 3 or 12 / 4."


def to_do_list() -> str:
    return "Suggested plan: 1) Choose the top priority, 2) Work on it for 25 minutes, 3) Take a short break, 4) Finish with a quick review."


def word_count(text: str) -> str:
    words = re.findall(r"\b\w+\b", text)
    return f"Your text has {len(words)} words and {len(text.replace(' ', ''))} characters without spaces."


def convert_temperature(text: str) -> str:
    match = re.search(r"(-?\d+(?:\.\d+)?)\s*(c|f)", text.lower())
    if not match:
        return "Example: 30 c to f or 86 f to c."
    value = float(match.group(1))
    unit = match.group(2)
    if unit == "c":
        converted = (value * 9 / 5) + 32
        return f"{value}°C = {converted:.2f}°F"
    converted = (value - 32) * 5 / 9
    return f"{value}°F = {converted:.2f}°C"


def bmi_info(text: str) -> str:
    nums = extract_numbers(text)
    if len(nums) < 2:
        return "Example: BMI 70 1.75 or BMI 68kg 1.7m."
    weight, height = nums[0], nums[1]
    if height <= 0 or weight <= 0:
        return "Please enter valid positive values."
    if height > 10:
        height = height / 100
    bmi = weight / (height ** 2)
    if bmi < 18.5:
        status = "underweight"
    elif bmi < 25:
        status = "healthy"
    elif bmi < 30:
        status = "overweight"
    else:
        status = "obese"
    return f"Your BMI is {bmi:.2f}, which is {status}."


def flip_coin() -> str:
    return random.choice(["Heads!", "Tails!"])


def roll_dice() -> str:
    return f"You rolled a {random.randint(1, 6)} and a {random.randint(1, 6)}."


def call_ai_api(prompt: str):
    if not AI_API_KEY:
        return None
    try:
        request_data = json.dumps({
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }).encode("utf-8")
        request = urllib.request.Request(
            f"{AI_BASE_URL}/chat/completions",
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {AI_API_KEY}",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return payload["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def generate_response(user_input: str) -> str:
    text = user_input.strip()
    if not text:
        return "I did not receive any input. Please ask me something."

    ai_reply = call_ai_api(text)
    if ai_reply:
        return ai_reply

    lower = text.lower()

    if trigger_any(lower, "hello", "hi", "hey", "greetings"):
        return "Hello! I am ready to assist you."

    if trigger_any(lower, "your name", "who are you", "what are you", "tell me about yourself"):
        return "I am a simple artificial assistant created to help with daily tasks, calculations, and friendly conversation."

    if trigger_any(lower, "time", "date", "clock"):
        now = datetime.now()
        return f"The current time is {now.strftime('%H:%M:%S')} on {now.strftime('%A, %d %B %Y')}."

    if trigger_any(lower, "help", "assist", "support", "what can you do"):
        return "I can help with greetings, dates, math, quotes, task planning, health ideas, word counts, jokes, and quick daily productivity support."

    if trigger_any(lower, "how are you", "you okay", "are you good"):
        return "I am doing well and ready to help. Thank you for asking!"

    if trigger_any(lower, "thank", "thanks"):
        return "You are welcome! I am always here to help."

    if trigger_any(lower, "bye", "goodbye", "exit", "quit", "see you"):
        return "Goodbye! Take care and come back anytime."

    if trigger_any(lower, "joke", "funny", "humor"):
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs.",
            "I told my computer I needed a break, and now it sends me to sleep mode.",
            "A SQL query walks into a bar, and the bartender says, 'Why are you here?' It says, 'I have a table for two.'",
            "Why did the developer go broke? Because they used up all their cache.",
        ]
        return random.choice(jokes)

    if trigger_any(lower, "fact", "interesting fact", "did you know"):
        facts = [
            "Honey never spoils. Archaeologists have found pots of honey in ancient tombs that are still edible.",
            "Octopuses have three hearts: two pump blood to the gills, and one pumps it to the rest of the body.",
            "A day on Venus is longer than a year on Venus.",
            "Bananas are berries, but strawberries are not.",
        ]
        return random.choice(facts)

    if trigger_any(lower, "quote", "inspiration", "motivational"):
        quotes = [
            "Success is the sum of small efforts repeated day in and day out.",
            "The future depends on what you do today.",
            "You do not have to be perfect to be amazing.",
            "Small steps still move you forward.",
        ]
        return random.choice(quotes)

    if trigger_any(lower, "motivation", "encourage", "inspire"):
        return "Keep going. Progress is built from the small wins you complete every single day."

    if trigger_any(lower, "calculate", "sum", "plus", "minus", "multiply", "divide", "math", "equation"):
        return simple_calculator(text)

    if trigger_any(lower, "weather", "temperature"):
        return "I cannot check live weather, but I can help with temperature conversion, planning, or explain weather terms."

    if trigger_any(lower, "convert", "celsius", "fahrenheit"):
        return convert_temperature(text)

    if trigger_any(lower, "bmi", "body mass"):
        return bmi_info(text)

    if trigger_any(lower, "word count", "count words", "wordcount"):
        return word_count(text)

    if trigger_any(lower, "story", "write", "poem", "creative"):
        return "Here is a quick idea: 'The stars whispered to the night, and the moon answered with a silver smile.'"

    if trigger_any(lower, "task", "plan", "reminder", "todo", "schedule"):
        return to_do_list()

    if trigger_any(lower, "brainstorm", "idea", "suggestion"):
        ideas = [
            "Create a 30-minute focus block for your most important task.",
            "Write a short note about what makes you feel energized.",
            "Pick one skill to practice for 20 minutes today.",
            "Plan one meaningful conversation or act of kindness.",
        ]
        return random.choice(ideas)

    if trigger_any(lower, "flip coin", "coin toss"):
        return flip_coin()

    if trigger_any(lower, "roll dice", "dice"):
        return roll_dice()

    if trigger_any(lower, "news", "latest update"):
        return "I cannot access live news, but I can summarize a topic or help you research one quickly."

    if trigger_any(lower, "define", "meaning of", "what does"):
        word = re.sub(r".*?(define|meaning of|what does)\s+|\?+", "", lower).strip()
        if not word:
            return "Please give me a word to define, for example: 'define courage'."
        meanings = {
            "courage": "Mental strength to face fear or difficulty.",
            "focus": "The ability to direct attention to one task.",
            "success": "The achievement of a goal through effort and persistence.",
            "kindness": "Showing care and consideration toward others.",
        }
        return meanings.get(word, f"{word.title()} means a concept or idea that can be understood more clearly with context and examples.")

    if trigger_any(lower, "favorite color", "favorite food", "favorite movie", "favorite song"):
        return "I do not have personal tastes, but I can suggest ideas if you want a recommendation."

    if trigger_any(lower, "who created you", "created you", "made you"):
        return "I was created as a simple assistive program to help with conversations, tasks, and automation."

    if trigger_any(lower, "ai", "artificial intelligence"):
        return "Artificial intelligence helps automate repetitive work, interpret patterns, and support decision-making in many tasks."

    if trigger_any(lower, "language", "translate"):
        return "I can help with simple translations and explanations, but I do not translate full documents in real time without a dedicated tool."

    if trigger_any(lower, "study", "learn", "teach"):
        return "A great learning method is: focus on one concept, practice it, explain it in your own words, and review it again later."

    if trigger_any(lower, "goal", "goal setting", "plan my day"):
        return "Here is a simple goal plan: identify one main goal, set three small actions, and finish the most important one before noon."

    if trigger_any(lower, "remind me", "set alarm"):
        return "I can help with reminder ideas: 'Check email at 10:00', 'Drink water', or 'Finish the report before 5 PM.'"

    if trigger_any(lower, "health", "fitness", "exercise"):
        return "A good routine includes movement, hydration, sleep, and consistent healthy meals."

    if trigger_any(lower, "music", "song", "playlist"):
        return "A calm and focused playlist often includes instrumental, soft pop, or ambient tracks."

    if trigger_any(lower, "write note", "journal", "note"):
        return "Quick journal prompt: What did I do today that made me feel proud, and what can I improve tomorrow?"

    if trigger_any(lower, "search", "look up"):
        return "I can help summarize or explain a topic, but I do not browse the internet in real time unless connected to a web tool."

    if trigger_any(lower, "love", "relationship", "romance"):
        return "Love grows through trust, respect, simple gestures, and consistent care."

    if trigger_any(lower, "happy", "sad", "stress", "anxious"):
        return "Take a short breath, lower the noise, and focus on one small thing you can do next."

    if trigger_any(lower, "python", "code", "programming"):
        return "Python is a great language for automation, data work, and web projects. I can help with small scripts and logic ideas."

    return (
        "I understand you are asking about: "
        f"{text}. I can help with simple conversations, quick tasks, math, planning, and many daily assistance features."
    )


class AssistantHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(WEB_HTML.encode("utf-8"))
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "ai_ready": bool(AI_API_KEY)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", 0))
        payload = self.rfile.read(content_length)

        try:
            data = json.loads(payload.decode("utf-8"))
            prompt = data.get("prompt", "")
        except json.JSONDecodeError:
            prompt = ""

        reply = generate_response(prompt)

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps({"reply": reply, "voice": True}).encode("utf-8"))

    def log_message(self, format, *args):
        return


def start_web_server(host: str = "127.0.0.1", port: int = 8003):
    server = HTTPServer((host, port), AssistantHandler)
    print(f"Assistant live server running at http://{host}:{port}")
    if AI_API_KEY:
        print("AI API integration is active")
    else:
        print("AI API not configured. Local assistant mode is active.")
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Simple artificial assistant")
    parser.add_argument("prompt", nargs="?", help="Optional prompt to answer immediately")
    parser.add_argument("--server", action="store_true", help="Launch the assistant in a live browser server")
    parser.add_argument("--host", default="127.0.0.1", help="Host for the live server")
    parser.add_argument("--port", type=int, default=8003, help="Port for the live server")
    args = parser.parse_args()

    if args.server:
        start_web_server(args.host, args.port)
        return

    if args.prompt:
        print(generate_response(args.prompt))
        return

    print(greet_user())
    while True:
        try:
            user_input = input("You: ")
        except KeyboardInterrupt:
            print("\nAssistant: Goodbye!")
            break

        response = generate_response(user_input)
        print(f"Assistant: {response}")

        if any(word in user_input.lower() for word in ["bye", "goodbye", "exit", "quit"]):
            break


if __name__ == "__main__":
    main()


class AssistantHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(WEB_HTML.encode("utf-8"))
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", 0))
        payload = self.rfile.read(content_length)

        try:
            data = json.loads(payload.decode("utf-8"))
            prompt = data.get("prompt", "")
        except json.JSONDecodeError:
            prompt = ""

        reply = generate_response(prompt)

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps({"reply": reply}).encode("utf-8"))

    def log_message(self, format, *args):
        return


def start_web_server(host: str = "127.0.0.1", port: int = 8003):
    server = HTTPServer((host, port), AssistantHandler)
    print(f"Assistant live server running at http://{host}:{port}")
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Simple artificial assistant")
    parser.add_argument("prompt", nargs="?", help="Optional prompt to answer immediately")
    parser.add_argument("--server", action="store_true", help="Launch the assistant in a live browser server")
    parser.add_argument("--host", default="127.0.0.1", help="Host for the live server")
    parser.add_argument("--port", type=int, default=8003, help="Port for the live server")
    args = parser.parse_args()

    if args.server:
        start_web_server(args.host, args.port)
        return

    if args.prompt:
        print(generate_response(args.prompt))
        return

    print(greet_user())
    while True:
        try:
            user_input = input("You: ")
        except KeyboardInterrupt:
            print("\nAssistant: Goodbye!")
            break

        response = generate_response(user_input)
        print(f"Assistant: {response}")

        if any(word in user_input.lower() for word in ["bye", "goodbye", "exit", "quit"]):
            break


if __name__ == "__main__":
    main()
