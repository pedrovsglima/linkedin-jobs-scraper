# LinkedIn Jobs Scraper

**Autor:** Pedro Vitor Soares Gomes de Lima

Requisitos para rodar a aplicação: arquivo com credenciais para acessar o Google Sheets e ter o Docker instalado.

<p><a href="https://github.com/peuvitor/linkedin-jobs-scraper">acesso aos arquivos</a></p>

## Overview

Periodicamente extrair do LinkedIn as vagas abertas de **Data Engineer** no **Brasil** e salvar os detalhes de cada uma delas em uma planilha do Google Sheets.

1. O script em shell extrai periodicamente as vagas abertas e salva em uma pasta compartilhada um arquivo .txt com o link de cada uma delas;

2. O script em python:

 - periodicamente (não sincronizado com o script em shell) verifica os arquivos presentes na pasta compartilhada;

 - para cada arquivo encontrado, varre todos os links existentes;

 - em cada link de vaga de emprego extrai-se: o título da vaga, a empresa que está ofertando, o local de trabalho e a descrição;

 - todas essas informações são salvas em uma planilha do Google Sheets, onde cada aba corresponde a um arquivo;

 - após finalizar a carga na planilha, o arquivo com os links das vagas é movido para uma subpasta da pasta compartilhada, de modo a manter o registro de todas as extrações realizadas e salvas.

Resumo do funcionamento:

<p><img src="https://github.com/peuvitor/linkedin-jobs-scraper/blob/main/images/overview.png?raw=true" class="center"></p>

## Mais detalhes

### Automação da aplicação

- a aplicação é executada com um cron job e, para efeito de demonstração, foram escolhidos intervalos de 2 e 11 minutos para os scripts em shell e em python, respectivamente;

- existência de uma aba de consolidação, que guarda um resumo dos dados de todas as outras abas existentes.

### Estrutura dos arquivos do repositório

- arquivo "docker-compose.yml": para funcionamento da aplicação, basta subir o container presente neste arquivo. Nele constam a criação da imagem e o mapeamento dos volumes;

- pasta "data": armazena o arquivo JSON com as credenciais que autorizam o acesso à planilha;

- pasta "docker-image": armazena o arquivo do Dockerfile para criação da imagem e o arquivo crontab que agenda a execução dos scripts;

- pasta "scripts": armazena os scripts em shell e em python;

- pasta "job-links": armazena os arquivos resultantes das coletas de dados do LinkedIn.

### Planilha final

Abaixo é a captura da tela assim que a planilha é aberta.

<p><img src="https://github.com/peuvitor/linkedin-jobs-scraper/blob/main/images/planilha-geral-1.PNG?raw=true" width="1080" height="523" class="center"></p>

Agora, um exemplo do conteúdo presente nas abas referentes a cada arquivo da pasta compartilhada. É interessante pontuar que o resultado obtido ao realizar a coleta de dados na pesquisa de vagas no LinkedIn conta sempre com 25 vagas de emprego. Quando você está conectado a uma conta do LinkedIn, o conteúdo é apresentado em diversas páginas de 25 vagas, o que permitiria a iteração via código ao mudar um parâmetro presente no URL da pesquisa do LinkedIn. 

Porém, da forma que está sendo feita a aplicação, não é realizado nenhum login antes da coleta de dados. Por conta disso, a página do LinkedIn é mostrada de maneira diferente, não por páginas contendo 25 vagas de emprego, mas sim com uma rolagem (scroll) infinita que apresenta mais 25 novas vagas assim que carregada. Dessa forma, para conseguir extrair mais de 25 vagas por vez, se faz necessário o acréscimo de um algoritmo que interaja com a página, o que, considerando o objetivo deste projeto, não foi realizado aqui.

<p><img src="https://github.com/peuvitor/linkedin-jobs-scraper/blob/main/images/planilha-exemplo-2.PNG?raw=true" width="1080" height="523" class="center"></p>

Por fim, é possível observar todas as abas existentes na planilha. É interessante observar a questão da periodicidade de execução dos scripts em shell e em python e também checar como os arquivos estão organizados na pasta "job-links/".

O script em shell (extrair links das vagas) executa diversas vezes antes do script em python (extrair informações de cada link e salvar na planilha), por isso, as abas presentes na planilha correspondem aos arquivos presentes na pasta "job-links/sent/". Ainda há outros arquivos na pasta "job-links/", mas a aplicação foi parada antes do script em python executar novamente.

<p><img src="https://github.com/peuvitor/linkedin-jobs-scraper/blob/main/images/planilha-abas-3.png?raw=true" width="1080" height="523" class="center"></p>

### Filtragem do conteúdo HTML

1. Página de vagas de emprego do LinkedIn de acordo com os filtros de título e local de trabalho;

<p><img src="https://github.com/peuvitor/linkedin-jobs-scraper/blob/main/images/linkedin-all-jobs-1.jpg?raw=true" width="1080" height="523" class="center"></p>

2. No resultado da coleta de dados da página que lista todas as vagas abertas, é possível observar que cada uma das 25 vagas são identificadas por um ID, acessível em "data-entity-urn";

<p><img src="https://github.com/peuvitor/linkedin-jobs-scraper/blob/main/images/html-all-jobs-2.jpg?raw=true" width="1080" height="523" class="center"></p>

3. Após extrair os IDs das vagas mostradas no momento do acesso, é possível acessar cada uma delas a partir do URL apresentado na imagem. Por conta disso, o arquivo de texto criado conta com o URL completo para cada uma das 25 vagas, onde será possível extrair: o título da vaga, a empresa que está ofertando, o local de trabalho e a descrição;

<p><img src="https://github.com/peuvitor/linkedin-jobs-scraper/blob/main/images/linkedin-job-3.jpg?raw=true" width="1080" height="523" class="center"></p>

4. Investigando o resultado da coleta de dados da página específica de uma vaga de emprego, são observadas as seguintes relações com o que se deseja extrair. Com isso, é implementado a extração dessas classes, que depois são armazenadas e enviadas para a planilha do Google Sheets.

<p><img src="https://github.com/peuvitor/linkedin-jobs-scraper/blob/main/images/html-job-4.jpg?raw=true" width="1080" height="523" class="center"></p>