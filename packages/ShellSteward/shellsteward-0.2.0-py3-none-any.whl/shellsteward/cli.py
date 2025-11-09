from typing import Optional
import typer, requests
import questionary
import re
import json, os
import pyperclip
from rich.console import Console
from rich.spinner import Spinner


from shellsteward.ShellSteward_ai import retrieve_command, build_index  # ✅ correct




from enum import Enum


ServiceURL = "https://api.deepseek.com/chat/completions"
API_KEY = "AIzaSyDR5hCQmJXsLJabtkMKP-EH4-JkB15xeE0"      

CONFIG_PATH = ".catalyst.json"
History_PATH = ".catalyst_history.txt"




app = typer.Typer(invoke_without_command=True)
console = Console()







def save_config(data):
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f)

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def save_history(command):
    with open(History_PATH, "a") as f:
        f.write(command + "\n")

def load_history():
    if os.path.exists(History_PATH):
        with open(History_PATH) as f:
            return f.read().strip().split("\n---\n")
    return []


def extract_first_command(text):
    blocks = re.findall(r"```(?:bash|cmd|powershell)?\n(.*?)\n```", text, re.DOTALL)
    if blocks:
        return blocks[0].strip().split('\n')[0]
    inline = re.findall(r"`(cd.*?)`", text)
    if inline:
        return inline[0].strip()
    return "No command found."


def start_free_trial(config):
    config["owner"] = "Me"
    config["api_key"] = API_KEY
    save_config(config)
    typer.echo("Free trial started. You can use the service now.")



def detect_shell():
    shell = os.environ.get("SHELL") or os.environ.get("COMSPEC")
    if shell:
        if "bash" in shell:
            return "bash"
        elif "zsh" in shell:
            return "zsh"
        elif "powershell" in shell.lower():
            return "powershell"
        elif "cmd" in shell.lower():
            return "cmd"
    return "unknown"



@app.command()
def version():
    """Display the version of Catalyst."""
    typer.echo("Catalyst version 0.1")
    typer.echo("Author: Lucifer")
    typer.echo("License: MIT")

def extract_command(text: str) -> str:
    match = re.search(r"Command:\s*(.+)", text)
    return match.group(1).strip() if match else "No command found."

@app.command()
def history(copy: Optional[bool] = typer.Option(False, help="Copy history to clipboard")):
    """Display the command history."""
    history = load_history()

    if not history:
        typer.echo("No history found.")
        return
    
    
    command = extract_command(history[-1]) if history else "No command found."

    if copy:
        try:
            pyperclip.copy(command)
            typer.echo("History copied to clipboard.")
            return
        except ImportError:
            typer.echo("pyperclip module not found. Please install it to use this feature.")
            return
    
    typer.echo("Last 10 commands from history:")
    typer.echo()

    for entry in history[-10:]:
        print(entry, end="\n---\n")

@app.command()
def init():
    global ServiceURL, API_KEY  # ✅ Declare globals first

    service = questionary.select(
        "Choose your Service",
        choices=[ "Gemini", "GPT-4", "ShellSteward AI(Beta)" ]
    ).ask()

    if service is None:
        typer.echo("No service selected. Exiting.")
        return
    
    if service == "ShellSteward AI(Beta)":
        typer.echo("You have selected ShellSteward AI as your service.")
        typer.echo("No API key is required for ShellSteward AI.")
        typer.echo()
        typer.echo("It is still in Beta version so it might not find some commands. It will improve over time with more data.")
        typer.echo("You can start using the 'ask' command to interact with ShellSteward AI.")
        config = {
            "service": service,
            "api_key": "N/A"
        }
        save_config(config)
        return

    config ={
        "service": service

    }

    if service == "Deepseek":
        ServiceURL = "https://api.deepseek.ai/v1/"
    elif service == "Gemini":
        ServiceURL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    elif service == "GPT-4":
        ServiceURL = "https://api.gpt-4.ai/v1/"

    config["service_url"] = ServiceURL

    typer.echo(f"You have selected {service} as your service.")
    typer.echo()
    typer.echo("Now, you are supposed to get an API key from the service provider. You can get one from the below link 👇")
    typer.echo(f"{ServiceURL}")
    typer.echo("If you don't have one, you can start a free trial.")
    typer.echo()

    key = questionary.select(
        "Choose your key option:",
        choices=["Have a key", "Start a free trial"]
    ).ask()

    if key == "Have a key":
        API_KEY = questionary.text("Please enter your API key:").ask()
        config["api_key"] = API_KEY
        save_config(config)
    else:

        if service != "Gemini":
            typer.echo("Free trial is only available for Gemini service.")
            return

        start_free_trial(config)
        typer.echo("Starting a free trial... (This is a placeholder action)")


@app.command()
def greet(name: str):
    """Greet a person by their name."""
    typer.echo(f"Hello, {name}!")



