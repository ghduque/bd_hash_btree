import csv
import time

# --- Constantes de Configuração ---
INT_SIZE = 4      # Tamanho de um inteiro em bytes

class HashLinear:
    """
    Implementação de Tabela Hash com Tratamento de Colisão Linear (Linear Probing).
    Simula um arquivo de tamanho fixo definido por bytes.
    """
    def __init__(self, num_campos, tamanho_total_bytes):
        self.num_fields = num_campos
        self.total_bytes = tamanho_total_bytes
        
        # Objeto sentinela para remoção lógica (Lazy Deletion)
        self.TOMBSTONE = object()

        # --- CÁLCULOS DE CAPACIDADE ---
        # Tamanho do Registro = num_campos * 4 bytes
        self.record_size = num_campos * INT_SIZE
        
        # Capacidade: Quantos registros cabem no total de bytes fornecido?
        # Na Hash, o "tamanho da página" aqui representa o tamanho total do array
        self.capacity = tamanho_total_bytes // self.record_size
        
        # Segurança mínima
        if self.capacity < 1: 
            self.capacity = 1

        # Inicializa a tabela com None
        self.table = [None] * self.capacity
        self.count = 0

        print(f"--- Hash Linear Inicializada ---")
        print(f"Espaço Total: {tamanho_total_bytes} bytes | Campos por registro: {num_campos}")
        print(f"Capacidade da Tabela: {self.capacity} registros")

    def _hash(self, chave):
        return chave % self.capacity

    # *********************************************************************************
    # MÉTODO DE INSERÇÃO
    # *********************************************************************************
    def inserir(self, registro):
        # Validação simples dos campos
        if len(registro) != self.num_fields:
            print(f"Erro: O registro deve ter exatamente {self.num_fields} campos.")
            return

        if self.count >= self.capacity:
            print("Erro: Tabela Hash CHEIA (Overflow). Não é possível inserir.")
            return

        chave = registro[0] # A chave primária é o primeiro campo
        idx = self._hash(chave)
        start_idx = idx

        # Busca slot vazio ou verifica duplicata
        while self.table[idx] is not None and self.table[idx] is not self.TOMBSTONE:
            # Se encontrar a chave, atualiza (ou rejeita duplicata)
            if self.table[idx][0] == chave:
                print(f"Erro: Chave {chave} já existe na posição {idx}.")
                return
            
            # Sondagem Linear
            idx = (idx + 1) % self.capacity
            
            # Se deu a volta completa (segurança, embora o check de count evite isso)
            if idx == start_idx:
                print("Erro crítico: Tabela cheia (loop detectado).")
                return

        # Insere no slot encontrado (None ou Tombstone)
        self.table[idx] = registro
        self.count += 1

    # *********************************************************************************
    # MÉTODO DE REMOÇÃO (Lazy Deletion)
    # *********************************************************************************
    def remover(self, chave):
        idx = self._hash(chave)
        start_idx = idx

        while self.table[idx] is not None:
            # Se não é Tombstone e a chave bate
            if self.table[idx] is not self.TOMBSTONE and self.table[idx][0] == chave:
                self.table[idx] = self.TOMBSTONE # Marca como deletado logicamente
                self.count -= 1
                return True
            
            idx = (idx + 1) % self.capacity
            if idx == start_idx:
                break
        
        return False # Não encontrado

    # *********************************************************************************
    # MÉTODOS DE BUSCA
    # *********************************************************************************
    def buscar(self, chave):
        idx = self._hash(chave)
        start_idx = idx

        while self.table[idx] is not None:
            if self.table[idx] is not self.TOMBSTONE and self.table[idx][0] == chave:
                return self.table[idx]
            
            idx = (idx + 1) % self.capacity
            if idx == start_idx:
                break
        
        return None

    def exibir(self, mostrar_tudo=False):
        print("\n--- Estrutura da Tabela Hash ---")
        print(f"Ocupação: {self.count}/{self.capacity}")
        print(f"Taxa de ocupação: {(self.count/self.capacity)*100:.2f}%\n")
        
        if mostrar_tudo:
            # Mostra toda a tabela
            for i, item in enumerate(self.table):
                if item is None:
                    print(f"[{i:04d}]: [ Livre ]")
                elif item is self.TOMBSTONE:
                    print(f"[{i:04d}]: [ REMOVIDO ]")
                else:
                    print(f"[{i:04d}]: {item}")
        else:
            # Mostra apenas registros ocupados e removidos
            print("Posições OCUPADAS:")
            ocupadas = 0
            for i, item in enumerate(self.table):
                if item is not None and item is not self.TOMBSTONE:
                    print(f"[{i:04d}]: {item}")
                    ocupadas += 1
                    if ocupadas >= 50:  # Limita a 50 registros mostrados
                        print(f"... (mostrando primeiros 50 registros ocupados)")
                        break
            
            print("\nPosições REMOVIDAS (TOMBSTONE):")
            removidas = 0
            for i, item in enumerate(self.table):
                if item is self.TOMBSTONE:
                    print(f"[{i:04d}]: [ REMOVIDO ]")
                    removidas += 1
                    if removidas >= 20:  # Limita a 20 removidos mostrados
                        print(f"... (mostrando primeiros 20 registros removidos)")
                        break
            
            if ocupadas == 0 and removidas == 0:
                print("(Tabela vazia)")
        
        print("\n")


