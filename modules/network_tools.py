import socket
import concurrent.futures
import time
import urllib.request
import json
from utils.display import print_header, print_table, print_panel, print_success, print_error, print_warning, print_info, show_spinner
from utils.helpers import pause, prompt_input, prompt_int

COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 6379: "Redis",
    8000: "HTTP-Alt", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 27017: "MongoDB"
}

def scan_single_port(host: str, port: int, timeout: float = 0.8) -> tuple:
    """Verifica se uma porta específica está aberta."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((host, port))
            if result == 0:
                service = COMMON_PORTS.get(port, "Desconhecido")
                return (port, True, service)
    except Exception:
        pass
    return (port, False, "")

def run_port_scanner():
    """Scanner de portas multithreaded ultrarrápido."""
    print_header("Port Scanner Multithreaded", "REDE")
    target = prompt_input("Host ou IP de destino (ex: scanme.nmap.org, 127.0.0.1)", default="127.0.0.1")
    
    print_info("Opções de portas:")
    print(" 1 - Portas mais comuns (Top 18 portas)")
    print(" 2 - Intervalo personalizado (ex: 1 a 1024)")
    print(" 3 - Lista específica de portas (ex: 80,443,8080)")
    mode = prompt_input("Selecione o modo", default="1")

    ports_to_scan = []
    if mode == "1":
        ports_to_scan = sorted(list(COMMON_PORTS.keys()))
    elif mode == "2":
        start_p = prompt_int("Porta inicial", min_val=1, max_val=65535, default=1)
        end_p = prompt_int("Porta final", min_val=start_p, max_val=65535, default=1000)
        ports_to_scan = list(range(start_p, end_p + 1))
    elif mode == "3":
        ports_raw = prompt_input("Digite as portas separadas por vírgula", default="80,443,3000,8080")
        for p in ports_raw.split(","):
            if p.strip().isdigit():
                ports_to_scan.append(int(p.strip()))
    else:
        ports_to_scan = sorted(list(COMMON_PORTS.keys()))

    if not ports_to_scan:
        print_error("Nenhuma porta válida selecionada.")
        pause()
        return

    try:
        ip_addr = socket.gethostbyname(target)
        print_info(f"Iniciando varredura em {target} ({ip_addr}) - {len(ports_to_scan)} portas...")
    except socket.gaierror:
        print_error(f"Não foi possível resolver o host '{target}'.")
        pause()
        return

    open_ports = []
    start_time = time.perf_counter()

    max_workers = min(100, len(ports_to_scan))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scan_single_port, ip_addr, p): p for p in ports_to_scan}
        for future in concurrent.futures.as_completed(futures):
            port, is_open, service = future.result()
            if is_open:
                open_ports.append([str(port), "ABERTA", service])

    scan_duration = time.perf_counter() - start_time

    if open_ports:
        open_ports.sort(key=lambda x: int(x[0]))
        print_table(f"Portas Abertas em {target} ({len(open_ports)} encontradas)", ["Porta", "Estado", "Serviço Provável"], open_ports, style="green")
    else:
        print_warning(f"Nenhuma porta aberta encontrada dentre as {len(ports_to_scan)} testadas.")

    print_info(f"Varredura concluída em {scan_duration:.2f} segundos.")
    pause()

def run_ping_latency_test():
    """Mede a latência e estabilidade da conexão para um host."""
    print_header("Teste de Latência & Conectividade", "REDE")
    target = prompt_input("Host ou IP de destino (ex: 8.8.8.8, google.com)", default="8.8.8.8")
    port = prompt_int("Porta para conexão TCP (ex: 80 para HTTP, 53 para DNS, 443 para HTTPS)", min_val=1, max_val=65535, default=80)
    count = prompt_int("Quantidade de pacotes/tentativas", min_val=1, max_val=30, default=5)

    try:
        ip = socket.gethostbyname(target)
        print_info(f"Testando latência com {target} ({ip}:{port})...")
    except Exception as e:
        print_error(f"Erro ao resolver host: {e}")
        pause()
        return

    latencies = []
    lost = 0

    for i in range(count):
        t_start = time.perf_counter()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2.0)
                s.connect((ip, port))
                latency_ms = (time.perf_counter() - t_start) * 1000
                latencies.append(latency_ms)
                print(f"  Resposta de {ip}: tempo = {latency_ms:.2f} ms")
        except Exception:
            lost += 1
            print(f"  Esgotado o tempo limite de resposta para tentativa {i + 1}.")
        time.sleep(0.3)

    if latencies:
        min_l = min(latencies)
        max_l = max(latencies)
        avg_l = sum(latencies) / len(latencies)
        loss_pct = (lost / count) * 100

        rows = [
            ["Pacotes Enviados", str(count)],
            ["Pacotes Recebidos", str(len(latencies))],
            ["Perda de Pacotes", f"{lost} ({loss_pct:.1f}%)"],
            ["Latência Mínima", f"{min_l:.2f} ms"],
            ["Latência Média", f"{avg_l:.2f} ms"],
            ["Latência Máxima", f"{max_l:.2f} ms"],
        ]
        print_table(f"Estatísticas de Latência para {target}", ["Métrica", "Valor"], rows, style="cyan")
    else:
        print_error("Todos os pacotes falharam ou o host não aceita conexões nesta porta.")

    pause()

def lookup_my_ip():
    """Consulta IP Local e IP Público com Geolocalização."""
    print_header("Meu Endereço IP & Localização", "REDE")
    show_spinner("Consultando dados de rede local e remota...", 0.5)

    # IP Local
    local_ip = "127.0.0.1"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
    except Exception:
        pass

    hostname = socket.gethostname()

    # IP Público
    public_ip = "Indisponível"
    city, region, country, org, timezone = ["N/D"] * 5

    try:
        req = urllib.request.Request("https://ipapi.co/json/", headers={"User-Agent": "Toolkit-CLI/1.0"})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode('utf-8'))
            public_ip = data.get("ip", "N/D")
            city = data.get("city", "N/D")
            region = data.get("region", "N/D")
            country = f"{data.get('country_name', 'N/D')} ({data.get('country_code', '')})"
            org = data.get("org", "N/D")
            timezone = data.get("timezone", "N/D")
    except Exception:
        try:
            req2 = urllib.request.Request("https://api.ipify.org?format=json", headers={"User-Agent": "Toolkit-CLI/1.0"})
            with urllib.request.urlopen(req2, timeout=3) as resp2:
                d2 = json.loads(resp2.read().decode('utf-8'))
                public_ip = d2.get("ip", "N/D")
        except Exception:
            pass

    rows = [
        ["Nome do Host Local", hostname],
        ["IP Local (Rede Interna)", local_ip],
        ["IP Público (Internet)", public_ip],
        ["Cidade / Região", f"{city}, {region}"],
        ["País", country],
        ["Provedor de Internet (ISP/Org)", org],
        ["Fuso Horário", timezone]
    ]

    print_table("Informações de Rede & Localização", ["Propriedade", "Valor"], rows, style="magenta")
    pause()

def inspect_http_headers():
    """Inspeciona cabeçalhos HTTP e informações de resposta de qualquer URL."""
    print_header("Inspetor de Cabeçalhos HTTP", "REDE")
    url = prompt_input("URL para inspeção (ex: https://example.com)", default="https://example.com")
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    show_spinner(f"Conectando a {url}...", 0.4)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        start_t = time.perf_counter()
        with urllib.request.urlopen(req, timeout=6) as resp:
            elapsed = (time.perf_counter() - start_t) * 1000
            status_code = resp.status
            reason = resp.reason
            headers = resp.getheaders()

            print_success(f"Status: {status_code} {reason} (Tempo de resposta: {elapsed:.2f} ms)")

            header_rows = [[k, v] for k, v in headers]
            print_table(f"Cabeçalhos Retornados por {url}", ["Cabeçalho (Header)", "Valor"], header_rows, style="green")

    except urllib.error.HTTPError as e:
        print_warning(f"Resposta HTTP com Erro: {e.code} {e.reason}")
        if e.headers:
            header_rows = [[k, v] for k, v in e.headers.items()]
            print_table(f"Cabeçalhos Retornados no Erro {e.code}", ["Cabeçalho", "Valor"], header_rows, style="yellow")
    except Exception as e:
        print_error(f"Falha ao conectar na URL: {e}")

    pause()

def network_menu():
    """Menu interativo de ferramentas de rede."""
    while True:
        print_header("Ferramentas de Rede & Conectividade", "REDE")
        options = [
            ("1", "📡 Port Scanner Multithreaded"),
            ("2", "📶 Teste de Latência & Ping"),
            ("3", "🌍 Meu Endereço IP & Geolocalização"),
            ("4", "🔍 Inspetor de Cabeçalhos HTTP & URLs"),
            ("0", "⬅ Voltar ao Menu Principal"),
        ]
        print_table("Opções Disponíveis", ["Opção", "Descrição"], options, style="cyan")
        choice = prompt_input("Escolha uma opção").strip()

        if choice == "1":
            run_port_scanner()
        elif choice == "2":
            run_ping_latency_test()
        elif choice == "3":
            lookup_my_ip()
        elif choice == "4":
            inspect_http_headers()
        elif choice == "0":
            break
        else:
            print_error("Opção inválida!")
            time.sleep(1)
