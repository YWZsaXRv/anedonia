#
# feito por YWZsaXRv
#

from rich.text import Text

from config import estilo


def barra(proporcao, tamanho, cor=estilo.cor_acento):
    cheio = round(max(0.0, min(proporcao, 1.0)) * tamanho)
    texto = Text()
    texto.append(estilo.simbolo_barra_cheia * cheio, style=cor)
    texto.append(estilo.simbolo_barra_vazia * (tamanho - cheio), style=estilo.cor_fraco)
    return texto
