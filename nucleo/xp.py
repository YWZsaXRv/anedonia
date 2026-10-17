#
# feito por YWZsaXRv
#

from config import xp as padroes
from nucleo import dados

regras = dict(padroes.padrao)


def carregar():
    regras.clear()
    regras.update(padroes.padrao)
    regras.update({chave: valor for chave, valor in dados.ler("xp", {}).items() if chave in padroes.padrao})
