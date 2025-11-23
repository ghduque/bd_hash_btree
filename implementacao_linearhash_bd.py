import sys

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
        # print(f"Debug: Inserido no índice {idx}")

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

    def buscar_intervalo(self, inicio, fim):
        """
        Retorna todos os registros cuja chave está entre inicio e fim.
        Obs: Em Hash, isso exige varredura completa (O(N)).
        """
        resultados = []
        for item in self.table:
            # Ignora espaços vazios e itens deletados
            if item is not None and item is not self.TOMBSTONE:
                chave = item[0]
                if inicio <= chave <= fim:
                    resultados.append(item)
        
        # Ordena pelo primeiro campo (chave) para manter consistência com a B-Tree
        resultados.sort(key=lambda x: x[0])
        return resultados

    def exibir(self):
        print("\n--- Estrutura da Tabela Hash ---")
        print(f"Ocupação: {self.count}/{self.capacity}")
        for i, item in enumerate(self.table):
            if item is None:
                print(f"[{i:03d}]: [ Livre ]")
            elif item is self.TOMBSTONE:
                print(f"[{i:03d}]: [ REMOVIDO ]")
            else:
                print(f"[{i:03d}]: {item}")
        print("\n")


# --- PROGRAMA PRINCIPAL ---
# (Mesma estrutura do seu código original)

print("Programa Tabela Hash Linear (Simulação)")
print("Configurando a tabela...")

try:
    entrada_pag = input("Digite o tamanho total em bytes (ex: 128, 1024) [Padrão: 128]: ")
    tam_total = int(entrada_pag) if entrada_pag.strip() else 128

    entrada_campos = input("Digite o número de campos inteiros por registro (ex: 3) [Padrão: 3]: ")
    num_campos = int(entrada_campos) if entrada_campos.strip() else 3

    # Instancia a Hash em vez da BTree
    tab = HashLinear(num_campos, tam_total)
except (ValueError, EOFError, KeyboardInterrupt):
    print("\nEntrada inválida ou interrompida. Usando padrões (128 bytes, 3 campos).")
    tab = HashLinear(3, 128)
    num_campos = 3

opcao = 0
while opcao != 6:
    print("\n***********************************")
    print("Entre com a opcao:")
    print(" --- 1: Inserir Registro")
    print(" --- 2: Excluir Chave")
    print(" --- 3: Pesquisar por Igualdade")
    print(" --- 4: Pesquisar por Intervalo (Range)")
    print(" --- 5: Exibir Estrutura")
    print(" --- 6: Sair")
    print("***********************************")
    
    try:
        entrada_op = input("-> ")
        if not entrada_op: 
            continue
        opcao = int(entrada_op)
    except ValueError:
        print("Opção inválida.")
        continue
    except (EOFError, KeyboardInterrupt):
        print("\nEntrada interrompida. Encerrando programa.")
        break

    if opcao == 1:
        print(f" Informe os {num_campos} valores inteiros separados por espaço.")
        print(" Exemplo: 10 100 200")
        try:
            entrada = input(" Valores -> ").split()
            if len(entrada) != num_campos:
                print(f" Erro: Você precisa digitar exatamente {num_campos} números.")
            else:
                registro = tuple(map(int, entrada))
                tab.inserir(registro)
                print(" Operação de inserção concluída.")
        except ValueError:
            print("Erro: Apenas números inteiros são aceitos.")
        except (EOFError, KeyboardInterrupt):
            break

    elif opcao == 2:
        try:
            chave = int(input(" Informe a chave (1º campo) para excluir -> "))
            if tab.remover(chave):
                print(" Removido com sucesso.")
            else:
                print(" Chave nao encontrada!")
        except ValueError:
            print("Erro: Chave deve ser um número.")
        except (EOFError, KeyboardInterrupt):
            break

    elif opcao == 3:
        try:
            chave = int(input(" Informe a chave para buscar -> "))
            res = tab.buscar(chave)
            if res:
                print(f" Registro Encontrado: {res}")
            else:
                print(" Valor nao encontrado!")     
        except ValueError:
            print("Erro: Chave deve ser um número.")
        except (EOFError, KeyboardInterrupt):
            break

    elif opcao == 4:
        try:
            ini = int(input(" Chave inicial -> "))
            fim = int(input(" Chave final -> "))
            lista = tab.buscar_intervalo(ini, fim)
            print(f" Encontrados {len(lista)} registros no intervalo [{ini}, {fim}]:")
            for item in lista:
                print(f"  -> {item}")
        except ValueError:
             print("Erro: Chaves devem ser números.")
        except (EOFError, KeyboardInterrupt):
            break

    elif opcao == 5:
        tab.exibir()

    elif opcao == 6:
        print(" Encerrando...")
        break