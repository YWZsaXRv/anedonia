#
# feito por YWZsaXRv
#

from config import ajustes

# mundo cinza-azulado e apagado: só o que você faz ganha cor
cor_fundo = "#13131a"
cor_painel = "#1a1a24"
cor_borda = "#33334a"
cor_texto = "#b9b9cc"
cor_fraco = "#6a6a82"
cor_selecao = "#2a2a3c"
cor_acento = "#ffb454"
cor_vida = "#ff6b81"
cor_feito = "#8fbf9f"
cor_atraso = "#c792ea"
cor_alerta = "#ff5f5f"
cor_excedente = "#a0c4ff"
cor_excedente = "#a0c4ff"

simbolo_barra_cheia = "▓"
simbolo_barra_vazia = "░"
conjunto_simbolos = "blocos"

conjuntos = {
    "blocos": dict(vida_cheia="█", vida_vazia="░", cursor="▌", hoje="▒", feito="█", falhou="░", vazio="·", atraso="<", cronometro="»"),
    "unicode": dict(vida_cheia="♥", vida_vazia="♥", cursor="►", hoje="♦", feito="■", falhou="□", vazio="·", atraso="←", cronometro="»"),
    "ascii": dict(vida_cheia="#", vida_vazia=".", cursor=">", hoje="*", feito="#", falhou="-", vazio=".", atraso="<", cronometro=">"),
}
_conjunto = conjuntos[conjunto_simbolos]
simbolo_vida_cheia = _conjunto["vida_cheia"]
simbolo_vida_vazia = _conjunto["vida_vazia"]
simbolo_cursor = _conjunto["cursor"]
simbolo_hoje = _conjunto["hoje"]
simbolo_feito = _conjunto["feito"]
simbolo_falhou = _conjunto["falhou"]
simbolo_vazio = _conjunto["vazio"]
simbolo_atraso = _conjunto["atraso"]
simbolo_cronometro = _conjunto["cronometro"]

selecao_com_fundo = False

altura_vida = len(ajustes.barras_vida) + 2
altura_semana = 5

variaveis = f"""
$fundo: {cor_fundo};
$painel: {cor_painel};
$borda: {cor_borda};
$texto: {cor_texto};
$fraco: {cor_fraco};
$selecao: {cor_selecao};
$acento: {cor_acento};
$feito: {cor_feito};
$excedente: {cor_excedente};
"""

regras = """
Screen { background: $fundo; color: $texto; }

#topo { height: 3; border: round $borda; border-title-color: $acento; background: $painel; padding: 0 1; }
#rodape { height: auto; padding: 0 1; }

#corpo { layout: grid; grid-size: 2 3; grid-columns: 2fr 3fr; height: 1fr; }
#hoje { row-span: 2; }
#missao { row-span: 2; }

.painel { height: 100%; border: round $borda; border-title-color: $fraco; border-subtitle-color: $fraco; background: $painel; padding: 0 1; }
.painel:focus { border: round $acento; border-title-color: $acento; }
.painel.cumprido { border: round $feito; border-title-color: $feito; }

.estreito #corpo { layout: vertical; overflow-y: auto; scrollbar-size-vertical: 1; scrollbar-color: $borda; scrollbar-color-hover: $fraco; scrollbar-color-active: $acento; scrollbar-background: $fundo; scrollbar-background-hover: $fundo; scrollbar-background-active: $fundo; }
.estreito .painel { height: 14; }
.estreito #vida { height: auto; }

ModalScreen { align: center middle; background: $fundo 70%; }
.janela { width: 72; max-width: 95%; height: auto; max-height: 100%; overflow-y: auto; border: round $acento; background: $painel; padding: 1 2; }
.janela.larga { width: 80; height: 85%; }
.janela.larga #historico { height: 1fr; }
.janela .linha_xp { height: 1; }
.janela .rotulo_xp { width: 30; }
.janela Input.compacto { border: none; height: 1; margin: 0; padding: 0 1; width: 1fr; }
.janela Input.compacto:focus { border: none; background: $selecao; }
.janela .ajuda { margin-top: 1; }
.janela Label { width: 100%; }
.janela Input { width: 100%; }
.janela .titulo { color: $acento; text-style: bold; }
.janela .dica { color: $fraco; margin-top: 1; }
.janela Input { border: tall $borda; background: $fundo; margin-top: 1; }
.janela Input:focus { border: tall $acento; }
"""

css = variaveis + regras + f"""
#semana {{ height: {altura_semana}; }}
#corpo {{ grid-rows: {altura_vida} 1fr {altura_semana}; }}
"""
