import hashlib
import itertools
import string
import os
import time

from utils.display import (
    print_header, print_table, print_panel, print_success,
    print_error, print_warning, print_info, show_spinner,
)
from utils.helpers import pause, prompt_input, prompt_int


# ─────────────────────────────────────────────
# Helpers internos
# ─────────────────────────────────────────────

def _hash_text(text: str, algorithm: str) -> str:
    """Calcula hash de um texto com o algoritmo especificado."""
    b = text.encode("utf-8")
    algs = {
        "md5":    hashlib.md5,
        "sha1":   hashlib.sha1,
        "sha256": hashlib.sha256,
        "sha512": hashlib.sha512,
    }
    fn = algs.get(algorithm.lower())
    if fn is None:
        raise ValueError(f"Algoritmo desconhecido: {algorithm}")
    return fn(b).hexdigest()


def _select_algorithm() -> str:
    """Prompt interativo para selecionar o algoritmo de hash."""
    print()
    print_info("Selecione o algoritmo de hash:")
    for opt, name in [("1", "MD5"), ("2", "SHA-1"), ("3", "SHA-256"), ("4", "SHA-512")]:
        print(f"  {opt} - {name}")
    choice = prompt_input("Algoritmo", default="3").strip()
    return {"1": "md5", "2": "sha1", "3": "sha256", "4": "sha512"}.get(choice, "sha256")


# ─────────────────────────────────────────────
# Ferramenta 1 — Hash Cracker via Wordlist
# ─────────────────────────────────────────────

def hash_cracker_wordlist():
    """Tenta quebrar um hash usando uma wordlist em disco."""
    print_header("Hash Cracker — Ataque por Wordlist", "BRUTE FORCE")

    target_hash = prompt_input("Cole o hash alvo (hex)").strip().lower()
    if not target_hash:
        print_warning("Hash não fornecido.")
        pause()
        return

    algorithm = _select_algorithm()

    wordlist_path = prompt_input(
        "Caminho para a wordlist (ex: C:/wordlists/rockyou.txt)"
    ).strip().strip("'\"")
    wordlist_path = os.path.expanduser(wordlist_path)

    if not os.path.isfile(wordlist_path):
        print_error(f"Arquivo não encontrado: {wordlist_path}")
        pause()
        return

    print_info(f"Algoritmo: {algorithm.upper()} | Wordlist: {os.path.basename(wordlist_path)}")
    print_info("Pressione Ctrl+C para interromper.\n")
    time.sleep(0.5)

    found = None
    attempts = 0
    start_time = time.time()

    try:
        with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                word = line.rstrip("\n\r")
                attempts += 1
                if _hash_text(word, algorithm) == target_hash:
                    found = word
                    break
                if attempts % 100_000 == 0:
                    elapsed = time.time() - start_time
                    rate = attempts / elapsed if elapsed > 0 else 0
                    print_info(f"  {attempts:,} tentativas | {rate:,.0f} hashes/s...")
    except KeyboardInterrupt:
        print_warning("\nAtaque interrompido pelo usuário.")

    elapsed = time.time() - start_time
    rate = attempts / elapsed if elapsed > 0 else 0

    rows = [
        ["Hash Alvo",       target_hash],
        ["Algoritmo",       algorithm.upper()],
        ["Tentativas",      f"{attempts:,}"],
        ["Tempo Decorrido", f"{elapsed:.2f}s"],
        ["Velocidade",      f"{rate:,.0f} hashes/s"],
        ["Resultado",       f"ENCONTRADO: {found}" if found else "NAO ENCONTRADO"],
    ]
    print_table("Resultado — Wordlist Attack", ["Campo", "Valor"], rows, style="red")

    if found:
        print_success(f"Senha encontrada: {found}")
    else:
        print_warning("Hash não encontrado na wordlist fornecida.")

    pause()


# ─────────────────────────────────────────────
# Ferramenta 2 — Hash Cracker por Força Bruta
# ─────────────────────────────────────────────

