#
# feito por YWZsaXRv
#

import argparse
import time

from textual.app import App
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen

from config import ajustes
from config import estilo
from nucleo import backup, dados, sintaxe, som, xp
from nucleo.dados import ErroDados
from nucleo.regras import Nucleo
from telas.hoje import PainelHoje
from telas.lista import Lista
from telas.missao import PainelMissao
from telas.modais import Confirmar, Historico, Pergunta, RegrasXP, ajuda
from telas.rodape import Rodape
from telas.semana import PainelSemana
from telas.topo import Topo
from telas.vida import PainelVida

acoes_app = ("painel_anterior", "painel_seguinte", "cronometro", "adicionar", "novo_habito", "nova_missao", "remover", "desfazer", "concluir", "editar", "historico", "xp", "backup", "sair")


class Anedonia(App):
    CSS = estilo.css
    TITLE = "anedonia"
    BINDINGS = [Binding(ajustes.teclas[acao], acao, show=False) for acao in acoes_app]

    def __init__(self, nucleo):
        super().__init__()
        self.nucleo = nucleo
        self.cronometro = None
        self.ultimo_erro = ""

    def compose(self):
        yield Topo(id="topo")
        with Container(id="corpo"):
            yield PainelVida(id="vida", classes="painel")
            yield PainelHoje(id="hoje", classes="painel")
            yield PainelMissao(id="missao", classes="painel")
            yield PainelSemana(id="semana", classes="painel")
        yield Rodape(id="rodape")

    def on_mount(self):
        self.query_one("#topo").border_title = "ANEDONIA"
        self.query_one("#vida").border_title = "VIDA"
        self.query_one("#vida").border_subtitle = "verde ganha · laranja perde"
        self.query_one("#missao").border_title = "MISSÃO PRINCIPAL"
        self.query_one("#semana").border_title = "SEQUÊNCIA"
        self.query_one("#hoje").focus()
        self.ao_redimensionar(self.size.width)
        self.atualizar()
        self.set_interval(1, self.pulso)

    def on_resize(self, evento):
        self.ao_redimensionar(evento.size.width)

    def ao_redimensionar(self, largura):
        self.set_class(largura < ajustes.largura_duas_colunas, "estreito")

    def check_action(self, action, parameters):
        if action in acoes_app and isinstance(self.screen, ModalScreen):
            return False
        return True

    # tela

    def processar_eventos(self):
        eventos, self.nucleo.eventos = self.nucleo.eventos, []
        subidas = [evento for evento in eventos if evento[0] == "nivel"]
        if subidas:
            som.tocar("nivel")
            self.query_one("#topo", Topo).animar_nivel(subidas[0][1], subidas[-1][2])
            self.notify(f"NÍVEL {subidas[-1][2]}!")
        elif eventos:
            som.tocar("concluir")

    def guardar_backup(self):
        try:
            backup.exportar()
        except OSError as erro:
            self.notify(f"backup falhou: {erro}", severity="error")

    def atualizar(self):
        nucleo = self.nucleo
        self.processar_eventos()
        ao_vivo, cronometro = None, None
        if self.cronometro:
            nome, inicio = self.cronometro
            segundos = time.monotonic() - inicio
            ao_vivo, cronometro = (nome, segundos / 60), (nome, segundos)
        hoje = self.query_one("#hoje", PainelHoje)
        linhas = nucleo.linhas_hoje(ao_vivo)
        hoje.definir(linhas)
        feitos, total, meta = nucleo.placar(linhas)
        faltam = f"faltam {meta - feitos}" if feitos < meta else "dia cumprido"
        excedente_hoje = sum(l.excedente for l in linhas if l.tipo == "missao" and l.feita)
        if excedente_hoje:
            faltam = f"dia cumprido +{excedente_hoje} min"
        hoje.border_title = f"HOJE · {feitos}/{total} · {faltam}"
        hoje.set_class(feitos >= meta, "cumprido")
        self.query_one("#missao", PainelMissao).definir(nucleo.linhas_missao())
        vida = nucleo.vida_projetada()
        self.query_one("#corpo").styles.grid_rows = f"{len(vida) + 2} 1fr {estilo.altura_semana}"
        self.query_one("#vida", PainelVida).definir(vida)
        self.query_one("#semana", PainelSemana).definir(nucleo.semana(), nucleo.sequencia())
        self.query_one("#topo", Topo).definir(
            dia=nucleo.dia_numero(),
            nivel=nucleo.nivel(),
            xp=nucleo.xp_no_nivel(),
            xp_nivel=xp.regras["por_nivel"],
            data=nucleo.data_curta(),
            cronometro=cronometro,
        )

    def esconder_cursor(self):
        try:
            self._driver.write("\x1b[?25l")
        except Exception:
            pass

    def pulso(self):
        self.esconder_cursor()
        try:
            if self.nucleo.mudou_fora():
                self.nucleo.recarregar()
                self.notify("dados recarregados do disco")
            elif self.nucleo.virou_dia():
                self.nucleo.virar_dias()
                self.guardar_backup()
                self.notify("novo dia")
            self.ultimo_erro = ""
        except ErroDados as erro:
            if str(erro) != self.ultimo_erro:
                self.ultimo_erro = str(erro)
                self.notify(f"erro no arquivo: {erro}", severity="error", timeout=10)
        if self.cronometro:
            nome, inicio = self.cronometro
            if self.nucleo.bater_meta(nome, (time.monotonic() - inicio) / 60):
                self.notify(f"meta do dia batida: {nome}")
        self.atualizar()

    # ações

    def avisar(self, aviso):
        if aviso:
            self.notify(aviso, severity="warning")

    def ao_marcar(self, linha, confirmado=False):
        if not confirmado:
            ao_vivo = (self.cronometro[0], (time.monotonic() - self.cronometro[1]) / 60) if self.cronometro else None
            pergunta = self.nucleo.aviso_sem_cronometro(linha, ao_vivo)
            if pergunta:
                return self.push_screen(Confirmar(pergunta), lambda sim: sim and self.ao_marcar(linha, True))
        self.avisar(self.nucleo.marcar(linha))
        self.atualizar()

    def criar(self, funcao, *argumentos):
        if argumentos[-1]:
            self.avisar(funcao(*argumentos))
            self.atualizar()

    def action_painel_seguinte(self):
        self.screen.focus_next()

    def action_painel_anterior(self):
        self.screen.focus_previous()

    def action_adicionar(self):
        painel = self.query_one("#missao", PainelMissao)
        if self.focused is painel:
            missao = painel.missao_atual()
            if not missao:
                return self.notify("nenhuma missão ativa para receber o marco", severity="warning")
            self.push_screen(
                Pergunta(f"novo marco em {missao['nome']}", ajuda("Seção 6 xp80", "xp = pontos (opcional)"), marcador="nome do marco"),
                lambda texto: self.criar(self.nucleo.adicionar_marco, missao, texto),
            )
        else:
            self.push_screen(
                Pergunta("nova tarefa avulsa", ajuda("pagar boleto xp15", "xp = pontos (opcional)"), marcador="o que fazer"),
                lambda texto: self.criar(self.nucleo.adicionar_avulsa, texto),
            )

    def action_novo_habito(self):
        self.push_screen(Pergunta("novo hábito diário", self.ajuda_habito(), marcador="nome do hábito"), lambda texto: self.criar(self.nucleo.adicionar_habito, texto))

    def action_nova_missao(self):
        self.push_screen(Pergunta("nova missão", self.ajuda_missao(), marcador="nome da missão"), lambda texto: self.criar(self.nucleo.adicionar_missao, texto))

    def ajuda_habito(self):
        return ajuda("Banho x3 @banho xp20", f"x3 = 3 vezes por dia · @ = barra de vida ({', '.join(ajustes.barras_vida)} ou uma nova) · xp = pontos")

    def ajuda_missao(self):
        return ajuda("Estudar Vim #curso 20min 10h /5 xp300", f"#{' ou #'.join(ajustes.categorias_missao)} · 20min por dia · 10h meta · /5 total de unidades · xp ao concluir")

    def action_remover(self):
        foco = self.focused
        linha = foco.linha_atual() if isinstance(foco, Lista) else None
        perguntas = {
            "habito": "remover o hábito",
            "avulsa": "remover a tarefa",
            "marco": "remover o marco",
            "cabecalho": "abandonar a missão",
        }
        if not linha or linha.tipo not in perguntas:
            return self.notify("selecione um hábito, tarefa, marco ou missão", severity="warning")
        nome = linha.ref["nome"] if linha.tipo == "cabecalho" else linha.texto
        self.push_screen(Confirmar(f"{perguntas[linha.tipo]} {nome}?"), lambda sim: self.efetivar_remocao(sim, linha))

    def efetivar_remocao(self, sim, linha):
        if sim:
            self.nucleo.remover(linha)
            self.atualizar()

    def action_cronometro(self):
        if self.cronometro:
            return self.parar_cronometro()
        nome = self.nome_sob_cursor()
        if not nome and self.nucleo.ativas():
            nome = self.nucleo.ativas()[0]["nome"]
        if not nome:
            return self.notify("nenhuma missão ativa", severity="warning")
        self.cronometro = (nome, time.monotonic())
        self.notify(f"cronômetro ligado: {nome}")
        self.atualizar()

    def linha_sob_cursor(self):
        foco = self.focused
        return foco.linha_atual() if isinstance(foco, Lista) else None

    def action_historico(self):
        self.push_screen(Historico(self.nucleo.dias_historico(), self.nucleo.encerradas()))

    def action_editar(self):
        linha = self.linha_sob_cursor()
        if not linha or linha.tipo not in ("habito", "avulsa", "marco", "cabecalho", "missao"):
            return self.notify("selecione um hábito, tarefa, marco ou missão", severity="warning")
        if linha.tipo in ("cabecalho", "missao"):
            return self.push_screen(
                Pergunta("editar missão", self.ajuda_missao(), valor=sintaxe.escrever_missao(linha.ref)),
                lambda texto: self.criar(self.nucleo.editar_missao, linha.ref, texto),
            )
        if linha.tipo == "habito":
            texto_atual, dica = sintaxe.escrever_habito(linha.ref), self.ajuda_habito()
        else:
            texto_atual, dica = sintaxe.escrever_item(linha.texto, linha.ref.get("xp")), ajuda("pagar boleto xp15", "xp = pontos (opcional)")
        self.push_screen(Pergunta("editar", dica, valor=texto_atual), lambda texto: self.criar(self.nucleo.editar, linha, texto))

    def nome_sob_cursor(self):
        linha = self.linha_sob_cursor()
        if not linha:
            return None
        if linha.tipo in ("missao", "cabecalho"):
            return linha.ref["nome"]
        if linha.tipo == "marco":
            return linha.pai["nome"]
        return linha.texto if linha.tipo in ("habito", "avulsa") else None

    def missao_sob_cursor(self):
        painel = self.query_one("#missao", PainelMissao)
        return painel.missao_atual() if self.focused is painel else None

    def action_desfazer(self):
        linha = self.linha_sob_cursor()
        missao = self.missao_sob_cursor()
        if linha and linha.tipo == "habito":
            self.nucleo.desfazer_habito(linha.ref)
        elif missao:
            self.nucleo.desfazer(missao)
        else:
            return self.notify("u tira 1 de um contador (hábito xN ou missão com total/marcos)", severity="warning")
        self.atualizar()

    def action_xp(self):
        self.push_screen(RegrasXP(xp.regras), lambda novos: self.criar(self.nucleo.atualizar_xp, novos))

    def action_backup(self):
        self.guardar_backup()
        self.notify(f"backup salvo em {backup.arquivo_padrao}")

    def action_concluir(self):
        missao = self.missao_sob_cursor()
        if not missao:
            return self.notify("selecione uma missão no painel de missão", severity="warning")
        self.push_screen(Confirmar(f"concluir a missão {missao['nome']}?"), lambda sim: self.efetivar_conclusao(sim, missao))

    def efetivar_conclusao(self, sim, missao):
        if sim:
            self.notify(self.nucleo.concluir(missao))
            self.atualizar()

    def parar_cronometro(self):
        nome, inicio = self.cronometro
        self.cronometro = None
        for aviso in self.nucleo.registrar_sessao(nome, (time.monotonic() - inicio) / 60):
            self.notify(aviso)
        self.atualizar()

    def action_sair(self):
        if self.cronometro:
            self.parar_cronometro()
        self.guardar_backup()
        self.exit()


