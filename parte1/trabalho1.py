# Luís Gustavo Ribeiro de  Freitas - RA: 143379 | Gabriel Akira Ikuta - RA: 145129 |Matheus Pinheiro Faria - RA: 145127
# Trabalho 1 - Manipulação de Registros
# Disciplina: Organização e Recuperação de Dados

NOME_ARQUIVO = "filmes.dat"
TAM_CABECALHO = 4
TAM_TAMANHO = 2
MARCADOR_REMOVIDO = b"*"


def abrir_arquivo():
    # Aula 3 - Criar e abrir arquivos / try-except.
    # Aqui o arquivo e aberto para leitura e escrita em modo binario, se ele ja existir, preseva o conteudo; 
    # mas se ainda nao existir é criado o arquivo e colocamos o cabecalho que o enunciado exige.
    try:
        arq = open(NOME_ARQUIVO, "r+b")
        return arq

    except:
        try:
            arq = open(NOME_ARQUIVO, "w+b")
            # O enunciado do trabalho pede 4 bytes com sinal no inicio do arquivo. O -1 nao sera
            # alterado nesta Parte 1, mas ja deixa o arquivo pronto para a LED da Parte 2.
            arq.write((-1).to_bytes(TAM_CABECALHO, signed=True))

            print("Arquivo filmes.dat criado com sucesso.")
            return arq

        except:
            print("Erro: nao foi possivel abrir ou criar o arquivo filmes.dat.")
            return None


def ler_registro(arq):
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


def registro_foi_removido(dados):
    # Aula 5 - Remocao logica.
    # Um asterisco no inicio dos dados avisa que aquele espaco ainda existe fisicamente,
    # mas o filme nao pode mais aparecer em buscas.
    return dados[0:1] == MARCADOR_REMOVIDO


def transformar_filme_em_bytes(filme):
    # Aula 3 - Arquivos binarios: encode transforma texto em bytes.
    # Aula 4 - Campos com delimitador: usamos | entre os 7 campos do filme.
    # Como o tamanho do registro ja informa onde ele termina, nao precisamos de um |
    # depois do elenco.
    texto = (filme[0] + "|" + filme[1] + "|" + filme[2] + "|" +
             filme[3] + "|" + filme[4] + "|" + filme[5] + "|" + filme[6])

    return texto.encode()


def transformar_bytes_em_filme(dados):
    # Aula 3 - decode transforma os bytes lidos de volta para texto.
    # Aula 4 - split pelo delimitador recupera os campos do registro.
    campos = dados.decode().split("|")

    if len(campos) != 7:
        return None

    return campos


def buscar_registro_por_id(arq, id_filme):
    # Aula 6 - Busca sequencial.
    # Professor, como os registros tem tamanho variavel e nao existe indice, a forma
    # adequada e percorrer o arquivo registro por registro a partir do byte 4.
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


def ler_numero_positivo(mensagem):
    # O ID, o ano e a duracao sao lidos como texto primeiro para evitar que uma
    # entrada invalida interrompa o programa.
    while True:
        valor = input(mensagem).strip()

        if valor.isdigit() and int(valor) > 0:
            # Transformar em inteiro e voltar para texto evita tratar 001 e 1
            # como IDs diferentes.
            return str(int(valor))

        print("Digite um numero inteiro maior que zero.")


def ler_texto_sem_delimitador(mensagem):
    # Aula 4 - O delimitador nao pode aparecer dentro dos valores dos campos.
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

    # O ID e chave primaria; antes de gravar, verificamos se ja existe um
    # registro ativo com o mesmo ID.
    registro = buscar_registro_por_id(arq, filme[0])

    if registro != None:
        print("Erro: ja existe um filme ativo com esse ID.")
        arq.close()
        return

    dados = transformar_filme_em_bytes(filme)
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

    # Aula 5 - Remocao logica.
    # Professor, o tamanho e os demais bytes do registro continuam no arquivo.
    # Aqui so trocamos o primeiro byte dos dados por *, sem mover os registros seguintes.
    # A LED nao e usada nesta Parte 1; ela sera acrescentada somente no Trabalho 2.
    arq.seek(registro[0] + TAM_TAMANHO)
    arq.write(MARCADOR_REMOVIDO)
    arq.close()

    print("Filme removido logicamente com sucesso.")


def mostrar_menu():
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

        elif opcao == "0":
            print("Programa encerrado.")

        else:
            print("Opcao invalida.")


if __name__ == "__main__":
    main()
