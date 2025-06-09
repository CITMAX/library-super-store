import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from tkinter import filedialog, Tk

# Configurações globais
REPO_DIR = Path("library-super-store")
DOCS_DIR = REPO_DIR / "Documentação do Projeto"
BOOKS_DIR = REPO_DIR / "Livros"
FILE_CATEGORIES = {
    'Livros': ['.pdf', '.epub'],
    'Documentos': ['.doc', '.docx', '.txt', '.odt', '.xlsx']
}

def setup_environment():
    """Configura o ambiente e estrutura de diretórios"""
    try:
        REPO_DIR.mkdir(exist_ok=True)
        DOCS_DIR.mkdir(exist_ok=True)
        BOOKS_DIR.mkdir(exist_ok=True)

        gitignore = REPO_DIR / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("*.DS_Store\n*.tmp\n*.bak\n__pycache__/\n")

    except Exception as e:
        print(f"Erro crítico na configuração: {e}")
        sys.exit(1)

def git_local_commit(arquivo):
    """Realiza commit local sem push automático"""
    try:
        subprocess.run(["git", "add", str(arquivo.relative_to(REPO_DIR))],
                       cwd=REPO_DIR, check=True)
        subprocess.run(["git", "commit", "-m", f"Adicionado: {arquivo.name}"],
                       cwd=REPO_DIR, check=True)
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Erro no Git: {e}")

def listar_arquivos(diretorio=BOOKS_DIR):
    """Lista recursivamente todos os arquivos com numeração"""
    arquivos = []
    print("\n📂 Conteúdo da Biblioteca:")
    for idx, item in enumerate(diretorio.rglob('*'), 1):
        if item.is_file():
            rel_path = item.relative_to(diretorio)
            arquivos.append((idx, rel_path, item))
            print(f"{idx}. {rel_path}")
    return arquivos

def selecionar_arquivo():
    """Interface para seleção de arquivo com navegação"""
    arquivos = listar_arquivos()
    if not arquivos:
        print("Nenhum arquivo encontrado!")
        return None

    while True:
        try:
            escolha = input("\nDigite o número do arquivo (0=Voltar): ").strip()
            if escolha == '0':
                return None
            escolha = int(escolha)
            if 1 <= escolha <= len(arquivos):
                return arquivos[escolha-1][2]
            print("Número inválido!")
        except ValueError:
            print("Entrada inválida!")

def abrir_arquivo(caminho):
    """Abre o arquivo com o aplicativo padrão do sistema"""
    try:
        if platform.system() == 'Darwin':
            subprocess.run(['open', caminho])
        elif platform.system() == 'Windows':
            os.startfile(caminho)
        else:
            subprocess.run(['xdg-open', caminho])
    except Exception as e:
        print(f"Erro ao abrir arquivo: {e}")

def menu_listar():
    """Menu para listar e abrir documentos"""
    while True:
        arquivo = selecionar_arquivo()
        if not arquivo:
            return
        abrir_arquivo(arquivo)

def handle_add_document():
    """Submenu para adição de documentos"""
    while True:
        print("\n📂 Adicionar Documento")
        print("1. Procurar arquivo no computador")
        print("2. Digitar caminho manualmente")
        print("0. Voltar")

        escolha = input("\nEscolha: ").strip()

        if escolha == '1':
            root = Tk()
            root.withdraw()
            caminho_origem = filedialog.askopenfilename(title="Selecione o documento")
            root.destroy()

            if not caminho_origem:
                print("\nOperação cancelada")
                continue

            try:
                arquivo_destino = BOOKS_DIR / Path(caminho_origem).name
                shutil.copy(caminho_origem, arquivo_destino)
                print(f"\n✅ Documento {arquivo_destino.name} adicionado!")
                git_local_commit(arquivo_destino)

            except Exception as e:
                print(f"\n❌ Erro: {e}")

        elif escolha == '2':
            caminho = input("\nDigite o caminho completo: ").strip()
            if not caminho:
                print("\n❌ Nenhum caminho fornecido")
                continue

            try:
                arquivo_destino = BOOKS_DIR / Path(caminho).name
                shutil.copy(caminho, arquivo_destino)
                print(f"\n✅ Documento {arquivo_destino.name} adicionado!")
                git_local_commit(arquivo_destino)

            except Exception as e:
                print(f"\n❌ Erro: {e}")

        elif escolha == '0':
            return

        else:
            print("\n❌ Opção inválida")

