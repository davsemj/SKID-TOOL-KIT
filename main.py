import sys
import os
import argparse
import time

# Garante que o diretório raiz esteja no PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.display import print_header, print_table, print_panel, print_success, print_error, print_info, clear_screen, show_banner
from utils.helpers import prompt_input, pause

# Importa os submódulos de ferramentas
from modules.system_tools import system_menu, show_system_info
from modules.network_tools import network_menu, run_port_scanner, lookup_my_ip
from modules.crypto_tools import crypto_menu, generate_text_hashes
from modules.dev_tools import dev_menu, generate_uuids
from modules.bruteforce_tools import bruteforce_menu
from modules.malware_tools import malware_menu

def toolkits_menu():
    """Menu dos Toolkits e Módulos de Ferramentas."""
    while True:
        try:
            clear_screen()
            show_banner("Toolkits & Módulos")

            menu_options = [
                ("1", "🖥️  Ferramentas de Sistema", "Hardware, CPU, RAM, Discos e Benchmark I/O"),
                ("2", "🌐  Ferramentas de Rede", "Port Scanner, Latência/Ping, Meu IP, HTTP Headers"),
                ("3", "🔐  Criptografia & Segurança", "Hashes, Base64/Hex/URL, Senhas Fortes, Cifras"),
                ("4", "🛠️  Dev & Produtividade", "UUIDs v4, Epoch Timestamp, API Tester, Mock Data"),
                ("5", "💥  Força Bruta & Hash Cracker", "Wordlist Attack, Brute Force, Verificador de Hash, Wordlist Gen"),
                ("6", "🧟  Malware & Payloads", "Criador de Keylogger (.exe) com Discord Webhook"),
                ("0", "⬅  Voltar ao Menu Inicial", "Retornar para a tela inicial"),
            ]

            print_table("Selecione o Toolkit Desejado", ["Opção", "Módulo", "Descrição"], menu_options, style="red")

            choice = prompt_input("Escolha um toolkit (0-6)").strip()

            if choice == "1":
                system_menu()
            elif choice == "2":
                network_menu()
            elif choice == "3":
                crypto_menu()
            elif choice == "4":
                dev_menu()
            elif choice == "5":
                bruteforce_menu()
            elif choice == "6":
                malware_menu()
            elif choice in ["0", "voltar", "v", "b"]:
                break
            else:
                print_error("Opção inválida! Digite um número de 0 a 6.")
                time.sleep(1)

        except (KeyboardInterrupt, EOFError):
            break

def main_initial_menu():
    """Menu inicial que é exibido ao rodar 'python main.py'."""
    while True:
        try:
            clear_screen()
            show_banner()

            menu_options = [
                ("1", "Toolkits", "Acessar todos os módulos e ferramentas do SKID"),
                ("2", "Sair", "Encerrar o SKID Toolkit"),
            ]

            print_table("Menu Principal", ["Opção", "Ação", "Descrição"], menu_options, style="red")

            choice = prompt_input().strip()

            if choice == "1" or choice.lower() in ["toolkits", "toolkit", "tools", "t"]:
                toolkits_menu()
            elif choice == "2" or choice.lower() in ["sair", "exit", "quit", "q", "0"]:
                clear_screen()
                print_success("O Nether Toolkit foi encerrado. Até logo!")
                break
            else:
                print_error("Opção inválida! Escolha 1 para Toolkits ou 2 para Sair.")
                time.sleep(1)

        except (KeyboardInterrupt, EOFError):
            print("\n")
            print_info("Sessão finalizada pelo usuário. Encerrando...")
            break
        except Exception as e:
            print_error(f"Ocorreu um erro inesperado: {e}")
            pause()

def handle_cli_arguments():
    """Trata execução direta via linha de comando."""
    parser = argparse.ArgumentParser(
        description="Nether Toolkit - Conjunto completo de ferramentas de sistema, rede, criptografia, texto e dev."
    )
    subparsers = parser.add_subparsers(dest="command", help="Comando direto")

    # Comando: sys
    subparsers.add_parser("sys", help="Exibe informações do sistema e hardware")
    
    # Comando: ip
    subparsers.add_parser("ip", help="Exibe IP local e público com geolocalização")

    # Comando: uuid
    subparsers.add_parser("uuid", help="Gera um UUID v4 rápido")

    # Comando: hash
    parser_hash = subparsers.add_parser("hash", help="Gera hashes criptográficos para um texto")
    parser_hash.add_argument("text", help="Texto para calcular os hashes")

    args = parser.parse_args()

    if args.command == "sys":
        show_system_info()
    elif args.command == "ip":
        lookup_my_ip()
    elif args.command == "uuid":
        import uuid as u
        print(f"UUID v4: {u.uuid4()}")
    elif args.command == "hash":
        import hashlib
        b = args.text.encode()
        print(f"Texto: {args.text}")
        print(f"MD5:    {hashlib.md5(b).hexdigest()}")
        print(f"SHA256: {hashlib.sha256(b).hexdigest()}")
        print(f"SHA512: {hashlib.sha512(b).hexdigest()}")
    else:
        main_initial_menu()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        handle_cli_arguments()
    else:
        main_initial_menu()
