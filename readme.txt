TRABALHO PRATICO - ORGANIZACAO E RECUPERACAO DE DADOS

1. CONTEUDO DA ENTREGA

Este trabalho possui duas versoes independentes do programa:

- parte1/trabalho1.py
  Implementa somente o Trabalho 1: busca, insercao ao final do arquivo e
  remocao logica simples.

- parte2/trabalho2.py
  Implementa o Trabalho 2: busca, insercao com Best Fit, remocao com LED,
  impressao da LED e calculo das estatisticas solicitadas.

- guia_das_aulas_e_requisitos.txt
  Relaciona as funcoes do codigo com os conteudos estudados e mostra como cada
  requisito do enunciado foi resolvido.



2. REQUISITOS PARA EXECUCAO

- Python 3
- Nenhuma biblioteca externa e necessaria.

O programa usa apenas recursos nativos de Python, principalmente:
open, try-except, close, read, write, seek, to_bytes, int.from_bytes,
encode e decode.


3. COMO EXECUTAR

Abra um terminal dentro da pasta desejada e execute:

PARTE 1

cd parte1
python trabalho1.py

PARTE 2

cd parte2
python trabalho2.py

Em alguns computadores, o comando pode ser:

python3 trabalho1.py
python3 trabalho2.py

O arquivo filmes.dat sera criado automaticamente na mesma pasta do programa
na primeira execucao. Cada parte possui seu proprio filmes.dat, evitando que
testes de uma parte alterem os dados da outra.

Caso queira iniciar a Parte 2 com os filmes cadastrados na Parte 1, copie o
arquivo parte1/filmes.dat para a pasta parte2/ antes de executar trabalho2.py.
A estrutura dos registros ativos e compativel entre as duas partes.


4. FORMATO FISICO DO ARQUIVO

Os 4 primeiros bytes sao o cabecalho do arquivo:

[4 bytes - inteiro com sinal]

- Na Parte 1, ele permanece com o valor -1.
- Na Parte 2, ele guarda o byte-offset do primeiro espaco da LED.
- O valor -1 representa LED vazia.

A partir do byte 4, cada registro possui:

[2 bytes - tamanho do registro][dados do filme]

Os dados de um filme ativo usam campos separados por |:

ID|Titulo|Diretor|Ano|Genero(s)|Duracao|Elenco

Exemplo:

10|Interestelar|Christopher Nolan|2014|Ficcao cientifica|169|Matthew McConaughey, Anne Hathaway

O caractere | nao pode ser utilizado dentro de nenhum campo digitado pelo
usuario, pois ele e o delimitador dos campos.


5. OPERACOES DO TRABALHO 1

1 - Buscar um filme
    Solicita o ID e percorre sequencialmente os registros ativos ate encontrar
o filme. Se o ID nao existir, mostra mensagem de erro.

2 - Inserir um novo filme
    Solicita ID, titulo, diretor, ano, genero(s), duracao e elenco. O programa
verifica se ja existe um registro ativo com o mesmo ID e, se nao existir,
gravara o novo registro no final do arquivo.

3 - Remover um filme
    Solicita o ID e realiza remocao logica. O primeiro byte dos dados do
registro e substituido por *. Os bytes do registro nao sao apagados e a LED
ainda nao e usada nesta parte.


6. OPERACOES DO TRABALHO 2

1 - Buscar um filme
    Igual a Parte 1, ignorando registros removidos.

2 - Inserir um novo filme
    Consulta a LED ordenada por tamanho crescente. O primeiro espaco que
comporta o novo registro e selecionado, implementando Best Fit. Quando nao
existe espaco suficiente, o registro e gravado no fim do arquivo.

3 - Remover um filme
    Realiza remocao logica e insere o espaco removido na LED, preservando o
tamanho e usando 4 bytes para o ponteiro para o proximo espaco disponivel.

4 - Imprimir LED e estatisticas
    Exibe cada offset e tamanho da LED, alem de quantidade de espacos, soma dos
bytes livres, maior espaco e menor espaco.


7. DECISAO SOBRE A SOBRA AO REUTILIZAR UM ESPACO

Quando um registro novo ocupa apenas parte de um espaco da LED, a sobra fica
como fragmentacao interna. O tamanho original do espaco e preservado para que
a proxima leitura do arquivo continue no offset correto. A sobra e preenchida
com espacos em branco e nao retorna para a LED, comportamento permitido pelo
enunciado para a estrategia Best Fit.

