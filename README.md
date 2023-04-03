# Controle Veícular - Rastreador

## Resumo

*  Projeto em Python para realizar o controle dos veículos da empresa.

## Visão geral

Afim de detectar a utilização dos veículos da empresa de forma inapropriada, rodando com os veículos para atividades pessoais e fora do periodo autorizado, foi desenvolvido este projeto em Python que visa utilizar da API de rastreamento que os veículos possuem.

Assim que um veículo ultrapassa, tanto antes, como depois do limite de rodagem, será registrado uma nova ocorrência no sistema, deixando registrado o primeiro e o ultimo horário que o veículo ficou em funcionamento durante o periodo restrito.

## Funcionamento

O programa foi desenvolvido em torno da biblioteca [Rocketry](https://github.com/Miksus/rocketry), o programa rodará a avaliação a cada 1 minuto, buscando por veículos em situação inconforme.

O programa se limita a execução no terminal, podendo e sendo utilizado como serviço.