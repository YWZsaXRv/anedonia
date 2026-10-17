#
# feito por YWZsaXRv
#

from rich.text import Text
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Static

from config import ajustes, estilo
from config import xp as padroes_xp


class Rolagem(VerticalScroll, can_focus=False):
    pass


def teclas(*pares):
    texto = Text()
    for posicao, (tecla, acao) in enumerate(pares):
        if posicao:
            texto.append("  ·  ", style=estilo.cor_fraco)
        texto.append(tecla, style=f"bold {estilo.cor_acento}")
        texto.append(f" {acao}", style=estilo.cor_fraco)
    return texto


def ajuda(exemplo, legenda):
    texto = Text("ex.: ", style=estilo.cor_fraco)
    texto.append(exemplo, style=estilo.cor_acento)
    texto.append(f"\n{legenda}", style=estilo.cor_fraco)
    return texto


class Pergunta(ModalScreen):
    BINDINGS = [Binding("escape", "dismiss(None)", show=False)]

    def __init__(self, titulo, ajuda_texto=None, valor="", marcador=""):
        super().__init__()
        self.titulo = titulo
        self.ajuda_texto = ajuda_texto
        self.valor = valor
        self.marcador = marcador

    def compose(self):
        with Vertical(classes="janela"):
            yield Label(self.titulo, classes="titulo")
            if self.ajuda_texto:
                yield Label(self.ajuda_texto, classes="ajuda")
            yield Input(value=self.valor, placeholder=self.marcador, select_on_focus=False)
            yield Label(teclas(("enter", "confirma"), ("esc", "cancela")), classes="dica")

    def on_mount(self):
        entrada = self.query_one(Input)
        entrada.cursor_position = len(self.valor)

    def on_input_submitted(self, evento):
        self.dismiss(evento.value.strip() or None)


class Confirmar(ModalScreen):
    BINDINGS = [
        Binding("s,enter", "dismiss(True)", show=False),
        Binding("n,escape", "dismiss(False)", show=False),
    ]

    def __init__(self, titulo):
        super().__init__()
        self.titulo = titulo

    def compose(self):
        with Vertical(classes="janela"):
            yield Label(self.titulo, classes="titulo")
            yield Label(teclas(("s", "sim"), ("n", "não")), classes="dica")


class RegrasXP(ModalScreen):
    BINDINGS = [Binding("escape", "dismiss(None)", show=False)]

    def __init__(self, regras):
        super().__init__()
        self.regras = regras

    def compose(self):
        with Vertical(classes="janela"):
            yield Label("regras de xp", classes="titulo")
            yield Label("nível = xp total ÷ xp por nível. um item pode ter o seu valor: xp25", classes="ajuda")
            for chave, rotulo in padroes_xp.rotulos.items():
                with Horizontal(classes="linha_xp"):
                    yield Label(rotulo, classes="rotulo_xp")
                    yield Input(value=str(self.regras[chave]), type="integer", select_on_focus=False, id=f"xp_{chave}", classes="compacto")
            yield Label(teclas(("tab", "muda de campo"), ("enter", "salva"), ("esc", "cancela")), classes="dica")

    def on_mount(self):
        self.query_one(Input).focus()

    def on_input_submitted(self, evento):
        novos = {chave: int(self.query_one(f"#xp_{chave}", Input).value or 0) for chave in padroes_xp.rotulos}
        if novos["por_nivel"] < 1:
            return self.notify("xp por nível precisa ser pelo menos 1", severity="warning")
        self.dismiss(novos)


class Historico(ModalScreen):
    BINDINGS = [
        Binding("escape,q,v", "dismiss(None)", show=False),
        Binding("tab,shift+tab", "alternar", show=False),
        Binding(ajustes.teclas["descer"], "rolar(1)", show=False),
        Binding(ajustes.teclas["subir"], "rolar(-1)", show=False),
    ]
    abas = ("histórico", "concluídas")

    def __init__(self, dias, encerradas):
        super().__init__()
        self.dias = dias
        self.encerradas = encerradas
        self.aba = 0

    def compose(self):
        with Vertical(classes="janela larga"):
            yield Static(id="abas")
            with Rolagem(id="historico"):
                yield Static(id="conteudo")
            yield Label(teclas(("tab", "alternar"), ("j/k", "navegar"), ("esc", "fechar")), classes="dica")

    def on_mount(self):
        self.desenhar()

    def action_alternar(self):
        self.aba = 1 - self.aba
        self.desenhar()

    def action_rolar(self, passo):
        self.query_one("#historico").scroll_relative(y=passo)

    def desenhar(self):
        titulos = Text()
        for posicao, nome in enumerate(self.abas):
            ativa = posicao == self.aba
            titulos.append(f" {nome} ", style=f"bold {estilo.cor_fundo} on {estilo.cor_acento}" if ativa else estilo.cor_fraco)
            titulos.append("  ")
        self.query_one("#abas", Static).update(titulos)
        self.query_one("#conteudo", Static).update(self.arvore() if self.aba == 0 else self.concluidas())
        self.query_one("#historico").scroll_home(animate=False)

    def arvore(self):
        texto = Text()
        for dia in self.dias:
            cor = estilo.cor_feito if dia["cumpriu"] else estilo.cor_acento
            texto.append(f"{estilo.simbolo_hoje} ", style=cor)
            texto.append(dia["titulo"], style=f"bold {estilo.cor_texto}")
            excedente = dia.get("excedente", 0)
            if excedente:
                texto.append(f"  +{excedente} min", style=estilo.cor_excedente)
            texto.append(f"  {dia['feitos']}/{dia['total']}", style=cor)
            texto.append("  dia cumprido\n" if dia["cumpriu"] else "\n", style=estilo.cor_feito)
            itens = [(True, item) for item in dia["itens"]] + [(False, item) for item in dia["faltaram"]]
            for posicao, (feito, item) in enumerate(itens):
                ramo = "└─" if posicao == len(itens) - 1 else "├─"
                texto.append(f"│  {ramo} ", style=estilo.cor_fraco)
                texto.append(f"{estilo.simbolo_feito if feito else estilo.simbolo_falhou} {item}\n", style=estilo.cor_feito if feito else estilo.cor_fraco)
            if not itens:
                texto.append("│  └─ sem registro\n", style=estilo.cor_fraco)
            texto.append("│\n", style=estilo.cor_fraco)
        return texto

    def concluidas(self):
        texto = Text()
        for dia in self.dias:
            texto.append(f"{dia['titulo']}\n", style=f"bold {estilo.cor_texto}")
            for item in dia["itens"] or ["nada marcado"]:
                feito = bool(dia["itens"])
                texto.append(f"  {estilo.simbolo_feito if feito else estilo.simbolo_vazio} {item}\n", style=estilo.cor_feito if feito else estilo.cor_fraco)
        if self.encerradas:
            texto.append("missões encerradas\n", style=f"bold {estilo.cor_atraso}")
        for missao in self.encerradas:
            rotulo = "concluída" if missao["estado"] == "concluida" else "abandonada"
            texto.append(f"  {missao['categoria']} · {missao['nome']} · {rotulo} {missao.get('encerrada_em', '')}\n", style=estilo.cor_atraso)
        return texto
