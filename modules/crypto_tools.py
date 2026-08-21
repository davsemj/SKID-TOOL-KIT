import hashlib
import base64
import urllib.parse
import string
import secrets
import math
import os
from utils.display import print_header, print_table, print_panel, print_success, print_error, print_warning, print_info, show_spinner
from utils.helpers import pause, prompt_input, prompt_int

def generate_text_hashes():
    """Gera múltiplos hashes criptográficos a partir de um texto."""
    print_header("Gerador de Hashes (Texto)", "CRIPTOGRAFIA")
    raw_text = prompt_input("Digite ou cole o texto para calcular os hashes")
    if not raw_text:
        print_warning("Texto vazio.")
        pause()
        return

    b_text = raw_text.encode('utf-8')
    rows = [
        ["MD5", hashlib.md5(b_text).hexdigest()],
        ["SHA-1", hashlib.sha1(b_text).hexdigest()],
        ["SHA-224", hashlib.sha224(b_text).hexdigest()],
        ["SHA-256", hashlib.sha256(b_text).hexdigest()],
        ["SHA-384", hashlib.sha384(b_text).hexdigest()],
        ["SHA-512", hashlib.sha512(b_text).hexdigest()],
    ]

    print_table(f"Hashes Criptográficos para '{raw_text[:30]}...'", ["Algoritmo", "Hash Hexadecimal"], rows, style="magenta")
    pause()

def generate_file_hashes():
    """Calcula hashes de arquivos no disco lendo em blocos."""
    print_header("Gerador de Hashes (Arquivo)", "CRIPTOGRAFIA")
    filepath = prompt_input("Caminho do arquivo (ex: ./arquivo.zip ou c:/teste.txt)")
    filepath = os.path.expanduser(filepath.strip('\'"'))

    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        print_error(f"Arquivo não encontrado: '{filepath}'")
        pause()
        return

    show_spinner(f"Processando arquivo '{os.path.basename(filepath)}'...", 0.3)
    try:
        md5_h = hashlib.md5()
        sha1_h = hashlib.sha1()
        sha256_h = hashlib.sha256()
        sha512_h = hashlib.sha512()

        file_size = os.path.getsize(filepath)
        with open(filepath, 'rb') as f:
            while chunk := f.read(65536):
                md5_h.update(chunk)
                sha1_h.update(chunk)
                sha256_h.update(chunk)
                sha512_h.update(chunk)

        rows = [
            ["Arquivo", os.path.basename(filepath)],
            ["Tamanho", f"{file_size:,} bytes"],
            ["MD5", md5_h.hexdigest()],
            ["SHA-1", sha1_h.hexdigest()],
            ["SHA-256", sha256_h.hexdigest()],
            ["SHA-512", sha512_h.hexdigest()],
        ]

        print_table("Hashes do Arquivo", ["Propriedade", "Valor"], rows, style="green")
    except Exception as e:
        print_error(f"Erro ao ler arquivo: {e}")

    pause()

def encode_decode_tools():
    """Menu para codificação e decodificação de dados."""
    print_header("Codificador / Decodificador", "CRIPTOGRAFIA")
    print_info("Formatos suportados: Base64, Hexadecimal, URL Encode, Rot13, Binário")
    
    print(" 1 - Codificar Texto")
    print(" 2 - Decodificar Texto")
    sub_choice = prompt_input("Escolha", default="1")

    text = prompt_input("Digite o texto de entrada")
    if not text:
        return

    if sub_choice == "1":
        # Codificação
        b64 = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        hex_val = text.encode('utf-8').hex()
        url_enc = urllib.parse.quote(text)
        rot13 = text.translate(str.maketrans(
            "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
            "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm"
        ))
        binary = ' '.join(format(ord(c), '08b') for c in text)

        rows = [
            ["Base64", b64],
            ["Hexadecimal", hex_val],
            ["URL Encoded", url_enc],
            ["Rot13", rot13],
            ["Binário (8-bit)", binary if len(binary) < 60 else binary[:57] + "..."],
        ]
        print_table("Resultados da Codificação", ["Formato", "Saída"], rows, style="cyan")
    else:
        # Decodificação
        print("\nEscolha o formato de origem:")
        print(" 1 - Base64")
        print(" 2 - Hexadecimal")
        print(" 3 - URL Decoded")
        print(" 4 - Rot13")
        print(" 5 - Binário (separado por espaços)")
        fmt = prompt_input("Formato", default="1")

        try:
            if fmt == "1":
                res = base64.b64decode(text.encode('utf-8')).decode('utf-8', errors='replace')
            elif fmt == "2":
                clean_hex = text.replace(" ", "").replace("0x", "")
                res = bytes.fromhex(clean_hex).decode('utf-8', errors='replace')
            elif fmt == "3":
                res = urllib.parse.unquote(text)
            elif fmt == "4":
                res = text.translate(str.maketrans(
                    "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
                    "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm"
                ))
            elif fmt == "5":
                binary_vals = text.strip().split()
                res = ''.join(chr(int(b, 2)) for b in binary_vals)
            else:
                res = "Formato desconhecido"

            print_success(f"Texto Decodificado:\n{res}")
        except Exception as e:
            print_error(f"Falha ao decodificar: {e}")

    pause()

