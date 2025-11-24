import math
import csv
import time

# --- Constantes de Configuração ---
INT_SIZE = 4      # Tamanho de um inteiro em bytes
POINTER_SIZE = 4  # Tamanho de um ponteiro em bytes

class No:
    """
    Representa uma 'Página' da árvore. 
    Pode ser uma folha (guarda registros) ou nó interno (guarda chaves e ponteiros).
    """
    def __init__(self, eh_folha=False, max_keys=0, min_keys=0):
        self.keys = []        # Lista de chaves (ou índices)
        self.children = []    # Se folha: Lista de Registros. Se interno: Lista de Nós filhos.
        self.is_leaf = eh_folha
        self.next_leaf = None # Ponteiro para a próxima folha (lista encadeada no nível inferior)
        self.parent = None    # Referência para o pai (facilita o subir na árvore)
        
        # Limites calculados dinamicamente baseados no tamanho da página
        self.max_keys = max_keys
        self.min_keys = min_keys

    def esta_cheio(self):
        return len(self.keys) > self.max_keys

    def esta_com_underflow(self):
        return len(self.keys) < self.min_keys

    def __repr__(self):
        return f"Keys: {self.keys}"

class BPlusTree:

    def __init__(self, num_campos, tamanho_pagina):
        self.root = None
        self.num_fields = num_campos
        self.page_size = tamanho_pagina
        
        # --- CÁLCULOS DE CAPACIDADE (Didático) ---
        # Tamanho do Registro = num_campos * 4 bytes
        self.record_size = num_campos * INT_SIZE
        self.key_size = INT_SIZE # Chave é o primeiro campo (int)

        # CÁLCULO DE SEGURANÇA: Tamanho Mínimo da Página
        # Para evitar loops infinitos ou estouro de recursão, a página DEVE
        # ser capaz de conter pelo menos 2 registros/chaves para funcionar bem.
        # Custo de 1 entrada na folha = Ponteiro + Chave + Registro (aprox)
        min_page_required = (POINTER_SIZE + self.key_size + self.record_size) * 2
        
        if tamanho_pagina < min_page_required:
            print(f"AVISO: Tamanho da página ({tamanho_pagina}B) muito pequeno para {num_campos} campos.")
            print(f"Ajustando automaticamente para o mínimo seguro: {min_page_required} Bytes.")
            self.page_size = min_page_required
            tamanho_pagina = min_page_required

        # 1. Capacidade do Nó Folha (Onde ficam os dados reais)
        entry_size_leaf = self.key_size + self.record_size
        # Quantos registros cabem na página descontando o ponteiro de ligação?
        self.leaf_capacity = (tamanho_pagina - POINTER_SIZE) // entry_size_leaf
        
        # Garante capacidade mínima de 1 para evitar erros de divisão por zero ou lógica
        if self.leaf_capacity < 1: self.leaf_capacity = 1

        self.leaf_max_keys = self.leaf_capacity
        self.leaf_min_keys = math.ceil(self.leaf_capacity / 2)

        # 2. Capacidade do Nó Interno (Onde ficam apenas referências de navegação)
        # Ordem m: m * ponteiro + (m-1) * chave <= tamanho_pagina
        denom = POINTER_SIZE + self.key_size
        self.internal_order = (tamanho_pagina + self.key_size) // denom
        
        # Garante ordem mínima de 3 (min 2 chaves) para estabilidade
        if self.internal_order < 3: self.internal_order = 3

        self.internal_max_keys = self.internal_order - 1 
        self.internal_min_keys = math.ceil(self.internal_order / 2) - 1

        # Cria a raiz inicial (começa como folha vazia)
        self.root = No(eh_folha=True, max_keys=self.leaf_max_keys, min_keys=self.leaf_min_keys)

        print(f"--- Árvore Inicializada ---")
        print(f"Página Configurada: {tamanho_pagina} bytes | Campos por registro: {num_campos}")
        print(f"Capacidade Folha: {self.leaf_max_keys} registros")
        print(f"Ordem Interna: {self.internal_order} filhos (Máx {self.internal_max_keys} chaves)")

    # *********************************************************************************
    # MÉTODO DE INSERÇÃO
    # Insere um registro completo (tupla). Se a página encher, realiza o SPLIT.
    # *********************************************************************************
    def inserir(self, registro):
        # Validação simples dos campos
        if len(registro) != self.num_fields:
            print(f"Erro: O registro deve ter exatamente {self.num_fields} campos.")
            return

        chave = registro[0] # A chave primária é o primeiro campo
        
        # 1. Busca a folha correta onde a chave deveria estar
        folha = self._buscar_folha(chave)
        
        # 2. Insere o registro na folha de forma ordenada
        self._inserir_na_folha(folha, chave, registro)

        # 3. Verifica se houve estouro da capacidade (Overflow)
        if folha.esta_cheio():
            # **************************************************************
            # A página encheu! Precisamos dividir (Split) e promover chaves.
            # **************************************************************
            chave_sobe, novo_no = self._split(folha)
            
            if folha == self.root:
                # Se a raiz estourou, a árvore cresce em altura
                nova_raiz = No(eh_folha=False, max_keys=self.internal_max_keys, min_keys=self.internal_min_keys)
                nova_raiz.keys = [chave_sobe]
                nova_raiz.children = [folha, novo_no]
                folha.parent = nova_raiz
                novo_no.parent = nova_raiz
                self.root = nova_raiz
            else:
                # Propaga a divisão para o pai
                self._inserir_no_pai(folha.parent, chave_sobe, novo_no)

    def _inserir_na_folha(self, folha, chave, registro):
        # Insere mantendo a ordenação
        if not folha.keys:
            folha.keys.append(chave)
            folha.children.append(registro)
        else:
            # Combina chaves e registros existentes com o novo
            pares_existentes = list(zip(folha.keys, folha.children))
            pares_existentes.append((chave, registro))
            # Ordena todos os pares pela chave
            pares_ordenados = sorted(pares_existentes, key=lambda x: x[0])
            # Separa novamente em chaves e registros
            folha.keys = [p[0] for p in pares_ordenados]
            folha.children = [p[1] for p in pares_ordenados]

    def _split(self, no):
        # Divide o nó em dois.
        # ponto_medio define onde cortamos a lista de chaves
        ponto_medio = len(no.keys) // 2
        
        novo_no = No(eh_folha=no.is_leaf, max_keys=no.max_keys, min_keys=no.min_keys)
        novo_no.parent = no.parent

        chave_sobe = no.keys[ponto_medio]

        if no.is_leaf:
            # Na folha, a chave "que sobe" permanece na direita (cópia) pois é onde está o dado
            novo_no.keys = no.keys[ponto_medio:]
            novo_no.children = no.children[ponto_medio:]
            no.keys = no.keys[:ponto_medio]
            no.children = no.children[:ponto_medio]
            
            # Atualiza a lista encadeada de folhas
            no.next_leaf, novo_no.next_leaf = novo_no, no.next_leaf
            chave_sobe = novo_no.keys[0] # Cópia para o índice
        else:
            # No nó interno, a chave sobe e DESAPARECE do nível atual (ela vira o separador no pai)
            novo_no.keys = no.keys[ponto_medio + 1:]
            novo_no.children = no.children[ponto_medio + 1:]
            no.keys = no.keys[:ponto_medio]
            
            # Move os filhos para o novo pai
            filhos_movidos = no.children[ponto_medio + 1:]
            no.children = no.children[:ponto_medio + 1]
            
            for filho in novo_no.children:
                filho.parent = novo_no

        return chave_sobe, novo_no

    def _inserir_no_pai(self, pai, chave_sobe, novo_filho):
        # Tenta inserir a chave promovida no pai
        if pai.esta_cheio():
            # Se o pai também estiver cheio, recursivamente divide o pai
            chave_pai_sobe, novo_pai = self._split(pai)
            
            # Descobre onde inserir a nova chave (no original ou no novo irmão do pai)
            if chave_sobe < chave_pai_sobe:
                alvo = pai
            else:
                alvo = novo_pai
            
            self._inserir_no_pai_simples(alvo, chave_sobe, novo_filho)
            
            # Verifica se precisa criar nova raiz
            if pai == self.root:
                nova_raiz = No(eh_folha=False, max_keys=self.internal_max_keys, min_keys=self.internal_min_keys)
                nova_raiz.keys = [chave_pai_sobe]
                nova_raiz.children = [pai, novo_pai]
                pai.parent = nova_raiz
                novo_pai.parent = nova_raiz
                self.root = nova_raiz
            else:
                self._inserir_no_pai(pai.parent, chave_pai_sobe, novo_pai)
        else:
            self._inserir_no_pai_simples(pai, chave_sobe, novo_filho)

    def _inserir_no_pai_simples(self, pai, chave, filho):
        # Insere ordenado na lista do pai
        idx = 0
        while idx < len(pai.keys) and chave > pai.keys[idx]:
            idx += 1
        pai.keys.insert(idx, chave)
        pai.children.insert(idx + 1, filho)
        filho.parent = pai

    # *********************************************************************************
    # MÉTODO DE REMOÇÃO
    # Remove a chave. Se houver Underflow (poucas chaves), faz Merge ou Empréstimo.
    # *********************************************************************************
    def remover(self, chave):
        folha = self._buscar_folha(chave)
        
        if chave not in folha.keys:
            return False # Valor não encontrado
        
        # Remove o item
        idx = folha.keys.index(chave)
        folha.keys.pop(idx)
        folha.children.pop(idx)

        # Se for a raiz e ficou vazia
        if folha == self.root:
            if len(folha.keys) == 0:
                # Reinicia a árvore se acabou tudo
                self.root = No(eh_folha=True, max_keys=self.leaf_max_keys, min_keys=self.leaf_min_keys)
        
        # Verifica Underflow (se ficou abaixo do mínimo)
        elif folha.esta_com_underflow():
            self._tratar_underflow(folha)
        
        return True

    def _tratar_underflow(self, no):
        if no == self.root:
            # Se a raiz ficou sem chaves mas tem filho, o filho vira a nova raiz (diminui altura)
            if len(no.keys) == 0 and len(no.children) > 0:
                self.root = no.children[0]
                self.root.parent = None
            return

        pai = no.parent
        idx = pai.children.index(no)
        
        # Tenta pegar irmão da esquerda ou direita
        irmao = None
        eh_irmao_esq = False
        
        if idx > 0:
            irmao = pai.children[idx - 1]
            eh_irmao_esq = True
        elif idx < len(pai.children) - 1:
            irmao = pai.children[idx + 1]
            eh_irmao_esq = False
        
        if not irmao: return 

        # Decisão: Fusão (Merge) ou Redistribuição (Empréstimo)?
        if len(no.keys) + len(irmao.keys) <= no.max_keys:
            self._merge(no, irmao, pai, idx, eh_irmao_esq)
        else:
            self._redistribuir(no, irmao, pai, idx, eh_irmao_esq)

    def _merge(self, no, irmao, pai, idx, eh_irmao_esq):
        # **************************************************************
        # Fusão: Junta o nó atual com o irmão e remove a entrada do pai
        # **************************************************************
        if eh_irmao_esq:
            esq, dir = irmao, no
            idx_sep = idx - 1
        else:
            esq, dir = no, irmao
            idx_sep = idx

        chave_sep = pai.keys[idx_sep]

        if no.is_leaf:
            esq.keys.extend(dir.keys)
            esq.children.extend(dir.children)
            esq.next_leaf = dir.next_leaf
        else:
            esq.keys.append(chave_sep)
            esq.keys.extend(dir.keys)
            esq.children.extend(dir.children)
            for filho in dir.children:
                filho.parent = esq

        # Remove do pai
        pai.keys.pop(idx_sep)
        pai.children.pop(idx_sep + 1)

        if pai.esta_com_underflow():
            self._tratar_underflow(pai)

    def _redistribuir(self, no, irmao, pai, idx, eh_irmao_esq):
        # **************************************************************
        # Empréstimo: Pega uma chave do irmão rico para o pobre
        # **************************************************************
        if no.is_leaf:
            if eh_irmao_esq:
                # Pega o último do irmão esquerdo
                chave = irmao.keys.pop()
                val = irmao.children.pop()
                no.keys.insert(0, chave)
                no.children.insert(0, val)
                pai.keys[idx - 1] = no.keys[0] # Atualiza índice no pai
            else:
                # Pega o primeiro do irmão direito
                chave = irmao.keys.pop(0)
                val = irmao.children.pop(0)
                no.keys.append(chave)
                no.children.append(val)
                pai.keys[idx] = irmao.keys[0] # Atualiza índice no pai
        else:
            # Empréstimo para nós internos (Índices)
            if eh_irmao_esq:
                # O separador do pai desce para o nó atual
                separator_idx = idx - 1
                chave_pai = pai.keys[separator_idx]
                
                # A última chave do irmão sobe para o pai
                chave_irmao = irmao.keys.pop()
                filho_irmao = irmao.children.pop()
                
                no.keys.insert(0, chave_pai)
                no.children.insert(0, filho_irmao)
                filho_irmao.parent = no # Atualiza pai do filho movido
                
                pai.keys[separator_idx] = chave_irmao
            else:
                # O separador do pai desce para o nó atual
                separator_idx = idx
                chave_pai = pai.keys[separator_idx]
                
                # A primeira chave do irmão sobe para o pai
                chave_irmao = irmao.keys.pop(0)
                filho_irmao = irmao.children.pop(0)
                
                no.keys.append(chave_pai)
                no.children.append(filho_irmao)
                filho_irmao.parent = no # Atualiza pai do filho movido
                
                pai.keys[separator_idx] = chave_irmao

    # *********************************************************************************
    # MÉTODOS DE BUSCA
    # *********************************************************************************
    def buscar(self, chave):
        folha = self._buscar_folha(chave)
        # Procura linearmente na página (poderia ser binária)
        for i, k in enumerate(folha.keys):
            if k == chave:
                return folha.children[i] # Retorna o registro completo
        return None

    def buscar_intervalo(self, inicio, fim):
        """Retorna todos os registros cuja chave está entre inicio e fim."""
        resultados = []
        # 1. Encontra a folha onde começa o intervalo
        no_atual = self._buscar_folha(inicio)
        
        # 2. Navega pela lista encadeada de folhas (Next Leaf)
        while no_atual is not None:
            for i, k in enumerate(no_atual.keys):
                if k >= inicio:
                    if k <= fim:
                        resultados.append(no_atual.children[i])
                    else:
                        # Passou do fim do intervalo
                        return resultados
            
            # Se a maior chave dessa página ainda é menor que o fim, vai para a próxima
            if len(no_atual.keys) > 0 and no_atual.keys[-1] <= fim:
                no_atual = no_atual.next_leaf
            else:
                break
        return resultados

    def _buscar_folha(self, chave):
        # Desce na árvore até achar a folha
        atual = self.root
        while not atual.is_leaf:
            idx = 0
            # Na B+ Tree, se chave >= separador, vamos para a direita (índice+1)
            # Ex: Chaves [10]. Filhos [Esq, Dir]. Se chave 10, vai para Dir.
            while idx < len(atual.keys) and chave >= atual.keys[idx]:
                idx += 1
            atual = atual.children[idx]
        return atual

    def exibir(self):
        print("\n--- Estrutura da Árvore (Nível a Nível) ---")
        if not self.root:
            print("Árvore vazia.")
            return
            
        fila = [(self.root, 0)]
        ultimo_nivel = -1
        while fila:
            atual, nivel = fila.pop(0)
            if nivel != ultimo_nivel:
                print(f"\n[Nível {nivel}]:", end=" ")
                ultimo_nivel = nivel
            
            tipo = "Folha" if atual.is_leaf else "Índice"
            print(f"({tipo}: {atual.keys})", end="  ")
            
            if not atual.is_leaf:
                for filho in atual.children:
                    fila.append((filho, nivel + 1))
        print("\n")