@app.command()
def find(
    name: str = typer.Argument(...),
    path: str = typer.Option(".", help="Directory to search"),
    include_files: bool = typer.Option(True),
    include_folders: bool = typer.Option(True)
):
    found = False
    search_name = name.lower()
    # your os.walk logic here
    for root, dirs, files in os.walk(path):
        if include_folders:
            for d in dirs:
                if search_name in d.lower():
                    typer.echo(f"Found folder: {os.path.join(root, d)}")
                    found = True
        if include_files:
            for f in files:
                if search_name in f.lower():
                    typer.echo(f"Found file: {os.path.join(root, f)}")
                    found = True
    if not found:
        typer.echo("File/Folder not found.")


def handle_shellsteward(prompt, config, trial_used):
    with console.status("[bold green]Thinking...[/]", spinner="dots"):
        data = build_index()
        response = retrieve_command(prompt, data)
        command = response["command"]

    typer.echo(f"\nHere is the command generated:\n{command}\n")
    save_history(f"Prompt: {prompt}\nCommand: {command}\n---\n")

    option = questionary.select(
        "What would you like to do next?",
        choices=["Execute", "Copy to Clipboard", "Want an explanation ?", "Exit"]
    ).ask()

    if option == "Execute":
        os.system(command)
    elif option == "Copy to Clipboard":
        pyperclip.copy(command)
        print("Command copied to clipboard.")
    elif option == "Want an explanation ?":
        typer.echo(response["explanation"])
    elif option == "Exit":
        typer.echo("Goodbye!")


def handle_remote_service(service, final_prompt, config, api_key, trial_used, prompt):
    if service == "GPT-4":
        url = "https://api.openai.com/v1/responses"
        headers = {
            "Content-Type": "application/json",
            "Authorization": api_key
        }
        payload = {
            "model": "gpt-5-nano",
            "input": final_prompt,
            "store": True
        }
    else:  # Gemini
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }
        payload = {
            "contents": [{"parts": [{"text": final_prompt}]}]
        }

    with console.status("[bold green]Thinking...[/]", spinner="dots"):
        response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            full_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            command = extract_first_command(full_text)
            typer.echo(f"\nHere is the command generated:\n{command}\n")

            config["trial_used"] = trial_used + 1
            save_config(config)
            save_history(f"Prompt: {prompt}\nCommand: {command}\n---\n")

            option = questionary.select(
                "What would you like to do next?",
                choices=["Execute", "Copy to Clipboard", "Want an explanation ?", "Exit"]
            ).ask()

            if option == "Execute":
                os.system(command)
            elif option == "Copy to Clipboard":
                pyperclip.copy(command)
                print("Command copied to clipboard.")
            elif option == "Want an explanation ?":
                typer.echo(full_text)
            elif option == "Exit":
                typer.echo("Goodbye!")

        except Exception as e:
            typer.echo("Error parsing response.")
            typer.echo(str(e))
    else:
        print("Error:", response.status_code)
        print(response.text)


def handle_local_find(raw_prompt):
    with console.status("[bold green]Finding...[/]", spinner="dots"):
        tokens = raw_prompt.split()
        for i, token in enumerate(tokens):
            if token in ["file", "folder"] and i + 1 < len(tokens):
                name = tokens[i + 1]
                return find(name=name, path=".", include_files=True, include_folders=True)
        typer.echo("Couldn't extract file/folder name. Try: 'Find file .env'")


@app.command()
def ask(prompt_parts: list[str] = typer.Argument(..., help="The prompt to send to the AI.")):
    """Generate a shell command from a natural language prompt."""
    raw_prompt = " ".join(prompt_parts).strip().lower()

    # 🔍 Handle file/folder search locally
    if any(kw in raw_prompt for kw in ["find file", "locate file", "search for file", "find folder", "locate folder"]):
        return handle_local_find(raw_prompt)

    prompt = " ".join(prompt_parts)
    if not prompt:
        typer.echo("Please enter a prompt.")
        raise typer.Exit()

    shell = detect_shell()
    shell_hint = f"Give me the shell command for {shell} only. Do not include other shells."
    final_prompt = f"{prompt}\n{shell_hint}"

    config = load_config()
    service = config.get("service", "Gemini")
    api_key = config.get("api_key", API_KEY)
    trial_used = config.get("trial_used", 0)
    owner = config.get("owner", "User")

    if trial_used >= 5 and owner == "Me":
        typer.echo("You have reached the maximum number of trials.")
        typer.echo("Please obtain a full API key to continue using the service.")
        return

    if service == "ShellSteward AI(Beta)":
        return handle_shellsteward(prompt, config, trial_used)

    return handle_remote_service(service, final_prompt, config, api_key, trial_used, prompt)

@app.command()
def doctor():
    from shellsteward.ShellSteward_ai import load_commands
    try:
        data = load_commands()
        typer.echo(f"✅ Loaded {len(data)} commands from commands.json")
    except Exception as e:
        typer.echo(f"❌ Error loading commands.json: {e}")

# @app.callback()
# def fallback(ctx: typer.Context):
#     if ctx.invoked_subcommand is None:
#         if ctx.args:
#             # Treat unknown command as prompt
#             prompt = " ".join(ctx.args)
#             ask(*ctx.args)
#         else:
#             typer.echo("Please enter a prompt or use --help.")


def main():
    config = load_config()
    if not config.get("api_key"):
        init()
    app()  # launch Typer CLI


if __name__ == "__main__":
    main()



