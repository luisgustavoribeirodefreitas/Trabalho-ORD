# Luís Gustavo Ribeiro de  Freitas - RA: 143379 | Gabriel Akira Ikuta - RA: 145129 |Matheus Pinheiro Faria - RA: 145127
# Trabalho 1 - Manipulação de Registros
# Disciplina: Organização e Recuperação de Dados

NOME_ARQ = "filmes.dat"
TAM_CABECALHO = 4
TAM_TAMANHO = 2
MARCADOR_REMOVIDO = b"*"


def abriArquivo():
    # Aula 3 - Criar e abrir arquivos / try-except.
    # Aqui o arquivo e aberto para leitura e escrita em modo binario, se ele ja existir, preseva o conteudo; 
    # mas se ainda nao existir é criado o arquivo e colocamos o cabecalho que o enunciado exige.
    try:
        arq = open(NOME_ARQ, "r+b")
        return arq

    except:
        try:
            arq = open(NOME_ARQ, "w+b")
            # O enunciado do trabalho pede 4 bytes com sinal no inicio do arquivo. O -1 nao sera
            # alterado nesta Parte 1, mas ja deixa o arquivo pronto para a LED da Parte 2.
            arq.write((-1).to_bytes(TAM_CABECALHO, signed=True))

            print("Arquivo filmes.dat criado com sucesso.")
            return arq

        except:
            print("Erro: nao foi possivel abrir ou criar o arquivo filmes.dat.")
            return None


def lerRegistro(arq):
    # Aula 4 - Registros com indicador de tamanho.
    # Professor, antes dos dados de cada filme existem 2 bytes informando o tamanho
    # do registro. Assim sabemos exatamente quantos bytes ler, mesmo que cada filme
    # tenha titulo, elenco e outros campos com tamanhos diferentes.
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


def registroFoiRemovido(dados):
    # Aula 5 - Remocao logica.
    # Um asterisco no inicio dos dados avisa que aquele espaco ainda existe fisicamente,
    # mas o filme nao pode mais aparecer em buscas.
    return dados[0:1] == MARCADOR_REMOVIDO


def transformarFilmeEmBytes(filme):
    # Aula 3 - Arquivos binarios: encode transforma texto em bytes.
    # Aula 4 - Campos com delimitador: usamos | entre os 7 campos do filme.
    # Como o tamanho do registro ja informa onde ele termina, nao precisamos de um |
    # depois do elenco.
    texto = (filme[0] + "|" + filme[1] + "|" + filme[2] + "|" +
             filme[3] + "|" + filme[4] + "|" + filme[5] + "|" + filme[6])

    return texto.encode()


def transformarBytesEmFilme(dados):
    # Aula 3 - decode transforma os bytes lidos de volta para texto.
    # Aula 4 - split pelo delimitador recupera os campos do registro.
    campos = dados.decode().split("|")

    if len(campos) != 7:
        return None

    return campos


def buscarRegistroPorId(arq, id_filme):
    # Aula 6 - Busca sequencial.
    # Professor, como os registros tem tamanho variavel e nao existe indice, a forma
    # adequada e percorrer o arquivo registro por registro a partir do byte 4.
    arq.seek(TAM_CABECALHO)
    registro = lerRegistro(arq)

    while registro != None:
        offset = registro[0]
        tamanho = registro[1]
        dados = registro[2]

        if not registroFoiRemovido(dados):
            filme = transformarBytesEmFilme(dados)

            if filme != None and filme[0] == id_filme:
                return [offset, tamanho, dados]

        registro = lerRegistro(arq)

    return None


def lerNumeroPositivo(mensagem):
    # O ID, o ano e a duracao sao lidos como texto primeiro para evitar que uma
    # entrada invalida interrompa o programa.
    while True:
        valor = input(mensagem).strip()

        if valor.isdigit() and int(valor) > 0:
            # Transformar em inteiro e voltar para texto evita tratar 001 e 1
            # como IDs diferentes.
            return str(int(valor))

        print("Digite um numero inteiro maior que zero.")


