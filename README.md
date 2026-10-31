# Company Policy Assistant

A free, locally powered comparison of three company-policy QA methods, with a Slack bot.

## Features
- Rules-based token keyword matching (no LLM tokens).
- LLM without vector search: sends all policy records to Ollama.
- LLM with vector index: Ollama embeddings, cosine similarity, top-3 retrieval, grounded generation.
- Actual local response latency and Ollama-reported token counts.
- Abstention instruction for questions outside the dataset.
- Slack app mentions using Socket Mode (no public server required).

## Prerequisites
- Python 3.10+
- Ollama installed locally (https://ollama.com/)
- Enough RAM for `llama3.2:3b` and `nomic-embed-text`.

## Start backend
```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
ollama pull llama3.2:3b
ollama pull nomic-embed-text
# Ensure Ollama is running (desktop app or `ollama serve`)
cd backend
uvicorn server:app --host 127.0.0.1 --port 8000
```

Open the GitHub Pages URL or open `docs/index.html` locally and enter a question. The page connects to `127.0.0.1:8000` on the viewer's machine, so **live LLM comparisons only work while the local backend is running**. The public page cannot provide live LLM responses to other visitors. For a universally live website, deploy a publicly accessible backend separately.

### GitHub Pages
In GitHub repository Settings -> Pages, set Deploy from branch, main, `/docs`. The URL is normally `https://YOUR_USERNAME.github.io/company-policy-assistant/` after GitHub finishes deployment. Do not claim the website is deployed before checking the link.

## Slack bot setup
1. Create a separate workspace and testing channel identifying you (e.g. `mathias-company-policy-test`). Invite `raz@sdu.dk` to the channel.
2. Create a Slack app at https://api.slack.com/apps, choose your workspace.
3. Enable **Socket Mode** and generate an app-level token with `connections:write` scope (`xapp-...`).
4. Under OAuth & Permissions, add bot token scopes `app_mentions:read` and `chat:write`; install the app to the workspace and copy the bot token (`xoxb-...`).
5. Under Event Subscriptions enable events and subscribe to `app_mention`. Invite your app to the testing channel.
6. Run the following in a separate terminal with the Python environment active and Ollama running:

   **PowerShell:**
   ```powershell
   $env:SLACK_BOT_TOKEN='xoxb-...'
   $env:SLACK_APP_TOKEN='xapp-...'
   python backend/slack_bot.py
   ```
   **macOS / Linux:**
   ```bash
   export SLACK_BOT_TOKEN='xoxb-...'
   export SLACK_APP_TOKEN='xapp-...'
   python backend/slack_bot.py
   ```
7. In the testing channel mention the app with a question, e.g. `@Policy Assistant How many days can employees work abroad?` Capture a screenshot showing the mention and the reply.

Never commit Slack tokens or secrets. `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN` are read from environment variables.

## Evaluation notes
The frontend shows **live** timings and token counts when the local server is available; no figures are fabricated. Rule-based token usage is 0; Ollama prompt and output token counts are counted for both LLM methods. Embedding token usage is not included in Ollama generation counts and should be recorded separately if required. The vector method's first request includes index construction, so warm-up before benchmarking and explicitly distinguish cold vs warm latency. An answer's support in the database must be **manually graded**; the UI does not pretend it can automatically detect hallucinations. Keyword matching can return an irrelevant policy: review all three outputs against source text.

## Assignment checklist
- [ ] GitHub repository created and code uploaded
- [ ] GitHub Pages enabled and site URL verified
- [ ] Local Ollama downloaded and comparison tested
- [ ] Manually evaluate unsupported answers using several policy and out-of-scope questions
- [ ] Separate Slack workspace/channel created and `raz@sdu.dk` invited
- [ ] Screenshot of bot mention and answer captured
- [ ] Two-paragraph comparison included on the website (already drafted; revise after measurements)