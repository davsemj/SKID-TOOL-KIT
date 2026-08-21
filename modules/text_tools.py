import re
import json
import xml.dom.minidom
import difflib
from collections import Counter
from utils.display import print_header, print_table, print_panel, print_syntax, print_success, print_error, print_warning, print_info
from utils.helpers import pause, prompt_input

def to_camel_case(s: str) -> str:
    words = re.split(r'[\s_\-]+', s.strip())
    return words[0].lower() + ''.join(w.capitalize() for w in words[1:]) if words else ""

def to_pascal_case(s: str) -> str:
    words = re.split(r'[\s_\-]+', s.strip())
    return ''.join(w.capitalize() for w in words)

def to_snake_case(s: str) -> str:
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', s)
    s = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s)
    return re.sub(r'[\s\-]+', '_', s).lower()

def to_kebab_case(s: str) -> str:
    return to_snake_case(s).replace('_', '-')

def to_dot_case(s: str) -> str:
    return to_snake_case(s).replace('_', '.')

def case_converter():
    """Converte texto para diversos estilos de casing."""
    print_header("Conversor de Casing (Nomenclatura)", "TEXTO")
    text = prompt_input("Digite o texto ou nome de variável a converter")
    if not text:
        return

    rows = [
        ["camelCase", to_camel_case(text)],
        ["PascalCase", to_pascal_case(text)],
        ["snake_case", to_snake_case(text)],
        ["kebab-case", to_kebab_case(text)],
        ["dot.case", to_dot_case(text)],
        ["UPPERCASE", text.upper()],
        ["lowercase", text.lower()],
        ["Title Case", text.title()],
    ]

    print_table(f"Variações de Casing para '{text}'", ["Estilo", "Resultado"], rows, style="cyan")
    pause()

def json_formatter_validator():
    """Formata e valida strings JSON."""
    print_header("Formatador & Validador de JSON", "TEXTO")
    print_info("Digite ou cole o conteúdo JSON:")
    raw_json = prompt_input("JSON")

    try:
        parsed = json.loads(raw_json)
        formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
        print_success("JSON Válido!")
        print_syntax(formatted, lexer="json", title="JSON Formatado")
    except json.JSONDecodeError as e:
        print_error(f"JSON Inválido: {e.msg} (Linha {e.lineno}, Coluna {e.colno})")

    pause()

def xml_formatter_validator():
    """Formata e valida strings XML."""
    print_header("Formatador & Validador de XML", "TEXTO")
    raw_xml = prompt_input("XML")

    try:
        dom = xml.dom.minidom.parseString(raw_xml)
        formatted = dom.toprettyxml(indent="  ")
        # Remove excess empty lines
        formatted = "\n".join([line for line in formatted.split("\n") if line.strip()])
        print_success("XML Válido!")
        print_syntax(formatted, lexer="xml", title="XML Formatado")
    except Exception as e:
        print_error(f"XML Inválido ou mal formatado: {e}")

    pause()

def regex_tester():
    """Testador interativo de Expressões Regulares (Regex)."""
    print_header("Testador de Expressões Regulares (Regex)", "TEXTO")
    pattern = prompt_input("Expressão Regular (ex: \\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b)")
    sample_text = prompt_input("Texto de teste para correspondência")

    if not pattern or not sample_text:
        return

    try:
        regex = re.compile(pattern)
        matches = list(regex.finditer(sample_text))
        
        if matches:
            print_success(f"{len(matches)} correspondência(s) encontrada(s)!")
            rows = []
            for idx, match in enumerate(matches, 1):
                start, end = match.span()
                match_val = match.group(0)
                groups = str(match.groups()) if match.groups() else "-"
                rows.append([str(idx), match_val, f"[{start}:{end}]", groups])
            print_table(f"Resultados para regex: {pattern}", ["#", "Match", "Posição", "Grupos"], rows, style="green")
        else:
            print_warning("Nenhuma correspondência encontrada no texto fornecido.")
    except re.error as e:
        print_error(f"Erro na sintaxe Regex: {e}")

    pause()

