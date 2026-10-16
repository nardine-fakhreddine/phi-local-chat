# Local Gradio Chatbot (Ollama)

A small Gradio chat UI that talks to a **local** LLM through Ollama’s OpenAI-compatible API.

You do **not** need an OpenAI paid API key. The Python `openai` library is only used as a client. Requests go to `http://localhost:11434/v1` (Ollama on your machine).

This repo is the starting point of a RAG chatbot project. Right now it is a working local chat app. Retrieval (documents + embeddings) is not wired in yet.

---

## What this project does

1. You type a message in the Gradio browser UI.
2. Python sends the **system prompt + previous turns + new message** to Ollama.
3. Ollama runs a local model (currently `phi:latest`).
4. The reply is shown in the chat window.

```
Browser (Gradio)
    → gradio_chatbot.py
        → OpenAI Python SDK
            → http://localhost:11434/v1  (Ollama)
                → local model (phi)
```

---

## Prerequisites (install once)

Do these **before** creating the virtual environment.

### 1. Python 3.10+

This project was last run with **Python 3.14.7** on Windows.

Check:

```powershell
python --version
```

### 2. Git

Needed to clone or push this repo.

```powershell
git --version
```

### 3. Ollama (local model server)

1. Install from [https://ollama.com](https://ollama.com).
2. Make sure Ollama is **running** (on Windows it often runs in the system tray).
3. Pull a model. The code currently uses `phi:latest`:

```powershell
ollama pull phi
```

4. Confirm the exact name Ollama knows:

```powershell
ollama list
```

Copy the **NAME** column (for example `phi:latest` or `phi`). It must match `model=` in `gradio_chatbot.py`.

5. Optional smoke test:

```powershell
ollama run phi
```

Type a sentence. If it answers, the model works.

Ollama’s OpenAI-compatible endpoint is:

```text
http://localhost:11434/v1
```

---

## Setup from zero (every new machine)

Open PowerShell in the project folder:

```powershell
cd C:\Users\nardi\OneDrive\Desktop\Development\RAG-CHATBOT
```

Or after cloning from GitHub:

```powershell
git clone https://github.com/<YOUR_GITHUB_USERNAME>/RAG-CHATBOT.git
cd RAG-CHATBOT
```

### 1. Create a virtual environment

```powershell
python -m venv .venv
```

This creates `.venv\` in the project. **Do not commit `.venv`** (it is already in `.gitignore`).

### 2. Activate it

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks scripts:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again.

You should see `(.venv)` at the start of the prompt.

### 3. Install Python packages

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Installed versions (as of last working run):

| Package | Version | Why |
|---|---|---|
| `gradio` | 6.30.0 | Browser chat UI |
| `openai` | 3.31.0 | Client for Ollama’s OpenAI-style API |

### 4. Start the app

Ollama must already be running.

```powershell
python .\gradio_chatbot.py
```

Gradio prints a local URL, usually:

```text
http://127.0.0.1:7860
```

Open that in the browser. Type a message, click **Send**. **Clear Chat** resets the transcript.

Stop the app with `Ctrl+C` in the terminal.

If you change `gradio_chatbot.py`, restart the app. Gradio does not always reload Python changes.

---

## Project layout

```text
RAG-CHATBOT/
├── gradio_chatbot.py   # Only application file: UI + Ollama call
├── requirements.txt    # Python dependencies
├── README.md           # This guide
└── .gitignore          # Keeps .venv, cache, and secrets out of Git
```

There is no `.env` yet. The dummy key `nokeyneeded` is only there because the OpenAI SDK requires *some* `api_key` string. Ollama ignores it.

---

## How `gradio_chatbot.py` works

### Client

```python
client = openai.OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="nokeyneeded",
)
```

- `base_url` sends traffic to Ollama, not api.openai.com.
- To use real OpenAI later: remove the custom `base_url`, put a real key in an environment variable, and change `model=` to something like `gpt-4o`.

### Chat turn

`chat_with_openai(message, history)`:

1. `history` is Gradio’s transcript: a list of `{"role": "user"|"assistant", "content": "..."}` dicts.
2. Build `conversation`:
   - system prompt
   - `conversation.extend(history)` — previous turns, one message each
   - the new user message
3. Call `client.chat.completions.create(...)`.
4. Read the reply with **`response.choices[0].message.content`** (attribute, not `["content"]`).
5. Return the updated history and `""` so the text box clears.

### UI

- `gr.Chatbot(..., type="messages")` is required on Gradio 6.
- **Send** runs `chat_with_openai`.
- **Clear Chat** returns an empty list and an empty input.

### `append` vs `extend` (easy to forget)

- `list.append(x)` adds **one** item (if `x` is a list, you nest a list inside a list).
- `list.extend(x)` adds **each item** from `x`.

Use `extend(history)` so each past message stays a separate dict for the API.

---

## Common errors (already hit on this project)

### `TypeError: 'ChatCompletionMessage' object is not subscriptable`

Wrong:

```python
response.choices[0].message['content']
```

Right (OpenAI Python SDK v1+):

```python
response.choices[0].message.content
```

### `Data incompatible with messages format`

Old Gradio used tuples: `("User", "hello")`.

Current Gradio Chatbot wants:

```python
{"role": "user", "content": "hello"}
{"role": "assistant", "content": "hi"}
```

Fix: `gr.Chatbot(type="messages")` and store history as those dicts.

### `openai.NotFoundError: model 'phi:latest' not found`

Ollama does not have that tag. Run:

```powershell
ollama list
```

Then either:

```powershell
ollama pull phi
```

or change `model=` in `gradio_chatbot.py` to an exact name from `ollama list`.

### Connection errors / 404 on the API

Ollama is not running, or the URL is wrong. Start Ollama, then confirm:

```powershell
curl http://localhost:11434/api/tags
```

### Gradio still shows old behavior

The process was not restarted after editing the file. Stop with `Ctrl+C` and run `python .\gradio_chatbot.py` again.

---

## Daily workflow (short)

```powershell
cd C:\Users\nardi\OneDrive\Desktop\Development\RAG-CHATBOT
.\.venv\Scripts\Activate.ps1
# make sure Ollama is running
python .\gradio_chatbot.py
```

Open http://127.0.0.1:7860

---

## Pushing to GitHub (after the repo exists)

```powershell
git add .
git status          # confirm .venv is NOT listed
git commit -m "Your message"
git push
```

Never commit `.venv`, API keys, or `.env`.

---

## Next steps toward RAG

When you come back to this later, typical RAG pieces still missing:

1. Load documents (PDF, markdown, text).
2. Split into chunks.
3. Embed chunks and store them (Chroma, FAISS, etc.).
4. On each question: retrieve the top chunks, put them in the prompt, then call the model.

The chat UI and Ollama client in `gradio_chatbot.py` can stay as the generation layer.

---

## License

Personal / learning project. Add a license file if you want others to reuse it.