def calculate_entropy(pwd: str) -> tuple[float, str]:
    """Calcula a entropia em bits e classifica a força da senha."""
    charset_size = 0
    if any(c in string.ascii_lowercase for c in pwd):
        charset_size += 26
    if any(c in string.ascii_uppercase for c in pwd):
        charset_size += 26
    if any(c in string.digits for c in pwd):
        charset_size += 10
    if any(c in string.punctuation for c in pwd):
        charset_size += len(string.punctuation)

    if charset_size == 0 or len(pwd) == 0:
        return 0.0, "Muito Fraca"

    entropy = len(pwd) * math.log2(charset_size)
    if entropy < 35:
        strength = "Muito Fraca (Vulnerável a força bruta)"
    elif entropy < 55:
        strength = "Média (Aceitável para uso comum)"
    elif entropy < 80:
        strength = "Forte (Segura)"
    else:
        strength = "Extremamente Segura (Grau Militar)"

    return entropy, strength

def generate_passwords():
    """Gerador de senhas aleatórias e passphrases seguras."""
    print_header("Gerador de Senhas & Entropia", "CRIPTOGRAFIA")
    
    print(" 1 - Senha com Caracteres Complexos (letras, números, símbolos)")
    print(" 2 - Passphrase (combinação de palavras legíveis)")
    mode = prompt_input("Selecione o tipo de geração", default="1")

    if mode == "1":
        length = prompt_int("Comprimento da senha (ex: 16 a 32)", min_val=6, max_val=128, default=18)
        include_upper = prompt_input("Incluir letras maiúsculas? (s/n)", default="s").lower() == 's'
        include_lower = prompt_input("Incluir letras minúsculas? (s/n)", default="s").lower() == 's'
        include_digits = prompt_input("Incluir dígitos numéricos? (s/n)", default="s").lower() == 's'
        include_symbols = prompt_input("Incluir símbolos especiais? (s/n)", default="s").lower() == 's'
        quantity = prompt_int("Quantidade de senhas a gerar", min_val=1, max_val=20, default=5)

        chars = ""
        if include_upper:
            chars += string.ascii_uppercase
        if include_lower:
            chars += string.ascii_lowercase
        if include_digits:
            chars += string.digits
        if include_symbols:
            chars += "!@#$%&*()-_=+[]{}<>?"

        if not chars:
            print_error("Você precisa selecionar pelo menos um conjunto de caracteres.")
            pause()
            return

        rows = []
        for i in range(quantity):
            pwd = "".join(secrets.choice(chars) for _ in range(length))
            entropy, strength = calculate_entropy(pwd)
            rows.append([f"Senha {i+1}", pwd, f"{entropy:.1f} bits", strength])

        print_table("Senhas Geradas", ["#", "Senha", "Entropia", "Nível de Segurança"], rows, style="green")

    else:
        # Passphrase com palavras comuns seguras
        wordlist = [
            "aurora", "cometa", "galaxia", "estrela", "universo", "horizonte",
            "castelo", "floresta", "oceano", "montanha", "vulcao", "cristal",
            "falcao", "pantera", "dragao", "leopardo", "aguia", "lobo",
            "tempestade", "neblina", "trovao", "relampago", "inverno", "solsticio",
            "codigo", "pixel", "quantum", "matrix", "cibernetico", "frequencia"
        ]
        word_count = prompt_int("Quantidade de palavras (ex: 4 a 6)", min_val=3, max_val=10, default=4)
        separator = prompt_input("Separador (ex: -, _, .)", default="-")
        quantity = prompt_int("Quantidade de frases a gerar", min_val=1, max_val=10, default=5)

        rows = []
        for i in range(quantity):
            selected = [secrets.choice(wordlist) for _ in range(word_count)]
            # Adiciona um número e caractere especial para extra segurança
            passphrase = separator.join(selected) + separator + str(secrets.randbelow(90) + 10)
            entropy, strength = calculate_entropy(passphrase)
            rows.append([f"Frase {i+1}", passphrase, f"{entropy:.1f} bits", strength])

        print_table("Passphrases Geradas", ["#", "Passphrase", "Entropia", "Nível de Segurança"], rows, style="green")

    pause()

