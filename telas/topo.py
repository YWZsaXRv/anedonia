#
# feito por YWZsaXRv
#

import colorsys
import time

from rich.text import Text
from textual.widget import Widget

from config import ajustes, estilo
from telas.barra import barra

tamanho_barra = 10


def arco_iris(posicao):
    r, g, b = colorsys.hsv_to_rgb(posicao % 1.0, 0.75, 1.0)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


def suavizar(valor):
    valor = max(0.0, min(valor, 1.0))
    return 1 - (1 - valor) ** 3


class Topo(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dados = {}
        self.animacao = None
        self.relogio = None

    def on_mount(self):
        self.relogio = self.set_interval(1 / 20, self.quadro, pause=True)

    def definir(self, **dados):
        self.dados = dados
        self.refresh()

    def animar_nivel(self, antes, depois):
        if ajustes.animacao_nivel and self.relogio:
            self.animacao = {"inicio": time.monotonic(), "antes": antes, "depois": depois}
            self.relogio.resume()

    def quadro(self):
        if self.animacao and time.monotonic() - self.animacao["inicio"] > ajustes.duracao_animacao_nivel:
            self.animacao = None
            self.relogio.pause()
        self.refresh()

    def fase_animacao(self):
        decorrido = time.monotonic() - self.animacao["inicio"]
        corte = ajustes.duracao_animacao_nivel * 0.65
        if decorrido < corte:
            return "subida", decorrido, decorrido / corte
        return "enchendo", decorrido, (decorrido - corte) / (ajustes.duracao_animacao_nivel - corte)

    def esquerda(self, com_barra):
        d = self.dados
        nivel, xp, cor_nivel = d["nivel"], d["xp"], estilo.cor_acento
        celulas = None
        if self.animacao:
            fase, decorrido, andamento = self.fase_animacao()
            if fase == "subida":
                nivel, xp = self.animacao["antes"], d["xp_nivel"]
                cor_nivel = arco_iris(decorrido * 2)
                celulas = [arco_iris(i / tamanho_barra + decorrido * 2) for i in range(tamanho_barra)]
            else:
                xp = round(d["xp"] * suavizar(andamento))
        texto = Text(f"Dia {d['dia']}", style=estilo.cor_texto)
        texto.append(" · ", style=estilo.cor_fraco)
        texto.append(f"Nível {nivel}", style=f"bold {cor_nivel}")
        if com_barra:
            texto.append("  XP ", style=estilo.cor_fraco)
            if celulas:
                for cor in celulas:
                    texto.append(estilo.simbolo_barra_cheia, style=cor)
            else:
                texto.append_text(barra(xp / d["xp_nivel"], tamanho_barra))
            texto.append(f" {xp}/{d['xp_nivel']}", style=estilo.cor_texto)
            if celulas:
                texto.append("  Boa!", style=f"bold {cor_nivel}")
        return texto

    def direita(self):
        cronometro = self.dados["cronometro"]
        if not cronometro:
            return Text(self.dados["data"], style=estilo.cor_fraco)
        nome, segundos = cronometro
        minutos, resto = divmod(int(segundos), 60)
        return Text(f"{estilo.simbolo_cronometro} {nome} {minutos:02d}:{resto:02d}", style=f"bold {estilo.cor_acento}")

    def render(self):
        if not self.dados:
            return Text("")
        largura = self.content_size.width
        direita = self.direita()
        for com_barra in (True, False):
            esquerda = self.esquerda(com_barra)
            espaco = largura - esquerda.cell_len - direita.cell_len
            if espaco >= 2:
                return Text.assemble(esquerda, " " * espaco, direita)
        return self.esquerda(False)
