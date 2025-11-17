"""
Script de setup automatizado para o Pokemon Data Agent
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def run_command(cmd, description):
    """Executa um comando e mostra o progresso"""
    print(f"\n{'='*60}")
    print(f" {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        print(f" {description} - Completo!")
        return True
    except subprocess.CalledProcessError as e:
        print(f" Erro: {e}")
        print(e.stderr)
        return False

def check_python_version():
    """Verifica se a versão do Python é adequada"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(" Python 3.10+ é necessário")
        print(f"   Versão atual: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f" Python {version.major}.{version.minor}.{version.micro} detectado")
    return True

def check_env_file():
    """Verifica se o arquivo .env existe"""
    if not Path(".env").exists():
        print("\n  Arquivo .env não encontrado")
        print("   Criando .env a partir de .env.example...")
        
        if Path(".env.example").exists():
            shutil.copy(".env.example", ".env")
            print(" Arquivo .env criado")
            print("\n  IMPORTANTE: Edite o arquivo .env e adicione sua OPENAI_API_KEY")
            return False
        else:
            print(" .env.example não encontrado")
            return False
    
    # Verificar se a API key está configurada
    
    if not os.getenv("OPENAI_API_KEY"):
        print("\n  OPENAI_API_KEY não configurada no .env")
        print("   Por favor, edite o arquivo .env e adicione sua chave")
        return False
    
    print(" Arquivo .env configurado")
    return True

def main():
    """Executa o setup completo"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║          POKEMON DATA AGENT - SETUP                      ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # 1. Verificar Python
    if not check_python_version():
        sys.exit(1)
    
    # 2. Instalar dependências
    if not run_command("pip install -r requirements.txt", "Instalando dependências"):
        print("\n Falha ao instalar dependências")
        sys.exit(1)
    
    # 3. Verificar .env
    env_ok = check_env_file()
    
    # 4. Perguntar sobre ingestão
    print("\n" + "="*60)
    print(" Ingestão de Dados")
    print("="*60)
    print("\nA ingestão baixa dados de 251 Pokémon da PokéAPI.")
    print("Isso pode levar 5-10 minutos.")
    
    if env_ok:
        response = input("\nDeseja executar a ingestão agora? (s/n): ").lower()
        
        if response == 's':
            if not run_command("python -m app.ingest --limit 251", "Ingerindo dados da PokéAPI"):
                print("\n  Ingestão falhou, mas você pode executá-la depois:")
                print("   python -m app.ingest --limit 251")
        else:
            print("\n  Pulando ingestão. Execute depois com:")
            print("   python -m app.ingest --limit 251")
    else:
        print("\n  Configure o .env primeiro, depois execute:")
        print("   python -m app.ingest --limit 251")
    
    # 5. Resumo
    print("\n" + "="*60)
    print(" SETUP COMPLETO!")
    print("="*60)
    
    print("\n Próximos passos:")
    
    if not env_ok:
        print("\n1. Configure sua OPENAI_API_KEY no arquivo .env")
        print("2. Execute a ingestão: python -m app.ingest --limit 251")
    
    print("\n3. Inicie a API:")
    print("   uvicorn app.api:app --reload")
    
    print("\n4. Acesse a documentação:")
    print("   http://localhost:8000/docs")
    
    print("\n5. Teste o agente:")
    print("   python examples/test_agent.py")
    
    print("\n6. Execute os testes:")
    print("   pytest tests/ -v")
    
    print("\n Documentação completa: README.md")
    print(" Guia rápido: QUICKSTART.md")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Setup cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n Erro inesperado: {e}")
        sys.exit(1)
