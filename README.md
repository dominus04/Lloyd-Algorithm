## Criação de um IVF par aplicação na rinha de backend

O desafio atual é a criação de uma api que processe pagamentos no cartão de crédito e categorize como fraud ou legit, baseando-se em transações passadas.
O problema é que temos um .json de 300MB e um limite de 350MB para rodar um load balancer e duas APIs.
Além disso temos um tempo máximo para retornar a resposta, sendo assim não havia como eu ficar procurando em cada uma das milhões de transações disponíveis. Depois de ler muitos materiais e assistir diversos vídeos, cheguei a conclusão de que a melhor abordagem era um Inverted Index, com a quantização dos dados.
Sendo assim, essa é a implementação em python do IVF, tanto da busca, quanto da clusterização dos dados.

- A ideia do IVF é separar os dados em K regiões de N dimensões, buscando possuir o maior nível belanceamento dos clusters.
- Na hora da busca, primeiro nós buscamos o cluster que está mais próximo do ponto que buscamos, e após isso buscamos na força bruta pelos 5 pontos vizinhos mais próximos do nosso ponto procurado.
- Após encontrar os 5, ainda temos um problema, caso o ponto estivesse localizado na borda de um cluster, é possível que houvesse um ponto mais próximo dele, no cluster vizinho, sendo assim, precisamos verificar a distância entre o 5 ponto mais próximo e o bounding box, que é a fronteira do próximo cluster.
Caso essa distância seja menor que a do pior ponto, verificamos também o cluster vizinho.
- O problema é que conforme crescem as dimensões, a distância entre as bordas começa a ficar muito pequena, enquanto a distância entre os pontos cresce, fazendo com que várias Bounding Boxes sejam consideradas próximas, para isso nós limitamos a quantidade de clusters visitados.
- O código foi todo feito por mim e posteriormente lapidado utilizando IA, apenas para melhorar a performance.

A ideia agora é utilizar essa lógica, para criar o mesmo algoritmo em Go, linguagem que eu utilizarei para a rinha e além disso fazer esse processamento apenas na inicialização do container, para que depois as APIs apenas consumam o binário já processado.