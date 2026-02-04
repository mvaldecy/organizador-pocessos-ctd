import csv
import os
from pathlib import Path

# Caminho do arquivo CSV
csv_path = "(OFICIAL) CTD - PROCESSOS - PROCESSOS.csv"

print("Lendo a planilha e organizando processos...")

try:
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        
        # Pular as primeiras 3 linhas
        for _ in range(3):
            next(reader)
        
        # Ler o cabeçalho
        header = next(reader)
        
        # Encontrar índices das colunas importantes
        try:
            idx_subcategoria = header.index('SUB-CATEGORIA PRINCIPAL')
            idx_id = header.index('ID')
            idx_processo = header.index('PROCESSO')
            idx_orgao = header.index('ÓRGÃO')
            idx_objeto = header.index('OBJETO')
            idx_valor = header.index('VALOR SOLICITADO')
            idx_status = header.index('STATUS DELIBERAÇÃO CONSELHO ou COMITÊ')
            idx_data = header.index('DATA RECEB CTD')
        except ValueError as e:
            print(f"Erro ao encontrar colunas: {e}")
            exit(1)
        
        # Contadores
        processos_organizados = {}
        total_processos = 0
        
        # Processar cada linha
        for row in reader:
            if len(row) > idx_subcategoria and row[idx_subcategoria].strip():
                subcategoria = row[idx_subcategoria].strip()
                
                if not subcategoria or subcategoria.lower() == 'nan':
                    continue
                
                # Normalizar nome da pasta
                nome_pasta = subcategoria.replace('/', '-')
                
                # Extrair informações do processo
                id_proc = row[idx_id].strip() if len(row) > idx_id else "N/A"
                processo = row[idx_processo].strip() if len(row) > idx_processo else "N/A"
                orgao = row[idx_orgao].strip() if len(row) > idx_orgao else "N/A"
                objeto = row[idx_objeto].strip() if len(row) > idx_objeto else "N/A"
                valor = row[idx_valor].strip() if len(row) > idx_valor else "N/A"
                status = row[idx_status].strip() if len(row) > idx_status else "N/A"
                data = row[idx_data].strip() if len(row) > idx_data else "N/A"
                
                # Criar arquivo para o processo
                if id_proc != "N/A" and processo != "N/A":
                    pasta_destino = Path(nome_pasta)
                    
                    # Criar nome de arquivo seguro
                    nome_arquivo = f"{id_proc}_{processo.replace('/', '-').replace('\\', '-')[:50]}.txt"
                    caminho_arquivo = pasta_destino / nome_arquivo
                    
                    # Escrever informações do processo
                    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                        f.write(f"=" * 80 + "\n")
                        f.write(f"ID: {id_proc}\n")
                        f.write(f"PROCESSO: {processo}\n")
                        f.write(f"=" * 80 + "\n\n")
                        f.write(f"ÓRGÃO: {orgao}\n\n")
                        f.write(f"SUBCATEGORIA: {subcategoria}\n\n")
                        f.write(f"DATA RECEBIMENTO CTD: {data}\n\n")
                        f.write(f"VALOR SOLICITADO: {valor}\n\n")
                        f.write(f"STATUS: {status}\n\n")
                        f.write(f"OBJETO:\n{objeto}\n\n")
                        f.write(f"=" * 80 + "\n")
                    
                    # Contabilizar
                    if subcategoria not in processos_organizados:
                        processos_organizados[subcategoria] = 0
                    processos_organizados[subcategoria] += 1
                    total_processos += 1
                    
                    print(f"✓ Processo {id_proc} organizado em: {nome_pasta}")
        
except Exception as e:
    print(f"Erro ao processar: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Resumo
print("\n" + "=" * 80)
print("RESUMO DA ORGANIZAÇÃO")
print("=" * 80)
print(f"\nTotal de processos organizados: {total_processos}\n")

print("Processos por subcategoria:")
for subcat in sorted(processos_organizados.keys()):
    print(f"  • {subcat}: {processos_organizados[subcat]} processos")

print("\n✓ Organização concluída com sucesso!")
