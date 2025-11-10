# -*- coding: utf-8 -*-
"""
BayiiAİ CLI — Gemini 2.5 Flash tabanlı sohbet ve kod üretimi
Komutlar:
  bayiiai chat
  bayiiai code "istek" --lang py --outfile script.py
"""
from __future__ import annotations

import os
import re
import sys
import json
from pathlib import Path
from datetime import datetime

import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.text import Text
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:
    print("google-generativeai paketi kurulu değil. Lütfen: pip install google-generativeai")
    sys.exit(1)

# stdout'u UTF-8'e sabitle (Windows için önemli)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()

APP_DIR = Path.home() / ".bayiiai"
SESS_DIR = APP_DIR / "sessions"
SESS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_MODEL = os.getenv("GAI_MODEL", "gemini-2.0-flash")

def _load_env():
    # Çalışma dizinindeki .env + HOME\.env (varsa) yükle
    load_dotenv(dotenv_path=Path.cwd() / ".env", override=False)
    home_env = Path.home() / ".env"
    if home_env.exists():
        load_dotenv(dotenv_path=home_env, override=False)

def _get_api_key() -> str | None:
    _load_env()
    return os.getenv("GOOGLE_API_KEY")

def _get_model_id(model: str | None) -> str:
    return model or os.getenv("GAI_MODEL", DEFAULT_MODEL)

def _ensure_model(model_id: str) -> genai.GenerativeModel:
    api_key = _get_api_key()
    if not api_key:
        console.print(
            Panel(
                Text(
                    "GOOGLE_API_KEY bulunamadı.\n\n"
                    "• Proje klasörüne veya %USERPROFILE%\\.env içine:\n"
                    "  GOOGLE_API_KEY=ANAHTARINIZ\n"
                    "• İsterseniz PowerShell ile kalıcı ayarlayın:\n"
                    "  setx GOOGLE_API_KEY \"ANAHTAR\"\n\n"
                    "Sonra terminali kapatıp açın.",
                    style="yellow",
                ),
                title="API Anahtarı Gerekli",
                border_style="red",
            )
        )
        sys.exit(2)
    genai.configure(api_key=api_key)
    try:
        return genai.GenerativeModel(model_id)
    except Exception as e:
        console.print(Panel(f"Model başlatılamadı: [red]{e}[/red]\nModel ID: [bold]{model_id}[/bold]", border_style="red"))
        sys.exit(3)

def _session_path(name: str) -> Path:
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "_", name.strip()) or "default"
    return SESS_DIR / f"{safe}.jsonl"

def _load_history(name: str) -> list[dict]:
    path = _session_path(name)
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    history: list[dict] = []
    for line in lines:
        try:
            history.append(json.loads(line))
        except Exception:
            continue
    return history

def _append_history(name: str, message: dict) -> None:
    path = _session_path(name)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(message, ensure_ascii=False) + "\n")

def _clear_history(name: str) -> None:
    path = _session_path(name)
    if path.exists():
        path.unlink()

def _extract_code(text: str) -> tuple[str, str | None]:
    """
    Üçlü backtick içindeki kodu ve dil etiketini ayıklar.
    Bulamazsa tüm metni kod olarak döner.
    """
    fence = re.search(r"```(\w+)?\s*\n(.*?)```", text, re.DOTALL)
    if fence:
        lang = fence.group(1)
        code = fence.group(2).strip("\n")
        return code, (lang or None)
    return text.strip(), None

_EXT_BY_LANG = {
    "python": "py", "py": "py",
    "javascript": "js", "js": "js", "node": "js", "tsx": "tsx",
    "typescript": "ts", "ts": "ts",
    "html": "html", "css": "css",
    "java": "java", "csharp": "cs", "cs": "cs",
    "cpp": "cpp", "c++": "cpp", "c": "c",
    "go": "go", "rust": "rs", "ruby": "rb", "rb": "rb",
    "kotlin": "kt", "swift": "swift",
    "php": "php", "sql": "sql",
    "bash": "sh", "sh": "sh", "powershell": "ps1", "ps1": "ps1",
    "json": "json", "yaml": "yml", "yml": "yml",
    "dart": "dart", "lua": "lua", "r": "r",
}

def _ensure_outfile(outfile: Path | None, lang_hint: str | None) -> Path | None:
    if outfile:
        parent = outfile.parent
        parent.mkdir(parents=True, exist_ok=True)
        return outfile
    return None

