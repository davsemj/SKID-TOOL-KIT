import sys
import os
from .display import HAS_RICH

if HAS_RICH:
    from rich.prompt import Prompt, IntPrompt
    from rich.console import Console
    console = Console()
else:
    console = None

def pause(msg: str = "Pressione [ENTER] para continuar..."):
    """Pausa a execução aguardando o usuário pressionar Enter."""
    print()
    if HAS_RICH:
        console.print(f"[bold red on white] {msg} [/bold red on white]", end="")
    else:
        print(msg, end="")
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        print()

def prompt_input(prompt_text: str = "", default: str = "") -> str:
    """Solicita texto ao usuário com prompt no estilo (root@skid) >."""
    if HAS_RICH:
        if prompt_text:
            p_str = f"[bold red](root@skid)[/bold red] [white]({prompt_text})[/white] [bold red]>[/bold red]"
        else:
            p_str = "[bold red](root@skid)[/bold red] [bold red]>[/bold red]"
        
        if default:
            return Prompt.ask(p_str, default=default)
        return Prompt.ask(p_str)
    else:
        label = f"(root@skid) ({prompt_text}) > " if prompt_text else "(root@skid) > "
        if default:
            val = input(f"{label}[{default}]: ").strip()
            return val if val else default
        return input(label).strip()

def prompt_int(prompt_text: str, min_val: int = None, max_val: int = None, default: int = None) -> int:
    """Solicita número inteiro validado ao usuário."""
    while True:
        try:
            if HAS_RICH:
                p_str = f"[bold red](root@skid)[/bold red] [white]({prompt_text})[/white] [bold red]>[/bold red]"
                if default is not None:
                    val = IntPrompt.ask(p_str, default=default)
                else:
                    val = IntPrompt.ask(p_str)
            else:
                d_str = f" [{default}]" if default is not None else ""
                raw = input(f"(root@skid) ({prompt_text}){d_str} > ").strip()
                if not raw and default is not None:
                    return default
                val = int(raw)

            if min_val is not None and val < min_val:
                print(f"O valor deve ser no mínimo {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"O valor deve ser no máximo {max_val}.")
                continue
            return val
        except (ValueError, TypeError):
            print("Por favor, digite um número inteiro válido.")
        except (KeyboardInterrupt, EOFError):
            return default if default is not None else 0

def format_bytes(num_bytes: float) -> str:
    """Formata bytes em unidade legível (KB, MB, GB, TB)."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:3.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} EB"

def format_duration(seconds: float) -> str:
    """Formata segundos em texto amigável (dias, horas, minutos, segundos)."""
    seconds = int(seconds)
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return " ".join(parts)