def menu_renomear():
    """Menu para renomear documentos"""
    print("\n✏️ Renomear Documento")
    arquivo = selecionar_arquivo()
    if not arquivo:
        return

    novo_nome = input("Novo nome (com extensão): ").strip()
    if not novo_nome:
        print("Nome inválido!")
        return

    try:
        novo_path = arquivo.parent / novo_nome
        arquivo.rename(novo_path)
        print("✅ Arquivo renomeado!")
        git_local_commit(novo_path)
    except Exception as e:
        print(f"❌ Erro: {e}")

def menu_remover():
    """Menu para remover documentos"""
    print("\n❌ Remover Documento")
    arquivo = selecionar_arquivo()
    if not arquivo:
        return

    confirmacao = input(f"Confirmar exclusão de {arquivo.name}? (s/n): ").lower()
    if confirmacao == 's':
        try:
            arquivo.unlink()
            print("✅ Arquivo removido!")

            subprocess.run(["git", "add", "."], cwd=REPO_DIR, check=True)
            subprocess.run(["git", "commit", "-m", f"Removido: {arquivo.name}"],
                           cwd=REPO_DIR, check=True)

        except Exception as e:
            print(f"❌ Erro: {e}")

def organizar_arquivos():
    """Organiza os arquivos por categoria e ano"""
    print("\n🔄 Organizando arquivos...")
    for arquivo in BOOKS_DIR.rglob('*'):
        if arquivo.is_file():
            categoria = next(
                (cat for cat, exts in FILE_CATEGORIES.items()
                 if arquivo.suffix.lower() in exts),
                'Outros'
            )

            ano = datetime.fromtimestamp(arquivo.stat().st_ctime).year
            destino = BOOKS_DIR / categoria / str(ano)
            destino.mkdir(parents=True, exist_ok=True)

            try:
                shutil.move(str(arquivo), destino / arquivo.name)
            except Exception as e:
                print(f"⚠️ Erro ao mover {arquivo.name}: {e}")

    print("✅ Organização concluída!")
    try:
        subprocess.run(["git", "add", "."], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "commit", "-m", "Organização automática"],
                       cwd=REPO_DIR, check=True)
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Erro no Git: {e}")

def mostrar_menu_principal():
    """Exibe o menu principal"""
    print("\n" + "="*50)
    print("📚 SISTEMA DE GESTÃO DE BIBLIOTECA DIGITAL".center(50))
    print("="*50)
    print("\n1. Listar documentos\n2. Adicionar documento\n3. Renomear documento")
    print("4. Remover documento\n5. Organizar arquivos\n6. Sair")

def main():
    setup_environment()

    if 'DISPLAY' in os.environ or platform.system() == 'Windows':
        Tk().withdraw()

    while True:
        try:
            mostrar_menu_principal()
            escolha = input("\n▶ Escolha uma opção: ").strip()

            if escolha == '1':
                menu_listar()
            elif escolha == '2':
                handle_add_document()
            elif escolha == '3':
                menu_renomear()
            elif escolha == '4':
                menu_remover()
            elif escolha == '5':
                organizar_arquivos()
            elif escolha == '6':
                print("\n👋 Programa encerrado!")
                sys.exit()
            else:
                print("\n❌ Opção inválida!")

        except KeyboardInterrupt:
            print("\n\n⚠ Operação cancelada pelo usuário")
        except Exception as e:
            print(f"\n‼️ Erro crítico: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()    