# --- FUNÇÃO PARA PROCESSAR CSV ---
def processar_csv(arquivo_csv, tabela):
    """
    Lê o arquivo CSV e executa as operações automaticamente.
    Formato esperado: OP,A1,A2,A3
    - +,val1,val2,val3 (INSERÇÃO)
    - -,chave (REMOÇÃO)
    - ?,chave (BUSCA)
    """
    # Variáveis para armazenar tempos
    tempos_insercao = []
    tempos_delecao = []
    tempos_busca = []
    
    try:
        with open(arquivo_csv, 'r', encoding='utf-8') as arquivo:
            leitor = csv.reader(arquivo)
            
            # Contadores
            insercoes = 0
            deletes = 0
            buscas = 0
            linha_num = 0
            
            # Pula o cabeçalho se existir
            primeira_linha = next(leitor, None)
            if primeira_linha and primeira_linha[0].strip().upper() == 'OP':
                print(f"Cabeçalho detectado: {primeira_linha}\n")
            else:
                # Se não é cabeçalho, processa essa linha
                if primeira_linha:
                    linha_num += 1
                    operacao = primeira_linha[0].strip()
                    if operacao == '+':
                        sucesso, tempo = processar_insercao(primeira_linha, tabela)
                        insercoes += sucesso
                        if sucesso:
                            tempos_insercao.append(tempo)
                    elif operacao == '-':
                        sucesso, tempo = processar_delete(primeira_linha, tabela)
                        deletes += sucesso
                        if sucesso:
                            tempos_delecao.append(tempo)
                    elif operacao == '?':
                        sucesso, tempo = processar_busca(primeira_linha, tabela)
                        buscas += sucesso
                        if sucesso:
                            tempos_busca.append(tempo)
            
            # Processa cada linha
            for linha in leitor:
                if not linha or not linha[0]:
                    continue
                
                linha_num += 1
                operacao = linha[0].strip()
                
                if operacao == '+':
                    sucesso, tempo = processar_insercao(linha, tabela)
                    insercoes += sucesso
                    if sucesso:
                        tempos_insercao.append(tempo)
                elif operacao == '-':
                    sucesso, tempo = processar_delete(linha, tabela)
                    deletes += sucesso
                    if sucesso:
                        tempos_delecao.append(tempo)
                elif operacao == '?':
                    sucesso, tempo = processar_busca(linha, tabela)
                    buscas += sucesso
                    if sucesso:
                        tempos_busca.append(tempo)
                else:
                    print(f"⚠ Linha {linha_num}: Operação desconhecida '{operacao}'")
            
            # Resumo final
            print("\n" + "="*60)
            print("RESUMO DAS OPERAÇÕES")
            print("="*60)
            print(f"Total de linhas processadas: {linha_num}")
            print(f"Total de Inserções: {insercoes}")
            print(f"Total de Deleções: {deletes}")
            print(f"Total de Buscas: {buscas}")
            print(f"Registros atualmente na tabela: {tabela.count}")
            print("="*60)
            
            # Estatísticas de tempo
            print("\nESTATÍSTICAS DE TEMPO DE EXECUÇÃO")
            print("="*60)
            
            if tempos_insercao:
                print(f"\nINSERÇÕES:")
                print(f"  - Tempo total: {sum(tempos_insercao)*1000:.4f} ms")
                print(f"  - Tempo médio: {(sum(tempos_insercao)/len(tempos_insercao))*1000:.4f} ms")
                print(f"  - Tempo mínimo: {min(tempos_insercao)*1000:.4f} ms")
                print(f"  - Tempo máximo: {max(tempos_insercao)*1000:.4f} ms")
            
            if tempos_delecao:
                print(f"\nDELEÇÕES:")
                print(f"  - Tempo total: {sum(tempos_delecao)*1000:.4f} ms")
                print(f"  - Tempo médio: {(sum(tempos_delecao)/len(tempos_delecao))*1000:.4f} ms")
                print(f"  - Tempo mínimo: {min(tempos_delecao)*1000:.4f} ms")
                print(f"  - Tempo máximo: {max(tempos_delecao)*1000:.4f} ms")
            
            if tempos_busca:
                print(f"\nBUSCAS:")
                print(f"  - Tempo total: {sum(tempos_busca)*1000:.4f} ms")
                print(f"  - Tempo médio: {(sum(tempos_busca)/len(tempos_busca))*1000:.4f} ms")
                print(f"  - Tempo mínimo: {min(tempos_busca)*1000:.4f} ms")
                print(f"  - Tempo máximo: {max(tempos_busca)*1000:.4f} ms")
            
            print("="*60)
            
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{arquivo_csv}' não encontrado!")
        print("Certifique-se de que o arquivo está no mesmo diretório do script.")
    except Exception as e:
        print(f"ERRO ao processar CSV: {e}")
        import traceback
        traceback.print_exc()

