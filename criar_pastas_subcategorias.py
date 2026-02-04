import csv
import os
from pathlib import Path

# Caminho do arquivo CSV
csv_path = "(OFICIAL) CTD - PROCESSOS - PROCESSOS.csv"

# Ler o CSV
print("Lendo a planilha...")
subcategorias = set()

try:
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        
        # Pular as primeiras 3 linhas (cabeçalho está na linha 4)
        for _ in range(3):
            next(reader)
        
        # Ler o cabeçalho
        header = next(reader)
        
        # Encontrar o índice da coluna SUB-CATEGORIA PRINCIPAL
        try:
            indice_subcategoria = header.index('SUB-CATEGORIA PRINCIPAL')
            print(f"Coluna 'SUB-CATEGORIA PRINCIPAL' encontrada no índice {indice_subcategoria}")
        except ValueError:
            print("Coluna 'SUB-CATEGORIA PRINCIPAL' não encontrada!")
            print("Colunas disponíveis:", header)
            exit(1)
        
        # Ler todas as linhas e extrair subcategorias
        linha_num = 4
        for row in reader:
            linha_num += 1
            if len(row) > indice_subcategoria:
                subcategoria = row[indice_subcategoria].strip()
                if subcategoria and subcategoria.lower() != 'nan' and subcategoria:
                    subcategorias.add(subcategoria)
        
        print(f"Total de linhas processadas: {linha_num}")
        
except Exception as e:
    print(f"Erro ao ler o arquivo: {e}")
    exit(1)

# Ordenar alfabeticamente
subcategorias_sorted = sorted(subcategorias)

print(f"\nTotal de subcategorias principais encontradas: {len(subcategorias_sorted)}")
print("\nSubcategorias principais:")
for i, subcat in enumerate(subcategorias_sorted, 1):
    print(f"{i}. {subcat}")

# Criar as pastas
print("\n" + "="*60)
print("Criando pastas para cada subcategoria principal...")
print("="*60 + "\n")

pastas_criadas = []
pastas_erro = []

for subcategoria in subcategorias_sorted:
    try:
        # Criar nome de pasta válido (remover caracteres especiais problemáticos)
        nome_pasta = subcategoria.replace('/', '-').replace('\\', '-')
        
        # Criar a pasta
        Path(nome_pasta).mkdir(parents=True, exist_ok=True)
        pastas_criadas.append(nome_pasta)
        print(f"✓ Pasta criada: {nome_pasta}")
    except Exception as e:
        pastas_erro.append((subcategoria, str(e)))
        print(f"✗ Erro ao criar pasta '{subcategoria}': {e}")

# Resumo final
print("\n" + "="*60)
print("RESUMO")
print("="*60)
print(f"Total de pastas criadas com sucesso: {len(pastas_criadas)}")
if pastas_erro:
    print(f"Total de erros: {len(pastas_erro)}")
    print("\nErros:")
    for nome, erro in pastas_erro:
        print(f"  - {nome}: {erro}")
else:
    print("Todas as pastas foram criadas com sucesso!")

print("\nProcesso concluído!")
