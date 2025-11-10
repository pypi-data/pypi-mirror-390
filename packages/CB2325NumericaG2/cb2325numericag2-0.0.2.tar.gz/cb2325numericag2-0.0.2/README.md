![Banner da biblioteca](./images/Banner%20Correção%20Uso%20da%20marca.jpg)

![Static Badge](https://img.shields.io/badge/python-3.10-336B9C)
![Static Badge](https://img.shields.io/badge/size-3.62%20mb-4687BC)
![Static Badge](https://img.shields.io/badge/pypi-v.0.0.1-FFD43A)
![Static Badge](https://img.shields.io/badge/test-passing-31C754?logo=github)


## Introdução 
A `CB2325NumericaG2` foi criada como forma de aprendizado para o trabalho de Programação 2 do périodo 1.2 do [IMPA Tech](https://impatech.edu.br/). O objetivo do trabalho era criar uma biblioteca numérica que contesse 5 módulos que são: integração, raizes de funções, aproximações e erros

<br>

Um simples exemplo de uso:
```python
from CB2325NumericaG2.interpolacao import linear 

valor_interpolado = linear(10, 20, 0.5)

print(valor_interpolado) # 15
```

<br>

- 🚩[Introdução](#introdução)
- [🛠️ Colaboradores](#️-colaboradores)
- [⌨️ Instalação](#️-instalação)
- [📦 Pacotes](#-pacotes)
- [🧪 Testes](#-testes)
- [🔗 Referências](#-referências)
- [📝 Licença](#-licença)





## 🛠️ Colaboradores

Agradecimentos a todo os aluunos do grupo 2 pelo apoio e persistência de todos os membros da equipe. Não teriámos como ter feito [esse trabalho]() sem eles.

<br>

<a href="./images/Huann.png"><img src="./images/Huann.png" width="60px" alt="User avatar: Huann" /></a>
<a href="./images/Alan.png"><img src="./images/Alan.png" width="60px" alt="User avatar: Alan" /></a>
<a href="./images/Lucas.jpeg"><img src="./images/Lucas.jpeg" width="60px" alt="User avatar: Lucas" /></a>
<a href="./images/Carlos.png"><img src="./images/Carlos.png" width="60px" alt="User avatar: Carlos" /></a>
<a href="./images/Dani.png"><img src="./images/Dani.png" width="60px" alt="User avatar: Dani" /></a>
<a href="./images/Gabrielle.png"><img src="./images/Gabrielle.png" width="60px" alt="User avatar: Gabrielle" /></a>
<a href="./images/Italo.jpeg"><img src="./images/Italo.jpeg" width="60px" alt="User avatar: Italo" /></a>
<a href="./images/Julia.png"><img src="./images/Julia.png" width="60px" alt="User avatar: Julia" /></a>
<a href="./images/Kaua.png"><img src="./images/Kaua.png" width="60px" alt="User avatar: Kaua" /></a>
<a href="./images/Samuel.png"><img src="./images/Samuel.png" width="60px" alt="User avatar: Samuel" /></a>
<a href="./images/Ogido.png"><img src="./images/Ogido.png" width="60px" alt="User avatar: Ogido" /></a>

## ⌨️ Instalação

### Básico:

Para começar a usar o nosso pacote primeiro você tem que ter o [python](https://www.python.org/downloads/) na versão **no mínimo 3.10**. Assim execute o comando abaixo para fazer a instalação do nosso pacote.

```bash
pip install CB2325NumericaG2
```
### Dependêcias (Desenvolvedor)

Caso você queira atuar como desenvolvedor do projeto, depois de clonar o repositório, 

```bash
pip install -r requirements.txt
```

## 📦 Pacotes
* [pytest](https://github.com/pytest-dev/pytest)  
* [numpy]()
* [sympy]()
* [matplotlib]()
* [plotly]()

## 🧪 Testes

Primeiro você tem que estar com todas as dependências baixadas, caso você não tenha, você pode buscar na [sessão de instalação](#️-instalação). Executando o comando abaixo você inicializa os [testes automatizados]()
```bash
  pytest tests/
```

## 🔗 Referências

Todas as referências vão estar disponíveis no [PyPI](https://pypi.org/project/cb2325numericag2/) para consulta e uso.

## 📝 Licença

&copy; Copyright todos os direitos reservados

Distruibuidos pelos termos de licença do [MIT](https://alguma.com) de graça e open source.