def preparar_dados():
    if dados.existe_algum():
        return
    if backup.arquivo_padrao.exists():
        backup.restaurar()
    else:
        dados.copiar_demo()


def principal():
    analisador = argparse.ArgumentParser(prog="anedonia")
    analisador.add_argument("--backup", action="store_true", help="grava o backup agora e sai")
    analisador.add_argument("--restaurar", nargs="?", const="", metavar="arquivo", help="restaura de um backup e sai")
    analisador.add_argument("--demo", action="store_true", help="volta os dados para a demo (faz backup antes) e sai")
    argumentos = analisador.parse_args()
    if argumentos.backup:
        raise SystemExit(f"backup salvo em {backup.exportar()}")
    if argumentos.restaurar is not None:
        raise SystemExit(f"{backup.restaurar(argumentos.restaurar or None)} arquivos restaurados")
    if argumentos.demo:
        if dados.existe_algum():
            backup.exportar()
        for nome in dados.nomes:
            dados.caminho(nome).unlink(missing_ok=True)
        dados.copiar_demo()
        raise SystemExit("dados da demo copiados (o backup anterior está em backup/)")
    preparar_dados()
    try:
        nucleo = Nucleo()
    except ErroDados as erro:
        raise SystemExit(f"erro nos dados: {erro}")
    Anedonia(nucleo).run()


if __name__ == "__main__":
    principal()