def symmetric_encrypt_decrypt():
    """Cifra e decifra texto usando algoritmo baseado em hash de chave com Salt."""
    print_header("Cifrador de Texto Simétrico", "CRIPTOGRAFIA")
    print(" 1 - Cifrar Texto com Senha")
    print(" 2 - Decifrar Texto Cifrado com Senha")
    action = prompt_input("Escolha a ação", default="1")

    if action == "1":
        plaintext = prompt_input("Digite o texto a ser protegido")
        password = prompt_input("Digite uma senha mestra para cifrar")
        if not plaintext or not password:
            print_warning("Texto e senha são obrigatórios.")
            pause()
            return

        salt = os.urandom(8)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, 32)
        
        # Keystream XOR cipher
        plain_bytes = plaintext.encode('utf-8')
        # Extend key if needed
        stream = hashlib.sha256(key + salt).digest()
        while len(stream) < len(plain_bytes):
            stream += hashlib.sha256(stream + key).digest()
        
        cipher_bytes = bytes([b ^ stream[i] for i, b in enumerate(plain_bytes)])
        final_payload = base64.b64encode(salt + cipher_bytes).decode('utf-8')

        print_success("Texto Cifrado com Sucesso!")
        print_panel(final_payload, title="Payload Cifrado (Base64)", style="green")

    else:
        ciphertext = prompt_input("Cole o Payload Cifrado (Base64)")
        password = prompt_input("Digite a senha mestra para decifrar")

        try:
            raw = base64.b64decode(ciphertext.strip())
            salt = raw[:8]
            cipher_bytes = raw[8:]

            key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, 32)
            stream = hashlib.sha256(key + salt).digest()
            while len(stream) < len(cipher_bytes):
                stream += hashlib.sha256(stream + key).digest()

            plain_bytes = bytes([b ^ stream[i] for i, b in enumerate(cipher_bytes)])
            decrypted = plain_bytes.decode('utf-8')
            print_success(f"Texto Decifrado com Sucesso:\n\n{decrypted}")
        except Exception:
            print_error("Falha na decifração. Senha incorreta ou formato inválido.")

    pause()

def crypto_menu():
    """Menu interativo de ferramentas criptográficas."""
    while True:
        print_header("Ferramentas Criptográficas & Segurança", "CRIPTOGRAFIA")
        options = [
            ("1", "🔑 Gerador de Hashes para Texto (MD5, SHA256, etc.)"),
            ("2", "📁 Gerador de Hashes para Arquivos"),
            ("3", "🔄 Codificador / Decodificador (Base64, Hex, URL, Rot13)"),
            ("4", "🛡️ Gerador de Senhas Fortes & Medidor de Entropia"),
            ("5", "🔒 Cifrador / Decifrador de Texto Simétrico"),
            ("0", "⬅ Voltar ao Menu Principal"),
        ]
        print_table("Opções Disponíveis", ["Opção", "Descrição"], options, style="cyan")
        choice = prompt_input("Escolha uma opção").strip()

        if choice == "1":
            generate_text_hashes()
        elif choice == "2":
            generate_file_hashes()
        elif choice == "3":
            encode_decode_tools()
        elif choice == "4":
            generate_passwords()
        elif choice == "5":
            symmetric_encrypt_decrypt()
        elif choice == "0":
            break
        else:
            print_error("Opção inválida!")
