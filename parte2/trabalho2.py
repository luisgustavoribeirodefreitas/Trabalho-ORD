# Luís Gustavo Ribeiro de  Freitas - RA: 143379 | Gabriel Akira Ikuta - RA: 145129 |Matheus Pinheiro Faria - RA: 145127
# Trabalho 2 - Gerenciamento da Lista de Espacos Disponiveis (LED)
# Disciplina: Organizacao e Recuperacao de Dados

NOME_ARQUIVO = "filmes.dat"
TAM_CABECALHO = 4
TAM_TAMANHO = 2
TAM_PONTEIRO = 4
MARCADOR_REMOVIDO = b"*"


def abrir_arquivo():
    # Aula 3 - Criar e abrir arquivos / try-except.
    # Professor, aqui o arquivo e aberto para leitura e escrita em modo binario.
    # Se ele ainda nao existir, criamos o arquivo e iniciamos a cabeca da LED com -1.
    try:
        arq = open(NOME_ARQUIVO, "r+b")
        return arq

    except:
        try:
            arq = open(NOME_ARQUIVO, "w+b")

            # Aula 6 - Registro de cabecalho.
            # O enunciado determina que os 4 primeiros bytes guardam o offset do
            # primeiro espaco da LED. -1 significa que a lista esta vazia.
            # signed=True e usado porque -1 e negativo; isso decorre do enunciado.
            arq.write((-1).to_bytes(TAM_CABECALHO, signed=True))

            print("Arquivo filmes.dat criado com sucesso.")
            return arq

        except:
            print("Erro: nao foi possivel abrir ou criar o arquivo filmes.dat.")
            return None


def ler_cabecalho(arq):
    # Aula 6 - Registro de cabecalho.
    # Professor, sempre que precisamos saber onde a LED comeca, voltamos aos
    # 4 primeiros bytes do arquivo. O valor lido e um byte-offset ou -1.
    arq.seek(0)
    bytes_cabecalho = arq.read(TAM_CABECALHO)
    return int.from_bytes(bytes_cabecalho, signed=True)


def escrever_cabecalho(arq, novo_offset):
    # Atualiza a cabeca da LED quando o primeiro no da lista muda.
    arq.seek(0)
    arq.write(novo_offset.to_bytes(TAM_CABECALHO, signed=True))


def ler_registro(arq):
    # Aula 4 - Registros com indicador de tamanho.
    # Os 2 bytes iniciais dizem quantos bytes pertencem ao registro atual, o que
    # permite chegar ao proximo registro sem precisar de um delimitador de registro.
    offset = arq.tell()
    bytes_tamanho = arq.read(TAM_TAMANHO)

    if bytes_tamanho == b"":
        return None

    if len(bytes_tamanho) != TAM_TAMANHO:
        print("Erro: tamanho de registro incompleto no offset", offset)
        return None

    tamanho = int.from_bytes(bytes_tamanho)
    dados = arq.read(tamanho)

    if len(dados) != tamanho:
        print("Erro: dados incompletos no offset", offset)
        return None

    return [offset, tamanho, dados]


def registro_foi_removido(dados):
    # Aula 5 - Remocao logica: * no inicio marca um registro como invalido.
    return dados[0:1] == MARCADOR_REMOVIDO


def transformar_filme_em_bytes(filme):
    # Aula 3 - encode / Aula 4 - campos com delimitador.
    texto = (filme[0] + "|" + filme[1] + "|" + filme[2] + "|" +
             filme[3] + "|" + filme[4] + "|" + filme[5] + "|" + filme[6])
    return texto.encode()


def transformar_bytes_em_filme(dados):
    # Quando reutilizamos um espaco maior que o novo registro, o final recebe
    # espacos em branco e vira fragmentacao interna. O rstrip remove apenas esses
    # espacos antes de separar os campos com |.
    texto = dados.decode().rstrip()
    campos = texto.split("|")

    if len(campos) != 7:
        return None

    return campos


def buscar_registro_por_id(arq, id_filme):
    # Aula 6 - Busca sequencial.
    # Como nao existe indice e os registros sao variaveis, percorremos cada registro
    # desde o final do cabecalho ate encontrar o ID ou chegar ao fim do arquivo.
    arq.seek(TAM_CABECALHO)
    registro = ler_registro(arq)

    while registro != None:
        offset = registro[0]
        tamanho = registro[1]
        dados = registro[2]

        if not registro_foi_removido(dados):
            filme = transformar_bytes_em_filme(dados)

            if filme != None and filme[0] == id_filme:
                return [offset, tamanho, dados]

        registro = ler_registro(arq)

    return None


def ler_tamanho_do_espaco(arq, offset):
    # Aula 6 - acesso direto por byte-offset.
    # O offset recebido aponta para o inicio do registro, ou seja, para os 2 bytes
    # que guardam o tamanho do espaco que esta na LED.
    arq.seek(offset)
    return int.from_bytes(arq.read(TAM_TAMANHO))


