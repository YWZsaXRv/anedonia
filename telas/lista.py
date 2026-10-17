#
# feito por YWZsaXRv
#

from rich.text import Text
from textual.binding import Binding
from textual.widget import Widget

from config import ajustes
from config import estilo


class Lista(Widget, can_focus=True):
    BINDINGS = [
        Binding(ajustes.teclas["descer"], "mover(1)", show=False),
        Binding(ajustes.teclas["subir"], "mover(-1)", show=False),
        Binding(ajustes.teclas["marcar"], "marcar", show=False),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.linhas = []
        self.cursor = 0
        self.janela = 0

    def procurar(self, inicio, passo):
        posicao = inicio
        while 0 <= posicao < len(self.linhas):
            if self.linhas[posicao].selecionavel:
                return posicao
            posicao += passo
        return None

    def definir(self, linhas):
        self.linhas = linhas
        self.cursor = min(self.cursor, max(len(linhas) - 1, 0))
        alvo = self.procurar(self.cursor, 1)
        if alvo is None:
            alvo = self.procurar(self.cursor, -1)
        self.cursor = alvo or 0
        self.refresh()

    def linha_atual(self):
        return self.linhas[self.cursor] if self.linhas else None

    def action_mover(self, passo):
        alvo = self.procurar(self.cursor + passo, passo)
        if alvo is not None:
            self.cursor = alvo
            self.refresh()

    def action_marcar(self):
        linha = self.linha_atual()
        if linha:
            self.app.ao_marcar(linha)

    def on_focus(self):
        self.refresh()

    def on_blur(self):
        self.refresh()

    def desenhar(self, linha, selecionada):
        raise NotImplementedError

    def render(self):
        altura = max(self.size.height, 1)
        if self.cursor < self.janela:
            self.janela = self.cursor
        elif self.cursor >= self.janela + altura:
            self.janela = self.cursor - altura + 1
        saida = []
        for posicao, linha in enumerate(self.linhas[self.janela:self.janela + altura], self.janela):
            selecionada = posicao == self.cursor
            texto = self.desenhar(linha, selecionada)
            if self.size.width:
                texto.truncate(self.size.width, overflow="ellipsis", pad=True)
            if selecionada and self.has_focus:
                texto.stylize(f"on {estilo.cor_selecao}" if estilo.selecao_com_fundo else "bold")
            saida.append(texto)
        return Text("\n").join(saida)
