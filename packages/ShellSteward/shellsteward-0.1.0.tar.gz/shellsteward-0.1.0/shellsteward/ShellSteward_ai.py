import os
from sentence_transformers import SentenceTransformer
import faiss, json, numpy as np
from rich.console import Console
from rich.spinner import Spinner

import importlib.resources

def load_commands():
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, "data", "commands.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

console = Console()

with console.status("[bold green]Loading...[/]", spinner="dots"):
    model = SentenceTransformer("all-MiniLM-L6-v2")

    def build_index():
        data = load_commands()
        prompts = [entry["prompt"] for entry in data]
        embeddings = model.encode(prompts)
        index = faiss.IndexFlatL2(384)
        index.add(np.array(embeddings))

    # ✅ Ensure the 'index' directory exists
        os.makedirs("index", exist_ok=True)

        faiss.write_index(index, "index/faiss.index")
        return data

def retrieve_command(query: str, data):
    index = faiss.read_index("index/faiss.index")
    query_vec = model.encode([query])
    D, I = index.search(np.array(query_vec), k=1)
    return data[I[0][0]]