#### fim da classe ####

# --- FUNÇÃO PARA PROCESSAR CSV ---
def processar_csv(arquivo_csv, arvore):
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
            
            # Pula o cabeçalho se existir
            primeira_linha = next(leitor, None)
            if primeira_linha and primeira_linha[0].strip().upper() == 'OP':
                print(f"Cabeçalho detectado: {primeira_linha}\n")
            else:
                # Se não é cabeçalho, processa essa linha
                if primeira_linha:
                    processar_linha(primeira_linha, arvore, tempos_insercao, tempos_delecao, tempos_busca)
            
            # Contadores
            insercoes = 0
            deletes = 0
            buscas = 0
            
            # Processa cada linha
            for linha in leitor:
                if not linha or not linha[0]:
                    continue
                
                operacao = linha[0].strip()
                
                if operacao == '+':
                    sucesso, tempo = processar_insercao(linha, arvore)
                    insercoes += sucesso
                    if sucesso:
                        tempos_insercao.append(tempo)
                elif operacao == '-':
                    sucesso, tempo = processar_delete(linha, arvore)
                    deletes += sucesso
                    if sucesso:
                        tempos_delecao.append(tempo)
                elif operacao == '?':
                    sucesso, tempo = processar_busca(linha, arvore)
                    buscas += sucesso
                    if sucesso:
                        tempos_busca.append(tempo)
            
            # Resumo final com estatísticas de tempo
            print("\n" + "="*60)
            print("RESUMO DAS OPERAÇÕES")
            print("="*60)
            print(f"Total de Inserções: {insercoes}")
            print(f"Total de Deleções: {deletes}")
            print(f"Total de Buscas: {buscas}")
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
    except Exception as e:
        print(f"ERRO ao processar CSV: {e}")

