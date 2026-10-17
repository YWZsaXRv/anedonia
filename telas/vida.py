#
# feito por YWZsaXRv
#

from rich.text import Text
from textual.widget import Widget

from config import ajustes
from config import estilo


class PainelVida(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vida = {}

    def definir(self, vida):
        self.vida = vida
        self.refresh()

    def render(self):
        largura = max((len(barra) for barra in self.vida), default=0) + 2
        linhas = []
        for barra, (base, projetado, ligada) in self.vida.items():
            firme, ganho, risco = min(base, projetado), max(projetado - base, 0), max(base - projetado, 0)
            vazio = ajustes.vida_maxima - firme - ganho - risco
            linha = Text(barra.capitalize().ljust(largura), style=estilo.cor_texto if ligada else estilo.cor_fraco)
            for quantidade, cor in ((firme, estilo.cor_vida), (ganho, estilo.cor_feito), (risco, estilo.cor_acento), (vazio, estilo.cor_fraco)):
                simbolo = estilo.simbolo_vida_vazia if cor == estilo.cor_fraco else estilo.simbolo_vida_cheia
                linha.append(" ".join([simbolo] * quantidade) + (" " if quantidade else ""), style=cor)
            if ganho:
                linha.append(f"+{ganho}", style=estilo.cor_feito)
            elif risco:
                linha.append(f"-{risco}", style=estilo.cor_acento)
            elif not ligada:
                linha.append("sem hábito", style=estilo.cor_fraco)
            elif projetado == 0:
                linha.append("zerada", style=estilo.cor_alerta)
            linhas.append(linha)
        return Text("\n").join(linhas)
