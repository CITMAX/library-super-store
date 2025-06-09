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
BOOKS_DIR = Path("Livros")
FILE_CATEGORIES = {
    'Livros': ['.pdf', '.epub'],
    'Documentos': ['.doc', '.docx', '.txt', '.odt', '.xlsx']
}

def setup_environment():
    """Configura diretórios e verifica dependências"""
    try:
        REPO_DIR.mkdir(exist_ok=True)
        DOCS_DIR.mkdir(exist_ok=True)
        BOOKS_DIR.mkdir(exist_ok=True)
    except OSError as e:
        print(f"Erro crítico na configuração: {e}")
        sys.exit(1)

def git_auto_commit():
    """Realiza commit automático das mudanças"""
    try:
        subprocess.run(["git", "add", "."], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "commit", "-m", "Auto-commit: Atualização de arquivos"], 
                      cwd=REPO_DIR, check=True)
        subprocess.run(["git", "push"], cwd=REPO_DIR, check=True)
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Erro no Git: {e}")

def listar_arquivos(diretorio=BOOKS_DIR):
    """Lista recursivamente todos os arquivos com numeração"""
    arquivos = []
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

def handle_add_document():
    """Submenu para adição de documentos com navegação"""
    while True:
        print("\n📂 Adicionar Documento")
        print("1. Procurar arquivo no computador")
        print("2. Digitar caminho manualmente")
        
        escolha = input("\nEscolha: ").strip()
        
        if escolha == '1':
            root = Tk()
            root.withdraw()
            arquivo = filedialog.askopenfilename(title="Selecione o documento")
            root.destroy()
            
            if not arquivo:
                print("\nOperação cancelada pelo usuário")
                continue
                
            try:
                destino = BOOKS_DIR / Path(arquivo).name
                shutil.copy(arquivo, destino)
                print(f"\n✅ Documento {destino.name} adicionado com sucesso!")
                git_auto_commit()
            except Exception as e:
                print(f"\n❌ Erro ao copiar arquivo: {e}")
        
        elif escolha == '2':
            caminho = input("\nDigite o caminho completo do arquivo: ").strip()
            if not caminho:
                print("\n❌ Nenhum caminho fornecido")
                continue
                
            try:
                destino = BOOKS_DIR / Path(caminho).name
                shutil.copy(caminho, destino)
                print(f"\n✅ Documento {destino.name} adicionado com sucesso!")
                git_auto_commit()
            except Exception as e:
                print(f"\n❌ Erro ao copiar arquivo: {e}")
        
        else:
            print("\n❌ Opção inválida")
            continue
            
        # Opções pós-operacao
        escolha = input("\n0. Voltar\n9. Sair\nEscolha: ").strip()
        if escolha == '0':
            return
        elif escolha == '9':
            sys.exit("👋 Programa encerrado pelo usuário")

def mostrar_menu_principal():
    """Menu principal com navegação aprimorada"""
    print("\n" + "="*50)
    print("📚 SISTEMA DE GESTÃO DE BIBLIOTECA DIGITAL".center(50))
    print("="*50)
    print("\n1. Listar documentos\n2. Adicionar documento\n3. Renomear documento")
    print("4. Remover documento\n5. Organizar arquivos\n6. Sair")

def main():
    setup_environment()
    
    # Inicialização do Tkinter se necessário
    if 'DISPLAY' in os.environ or platform.system() == 'Windows':
        Tk().withdraw()
    
    while True:
        try:
            mostrar_menu_principal()
            escolha = input("\n▶ Escolha uma opção: ").strip()
            
            if escolha == '1':
                # Implementação existente
                pass
            elif escolha == '2':
                handle_add_document()
            elif escolha == '6':
                sys.exit("\n👋 Programa encerrado com sucesso!")
            else:
                print("\n❌ Opção inválida! Tente novamente.")
                
        except KeyboardInterrupt:
            print("\n\n⚠ Operação interrompida pelo usuário")
        except Exception as e:
            print(f"\n‼️ Erro crítico: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
