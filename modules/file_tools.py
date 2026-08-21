import os
import hashlib
import zipfile
import shutil
from collections import defaultdict
from utils.display import print_header, print_table, print_panel, print_success, print_error, print_warning, print_info, show_spinner
from utils.helpers import pause, prompt_input, prompt_int, format_bytes

def get_file_hash(filepath: str) -> str:
    """Calcula hash SHA-256 de um arquivo."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def find_duplicate_files():
    """Localiza arquivos duplicados em uma pasta comparando hashes SHA-256."""
    print_header("Localizador de Arquivos Duplicados", "ARQUIVOS")
    folder_path = prompt_input("Caminho da pasta a analisar (ex: . ou C:/Projetos)", default=".")
    folder_path = os.path.abspath(folder_path.strip('\'"'))

    if not os.path.isdir(folder_path):
        print_error(f"Diretório não encontrado: {folder_path}")
        pause()
        return

    show_spinner(f"Varrendo diretório '{folder_path}'...", 0.4)
    size_map = defaultdict(list)
    total_scanned = 0

    for root, _, files in os.walk(folder_path):
        for f in files:
            full_path = os.path.join(root, f)
            try:
                size = os.path.getsize(full_path)
                size_map[size].append(full_path)
                total_scanned += 1
            except OSError:
                continue

    # Filtrar apenas tamanhos que possuem mais de 1 arquivo
    potential_duplicates = [paths for size, paths in size_map.items() if len(paths) > 1 and size > 0]
    hash_map = defaultdict(list)

    for paths in potential_duplicates:
        for p in paths:
            try:
                h = get_file_hash(p)
                hash_map[h].append(p)
            except OSError:
                continue

    duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}

    if duplicates:
        print_warning(f"Encontrados {len(duplicates)} grupos de arquivos duplicados entre {total_scanned} analisados:")
        wasted_bytes = 0
        rows = []
        for idx, (h, paths) in enumerate(duplicates.items(), 1):
            file_size = os.path.getsize(paths[0])
            wasted_bytes += file_size * (len(paths) - 1)
            first = paths[0]
            dupes = "\n".join(paths[1:])
            rows.append([f"Grupo {idx} ({format_bytes(file_size)})", f"Original: {os.path.basename(first)}\nDuplicados: {len(paths)-1}\n{dupes}"])

        print_table("Arquivos Duplicados Detectados", ["Grupo", "Caminhos"], rows, style="yellow")
        print_info(f"Espaço em disco desperdiçado com duplicatas: {format_bytes(wasted_bytes)}")
    else:
        print_success(f"Nenhum arquivo duplicado encontrado entre os {total_scanned} analisados.")

    pause()

def batch_file_renamer():
    """Renomeador em lote com visualização prévia (Dry-Run)."""
    print_header("Renomeador de Arquivos em Lote", "ARQUIVOS")
    folder_path = prompt_input("Caminho da pasta com os arquivos", default=".")
    folder_path = os.path.abspath(folder_path.strip('\'"'))

    if not os.path.isdir(folder_path):
        print_error(f"Diretório não encontrado: {folder_path}")
        pause()
        return

    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    if not files:
        print_warning("Nenhum arquivo encontrado nesta pasta.")
        pause()
        return

    print_info(f"{len(files)} arquivos encontrados.")
    print(" 1 - Adicionar Prefixo (ex: '2026_')")
    print(" 2 - Adicionar Sufixo (ex: '_final')")
    print(" 3 - Substituir Texto no Nome (ex: 'foto' por 'imagem')")
    print(" 4 - Renomear com Numeração Sequencial (ex: 'arquivo_01.ext')")
    mode = prompt_input("Escolha o método", default="1")

    renamed_pairs = []

    if mode == "1":
        prefix = prompt_input("Prefixo a adicionar")
        for f in files:
            renamed_pairs.append((f, f"{prefix}{f}"))
    elif mode == "2":
        suffix = prompt_input("Sufixo a adicionar")
        for f in files:
            name, ext = os.path.splitext(f)
            renamed_pairs.append((f, f"{name}{suffix}{ext}"))
    elif mode == "3":
        old_str = prompt_input("Texto a substituir")
        new_str = prompt_input("Novo texto")
        for f in files:
            if old_str in f:
                renamed_pairs.append((f, f.replace(old_str, new_str)))
    elif mode == "4":
        base_name = prompt_input("Nome base", default="item")
        pad = prompt_int("Quantidade de dígitos de zero (ex: 2 para 01, 3 para 001)", min_val=1, max_val=6, default=2)
        for idx, f in enumerate(files, 1):
            _, ext = os.path.splitext(f)
            new_name = f"{base_name}_{str(idx).zfill(pad)}{ext}"
            renamed_pairs.append((f, new_name))

    if not renamed_pairs:
        print_warning("Nenhum arquivo elegível para alteração.")
        pause()
        return

    preview_rows = [[old, new] for old, new in renamed_pairs[:15]]
    if len(renamed_pairs) > 15:
        preview_rows.append(["...", f"(e mais {len(renamed_pairs)-15} arquivos)"])
    print_table("Prévia das Renomeações", ["Nome Atual", "Novo Nome"], preview_rows, style="cyan")

    confirm = prompt_input(f"Deseja aplicar a renomeação a esses {len(renamed_pairs)} arquivos? (s/n)", default="n").lower()
    if confirm == 's':
        applied = 0
        for old, new in renamed_pairs:
            old_p = os.path.join(folder_path, old)
            new_p = os.path.join(folder_path, new)
            if old_p != new_p:
                try:
                    os.rename(old_p, new_p)
                    applied += 1
                except Exception as e:
                    print_error(f"Erro ao renomear {old}: {e}")
        print_success(f"{applied} arquivos renomeados com sucesso!")
    else:
        print_info("Operação cancelada pelo usuário.")

    pause()

def zip_compress_extract():
    """Compactador e extrator de arquivos ZIP."""
    print_header("Compactador / Extrator ZIP", "ARQUIVOS")
    print(" 1 - Compactar Pasta ou Arquivo para .ZIP")
    print(" 2 - Extrair Conteúdo de um arquivo .ZIP")
    choice = prompt_input("Escolha", default="1")

    if choice == "1":
        source = prompt_input("Caminho do arquivo ou pasta a compactar")
        source = os.path.abspath(source.strip('\'"'))
        if not os.path.exists(source):
            print_error("Caminho de origem não existe.")
            pause()
            return

        out_zip = prompt_input("Nome do arquivo ZIP de destino", default=f"{os.path.basename(source)}.zip")
        if not out_zip.endswith(".zip"):
            out_zip += ".zip"

        show_spinner("Compactando dados...", 0.4)
        try:
            with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                if os.path.isfile(source):
                    zf.write(source, os.path.basename(source))
                else:
                    for root, _, files in os.walk(source):
                        for file in files:
                            full_path = os.path.join(root, file)
                            arcname = os.path.relpath(full_path, source)
                            zf.write(full_path, arcname)
            print_success(f"Arquivo compactado com sucesso em: {os.path.abspath(out_zip)} ({format_bytes(os.path.getsize(out_zip))})")
        except Exception as e:
            print_error(f"Falha ao compactar: {e}")

    else:
        zip_path = prompt_input("Caminho do arquivo .ZIP a extrair")
        zip_path = os.path.abspath(zip_path.strip('\'"'))
        if not os.path.isfile(zip_path) or not zip_path.endswith(".zip"):
            print_error("Arquivo .zip não encontrado ou inválido.")
            pause()
            return

        dest_dir = prompt_input("Pasta de destino para extração", default="./extraido")
        os.makedirs(dest_dir, exist_ok=True)

        show_spinner("Extraindo arquivos...", 0.4)
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(dest_dir)
            print_success(f"Arquivos extraídos com sucesso para: {os.path.abspath(dest_dir)}")
        except Exception as e:
            print_error(f"Falha ao extrair: {e}")

    pause()

def analyze_folder_size():
    """Analisa e lista os maiores arquivos e subpastas de um diretório."""
    print_header("Analisador de Espaço em Diretório", "ARQUIVOS")
    folder_path = prompt_input("Caminho da pasta a analisar", default=".")
    folder_path = os.path.abspath(folder_path.strip('\'"'))

    if not os.path.isdir(folder_path):
        print_error("Diretório inválido.")
        pause()
        return

    show_spinner(f"Analisando espaço em '{folder_path}'...", 0.5)
    file_list = []
    total_size = 0
    total_files = 0

    for root, _, files in os.walk(folder_path):
        for f in files:
            fp = os.path.join(root, f)
            try:
                sz = os.path.getsize(fp)
                total_size += sz
                total_files += 1
                file_list.append((fp, sz))
            except OSError:
                continue

    file_list.sort(key=lambda x: x[1], reverse=True)
    top_10 = file_list[:10]

    rows = []
    for fp, sz in top_10:
        rel = os.path.relpath(fp, folder_path)
        rows.append([rel if len(rel) < 55 else "..." + rel[-52:], format_bytes(sz), f"{(sz/total_size*100):.1f}%" if total_size else "0%"])

    print_panel(f"Total de Arquivos: {total_files:,}\nEspaço Total Ocupado: {format_bytes(total_size)}", title=f"Resumo da Pasta: {folder_path}", style="magenta")
    if rows:
        print_table("Top 10 Maiores Arquivos", ["Arquivo", "Tamanho", "% do Total"], rows, style="green")

    pause()

def file_menu():
    """Menu interativo de ferramentas de arquivos."""
    while True:
        print_header("Ferramentas de Arquivos & Armazenamento", "ARQUIVOS")
        options = [
            ("1", "🔍 Localizador de Arquivos Duplicados (Hash SHA-256)"),
            ("2", "🏷️ Renomeador de Arquivos em Lote (com Prévia)"),
            ("3", "📦 Compactador & Extrator ZIP"),
            ("4", "📊 Analisador de Espaço e Maiores Arquivos"),
            ("0", "⬅ Voltar ao Menu Principal"),
        ]
        print_table("Opções Disponíveis", ["Opção", "Descrição"], options, style="cyan")
        choice = prompt_input("Escolha uma opção").strip()

        if choice == "1":
            find_duplicate_files()
        elif choice == "2":
            batch_file_renamer()
        elif choice == "3":
            zip_compress_extract()
        elif choice == "4":
            analyze_folder_size()
        elif choice == "0":
            break
        else:
            print_error("Opção inválida!")
