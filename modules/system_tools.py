import os
import sys
import platform
import shutil
import time
import tempfile
from utils.display import print_header, print_table, print_panel, print_success, print_error, print_info, show_spinner
from utils.helpers import pause, prompt_input, prompt_int, format_bytes, format_duration

def get_system_uptime() -> str:
    """Obtém o tempo de atividade (uptime) do sistema."""
    try:
        if sys.platform == "win32":
            import ctypes
            kernel32 = ctypes.windll.kernel32
            uptime_ms = kernel32.GetTickCount64()
            return format_duration(uptime_ms / 1000)
        else:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                return format_duration(uptime_seconds)
    except Exception:
        return "Indisponível"

def get_memory_info() -> dict:
    """Obtém informações de memória RAM."""
    try:
        if sys.platform == "win32":
            import ctypes
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            total = stat.ullTotalPhys
            avail = stat.ullAvailPhys
            used = total - avail
            load = stat.dwMemoryLoad
            return {
                "total": format_bytes(total),
                "used": format_bytes(used),
                "free": format_bytes(avail),
                "percent": f"{load}%"
            }
    except Exception:
        pass
    return {"total": "N/D", "used": "N/D", "free": "N/D", "percent": "N/D"}

def show_system_info():
    """Exibe painel com especificações completas do sistema."""
    print_header("Informações do Sistema", "SISTEMA")
    show_spinner("Coletando informações de hardware e SO...", 0.5)

    mem = get_memory_info()
    cpu_count = os.cpu_count() or "N/D"
    uptime = get_system_uptime()

    sys_rows = [
        ["Sistema Operacional", f"{platform.system()} {platform.release()} ({platform.version()})"],
        ["Arquitetura da CPU", f"{platform.machine()} ({platform.architecture()[0]})"],
        ["Processador", platform.processor() or "Desconhecido"],
        ["Núcleos de CPU", f"{cpu_count} lógicos"],
        ["Memória RAM Total", mem["total"]],
        ["Memória RAM Usada", f"{mem['used']} ({mem['percent']})"],
        ["Memória RAM Livre", mem["free"]],
        ["Tempo de Atividade (Uptime)", uptime],
        ["Nome do Computador (Hostname)", platform.node()],
        ["Versão do Python", f"{platform.python_version()} ({platform.python_implementation()})"],
        ["Caminho do Python", sys.executable],
    ]

    print_table("Especificações do Sistema & Hardware", ["Parâmetro", "Valor"], sys_rows, style="cyan")

    # Informações de Armazenamento
    disk_rows = []
    if sys.platform == "win32":
        import string
        available_drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
        for drive in available_drives:
            try:
                usage = shutil.disk_usage(drive)
                percent = (usage.used / usage.total) * 100
                disk_rows.append([
                    drive,
                    format_bytes(usage.total),
                    format_bytes(usage.used),
                    format_bytes(usage.free),
                    f"{percent:.1f}%"
                ])
            except Exception:
                continue
    else:
        try:
            usage = shutil.disk_usage("/")
            percent = (usage.used / usage.total) * 100
            disk_rows.append([
                "/",
                format_bytes(usage.total),
                format_bytes(usage.used),
                format_bytes(usage.free),
                f"{percent:.1f}%"
            ])
        except Exception:
            pass

    if disk_rows:
        print_table("Discos e Armazenamento", ["Unidade", "Total", "Usado", "Livre", "% Uso"], disk_rows, style="green")

    pause()

def run_disk_benchmark():
    """Realiza um teste rápido de velocidade de leitura e escrita de disco."""
    print_header("Benchmark de Disco (I/O)", "SISTEMA")
    print_info("Este teste grava e lê um arquivo temporário para medir a velocidade de escrita/leitura do seu disco.")
    
    size_mb = prompt_int("Tamanho do arquivo de teste em MB (recomendado: 50 a 200)", min_val=10, max_val=1000, default=50)
    data = os.urandom(1024 * 1024) # 1 MB chunk

    temp_dir = tempfile.gettempdir()
    test_file = os.path.join(temp_dir, f"toolkit_benchmark_{int(time.time())}.tmp")

    try:
        # Teste de Escrita
        show_spinner(f"Gravando {size_mb} MB no disco ({test_file})...", 0.2)
        start_write = time.perf_counter()
        with open(test_file, "wb") as f:
            for _ in range(size_mb):
                f.write(data)
            f.flush()
            os.fsync(f.fileno())
        write_time = time.perf_counter() - start_write
        write_speed = size_mb / write_time

        # Teste de Leitura
        show_spinner(f"Lendo {size_mb} MB do disco...", 0.2)
        start_read = time.perf_counter()
        with open(test_file, "rb") as f:
            while f.read(1024 * 1024):
                pass
        read_time = time.perf_counter() - start_read
        read_speed = size_mb / read_time

        rows = [
            ["Velocidade de Escrita", f"{write_speed:.2f} MB/s", f"{write_time:.3f} s"],
            ["Velocidade de Leitura", f"{read_speed:.2f} MB/s", f"{read_time:.3f} s"],
            ["Tamanho Testado", f"{size_mb} MB", "-"],
            ["Diretório de Teste", temp_dir, "-"]
        ]

        print_table("Resultados do Benchmark de I/O", ["Operação", "Velocidade", "Tempo Total"], rows, style="magenta")
        print_success("Benchmark concluído com sucesso!")

    except Exception as e:
        print_error(f"Falha ao executar benchmark: {e}")
    finally:
        if os.path.exists(test_file):
            try:
                os.remove(test_file)
            except Exception:
                pass

    pause()

def show_env_variables():
    """Lista e permite buscar variáveis de ambiente."""
    print_header("Variáveis de Ambiente", "SISTEMA")
    filter_query = prompt_input("Filtrar por nome (ou pressione Enter para ver todas)").lower()

    rows = []
    for k, v in sorted(os.environ.items()):
        if not filter_query or filter_query in k.lower() or filter_query in v.lower():
            val_display = v if len(v) <= 60 else v[:57] + "..."
            rows.append([k, val_display])

    if rows:
        print_table(f"Variáveis de Ambiente ({len(rows)} encontradas)", ["Variável", "Valor"], rows, style="yellow")
    else:
        print_error("Nenhuma variável de ambiente corresponde ao filtro.")

    pause()

def system_menu():
    """Menu interativo de ferramentas de sistema."""
    while True:
        print_header("Ferramentas de Sistema", "SISTEMA")
        options = [
            ("1", "📊 Especificações Completas do Sistema & Hardware"),
            ("2", "⚡ Benchmark de Velocidade de Disco (I/O)"),
            ("3", "🔍 Visualizador de Variáveis de Ambiente"),
            ("0", "⬅ Voltar ao Menu Principal"),
        ]
        print_table("Opções Disponíveis", ["Opção", "Descrição"], options, style="cyan")
        choice = prompt_input("Escolha uma opção").strip()

        if choice == "1":
            show_system_info()
        elif choice == "2":
            run_disk_benchmark()
        elif choice == "3":
            show_env_variables()
        elif choice == "0":
            break
        else:
            print_error("Opção inválida!")
            time.sleep(1)
