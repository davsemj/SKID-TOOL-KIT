import uuid
import time
import datetime
import random
import json
import urllib.request
import urllib.error
from utils.display import print_header, print_table, print_panel, print_syntax, print_success, print_error, print_warning, print_info, show_spinner
from utils.helpers import pause, prompt_input, prompt_int

def generate_uuids():
    """Gerador de identificadores universais únicos (UUIDs)."""
    print_header("Gerador de UUIDs", "DEV TOOLS")
    qty = prompt_int("Quantidade de UUIDs a gerar", min_val=1, max_val=50, default=5)
    uppercase = prompt_input("Letras maiúsculas? (s/n)", default="n").lower() == 's'
    remove_hyphens = prompt_input("Remover hífens? (s/n)", default="n").lower() == 's'

    rows = []
    for i in range(qty):
        u = str(uuid.uuid4())
        if uppercase:
            u = u.upper()
        if remove_hyphens:
            u = u.replace("-", "")
        rows.append([str(i + 1), u])

    print_table("UUIDs v4 Gerados", ["#", "UUID"], rows, style="green")
    pause()

def timestamp_converter():
    """Conversor bidirecional de Timestamp Unix / Epoch."""
    print_header("Conversor de Timestamp Unix / Epoch", "DEV TOOLS")
    now_ts = int(time.time())
    now_dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print_panel(f"Timestamp Atual (Segundos): {now_ts}\nTimestamp Atual (Milissegundos): {int(time.time() * 1000)}\nData Local Atual: {now_dt}", title="Horário Atual", style="cyan")

    print(" 1 - Converter Timestamp Unix para Data/Hora Legível")
    print(" 2 - Converter Data/Hora para Timestamp Unix")
    choice = prompt_input("Escolha", default="1")

    if choice == "1":
        ts_input = prompt_input("Digite o Timestamp Unix (ex: 1718000000)", default=str(now_ts))
        try:
            ts_val = float(ts_input)
            if ts_val > 1e11: # Milissegundos
                ts_val /= 1000.0
            
            dt_local = datetime.datetime.fromtimestamp(ts_val)
            dt_utc = datetime.datetime.fromtimestamp(ts_val, tz=datetime.timezone.utc)

            rows = [
                ["Timestamp Fornecido", str(ts_input)],
                ["Horário Local", dt_local.strftime("%d/%m/%Y %H:%M:%S (%A)")],
                ["Horário UTC (ISO 8601)", dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")],
            ]
            print_table("Resultado da Conversão", ["Formato", "Data / Hora"], rows, style="green")
        except Exception as e:
            print_error(f"Timestamp inválido: {e}")

    else:
        dt_input = prompt_input("Digite a Data/Hora no formato 'AAAA-MM-DD HH:MM:SS' (ex: 2026-12-31 23:59:59)")
        try:
            parsed_dt = datetime.datetime.strptime(dt_input.strip(), "%Y-%m-%d %H:%M:%S")
            ts = int(parsed_dt.timestamp())
            rows = [
                ["Data Informada", dt_input],
                ["Timestamp Unix (Segundos)", str(ts)],
                ["Timestamp Unix (Milissegundos)", str(ts * 1000)],
            ]
            print_table("Resultado da Conversão", ["Formato", "Valor"], rows, style="green")
        except Exception as e:
            print_error(f"Formato de data inválido (use AAAA-MM-DD HH:MM:SS): {e}")

    pause()

def http_api_client():
    """Mini Cliente HTTP / Tester de API."""
    print_header("Mini Cliente HTTP / API Tester", "DEV TOOLS")
    url = prompt_input("URL da API (ex: https://httpbin.org/get)", default="https://httpbin.org/get")
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    print("Métodos HTTP: 1-GET, 2-POST, 3-PUT, 4-DELETE")
    m_choice = prompt_input("Método", default="1")
    methods = {"1": "GET", "2": "POST", "3": "PUT", "4": "DELETE"}
    method = methods.get(m_choice, "GET")

    headers = {
        "User-Agent": "Power-Toolkit/1.0",
        "Accept": "application/json"
    }

    custom_head = prompt_input("Adicionar cabeçalho customizado? (Formato: Chave:Valor ou deixe vazio)")
    if ":" in custom_head:
        k, v = custom_head.split(":", 1)
        headers[k.strip()] = v.strip()

    body_data = None
    if method in ["POST", "PUT"]:
        body_input = prompt_input("Payload JSON para o corpo da requisição (ex: {\"teste\": 123})")
        if body_input:
            body_data = body_input.encode('utf-8')
            headers["Content-Type"] = "application/json"

    show_spinner(f"Enviando requisição {method} para {url}...", 0.4)
    start_t = time.perf_counter()

    try:
        req = urllib.request.Request(url, data=body_data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=10) as resp:
            elapsed = (time.perf_counter() - start_t) * 1000
            resp_body = resp.read().decode('utf-8', errors='replace')
            status = resp.status
            reason = resp.reason

            print_success(f"Resposta {status} {reason} recebida em {elapsed:.2f} ms")

            # Tenta exibir como JSON formatado se possível
            try:
                parsed_json = json.loads(resp_body)
                print_syntax(json.dumps(parsed_json, indent=2, ensure_ascii=False), lexer="json", title="Corpo da Resposta (JSON)")
            except Exception:
                print_panel(resp_body if len(resp_body) < 1500 else resp_body[:1490] + "\n...", title="Corpo da Resposta", style="cyan")

    except urllib.error.HTTPError as e:
        elapsed = (time.perf_counter() - start_t) * 1000
        print_warning(f"Erro HTTP {e.code} ({e.reason}) em {elapsed:.2f} ms")
        err_body = e.read().decode('utf-8', errors='replace')
        if err_body:
            print_panel(err_body[:1000], title="Corpo do Erro", style="yellow")
    except Exception as e:
        print_error(f"Falha na requisição: {e}")

    pause()

def generate_valid_cpf() -> str:
    """Gera um número de CPF válido com cálculo de dígitos verificadores."""
    digits = [random.randint(0, 9) for _ in range(9)]
    # 1º dígito
    s1 = sum(d * w for d, w in zip(digits, range(10, 1, -1)))
    d1 = (s1 * 10 % 11) % 10
    digits.append(d1)
    # 2º dígito
    s2 = sum(d * w for d, w in zip(digits, range(11, 1, -1)))
    d2 = (s2 * 10 % 11) % 10
    digits.append(d2)
    s = ''.join(map(str, digits))
    return f"{s[:3]}.{s[3:6]}.{s[6:9]}-{s[9:]}"

def generate_mock_data():
    """Gerador de dados fictícios para testes e desenvolvimento."""
    print_header("Gerador de Dados Fictícios / Mock Data", "DEV TOOLS")
    print(" 1 - Gerador de Pessoas (Nome, E-mail, CPF Válido, Telefone, Cidade)")
    print(" 2 - Gerador de Texto Lorem Ipsum")
    choice = prompt_input("Escolha", default="1")

    first_names = ["Lucas", "Gabriel", "Matheus", "Felipe", "Juliana", "Mariana", "Beatriz", "Camila", "Rodrigo", "Larissa", "Bruno", "Amanda", "Thiago", "Fernanda", "Rafael"]
    last_names = ["Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Almeida", "Pereira", "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho", "Melo"]
    domains = ["email.com", "teste.com.br", "techdev.io", "empresa.com", "cloudcorp.net"]
    cities = [("São Paulo", "SP"), ("Rio de Janeiro", "RJ"), ("Belo Horizonte", "MG"), ("Curitiba", "PR"), ("Porto Alegre", "RS"), ("Salvador", "BA"), ("Brasília", "DF"), ("Recife", "PE")]

    if choice == "1":
        qty = prompt_int("Quantidade de perfis a gerar", min_val=1, max_val=20, default=5)
        rows = []
        for i in range(qty):
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            full_name = f"{fn} {ln}"
            email = f"{fn.lower()}.{ln.lower()}{random.randint(10,99)}@{random.choice(domains)}"
            cpf = generate_valid_cpf()
            phone = f"({random.randint(11, 99)}) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            city, state = random.choice(cities)
            rows.append([full_name, email, cpf, phone, f"{city}/{state}"])

        print_table("Perfis Fictícios Gerados (Para Testes)", ["Nome Completo", "E-mail", "CPF", "Telefone", "Localidade"], rows, style="green")

    else:
        lorem_words = [
            "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit",
            "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore",
            "magna", "aliqua", "enim", "ad", "minim", "veniam", "quis", "nostrud",
            "exercitation", "ullamco", "laboris", "nisi", "ut", "aliquip", "ex", "ea",
            "commodo", "consequat", "duis", "aute", "irure", "in", "reprehenderit"
        ]
        paragraphs_count = prompt_int("Quantidade de parágrafos", min_val=1, max_val=10, default=2)
        paragraphs = []
        for _ in range(paragraphs_count):
            sentences = []
            for _ in range(random.randint(4, 7)):
                words = [random.choice(lorem_words) for _ in range(random.randint(8, 15))]
                sentence = " ".join(words).capitalize() + "."
                sentences.append(sentence)
            paragraphs.append(" ".join(sentences))

        full_lorem = "\n\n".join(paragraphs)
        print_panel(full_lorem, title="Lorem Ipsum Gerado", style="cyan")

    pause()

def dev_menu():
    """Menu interativo de ferramentas de desenvolvimento."""
    while True:
        print_header("Ferramentas para Desenvolvedores", "DEV TOOLS")
        options = [
            ("1", "🆔 Gerador de UUIDs v4 (Únicos ou em Lote)"),
            ("2", "⏰ Conversor de Timestamp Unix / Epoch"),
            ("3", "🌐 Mini Cliente HTTP / API Tester (GET, POST, etc.)"),
            ("4", "🎭 Gerador de Dados Fictícios / Mock Data & Lorem Ipsum"),
            ("0", "⬅ Voltar ao Menu Principal"),
        ]
        print_table("Opções Disponíveis", ["Opção", "Descrição"], options, style="cyan")
        choice = prompt_input("Escolha uma opção").strip()

        if choice == "1":
            generate_uuids()
        elif choice == "2":
            timestamp_converter()
        elif choice == "3":
            http_api_client()
        elif choice == "4":
            generate_mock_data()
        elif choice == "0":
            break
        else:
            print_error("Opção inválida!")
