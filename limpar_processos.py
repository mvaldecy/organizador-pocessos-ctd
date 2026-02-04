import os
from pathlib import Path

# Lista de pastas (subcategorias)
pastas = [
    "Banco de Dados",
    "Comunicação de dados",
    "Consultoria - Análise de Dados",
    "Consultoria - Inteligência Artificial",
    "Datacenter - Soluções de Armazenamento",
    "Datacenter - Soluções de Segurança",
    "Equipamentos de TIC",
    "Hiperconvergência",
    "Novo Sistema - Assinatura",
    "Novo Sistema - Contratação de Pessoa Jurídica",
    "Novo Sistema - ETIPI",
    "Novo Sistema - Fábrica Software",
    "Novo Sistema - Licença",
    "Outros Equipamentos",
    "Serviços - Digitalização de Documentos",
    "Serviços - Nuvem",
    "Serviços - Outros Serviços Especializados",
    "Serviços - Outsourcing de Impressão",
    "Sistema Existente - Contratação de Pessoa Jurídica",
    "Sistema Existente - ETIPI",
    "Sistema Existente - Fábrica Software",
    "Sistema Existente- Assinatura",
    "Sistema Existente- Licença"
]

total_arquivos_deletados = 0

print("Apagando arquivos de processos...")

for pasta in pastas:
    pasta_path = Path(pasta)
    if pasta_path.exists():
        # Listar todos os arquivos .txt na pasta
        arquivos = list(pasta_path.glob("*.txt"))
        
        for arquivo in arquivos:
            try:
                arquivo.unlink()
                total_arquivos_deletados += 1
                print(f"✓ Deletado: {pasta}/{arquivo.name}")
            except Exception as e:
                print(f"✗ Erro ao deletar {arquivo}: {e}")

print("\n" + "=" * 80)
print(f"Total de arquivos deletados: {total_arquivos_deletados}")
print("✓ Limpeza concluída!")