def ler_proximo_da_led(arq, offset):
    # Aula 5 - LED dentro do proprio arquivo.
    # Layout de um registro removido: [2 bytes tamanho][*][4 bytes proximo offset].
    arq.seek(offset + TAM_TAMANHO + 1)
    return int.from_bytes(arq.read(TAM_PONTEIRO), signed=True)


def escrever_proximo_da_led(arq, offset, proximo_offset):
    # Atualiza o ponteiro do no localizado em offset. Este ponteiro liga um espaco
    # removido ao proximo espaco disponivel da lista.
    arq.seek(offset + TAM_TAMANHO + 1)
    arq.write(proximo_offset.to_bytes(TAM_PONTEIRO, signed=True))


def inserir_na_led_ordenada(arq, novo_offset, novo_tamanho):
    # Aula 5 - Melhor ajuste (best fit).
    # Professor, para que a insercao encontre o menor espaco que comporta o filme,
    # a LED precisa permanecer ordenada do menor tamanho para o maior tamanho.
    atual = ler_cabecalho(arq)
    anterior = -1

    while atual != -1:
        tamanho_atual = ler_tamanho_do_espaco(arq, atual)

        if novo_tamanho < tamanho_atual:
            break

        anterior = atual
        atual = ler_proximo_da_led(arq, atual)

    # O novo no vai apontar para o no que ficara depois dele na lista.
    escrever_proximo_da_led(arq, novo_offset, atual)

    if anterior == -1:
        # O novo espaco e o menor da lista, entao ele passa a ser a cabeca da LED.
        escrever_cabecalho(arq, novo_offset)

    else:
        # O no anterior agora precisa apontar para o espaco que acabou de entrar.
        escrever_proximo_da_led(arq, anterior, novo_offset)


def encontrar_melhor_espaco(arq, tamanho_necessario):
    # Aula 5 - Best fit.
    # Como a LED esta em ordem crescente, o primeiro espaco com tamanho suficiente
    # ja e o menor espaco capaz de armazenar o novo registro.
    atual = ler_cabecalho(arq)
    anterior = -1

    while atual != -1:
        tamanho_atual = ler_tamanho_do_espaco(arq, atual)

        if tamanho_atual >= tamanho_necessario:
            proximo = ler_proximo_da_led(arq, atual)
            return [anterior, atual, tamanho_atual, proximo]

        anterior = atual
        atual = ler_proximo_da_led(arq, atual)

    return None


def retirar_espaco_da_led(arq, anterior, atual, proximo):
    # Antes de reutilizar um espaco, ele deixa de fazer parte da LED.
    if anterior == -1:
        escrever_cabecalho(arq, proximo)

    else:
        escrever_proximo_da_led(arq, anterior, proximo)


def gravar_no_espaco_reutilizado(arq, offset, tamanho_espaco, dados):
    # Aula 5 - Fragmentacao interna.
    # O tamanho gravado continua sendo o tamanho original do espaco. Assim, a leitura
    # do proximo registro continua no offset correto. A sobra vira espacos em branco
    # dentro do mesmo registro e nao volta para a LED, como permite o enunciado.
    sobra = tamanho_espaco - len(dados)

    arq.seek(offset)
    arq.write(tamanho_espaco.to_bytes(TAM_TAMANHO))
    arq.write(dados)
    arq.write(b" " * sobra)


def ler_numero_positivo(mensagem):
    while True:
        valor = input(mensagem).strip()

        if valor.isdigit() and int(valor) > 0:
            # Transformar em inteiro e voltar para texto evita tratar 001 e 1
            # como IDs diferentes.
            return str(int(valor))

        print("Digite um numero inteiro maior que zero.")


def ler_texto_sem_delimitador(mensagem):
    # Aula 4 - o delimitador escolhido nao pode aparecer nos valores dos campos.
    while True:
        valor = input(mensagem).strip()

        if valor == "":
            print("Este campo nao pode ficar vazio.")

        elif "|" in valor:
            print("Este campo nao pode conter o caractere |.")

        else:
            return valor


def ler_dados_do_filme():
    print("\nInforme os dados do filme:")

    id_filme = ler_numero_positivo("ID: ")
    titulo = ler_texto_sem_delimitador("Titulo: ")
    diretor = ler_texto_sem_delimitador("Diretor: ")
    ano = ler_numero_positivo("Ano: ")
    generos = ler_texto_sem_delimitador("Genero(s): ")
    duracao = ler_numero_positivo("Duracao em minutos: ")
    elenco = ler_texto_sem_delimitador("Elenco: ")

    return [id_filme, titulo, diretor, ano, generos, duracao, elenco]


def exibir_filme(filme):
    print("\nFilme encontrado")
    print("-" * 45)
    print("ID:      ", filme[0])
    print("Titulo:  ", filme[1])
    print("Diretor: ", filme[2])
    print("Ano:     ", filme[3])
    print("Genero(s):", filme[4])
    print("Duracao: ", filme[5], "minutos")
    print("Elenco:  ", filme[6])
    print("-" * 45)