def processar_linha(linha, tabela):
    """Processa uma única linha do CSV"""
    if not linha or not linha[0]:
        return
    
    operacao = linha[0].strip()
    
    if operacao == '+':
        processar_insercao(linha, tabela)
    elif operacao == '-':
        processar_delete(linha, tabela)
    elif operacao == '?':
        processar_busca(linha, tabela)

def processar_insercao(linha, tabela):
    """Processa uma operação de inserção (+,A1,A2,A3)"""
    try:
        valores = [int(v.strip()) for v in linha[1:] if v.strip()]
        if len(valores) == tabela.num_fields:
            registro = tuple(valores)
            
            # Marca o tempo de início
            inicio = time.perf_counter()
            tabela.inserir(registro)
            # Marca o tempo de fim
            fim = time.perf_counter()
            tempo_execucao = fim - inicio
            
            print(f"✓ INSERÇÃO (+): {registro} - Tempo: {tempo_execucao*1000:.4f} ms")
            return 1, tempo_execucao
        else:
            print(f"✗ INSERÇÃO (+): Número incorreto de campos. Esperado {tabela.num_fields}, recebido {len(valores)}")
            return 0, 0
    except ValueError as e:
        print(f"✗ INSERÇÃO (+): Erro ao converter valores - {e}")
        return 0, 0

def processar_delete(linha, tabela):
    """Processa uma operação de deleção (-,chave)"""
    try:
        chave = int(linha[1].strip())
        
        # Marca o tempo de início
        inicio = time.perf_counter()
        resultado = tabela.remover(chave)
        # Marca o tempo de fim
        fim = time.perf_counter()
        tempo_execucao = fim - inicio
        
        if resultado:
            print(f"✓ REMOÇÃO (-): Chave {chave} removida - Tempo: {tempo_execucao*1000:.4f} ms")
            return 1, tempo_execucao
        else:
            print(f"✗ REMOÇÃO (-): Chave {chave} não encontrada")
            return 0, 0
    except (ValueError, IndexError) as e:
        print(f"✗ REMOÇÃO (-): Erro - {e}")
        return 0, 0

def processar_busca(linha, tabela):
    """Processa uma operação de busca (?,chave)"""
    try:
        chave = int(linha[1].strip())
        
        # Marca o tempo de início
        inicio = time.perf_counter()
        resultado = tabela.buscar(chave)
        # Marca o tempo de fim
        fim = time.perf_counter()
        tempo_execucao = fim - inicio
        
        if resultado:
            print(f"✓ BUSCA (?): Chave {chave} -> {resultado} - Tempo: {tempo_execucao*1000:.4f} ms")
            return 1, tempo_execucao
        else:
            print(f"✗ BUSCA (?): Chave {chave} não encontrada")
            return 0, 0
    except (ValueError, IndexError) as e:
        print(f"✗ BUSCA (?): Erro - {e}")
        return 0, 0


# --- PROGRAMA PRINCIPAL ---
if __name__ == "__main__":
    print("="*60)
    print("TABELA HASH LINEAR COM AUTOMAÇÃO VIA CSV")
    print("="*60)
    
    # Configuração: 256KB de espaço total
    TAMANHO_TOTAL = 256 * 1024  # 256KB = 262144 bytes
    
    # Número de campos por registro (ajuste conforme seu CSV)
    NUM_CAMPOS = 3
    
    print(f"\nConfigurações:")
    print(f"- Tamanho total: {TAMANHO_TOTAL} bytes (256 KB)")
    print(f"- Campos por registro: {NUM_CAMPOS}")
    
    # Inicializa a tabela hash
    tabela = HashLinear(NUM_CAMPOS, TAMANHO_TOTAL)
    
    # Nome do arquivo CSV
    arquivo_csv = "dados_hash.csv"
    
    print(f"\nProcessando arquivo: {arquivo_csv}")
    print("="*60)
    
    # Processa o CSV
    processar_csv(arquivo_csv, tabela)
    
    # Exibe a estrutura final da tabela
    print("\n" + "="*60)
    print("ESTRUTURA FINAL DA TABELA HASH")
    print("="*60)
    tabela.exibir()