def hash_cracker_bruteforce():
    """Quebra um hash por enumeração exaustiva de combinações de caracteres."""
    print_header("Hash Cracker — Força Bruta Pura", "BRUTE FORCE")

    target_hash = prompt_input("Cole o hash alvo (hex)").strip().lower()
    if not target_hash:
        print_warning("Hash não fornecido.")
        pause()
        return

    algorithm = _select_algorithm()

    print()
    print_info("Conjuntos de caracteres:")
    print("  1 - Apenas dígitos (0-9)")
    print("  2 - Letras minúsculas (a-z)")
    print("  3 - Alfanumérico (letras + dígitos)")
    print("  4 - Alfanumérico + símbolos comuns")
    charset_choice = prompt_input("Conjunto de caracteres", default="2").strip()

    charsets = {
        "1": string.digits,
        "2": string.ascii_lowercase,
        "3": string.ascii_lowercase + string.digits,
        "4": string.ascii_lowercase + string.digits + "!@#$%&*-_=+?",
    }
    charset = charsets.get(charset_choice, string.ascii_lowercase)

    max_len = prompt_int("Comprimento máximo (ex: 1 a 8)", min_val=1, max_val=10, default=6)

    print_info(f"Charset: {len(charset)} chars | Algoritmo: {algorithm.upper()} | Máx: {max_len}")
    print_info("Pressione Ctrl+C para interromper.\n")
    time.sleep(0.5)

    found = None
    attempts = 0
    start_time = time.time()

    try:
        for length in range(1, max_len + 1):
            print_info(f"Testando comprimento {length}...")
            for combo in itertools.product(charset, repeat=length):
                candidate = "".join(combo)
                attempts += 1
                if _hash_text(candidate, algorithm) == target_hash:
                    found = candidate
                    raise StopIteration
                if attempts % 500_000 == 0:
                    elapsed = time.time() - start_time
                    rate = attempts / elapsed if elapsed > 0 else 0
                    print_info(f"  {attempts:,} tentativas | {rate:,.0f} hashes/s | atual: {candidate!r}")
    except StopIteration:
        pass
    except KeyboardInterrupt:
        print_warning("\nAtaque interrompido pelo usuário.")

    elapsed = time.time() - start_time
    rate = attempts / elapsed if elapsed > 0 else 0

    rows = [
        ["Hash Alvo",        target_hash],
        ["Algoritmo",        algorithm.upper()],
        ["Charset",          f"{len(charset)} caracteres"],
        ["Comprimento Máx",  str(max_len)],
        ["Tentativas",       f"{attempts:,}"],
        ["Tempo Decorrido",  f"{elapsed:.2f}s"],
        ["Velocidade",       f"{rate:,.0f} hashes/s"],
        ["Resultado",        f"ENCONTRADO: {found}" if found else "NAO ENCONTRADO"],
    ]
    print_table("Resultado — Força Bruta", ["Campo", "Valor"], rows, style="red")

    if found:
        print_success(f"Senha encontrada: {found}")
    else:
        print_warning("Senha não encontrada no espaço de busca definido.")

    pause()


# ─────────────────────────────────────────────
# Ferramenta 3 — Verificador de Hash
# ─────────────────────────────────────────────

def hash_verifier():
    """Verifica se uma senha/texto corresponde a um hash conhecido."""
    print_header("Verificador de Hash", "BRUTE FORCE")

    plaintext = prompt_input("Digite o texto/senha a verificar")
    if not plaintext:
        print_warning("Texto vazio.")
        pause()
        return

    target_hash = prompt_input("Cole o hash para comparar").strip().lower()
    if not target_hash:
        print_warning("Hash não fornecido.")
        pause()
        return

    rows = []
    for alg in ["md5", "sha1", "sha256", "sha512"]:
        computed = _hash_text(plaintext, alg)
        match = "MATCH" if computed == target_hash else "-"
        rows.append([alg.upper(), computed, match])

    print_table(
        f"Verificação de Hash para '{plaintext[:30]}'",
        ["Algoritmo", "Hash Calculado", "Match"],
        rows,
        style="red",
    )

    matched_alg = next((r[0] for r in rows if "MATCH" in r[2]), None)
    if matched_alg:
        print_success(f"Hash verificado com sucesso! Algoritmo: {matched_alg}")
    else:
        print_warning("Nenhum algoritmo produziu o hash informado.")

    pause()


# ─────────────────────────────────────────────
# Ferramenta 4 — Gerador de Wordlist Customizada
# ─────────────────────────────────────────────