def buscar_filme():
    id_filme = ler_numero_positivo("\nInforme o ID do filme que deseja buscar: ")
    arq = abrir_arquivo()

    if arq == None:
        return

    registro = buscar_registro_por_id(arq, id_filme)
    arq.close()

    if registro == None:
        print("Erro: filme nao encontrado.")

    else:
        filme = transformar_bytes_em_filme(registro[2])
        exibir_filme(filme)


def inserir_filme():
    filme = ler_dados_do_filme()
    arq = abrir_arquivo()

    if arq == None:
        return

    # O ID continua sendo chave primaria, portanto nao pode existir outro filme
    # ativo com o mesmo identificador.
    registro = buscar_registro_por_id(arq, filme[0])

    if registro != None:
        print("Erro: ja existe um filme ativo com esse ID.")
        arq.close()
        return

    dados = transformar_filme_em_bytes(filme)
    tamanho = len(dados)

    if tamanho > 65535:
        print("Erro: o registro ultrapassa o limite de 65535 bytes.")
        arq.close()
        return

    espaco = encontrar_melhor_espaco(arq, tamanho)

    if espaco == None:
        # Aula 5 - se nenhum espaco da LED comportar o registro, a gravacao e feita
        # no final do arquivo e a LED permanece como estava.
        arq.seek(0, 2)
        arq.write(tamanho.to_bytes(TAM_TAMANHO))
        arq.write(dados)
        print("Filme inserido no final do arquivo.")

    else:
        anterior = espaco[0]
        offset = espaco[1]
        tamanho_espaco = espaco[2]
        proximo = espaco[3]

        retirar_espaco_da_led(arq, anterior, offset, proximo)
        gravar_no_espaco_reutilizado(arq, offset, tamanho_espaco, dados)
        print("Filme inserido reutilizando um espaco da LED (best fit).")

    arq.close()


def remover_filme():
    id_filme = ler_numero_positivo("\nInforme o ID do filme que deseja remover: ")
    arq = abrir_arquivo()

    if arq == None:
        return

    registro = buscar_registro_por_id(arq, id_filme)

    if registro == None:
        print("Erro: filme nao encontrado.")
        arq.close()
        return

    offset = registro[0]
    tamanho = registro[1]

    # Aula 5 - LED dentro do arquivo.
    # Professor, primeiro marcamos o registro com *. Depois usamos os 4 bytes seguintes
    # para guardar o ponteiro da lista. O tamanho original permanece preservado.
    arq.seek(offset + TAM_TAMANHO)
    arq.write(MARCADOR_REMOVIDO)

    inserir_na_led_ordenada(arq, offset, tamanho)
    arq.close()

    print("Filme removido e espaco inserido na LED com sucesso.")


def imprimir_led():
    arq = abrir_arquivo()

    if arq == None:
        return

    atual = ler_cabecalho(arq)

    print("\nLED")

    if atual == -1:
        print("[offset: -1]")
        print("Total de espacos: 0")
        print("Total de bytes livres: 0")
        print("Maior espaco: 0 bytes")
        print("Menor espaco: 0 bytes")
        arq.close()
        return

    quantidade = 0
    total_bytes = 0
    maior = 0
    menor = 0

    # Aula 5 - percorremos os ponteiros gravados dentro dos proprios registros removidos.
    while atual != -1:
        tamanho = ler_tamanho_do_espaco(arq, atual)
        proximo = ler_proximo_da_led(arq, atual)

        print("[offset: " + str(atual) + ", tam: " + str(tamanho) + "]")

        quantidade = quantidade + 1
        total_bytes = total_bytes + tamanho

        if quantidade == 1:
            maior = tamanho
            menor = tamanho
        else:
            if tamanho > maior:
                maior = tamanho
            if tamanho < menor:
                menor = tamanho

        atual = proximo

    print("[offset: -1]")
    print("Total de espacos:", quantidade)
    print("Total de bytes livres:", total_bytes)
    print("Maior espaco:", maior, "bytes")
    print("Menor espaco:", menor, "bytes")

    arq.close()


def mostrar_menu():
    print("\n" + "=" * 52)
    print("TRABALHO 2 - LISTA DE ESPACOS DISPONIVEIS (LED)")
    print("=" * 52)
    print("1 - Buscar um filme")
    print("2 - Inserir um novo filme")
    print("3 - Remover um filme")
    print("4 - Imprimir LED e estatisticas")
    print("0 - Sair")


def main():
    arq = abrir_arquivo()

    if arq == None:
        return

    arq.close()

    opcao = ""

    while opcao != "0":
        mostrar_menu()
        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            buscar_filme()

        elif opcao == "2":
            inserir_filme()

        elif opcao == "3":
            remover_filme()

        elif opcao == "4":
            imprimir_led()

        elif opcao == "0":
            print("Programa encerrado.")

        else:
            print("Opcao invalida.")


if __name__ == "__main__":
    main()
