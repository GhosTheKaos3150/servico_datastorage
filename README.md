# servico_datastorage

## Disclaimer

Este programa utiliza Python 3.8.x

Este programa utiliza o framework FLASK como base.
Versão FLASK: 1.1.2


Este programa depende do Banco de Dados MONGODB devidamente instalado para seu funcionamento correto.
Por favor, instale o MongoDB de acordo com o tutorial disponível nesse [guia](https://docs.mongodb.com/manual/installation/)

Certifique-se de utilizar Usuário e Senha para melhor segurança. É ideal que se configure usuário e senha em variáveis de ambiente para as mesmas serem transparentes a terceiros. Nesse caso, use "MONGODB_USER" e "MONGODB_PASSWORD" como variáveis. Mais informações disponíveis [aqui](https://docs.mongodb.com/manual/tutorial/enable-authentication/) e [aqui](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwjch-GZjYTzAhUvppUCHaZVAVQQFnoECCAQAQ&url=https%3A%2F%2Fmedium.com%2Fmongoaudit%2Fhow-to-enable-authentication-on-mongodb-b9e8a924efac&usg=AOvVaw0sgRt62G8fSeJ8vqnHGAjy).

# Instalando Localmente
## Serviço Datastorage
+ Baixe a Release mais recente da aplicação na aba Releases, ambos Source Code e arquivo .whl
+ Instale a bibilioteca Wheel usando `pip install wheel`
+ É Indicado criar um ambiente virtual. Se desejar, dê preferência a usar o [Anaconda](https://docs.anaconda.com/anaconda/install/index.html)
+ (Com a venv selecionada) Use o comando `pip install servico_datastorage-1.0-py3-none-any.whl`
+ Verifique se todos os modulos foram instalados corretamente. Caso algum esteja em falta, instale via `pip install <modulo>`

## Treinamento Recorrente
+ Instale o Cron usando
```
$ sudo apt-get update
$ sudo apt-get install cron
```
+ Abra o terminal na pasta do arquivo "cron_train.py" e execute o seguinte comando:
```
$ <minuto> <hora> <dia> <mês> <semana> python cron_train.py
```
+ minuto: 0-59 ou *(todos);
+ hora: 0-23 ou *(todos);
+ dia: 1-31 ou *(todos);
+ mês 1-12, jan-dez ou *(todos);
+ semana 0-6, sun-sat ou *(todos);
  
#### Exemplos do Comando Acima
+ Para executar todo dia as 12 horas: `0 12 * * * python cron_train.py`
+ Para executar todo dia 1º as 15 horas: `0 15 1 * * python cron_train.py`
+ Para executar todo sabado ás 8 horas: `0 8 * * 6 python cron_train.py` ou `0 8 * * sat python cron_train.py`

# Iniciando a Aplicação

### Desenvolvimento
+ Para iniciar a aplicação use `python main.py`

### Produção (WSGI)
+ Instale a biblioteca Waitress usando `pip instal waitress`
+ Usando o comando a seguir, inicie o server:
```
$ waitress-serve --port 8045 main:app
$ waitress-serve --port 8040 main:model_app
```

## Pacotes
+ pymongo
+ re
+ pandas
+ flask
+ flask_cors

# Portas
+ Porta do Serviço: 8045
+ Porta do BD: 27017