def processar_linha(linha, arvore, tempos_insercao, tempos_delecao, tempos_busca):
    """Processa uma única linha do CSV"""
    if not linha or not linha[0]:
        return
    
    operacao = linha[0].strip()
    
    if operacao == '+':
        sucesso, tempo = processar_insercao(linha, arvore)
        if sucesso:
            tempos_insercao.append(tempo)
    elif operacao == '-':
        sucesso, tempo = processar_delete(linha, arvore)
        if sucesso:
            tempos_delecao.append(tempo)
    elif operacao == '?':
        sucesso, tempo = processar_busca(linha, arvore)
        if sucesso:
            tempos_busca.append(tempo)

def processar_insercao(linha, arvore):
    """Processa uma operação de inserção (+,A1,A2,A3)"""
    try:
        valores = [int(v.strip()) for v in linha[1:] if v.strip()]
        if len(valores) == arvore.num_fields:
            registro = tuple(valores)
            
            # Marca o tempo de início
            inicio = time.perf_counter()
            arvore.inserir(registro)
            # Marca o tempo de fim
            fim = time.perf_counter()
            tempo_execucao = fim - inicio
            
            print(f"✓ INSERÇÃO (+): {registro} - Tempo: {tempo_execucao*1000:.4f} ms")
            return 1, tempo_execucao
        else:
            print(f"✗ INSERÇÃO (+): Número incorreto de campos. Esperado {arvore.num_fields}, recebido {len(valores)}")
            return 0, 0
    except ValueError as e:
        print(f"✗ INSERÇÃO (+): Erro ao converter valores - {e}")
        return 0, 0

