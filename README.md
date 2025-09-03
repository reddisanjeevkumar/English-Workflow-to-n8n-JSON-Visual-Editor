# n8n Workflow generator and Visual Editor

This project lets you **describe a workflow in plain English** (e.g. "Start, fetch user data, send email") and instantly converts it into a [n8n](https://n8n.io/) workflow JSON, which you can edit and visualize using [React Flow](https://reactflow.dev/).

## Features

- **Natural Language Workflow Input:**  
  Write step-by-step instructions in English.
- **Automatic n8n Workflow Generation:**  
  The backend parses your description and returns a valid n8n workflow JSON.
- **Visual Editor:**  
  Drag, connect, and edit nodes visually in a flowchart.
- **JSON Editing:**  
  Directly edit the workflow JSON in a code editor.
- **Downloadable Workflows:**  
  Save your workflow JSON for use in n8n or sharing.

## How It Works

1. **Describe your workflow in English** in the left panel textarea.
2. **Click "Generate Workflow"** to send your description to the backend API.
3. The API returns a n8n-style workflow JSON, which is:
    - Rendered as a visual flowchart (React Flow)
    - Editable as raw JSON
4. You can:
    - **Edit nodes visually**
    - **Edit the JSON directly**
    - **Download the workflow JSON**

## Example

**Input (English):**
```
Start, fetch user data, send email to user
```

**Produces (JSON):**
```json
{
  "nodes": [
    { "id": "start", "type": "n8n-nodes-base.manualTrigger", "position": { "x": 50, "y": 50 } },
    { "id": "httpGetUser", "type": "n8n-nodes-base.httpRequest", "position": { "x": 250, "y": 50 } },
    { "id": "jsonParseUser", "type": "n8n-nodes-base.jsonParse", "position": { "x": 450, "y": 50 } },
    { "id": "emailSend", "type": "n8n-nodes-base.email", "position": { "x": 650, "y": 50 } }
  ],
  "connections": {
    "start": { "main": [[{ "node": "httpGetUser", "input": "main" }]] },
    "httpGetUser": { "main": [[{ "node": "jsonParseUser", "input": "main" }]] },
    "jsonParseUser": { "main": [[{ "node": "emailSend", "input": "main" }]] }
  }
}
```
<img width="663" height="663" alt="Screenshot 2025-09-03 at 10 33 50 PM" src="https://github.com/user-attachments/assets/b314557e-04c1-47c1-be62-c369d82da0e9" />
<img width="663" height="646" alt="Screenshot 2025-09-03 at 10 34 53 PM" src="https://github.com/user-attachments/assets/26c6b8d0-f91e-4f6b-ba60-f208dd90dcac" />
<img width="663" height="647" alt="Screenshot 2025-09-03 at 10 39 52 PM" src="https://github.com/user-attachments/assets/fb1ec11a-1e9b-4063-9360-987013675b95" />




**Visual Editor:**  
The workflow above is displayed as a flowchart. You can drag nodes, edit them, or change the connections.

## Usage

### 1. Write your workflow in English
Type instructions in the "English Workflow Description" box.

### 2. Generate workflow
Click **"Generate Workflow"**. The backend creates the JSON.

### 3. Edit the workflow
- **Visually:** Move and connect nodes in the diagram.
- **Directly:** Edit the JSON in the "Edit Workflow JSON" box.

### 4. Download JSON
Click **"Download JSON"** to save your workflow.

## Tech Stack

- **Frontend:** React, [React Flow](https://reactflow.dev/)
- **Backend:** (Your own API for English → n8n JSON)

## Development

```bash
npm install
npm start
```
The frontend expects a backend at `http://localhost:5000/api/generate-workflow` that accepts:
```json
{ "description": "your english workflow description" }
```
and returns n8n workflow JSON.

## Integration with n8n

- Download your JSON
- Import into your n8n editor (or use via API)

# Tools and Dependencies Required for backend api

To run the `generate_workflow.py` file (the Flask API for English to n8n workflow JSON), you will need the following tools and Python packages:

## 1. Python

- **Version:** Python 3.7 or above is recommended.

## 2. Python Packages

Install these using `pip install ...`:

- **Flask** — for the web API
- **flask_cors** — to allow cross-origin requests from your frontend
- **requests** — for making HTTP requests to LLM APIs
- **demjson3** — (optional, used for robust JSON parsing; can be omitted if not needed)
- **os, re, json** — part of Python standard library

### Install all necessary packages:

```bash
pip install flask flask-cors requests demjson3
```

## 3. LLM Backend

You need at least one LLM backend running and accessible:

### a. Ollama

- **URL:** Configurable via `OLLAMA_URL` env variable (default: `http://localhost:11434/api/generate`)
- **How to run:** See [Ollama docs](https://ollama.com/) for setup

### b. OpenAI

- **API Key:** Set `OPENAI_API_KEY` in your environment
- **API Endpoint:** Default is `https://api.openai.com/v1/chat/completions`
- **How to get API key:** [OpenAI docs](https://platform.openai.com/docs/overview)

## 4. Environment Variables

Set the following environment variables as needed:

- `OLLAMA_URL` — (optional) the URL to your Ollama instance
- `OPENAI_API_KEY` — (required for OpenAI mode) your OpenAI API key
- `OPENAI_API_URL` — (optional) override the default OpenAI endpoint
- `OLLAMA_DEFAULT_MODEL` — (optional) default Ollama model (e.g. "llama3")
- `OPENAI_DEFAULT_MODEL` — (optional) default OpenAI model (e.g. "gpt-3.5-turbo")
- `DEFAULT_ENGINE` — (optional) default engine ("ollama" or "openai")
- `PORT` — (optional) port for Flask (default: 5000)

You can set these in your shell or in a `.env` file (with [python-dotenv](https://pypi.org/project/python-dotenv/)).

## 5. Running

Start the Flask server:

```bash
python generate_workflow.py
```

By default, it runs on `http://localhost:5000`.

---

## Summary Table

| Tool/Package   | Purpose                         | Install/Configure     |
|----------------|---------------------------------|----------------------|
| Python         | Language runtime                | [python.org](https://www.python.org/) |
| Flask          | REST API server                 | `pip install flask`  |
| flask_cors     | Allow CORS for frontend         | `pip install flask-cors` |
| requests       | HTTP requests                   | `pip install requests` |
| demjson3       | Robust JSON parsing (optional)  | `pip install demjson3` |
| Ollama         | Local LLM backend (optional)    | [Ollama docs](https://ollama.com/) |
| OpenAI API Key | Cloud LLM backend (optional)    | [OpenAI docs](https://platform.openai.com/docs/overview) |

---

## License

MIT

## Credits

- [n8n](https://n8n.io/)
- [React Flow](https://reactflow.dev/)