def analyze_text_statistics():
    """Calcula estatísticas avançadas de texto."""
    print_header("Analisador de Estatísticas de Texto", "TEXTO")
    text = prompt_input("Digite ou cole o texto para análise")
    if not text:
        return

    total_chars = len(text)
    chars_no_spaces = len(text.replace(" ", "").replace("\n", "").replace("\t", ""))
    words = re.findall(r'\b\w+\b', text.lower())
    total_words = len(words)
    lines = text.count('\n') + 1 if text else 0
    sentences = len(re.findall(r'[\.\?!]+', text)) or (1 if text else 0)
    
    # Estimativa de leitura (média de 200 palavras por minuto)
    reading_seconds = (total_words / 200) * 60

    stats_rows = [
        ["Total de Caracteres (com espaços)", f"{total_chars:,}"],
        ["Total de Caracteres (sem espaços)", f"{chars_no_spaces:,}"],
        ["Total de Palavras", f"{total_words:,}"],
        ["Total de Linhas", f"{lines:,}"],
        ["Total de Frases/Sentenças", f"{sentences:,}"],
        ["Comprimento Médio de Palavra", f"{(chars_no_spaces / total_words):.2f} caracteres" if total_words else "0"],
        ["Tempo Estimado de Leitura", f"{reading_seconds:.1f} segundos (~{max(1, round(reading_seconds/60))} min)"],
    ]

    print_table("Estatísticas Gerais", ["Métrica", "Valor"], stats_rows, style="magenta")

    if words:
        counter = Counter(words)
        top_words = counter.most_common(8)
        top_rows = [[word, f"{cnt}x ({cnt/total_words*100:.1f}%)"] for word, cnt in top_words]
        print_table("Palavras Mais Frequentes", ["Palavra", "Ocorrências"], top_rows, style="cyan")

    pause()

def compare_texts_diff():
    """Compara dois blocos de texto e exibe as diferenças."""
    print_header("Comparador de Textos (Diff)", "TEXTO")
    print_info("Digite o Texto Original (Linha A):")
    text_a = prompt_input("Original")
    print_info("Digite o Novo Texto Modificado (Linha B):")
    text_b = prompt_input("Modificado")

    lines_a = text_a.splitlines(keepends=True) or [text_a]
    lines_b = text_b.splitlines(keepends=True) or [text_b]

    diff = list(difflib.unified_diff(lines_a, lines_b, fromfile='Original', tofile='Modificado'))
    if diff:
        diff_text = "".join(diff)
        print_panel(diff_text, title="Diferenças Detectadas", style="yellow")
    else:
        print_success("Os dois textos são idênticos!")

    pause()

def text_menu():
    """Menu interativo de ferramentas de texto e dados."""
    while True:
        print_header("Ferramentas de Texto & Formatação", "TEXTO")
        options = [
            ("1", "🔤 Conversor de Casing (camelCase, snake_case, Pascal, etc.)"),
            ("2", "📋 Formatador & Validador de JSON"),
            ("3", "📑 Formatador & Validador de XML"),
            ("4", "🎯 Testador de Regex com Destaque"),
            ("5", "📊 Analisador de Estatísticas e Frequência de Palavras"),
            ("6", "🔍 Comparador de Textos (Diff)"),
            ("0", "⬅ Voltar ao Menu Principal"),
        ]
        print_table("Opções Disponíveis", ["Opção", "Descrição"], options, style="cyan")
        choice = prompt_input("Escolha uma opção").strip()

        if choice == "1":
            case_converter()
        elif choice == "2":
            json_formatter_validator()
        elif choice == "3":
            xml_formatter_validator()
        elif choice == "4":
            regex_tester()
        elif choice == "5":
            analyze_text_statistics()
        elif choice == "6":
            compare_texts_diff()
        elif choice == "0":
            break
        else:
            print_error("Opção inválida!")
