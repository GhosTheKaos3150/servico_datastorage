# servico_datastorage

## Disclaimer

Este programa utiliza Python 3.8.x

Este programa utiliza o framework FLASK como base.
Versão FLASK: 1.1.2

Certifique-se de utilizar Usuário e Senha para melhor segurança. É ideal que se configure usuário e senha em variáveis de ambiente para as mesmas serem transparentes a terceiros. Nesse caso, use "MONGODB_USER" e "MONGODB_PASSWORD" como variáveis. Mais informações disponíveis aqui e aqui.

# Instalando Localmente
+ Baixe a Release mais recente da aplicação na aba Releases.
+ Instale a bibilioteca Wheel usando `pip install wheel`
+ É Indicado criar um ambiente virtual. Se desejar, dê preferência a usar o [Anaconda](https://docs.anaconda.com/anaconda/install/index.html)
+ (Com a venv selecionada) Use o comando `pip install servico_datastorage-1.0-py3-none-any.whl`
+ Verifique se todos os modulos foram instalados corretamente. Caso algum esteja em falta, instale via `pip install <modulo>`

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
