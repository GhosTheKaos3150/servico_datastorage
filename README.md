# servico_datastorage

Este programa utiliza Python 3.8.x

Este programa utiliza o framework FLASK como base.
Versão FLASK: 1.1.2

# Instalando Localmente
+ Baixe a Release mais recente da aplicação na aba Releases.
+ Instale a bibilioteca Wheel usando `pip install wheel`
+ É Indicado criar um ambiente virtual. Se desejar, dê preferência a usar o [Anaconda](https://docs.anaconda.com/anaconda/install/index.html)
+ (Com a venv selecionada) Use o comando `pip install servico_datastorage-1.0-py3-none-any.whl`
+ Para finalizar, use o seguinte comando para instalar a Release:
```
$ export FLASK_APP=main
$ flask init-db
```

# Iniciando a Aplicação

### Desenvolvimento
+ Para iniciar a aplicação use `python main.py`

### Produção (WSGI)
+ Instale a biblioteca Waitress usando `pip instal waitress`
+ Usando o comando a seguir, inicie o server:
```
$ waitress-serve --host 0.0.0.0 --port 8045 'main:app'
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
