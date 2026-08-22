import os
import sys
import time

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.align import Align
    from rich.syntax import Syntax
    from rich.progress import Progress, SpinnerColumn, TextColumn
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None

# Banner estilizado NETHER na cor vermelha
SKID_BANNER = r"""
 ██████╗██╗  ██╗██╗██████╗ 
██╔════╝██║ ██╔╝██║██╔══██╗
╚█████╗ █████╔╝ ██║██║  ██║
 ╚═══██╗██╔═██╗ ██║██║  ██║
██████╔╝██║  ██╗██║██████╔╝
╚═════╝ ╚═╝  ╚═╝╚═╝╚═════╝ 

"""

VERSION = "2026"

def clear_screen():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner(subtitle: str = ""):
    """Exibe o banner skid em vermelho."""
    if HAS_RICH:
        # Banner NETHER em vermelho vivo
        banner_text = Text(SKID_BANNER, style="bold red")
        console.print(Align.center(banner_text))
        
        if subtitle:
            sub = Text(f"🔥 {subtitle.upper()} 🔥", style="bold red on white")
            console.print(Align.center(sub))
            console.print(Align.center(Text("━" * 55, style="bold red")))
            print()
    else:
        print(SKID_BANNER)
        if subtitle:
            print(f"=== {subtitle.upper()} ===")
            print("=" * 55)

def print_header(title: str, category: str = "SKID"):
    """Exibe cabeçalho de seção."""
    clear_screen()
    show_banner(f"{category} ➔ {title}")

def print_success(message: str):
    """Exibe mensagem de sucesso."""
    if HAS_RICH:
        console.print(f"[bold red on white] ✔ SUCESSO [/bold red on white] [bold white]{message}[/bold white]")
    else:
        print(f"[+] SUCESSO: {message}")

def print_error(message: str):
    """Exibe mensagem de erro."""
    if HAS_RICH:
        console.print(f"[bold white on red] ✘ ERRO [/bold white on red] [bold red]{message}[/bold red]")
    else:
        print(f"[-] ERRO: {message}")

def print_warning(message: str):
    """Exibe mensagem de alerta."""
    if HAS_RICH:
        console.print(f"[bold red]▲ AVISO:[/bold red] [white]{message}[/white]")
    else:
        print(f"[!] AVISO: {message}")

def print_info(message: str):
    """Exibe mensagem informativa."""
    if HAS_RICH:
        console.print(f"[bold white]ℹ INFO:[/bold white] [bold red]{message}[/bold red]")
    else:
        print(f"[*] INFO: {message}")

def print_panel(content: str, title: str = "", style: str = "red"):
    """Exibe um painel estilizado com bordas vermelhas e texto branco."""
    if HAS_RICH:
        console.print(Panel(
            f"[bold white]{content}[/bold white]",
            title=f"[bold white on red] {title} [/bold white on red]" if title else "",
            border_style="bold red",
            expand=False
        ))
    else:
        print(f"\n--- {title} ---")
        print(content)
        print("-" * (len(title) + 8))

def print_table(title: str, columns: list, rows: list, style: str = "red"):
    """Exibe uma tabela com estilo Vermelho e Branco do skid."""
    if HAS_RICH:
        table = Table(
            title=f"[bold white on red] {title} [/bold white on red]",
            border_style="bold red",
            header_style="bold white on red",
            title_style="bold white",
            show_lines=True
        )
        for col in columns:
            if isinstance(col, tuple):
                name, justify = col
                table.add_column(f"[bold white]{name}[/bold white]", justify=justify)
            else:
                table.add_column(f"[bold white]{str(col)}[/bold white]")
        for row in rows:
            formatted_cells = []
            for idx, cell in enumerate(row):
                if idx == 0:
                    formatted_cells.append(f"[bold red]{cell}[/bold red]")
                else:
                    formatted_cells.append(f"[white]{cell}[/white]")
            table.add_row(*formatted_cells)
        console.print(table)
    else:
        print(f"\n=== {title} ===")
        header_line = " | ".join(str(c[0] if isinstance(c, tuple) else c) for c in columns)
        print(header_line)
        print("-" * len(header_line))
        for row in rows:
            print(" | ".join(str(cell) for cell in row))
        print()

def print_syntax(code: str, lexer: str = "json", title: str = ""):
    """Exibe código com syntax highlighting em tema escuro com painel vermelho."""
    if HAS_RICH:
        syntax = Syntax(code, lexer, theme="monokai", line_numbers=True)
        if title:
            console.print(Panel(syntax, title=f"[bold white on red] {title} [/bold white on red]", border_style="bold red"))
        else:
            console.print(syntax)
    else:
        if title:
            print(f"\n--- {title} ---")
        print(code)

def show_spinner(text: str, duration: float = 0.8):
    """Exibe um spinner de carregamento vermelho."""
    if HAS_RICH:
        with Progress(
            SpinnerColumn(spinner_name="dots", style="bold red"),
            TextColumn("[bold red]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description=text, total=None)
            time.sleep(duration)
    else:
        print(f"{text}...")
        time.sleep(duration)
