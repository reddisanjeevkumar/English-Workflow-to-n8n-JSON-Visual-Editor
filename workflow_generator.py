import requests
import os
import re
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import demjson3

# Take configuration from environment variables
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OPENAI_API_URL = os.environ.get("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OLLAMA_DEFAULT_MODEL = os.environ.get("OLLAMA_DEFAULT_MODEL", "qwen3:8b")
OPENAI_DEFAULT_MODEL = os.environ.get("OPENAI_DEFAULT_MODEL", "gpt-3.5-turbo")
DEFAULT_ENGINE = os.environ.get("DEFAULT_ENGINE", "ollama")

def extract_json_from_llm_output(raw_output):
    raw_output = re.sub(r"<think>[\s\S]*?</think>", "", raw_output)
    raw_output = re.sub(r"[\s\S]*?</think>", "", raw_output)
    match = re.search(r"\{[\s\S]*\}", raw_output.strip())
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except Exception as e:
            print("Error parsing JSON:", e)
            return None
    else:
        print("No JSON object found.")
        return None

def autofix_n8n_workflow(raw_json):
    import copy
    workflow = copy.deepcopy(raw_json)
    for idx, node in enumerate(workflow.get('nodes', [])):
        if 'id' not in node or not node['id']:
            node['id'] = str(idx + 1)
        pos = node.get('position')
        if pos is None or not isinstance(pos, (list, tuple)) or len(pos) != 2:
            node['position'] = [80 + idx * 160, 120]
    node_ids = [node['id'] for node in workflow.get('nodes', [])]
    fixed_connections = {}
    for key, arr in workflow.get('connections', {}).items():
        if isinstance(arr, dict) and "main" in arr:
            fixed_connections[key] = arr
        else:
            try:
                src_idx = node_ids.index(key)
            except ValueError:
                src_idx = None
            next_node_id = node_ids[src_idx + 1] if src_idx is not None and src_idx + 1 < len(node_ids) else None
            corrected_conn = []
            for conn in arr:
                if (isinstance(conn, dict) and conn.get("node") == "to") or (isinstance(conn, str) and conn == "to"):
                    target_id = next_node_id
                else:
                    target_id = conn.get("node") if isinstance(conn, dict) else conn
                corrected_conn.append({
                    "node": target_id,
                    "input": conn.get("input", "main") if isinstance(conn, dict) else "main"
                })
            fixed_connections[key] = {
                "main": [corrected_conn]
            }
    workflow["connections"] = fixed_connections
    return workflow

def prompt_n8n_json(description, engine=None, model=None):
    engine = engine or DEFAULT_ENGINE
    if engine == "ollama":
        model = model or OLLAMA_DEFAULT_MODEL
    elif engine == "openai":
        model = model or OPENAI_DEFAULT_MODEL
    else:
        # fallback to ollama
        engine = "ollama"
        model = OLLAMA_DEFAULT_MODEL

    system_prompt = (
        "You are an expert n8n workflow automation engineer. "
        "Given a plain English description, output a strictly valid n8n workflow JSON. "
        "Requirements:\n"
        " - Each node must have an 'id', a 'type', and a 'position' field (example: {x:80, y:120}) a 'name' it should be unique for each node.\n"
        " - The 'connections' object must use node 'id' only, never 'to', 'next', or similar. "
        " - For each node except the last, connect its output to the next node in the nodes array using its id.\n"
        " - The format for 'connections' is: {\"sourceNodeId\": {\"main\": [[{ \"node\": \"targetNodeId\", \"input\": \"main\" }]]}, ... }\n"
        " - Use only double quotes for property names and values.\n"
        " - Do not include any explanation, comments, or markdown, only return the pure JSON object that can be parsed by json.loads in Python.\n"
    )
    user_prompt = f"Workflow description:\n{description}\n\nOutput the n8n workflow JSON."

    if engine == "ollama":
        payload = {
            "model": model,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False
        }
        resp = requests.post(OLLAMA_URL, json=payload)
        resp.raise_for_status()
        result = resp.json()["response"]
    else:
        if not OPENAI_API_KEY:
            raise Exception("OPENAI_API_KEY environment variable not set")
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1
        }
        resp = requests.post(OPENAI_API_URL, headers=headers, json=payload)
        resp.raise_for_status()
        result = resp.json()["choices"][0]["message"]["content"]

    match = re.search(r"\{[\s\S]*\}", result)
    if match:
        workflow_json = extract_json_from_llm_output(result)
    else:
        print("No JSON object found in response.")
        workflow_json = None

    return workflow_json

app = Flask(__name__)
CORS(app)

@app.route("/api/generate-workflow", methods=["POST"])
def api_generate_workflow():
    data = request.get_json(force=True)
    description = data.get("description", "")
    engine = data.get("engine") or DEFAULT_ENGINE
    model = data.get("model")
    workflow_json = prompt_n8n_json(description, engine=engine, model=model)
    if workflow_json:
        print("\n===== Final workflow_json =====\n", json.dumps(workflow_json, indent=2), "\n==============================\n")
        return jsonify(workflow_json)
    else:
        return jsonify({"error": "Failed to generate workflow JSON."}), 500

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), debug=True)