def lerTexto(mensagem):
    # Aula 4 - O delimitador nao pode aparecer dentro dos valores dos campos.
    while True:
        valor = input(mensagem).strip()

        if valor == "":
            print("Este campo nao pode ficar vazio.")

        elif "|" in valor:
            print("Este campo nao pode conter o caractere |.")

        else:
            return valor


def lerDadosDoFilme():
    print("\nInforme os dados do filme:")

    id_filme = lerNumeroPositivo("ID: ")
    titulo = lerTexto("Titulo: ")
    diretor = lerTexto("Diretor: ")
    ano = lerNumeroPositivo("Ano: ")
    generos = lerTexto("Genero(s): ")
    duracao = lerNumeroPositivo("Duracao em minutos: ")
    elenco = lerTexto("Elenco: ")

    return [id_filme, titulo, diretor, ano, generos, duracao, elenco]


def exibirFilme(filme):
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


def buscarFilme():
    id_filme = lerNumeroPositivo("\nInforme o ID do filme que deseja buscar: ")
    arq = abriArquivo()

    if arq == None:
        return

    registro = buscarRegistroPorId(arq, id_filme)
    arq.close()

    if registro == None:
        print("Erro: filme nao encontrado.")

    else:
        filme = transformarBytesEmFilme(registro[2])
        exibirFilme(filme)


def inserirFilme():
    filme = lerDadosDoFilme()
    arq = abriArquivo()

    if arq == None:
        return

    # O ID e chave primaria; antes de gravar, verificamos se ja existe um
    # registro ativo com o mesmo ID.
    registro = buscarRegistroPorId(arq, filme[0])

    if registro != None:
        print("Erro: ja existe um filme ativo com esse ID.")
        arq.close()
        return

    dados = transformarFilmeEmBytes(filme)
    tamanho = len(dados)

    # O enunciado reserva 2 bytes sem sinal para o tamanho, portanto o maior
    # registro possivel tem 65535 bytes.
    if tamanho > 65535:
        print("Erro: o registro ultrapassa o limite de 65535 bytes.")
        arq.close()
        return

    # Aula 3 - seek(). O segundo parametro 2 posiciona o ponteiro no fim do arquivo.
    # Na Parte 1 todos os novos filmes sao gravados no final, pois ainda nao existe LED.
    arq.seek(0, 2)
    arq.write(tamanho.to_bytes(TAM_TAMANHO))
    arq.write(dados)
    arq.close()

    print("Filme inserido com sucesso.")


def removerFilme():
    id_filme = lerNumeroPositivo("\nInforme o ID do filme que deseja remover: ")
    arq = abriArquivo()

    if arq == None:
        return

    registro = buscarRegistroPorId(arq, id_filme)

    if registro == None:
        print("Erro: filme nao encontrado.")
        arq.close()
        return

    # Aula 5 - Remocao logica.
    # Professor, o tamanho e os demais bytes do registro continuam no arquivo.
    # Aqui so trocamos o primeiro byte dos dados por *, sem mover os registros seguintes.
    # A LED nao e usada nesta Parte 1; ela sera acrescentada somente no Trabalho 2.
    arq.seek(registro[0] + TAM_TAMANHO)
    arq.write(MARCADOR_REMOVIDO)
    arq.close()

    print("Filme removido logicamente com sucesso.")


def mostrarMenu():
    print("\n" + "=" * 45)
    print("TRABALHO 1 - MANIPULACAO DE REGISTROS")
    print("=" * 45)
    print("1 - Buscar um filme")
    print("2 - Inserir um novo filme")
    print("3 - Remover um filme")
    print("0 - Sair")


def main():
    # Primeiro garantimos que o arquivo exista. Depois cada operacao abre e fecha
    # o arquivo por conta propria, seguindo o tratamento de abertura da Aula 3.
    arq = abriArquivo()

    if arq == None:
        return

    arq.close()

    opcao = ""

    while opcao != "0":
        mostrarMenu()
        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            buscarFilme()

        elif opcao == "2":
            inserirFilme()

        elif opcao == "3":
            removerFilme()

        elif opcao == "0":
            print("Programa encerrado.")

        else:
            print("Opcao invalida.")


if __name__ == "__main__":
    main()
