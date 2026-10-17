#
# feito por YWZsaXRv
#

from rich.text import Text
from textual.widgets import Static

from config import ajustes
from config import estilo

dicas = (
    ("marcar", "marcar"),
    ("cronometro", "cronômetro"),
    ("adicionar", "adicionar"),
    ("novo_habito", "hábito"),
    ("nova_missao", "missão"),
    ("editar", "editar"),
    ("remover", "remover"),
    ("desfazer", "-1"),
    ("concluir", "concluir"),
    ("historico", "histórico"),
    ("xp", "xp"),
    ("backup", "backup"),
    ("sair", "sair"),
)
nomes_teclas = {"space": "espaço", "enter": "enter"}


def primeira(acao):
    tecla = ajustes.teclas[acao].split(",")[0]
    return nomes_teclas.get(tecla, tecla)


def montar():
    texto = Text()
    movimento = (
        (f"{primeira('subir')}{primeira('descer')}", "mover"),
        (f"{primeira('painel_anterior')}{primeira('painel_seguinte')}", "painel"),
    )
    pares = movimento + tuple((primeira(acao), nome) for acao, nome in dicas)
    for posicao, (tecla, nome) in enumerate(pares):
        if posicao:
            texto.append("  ")
        texto.append(tecla, style=estilo.cor_acento)
        texto.append(f" {nome}", style=estilo.cor_fraco)
    return texto


class Rodape(Static):
    def __init__(self, **kwargs):
        super().__init__(montar(), **kwargs)
