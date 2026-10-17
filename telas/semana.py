#
# feito por YWZsaXRv
#

from rich.text import Text
from textual.widget import Widget

from config import estilo

marcas = {
    "cumpriu": (estilo.simbolo_feito, estilo.cor_feito),
    "cumprido": (estilo.simbolo_feito, estilo.cor_feito),
    "hoje": (estilo.simbolo_hoje, estilo.cor_acento),
    "falhou": (estilo.simbolo_falhou, estilo.cor_fraco),
    "vazio": (estilo.simbolo_vazio, estilo.cor_fraco),
}


class PainelSemana(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dias = []
        self.sequencia = 0

    def definir(self, dias, sequencia):
        self.dias = dias
        self.sequencia = sequencia
        self.refresh()

    def render(self):
        celula = max(2, min(5, self.size.width // 7))
        rotulos, simbolos = Text(), Text()
        for rotulo, situacao in self.dias:
            simbolo, cor = marcas[situacao]
            rotulos.append((rotulo if celula >= 4 else rotulo[0]).center(celula), style=estilo.cor_fraco)
            simbolos.append(simbolo.center(celula), style=cor)
        plural = "dia" if self.sequencia == 1 else "dias"
        rodape = Text(f"sequência: {self.sequencia} {plural}", style=estilo.cor_acento if self.sequencia else estilo.cor_fraco)
        return Text("\n").join([rotulos, simbolos, rodape])
