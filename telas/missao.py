#
# feito por YWZsaXRv
#

from rich.text import Text

from config import estilo
from telas.barra import barra
from telas.lista import Lista


class PainelMissao(Lista):
    def missao_atual(self):
        linha = self.linha_atual()
        if not linha:
            return None
        return linha.pai if linha.tipo == "marco" else linha.ref

    def desenhar(self, linha, selecionada):
        texto = Text()
        marca = f"{estilo.simbolo_cursor} " if selecionada else "  "
        if linha.tipo == "cabecalho":
            texto.append(marca, style=estilo.cor_acento)
            texto.append(linha.texto, style=f"bold {estilo.cor_acento}")
            if linha.detalhe:
                texto.append(f"  {linha.detalhe}", style=estilo.cor_fraco)
        elif linha.tipo == "barra" and linha.progresso is None:
            texto.append(f"  {linha.detalhe} registrados", style=estilo.cor_fraco)
        elif linha.tipo == "resumo":
            texto.append(f"  {estilo.simbolo_feito} {linha.texto}", style=estilo.cor_feito)
        elif linha.tipo == "barra":
            sufixo = f" {round(linha.progresso * 100)}% · {linha.detalhe}"
            tamanho = max(self.size.width - len(sufixo) - 2, 4)
            texto.append("  ")
            texto.append_text(barra(linha.progresso, tamanho))
            texto.append(sufixo, style=estilo.cor_texto)
        elif linha.tipo == "marco":
            texto.append(marca, style=estilo.cor_acento)
            texto.append(f"[{'x' if linha.feita else ' '}] {linha.texto}", style=estilo.cor_feito if linha.feita else estilo.cor_texto)
        else:
            texto.append(f"  sem missão de {linha.texto} · m cria", style=estilo.cor_fraco)
        return texto