def processar_delete(linha, arvore):
    """Processa uma operação de deleção (-,chave)"""
    try:
        chave = int(linha[1].strip())
        
        # Marca o tempo de início
        inicio = time.perf_counter()
        resultado = arvore.remover(chave)
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

def processar_busca(linha, arvore):
    """Processa uma operação de busca (?,chave)"""
    try:
        chave = int(linha[1].strip())
        
        # Marca o tempo de início
        inicio = time.perf_counter()
        resultado = arvore.buscar(chave)
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
    print("ÁRVORE B+ COM AUTOMAÇÃO VIA CSV")
    print("="*60)
    
    # Configuração: 256KB de página
    TAMANHO_PAGINA = 256 * 1024  # 256KB = 262144 bytes
    
    # Número de campos por registro (ajuste conforme seu CSV)
    NUM_CAMPOS = 3
    
    print(f"\nConfigurações:")
    print(f"- Tamanho da página: {TAMANHO_PAGINA} bytes (256 KB)")
    print(f"- Campos por registro: {NUM_CAMPOS}")
    
    # Inicializa a árvore
    arvore = BPlusTree(NUM_CAMPOS, TAMANHO_PAGINA)
    
    # Nome do arquivo CSV
    arquivo_csv = "dados_btree.csv"
    
    print(f"\nProcessando arquivo: {arquivo_csv}")
    print("="*60)
    
    # Processa o CSV
    processar_csv(arquivo_csv, arvore)
    
    # Exibe a estrutura final da árvore
    print("\n" + "="*60)
    print("ESTRUTURA FINAL DA ÁRVORE")
    print("="*60)
    arvore.exibir()