# --------------------------
# Komut: chat (etkileşimli)
# --------------------------
@app.command(help="Etkileşimli sohbet (Gemini 2.5 Flash)")
def chat(
    session: str = typer.Option("default", "--session", "-s", help="Oturum adı (geçmiş kaydı için)"),
    model: str = typer.Option(None, "--model", "-m", help=f"Model ID (varsayılan: {DEFAULT_MODEL})"),
    temperature: float = typer.Option(0.6, "--temp", help="Yaratıcılık (0.0–1.0)"),
    markdown: bool = typer.Option(True, "--markdown/--no-markdown", help="Yanıtı Markdown olarak render et")
):
    model_id = _get_model_id(model)
    gm = _ensure_model(model_id)

    history = _load_history(session)
    chat = gm.start_chat(history=history)

    console.print(Panel(Text(f"BayiiAİ — {model_id}\n\n/exit ile çık, /clear ile geçmişi sıfırla.", justify="center"), border_style="cyan", title="Sohbet"))

    while True:
        user_msg = Prompt.ask("[bold cyan]👤 Sen[/bold cyan]")
        if not user_msg.strip():
            continue
        if user_msg.strip() == "/exit":
            console.print("[green]Görüşürüz![/green]")
            break
        if user_msg.strip() == "/clear":
            _clear_history(session)
            chat = gm.start_chat(history=[])
            console.print("[yellow]Oturum geçmişi sıfırlandı.[/yellow]")
            continue

        # Tarihli kullanıcı mesajını kaydet
        user_entry = {"role": "user", "parts": [{"text": user_msg}], "ts": datetime.utcnow().isoformat()}
        _append_history(session, user_entry)

        try:
            response = chat.send_message(
                user_msg,
                generation_config={"temperature": float(temperature)}
            )
            text = getattr(response, "text", "") or ""
        except Exception as e:
            console.print(Panel(f"[red]İstek başarısız:[/red] {e}", border_style="red"))
            continue

        # Model cevabını yazdır + kaydet
        if markdown:
            console.print(Markdown(text))
        else:
            console.print(text)

        model_entry = {"role": "model", "parts": [{"text": text}], "ts": datetime.utcnow().isoformat()}
        _append_history(session, model_entry)

# --------------------------
# Komut: code (yalnızca kod)
# --------------------------
@app.command(help="Prompt'tan yalnızca KOD üretir; istersen dosyaya kaydeder.")
def code(
    prompt: str = typer.Argument(..., help="Ne yazmasını istiyorsun? (örn: 'Flask ile basit API yaz')"),
    lang: str = typer.Option(None, "--lang", "-l", help="Dil ipucu (py, js, ts, html, css, vb.)"),
    outfile: Path = typer.Option(None, "--outfile", "-o", help="Çıktı kod dosyası yolu (örn: app.py)")
):
    model_id = _get_model_id(None)
    gm = _ensure_model(model_id)

    system_hint = (
        "You are a coding assistant. Return ONLY one fenced code block. "
        "Do not include explanations, comments, or extra text outside the fence. "
        "Prefer runnable, minimal, production-ready code."
    )
    full_prompt = f"{system_hint}\n\nUser request:\n{prompt}"

    try:
        resp = gm.generate_content(
            full_prompt,
            generation_config={"temperature": 0.2}
        )
        text = getattr(resp, "text", "") or ""
    except Exception as e:
        console.print(Panel(f"[red]Kod üretimi başarısız:[/red] {e}", border_style="red"))
        raise typer.Exit(code=4)

    code_text, detected_lang = _extract_code(text)
    picked_lang = (lang or detected_lang or "").lower().strip() or None

    dest = _ensure_outfile(outfile, picked_lang)
    if dest is None and picked_lang and not outfile:
        # Dosya adı verilmediyse dil uzantısına göre öneri
        ext = _EXT_BY_LANG.get(picked_lang, "txt")
        dest = None  # terminale basacağız

    if dest:
        dest.write_text(code_text, encoding="utf-8")
        console.print(Panel(f"Kod kaydedildi: [bold]{dest}[/bold]", border_style="green"))
    else:
        # Terminale yalın kod
        console.print(Panel(Markdown(f"```{picked_lang or ''}\n{code_text}\n```"), title="Üretilen Kod", border_style="green"))
        # İstersen sadece ham metni bas:
        # console.print(code_text)

if __name__ == "__main__":
    app()
