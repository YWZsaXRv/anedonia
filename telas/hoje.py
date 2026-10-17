#
# feito por YWZsaXRv
#

from rich.text import Text

from config import estilo
from telas.lista import Lista


class PainelHoje(Lista):
    def desenhar(self, linha, selecionada):
        if linha.feita:
            cor = estilo.cor_feito
        elif linha.atraso:
            cor = estilo.cor_atraso
        else:
            cor = estilo.cor_texto
        texto = Text()
        texto.append(f"{estilo.simbolo_cursor} " if selecionada else "  ", style=estilo.cor_acento)
        texto.append(f"[{'x' if linha.feita else ' '}] {linha.texto}", style=cor)
        if linha.detalhe:
            texto.append(f"  {linha.detalhe}", style=estilo.cor_fraco)
        if linha.correndo:
            texto.append(f" {estilo.simbolo_cronometro}", style=f"bold {estilo.cor_acento}")
        if linha.excedente > 0:
            texto.append(f"  +{linha.excedente} min", style=estilo.cor_excedente)
        if linha.atraso:
            texto.append(f"  {estilo.simbolo_atraso} {'ontem' if linha.atraso == 1 else f'há {linha.atraso}d'}", style=estilo.cor_atraso)
        return texto