def wordlist_generator():
    """Gera uma wordlist com mutações baseadas em palavras fornecidas pelo usuário."""
    print_header("Gerador de Wordlist Customizada", "BRUTE FORCE")

    base_words_raw = prompt_input(
        "Palavras-base separadas por vírgula (ex: admin,senha,user,nether)"
    )
    if not base_words_raw.strip():
        print_warning("Nenhuma palavra-base fornecida.")
        pause()
        return

    base_words = [w.strip() for w in base_words_raw.split(",") if w.strip()]

    print()
    use_leet = prompt_input(
        "Substituições leet (a->4, e->3, i->1, o->0, s->5)? (s/n)", default="s"
    ).lower() == "s"
    use_case = prompt_input(
        "Variações de capitalização (Title, UPPER)? (s/n)", default="s"
    ).lower() == "s"
    use_numbers = prompt_input(
        "Adicionar sufixos numéricos (1-99, anos)? (s/n)", default="s"
    ).lower() == "s"
    use_specials = prompt_input(
        "Adicionar sufixos especiais (!@#$%)? (s/n)", default="n"
    ).lower() == "s"

    output_path = prompt_input(
        "Caminho de saída para a wordlist",
        default="./wordlist_custom.txt",
    ).strip().strip("'\"")
    output_path = os.path.expanduser(output_path)

    show_spinner("Gerando wordlist...", 0.5)

    leet_map = str.maketrans("aeiost", "431057")
    year_suffixes = [str(y) for y in range(1970, 2026)]
    num_suffixes = [str(n) for n in range(0, 100)]
    spec_suffixes = ["!", "@", "#", "$", "%", "!!", "@@"]

    generated = set()

    def _add_with_mutations(word: str):
        variants = [word]
        if use_case:
            variants.append(word.capitalize())
            variants.append(word.upper())
        if use_leet:
            variants.append(word.translate(leet_map))
            if use_case:
                variants.append(word.translate(leet_map).capitalize())
        for v in variants:
            generated.add(v)
            if use_numbers:
                for n in num_suffixes + year_suffixes:
                    generated.add(v + n)
            if use_specials:
                for s in spec_suffixes:
                    generated.add(v + s)

    for bw in base_words:
        _add_with_mutations(bw)

    out_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for entry in sorted(generated):
            f.write(entry + "\n")

    rows = [
        ["Palavras-Base",      str(len(base_words))],
        ["Leet Speak",         "Sim" if use_leet     else "Não"],
        ["Capitalização",      "Sim" if use_case     else "Não"],
        ["Sufixos Numéricos",  "Sim" if use_numbers  else "Não"],
        ["Sufixos Especiais",  "Sim" if use_specials else "Não"],
        ["Total de Entradas",  f"{len(generated):,}"],
        ["Arquivo de Saída",   output_path],
    ]
    print_table("Wordlist Gerada com Sucesso", ["Parâmetro", "Valor"], rows, style="red")
    print_success(f"Wordlist salva em: {output_path}")
    pause()


# ─────────────────────────────────────────────
# Menu Principal do Módulo
# ─────────────────────────────────────────────

def bruteforce_menu():
    """Menu interativo do módulo de Força Bruta."""
    while True:
        print_header("Ferramentas de Força Bruta", "BRUTE FORCE")
        options = [
            ("1", "Hash Cracker — Ataque por Wordlist",    "Tenta quebrar hashes via lista de palavras"),
            ("2", "Hash Cracker — Força Bruta Pura",       "Enumeração exaustiva de combinações"),
            ("3", "Verificador de Hash",                    "Confirma se um texto corresponde a um hash"),
            ("4", "Gerador de Wordlist Customizada",        "Cria wordlists com mutações e variações"),
            ("0", "Voltar ao Menu Principal",               "Retornar para o menu de toolkits"),
        ]
        print_table("Opções Disponíveis", ["Opção", "Módulo", "Descrição"], options, style="red")
        choice = prompt_input("Escolha uma opção (0-4)").strip()

        if choice == "1":
            hash_cracker_wordlist()
        elif choice == "2":
            hash_cracker_bruteforce()
        elif choice == "3":
            hash_verifier()
        elif choice == "4":
            wordlist_generator()
        elif choice in ("0", "voltar", "v", "b"):
            break
        else:
            print_error("Opção inválida! Digite um número de 0 a 4.")
            time.sleep(1)
