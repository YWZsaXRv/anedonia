#
# feito por YWZsaXRv
#

from dataclasses import dataclass
from datetime import date, timedelta

from config import ajustes
from nucleo import dados, sintaxe, xp
from nucleo.sintaxe import vezes_do

arquivos = ("habitos", "missoes", "tarefas", "estado", "historico", "xp")
dias_semana = ("seg", "ter", "qua", "qui", "sex", "sáb", "dom")
meses = ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez")


@dataclass
class Linha:
    tipo: str
    texto: str = ""
    feita: bool = False
    atraso: int = 0
    selecionavel: bool = True
    ref: dict | None = None
    pai: dict | None = None
    progresso: float | None = None
    detalhe: str = ""
    correndo: bool = False
    excedente: int = 0


def hoje_iso():
    return date.today().isoformat()


def horas_texto(valor):
    return f"{valor:.1f}".replace(".", ",").removesuffix(",0")


def progresso(missao):
    marcos = missao["marcos"]
    if marcos:
        return sum(marco["feito"] for marco in marcos) / len(marcos)
    if missao.get("total"):
        return min(missao["feitos"] / missao["total"], 1.0)
    if missao.get("meta_horas"):
        return min(missao["minutos"] / (missao["meta_horas"] * 60), 1.0)
    return None


def tempo_texto(minutos):
    total = int(minutos)
    if total < 60:
        return f"{total}min"
    horas, resto = divmod(total, 60)
    return f"{horas}h{resto:02d}" if resto else f"{horas}h"


def descrever(linha):
    return f"{linha.texto} · {linha.detalhe}" if linha.detalhe else linha.texto


def pontos_de(item, padrao):
    return item.get("xp", xp.regras[padrao])


def normalizar_avulsa(item):
    item = {"texto": item} if isinstance(item, str) else item
    item.setdefault("criada", hoje_iso())
    item.setdefault("feita_em", None)
    return item


def normalizar_missoes(lista):
    lista[:] = [{"nome": item} if isinstance(item, str) else item for item in lista]
    for missao in lista:
        missao.setdefault("categoria", ajustes.categorias_missao[0])
        missao.setdefault("minutos_dia", ajustes.minutos_padrao)
        missao.setdefault("minutos", 0)
        missao.setdefault("feitos", 0)
        missao.setdefault("estado", "fila")
        missao["marcos"] = [{"nome": m, "feito": False} if isinstance(m, str) else m for m in missao.get("marcos", [])]
    for categoria in ajustes.categorias_missao:
        vivas = [m for m in lista if m["categoria"] == categoria and m["estado"] in ("ativa", "fila")]
        ativas = [m for m in vivas if m["estado"] == "ativa"]
        for sobra in ativas[1:]:
            sobra["estado"] = "fila"
        if not ativas and vivas:
            vivas[0]["estado"] = "ativa"
    return lista


def normalizar_estado(bruto):
    hoje = hoje_iso()
    estado = {"dia": hoje, "inicio": hoje, "marcados": [], "contagens": {}, "minutos_hoje": {}, "xp": 0, **bruto}
    vida = estado.get("vida", {})
    estado["vida"] = {barra: vida.get(barra, ajustes.vida_inicial) for barra in ajustes.barras_vida}
    return estado


class Nucleo:
    def __init__(self):
        self.eventos = []
        self.carregar()
        self.virar_dias()
        self.salvar("estado")

    def carregar(self):
        xp.carregar()
        brutas = dados.ler("tarefas", [])
        precisa_carimbar = any(isinstance(a, str) or "criada" not in a for a in brutas)
        self.habitos = [{"nome": h} if isinstance(h, str) else h for h in dados.ler("habitos", [])]
        self.missoes = normalizar_missoes(dados.ler("missoes", []))
        self.avulsas = [normalizar_avulsa(a) for a in brutas]
        self.historico = dados.ler("historico", {})
        self.estado = normalizar_estado(dados.ler("estado", {}))
        self.sincronizar_vida()
        self.modificados = {nome: dados.modificado(nome) for nome in arquivos}
        if precisa_carimbar:
            self.salvar("tarefas")

    def salvar(self, *nomes):
        conteudo = {
            "habitos": self.habitos,
            "missoes": self.missoes,
            "tarefas": self.avulsas,
            "estado": self.estado,
            "historico": self.historico,
            "xp": xp.regras,
        }
        for nome in nomes:
            dados.gravar(nome, conteudo[nome])
            self.modificados[nome] = dados.modificado(nome)

    def barras(self):
        extras = [h["vida"] for h in self.habitos if h.get("vida")]
        return list(dict.fromkeys(ajustes.barras_vida + tuple(extras)))

    def sincronizar_vida(self):
        vida, barras = self.estado["vida"], self.barras()
        for barra in barras:
            vida.setdefault(barra, ajustes.vida_inicial)
        for barra in [b for b in vida if b not in barras]:
            del vida[barra]

    def mudou_fora(self):
        return any(dados.modificado(nome) != self.modificados[nome] for nome in arquivos)

    def recarregar(self):
        self.carregar()
        self.virar_dias()
        self.salvar("estado")

    def virou_dia(self):
        return self.estado["dia"] != hoje_iso()

    # consultas

    def missao_da(self, categoria):
        return next((m for m in self.missoes if m["categoria"] == categoria and m["estado"] == "ativa"), None)

    def ativas(self):
        return [m for m in map(self.missao_da, ajustes.categorias_missao) if m]

    def missao_por_nome(self, nome):
        return next((m for m in self.ativas() if m["nome"] == nome), None)

    def nivel(self):
        return self.estado["xp"] // xp.regras["por_nivel"] + 1

    def xp_no_nivel(self):
        return self.estado["xp"] % xp.regras["por_nivel"]

    def dia_numero(self):
        return (date.fromisoformat(self.estado["dia"]) - date.fromisoformat(self.estado["inicio"])).days + 1

    def data_curta(self, iso=None):
        dia = date.fromisoformat(iso or self.estado["dia"])
        return f"{dias_semana[dia.weekday()]} {dia.day} {meses[dia.month - 1]}"

    def vida_projetada(self):
        marcados = self.estado["marcados"]
        resultado = {}
        for barra, valor in self.estado["vida"].items():
            ligados = [h for h in self.habitos if h.get("vida") == barra]
            delta = sum(1 if f"h:{h['nome']}" in marcados else -1 for h in ligados)
            resultado[barra] = (valor, min(max(valor + delta, 0), ajustes.vida_maxima), bool(ligados))
        return resultado

    def dias_historico(self):
        linhas = self.linhas_hoje()
        feitos, total, meta = self.placar(linhas)
        dias = [{
            "titulo": f"{self.data_curta()} (hoje)", "feitos": feitos, "total": total, "cumpriu": feitos >= meta,
            "itens": [descrever(l) for l in linhas if l.feita], "faltaram": [descrever(l) for l in linhas if not l.feita],
        }]
        for iso in sorted(self.historico, reverse=True)[:ajustes.dias_no_historico]:
            registro = self.historico[iso]
            dias.append({
                "titulo": self.data_curta(iso), "feitos": registro.get("feitos", 0), "total": registro.get("total", 0),
                "cumpriu": registro.get("cumpriu", False), "itens": registro.get("itens", []), "faltaram": registro.get("faltaram", []),
            })
        return dias

    def encerradas(self):
        return [m for m in self.missoes if m["estado"] in ("concluida", "abandonada")]

    def linhas_hoje(self, ao_vivo=None):
        dia = date.fromisoformat(self.estado["dia"])
        marcados = self.estado["marcados"]
        atrasadas, avulsas_dia = [], []
        for avulsa in sorted(self.avulsas, key=lambda a: a["criada"]):
            feita = avulsa["feita_em"] is not None
            if feita and avulsa["feita_em"] != self.estado["dia"]:
                continue
            atraso = 0 if feita else max((dia - date.fromisoformat(avulsa["criada"])).days, 0)
            linha = self.linha_simples("avulsa", avulsa["texto"], feita, avulsa, ao_vivo)
            linha.atraso = atraso
            (atrasadas if atraso else avulsas_dia).append(linha)
        habitos = [self.linha_habito(h, ao_vivo) for h in self.habitos]
        missoes = [self.linha_missao(m, ao_vivo) for m in self.ativas()]
        return atrasadas + habitos + missoes + avulsas_dia

    def minutos_de(self, nome, ao_vivo):
        correndo = bool(ao_vivo) and ao_vivo[0] == nome
        return self.estado["minutos_hoje"].get(nome, 0) + (ao_vivo[1] if correndo else 0), correndo

    def linha_simples(self, tipo, nome, feita, ref, ao_vivo, contagem=""):
        minutos, correndo = self.minutos_de(nome, ao_vivo)
        partes = [parte for parte in (contagem, f"{int(minutos)} min" if minutos >= 1 else "") if parte]
        return Linha(tipo, nome, feita, ref=ref, detalhe=" · ".join(partes), correndo=correndo)

    def linha_habito(self, habito, ao_vivo):
        id_marca, vezes = f"h:{habito['nome']}", vezes_do(habito)
        contagem = f"{self.estado['contagens'].get(id_marca, 0)}/{vezes}" if vezes > 1 else ""
        return self.linha_simples("habito", habito["nome"], id_marca in self.estado["marcados"], habito, ao_vivo, contagem)

    def linha_missao(self, missao, ao_vivo):
        nome = missao["nome"]
        minutos, correndo = self.minutos_de(nome, ao_vivo)
        feita = f"m:{nome}" in self.estado["marcados"]
        texto = f"{nome} · {missao['minutos_dia']} min" if feita else f"{nome} · {int(minutos)}/{missao['minutos_dia']} min"
        excedente = max(0, int(minutos) - missao["minutos_dia"]) if feita else 0
        return Linha("missao", texto, feita, ref=missao, correndo=correndo, excedente=excedente)

    def linhas_missao(self):
        linhas = []
        for categoria in ajustes.categorias_missao:
            missao = self.missao_da(categoria)
            if not missao:
                linhas.append(Linha("vazio", categoria, selecionavel=False))
                continue
            fila = sum(1 for m in self.missoes if m["categoria"] == categoria and m["estado"] == "fila")
            percentual = progresso(missao)
            horas = tempo_texto(missao["minutos"])
            if missao.get("meta_horas"):
                horas += f"/{horas_texto(missao['meta_horas'])}h"
            partes = [f"{missao['feitos']}/{missao['total']}"] if missao.get("total") and not missao["marcos"] else []
            linhas.append(Linha("cabecalho", f"{categoria.upper()} · {missao['nome']}", ref=missao, detalhe=f"+{fila} na fila" if fila else ""))
            linhas.append(Linha("barra", selecionavel=False, ref=missao, progresso=percentual, detalhe=" · ".join(partes + [horas])))
            concluidos = sum(m["feito"] for m in missao["marcos"])
            if ajustes.ocultar_marcos_feitos and concluidos:
                linhas.append(Linha("resumo", f"{concluidos} concluídos", True, selecionavel=False))
            for marco in missao["marcos"]:
                if not (ajustes.ocultar_marcos_feitos and marco["feito"]):
                    linhas.append(Linha("marco", marco["nome"], marco["feito"], ref=marco, pai=missao))
        return linhas

    def placar(self, linhas=None):
        linhas = self.linhas_hoje() if linhas is None else linhas
        feitos = sum(linha.feita for linha in linhas)
        meta = max(1, min(ajustes.minimo_dia, len(linhas)))
        return feitos, len(linhas), meta

    def sequencia(self):
        feitos, _, meta = self.placar()
        total = 1 if feitos >= meta else 0
        dia = date.fromisoformat(self.estado["dia"]) - timedelta(days=1)
        while self.historico.get(dia.isoformat(), {}).get("cumpriu"):
            total += 1
            dia -= timedelta(days=1)
        return total

    def semana(self):
        hoje = date.fromisoformat(self.estado["dia"])
        segunda = hoje - timedelta(days=hoje.weekday())
        inicio = date.fromisoformat(self.estado["inicio"])
        feitos, _, meta = self.placar()
        resultado = []
        for posicao, rotulo in enumerate(dias_semana):
            dia = segunda + timedelta(days=posicao)
            if dia == hoje:
                situacao = "cumprido" if feitos >= meta else "hoje"
            elif dia > hoje or dia < inicio:
                situacao = "vazio"
            else:
                situacao = "cumpriu" if self.historico.get(dia.isoformat(), {}).get("cumpriu") else "falhou"
            resultado.append((rotulo, situacao))
        return resultado

    # ações

    def mudar_xp(self, valor):
        antes = self.nivel()
        self.estado["xp"] = max(0, self.estado["xp"] + valor)
        if self.nivel() > antes:
            self.eventos.append(("nivel", antes, self.nivel()))

    def celebrar(self):
        self.eventos.append(("concluir",))

    def alternar(self, id_marca, xp):
        marcados = self.estado["marcados"]
        if id_marca in marcados:
            marcados.remove(id_marca)
            self.mudar_xp(-xp)
        else:
            marcados.append(id_marca)
            self.mudar_xp(xp)

    def marcar(self, linha):
        if linha.tipo == "habito":
            self.marcar_habito(linha.ref)
            self.salvar("estado")
        elif linha.tipo == "avulsa":
            avulsa = linha.ref
            desfazer = avulsa["feita_em"] is not None
            pontos = pontos_de(avulsa, "avulsa")
            avulsa["feita_em"] = None if desfazer else self.estado["dia"]
            self.mudar_xp(-pontos if desfazer else pontos)
            if not desfazer:
                self.celebrar()
            self.salvar("tarefas", "estado")
        elif linha.tipo == "missao":
            if not ajustes.permitir_marcar_missao_manual:
                return "missões se marcam pelo cronômetro"
            self.alternar(f"m:{linha.ref['nome']}", xp.regras["habito"])
            self.salvar("estado")
        elif linha.tipo == "marco":
            marco = linha.ref
            marco["feito"] = not marco["feito"]
            pontos = pontos_de(marco, "marco")
            self.mudar_xp(pontos if marco["feito"] else -pontos)
            if marco["feito"]:
                self.celebrar()
            aviso = self.verificar_conclusao(linha.pai)
            self.salvar("missoes", "estado")
            return aviso
        elif linha.tipo == "cabecalho":
            return self.avancar(linha.ref)
        return ""

    def pode_avancar(self, missao):
        if missao["marcos"]:
            return any(not m["feito"] for m in missao["marcos"])
        return bool(missao.get("total")) and missao["feitos"] < missao["total"]

    def aviso_sem_cronometro(self, linha, ao_vivo=None):
        minimo = ajustes.minutos_minimos_marco
        if linha.tipo == "marco" and not linha.feita:
            missao = linha.pai
        elif linha.tipo == "cabecalho" and self.pode_avancar(linha.ref):
            missao = linha.ref
        else:
            return ""
        minutos, _ = self.minutos_de(missao["nome"], ao_vivo)
        if not minimo or minutos >= minimo:
            return ""
        return f"{missao['nome']}: {int(minutos)} min cronometrados hoje (mínimo {minimo}). marcar mesmo assim?"

    def xp_do_passo(self, habito, passo):
        total, vezes = habito.get("xp", xp.regras["habito"]), vezes_do(habito)
        return total // vezes + (total % vezes if passo == vezes else 0)

    def marcar_habito(self, habito):
        id_marca, vezes = f"h:{habito['nome']}", vezes_do(habito)
        marcados, contagens = self.estado["marcados"], self.estado["contagens"]
        atual = contagens.get(id_marca, 0) if vezes > 1 else int(id_marca in marcados) * vezes
        if atual >= vezes:
            contagens.pop(id_marca, None)
            if id_marca in marcados:
                marcados.remove(id_marca)
            self.mudar_xp(-sum(self.xp_do_passo(habito, passo) for passo in range(1, atual + 1)))
            return
        if vezes > 1:
            contagens[id_marca] = atual + 1
        self.mudar_xp(self.xp_do_passo(habito, atual + 1))
        self.celebrar()
        if atual + 1 == vezes:
            marcados.append(id_marca)

    def desfazer_habito(self, habito):
        id_marca, vezes = f"h:{habito['nome']}", vezes_do(habito)
        contagens, marcados = self.estado["contagens"], self.estado["marcados"]
        atual = contagens.get(id_marca, 0)
        if vezes < 2 or not atual:
            return
        contagens[id_marca] = atual - 1
        if id_marca in marcados:
            marcados.remove(id_marca)
        self.mudar_xp(-self.xp_do_passo(habito, atual))
        self.salvar("estado")

    def avancar(self, missao):
        if missao["marcos"]:
            marco = next((m for m in missao["marcos"] if not m["feito"]), None)
            if not marco:
                return "todos os marcos já foram feitos"
            marco["feito"] = True
            self.mudar_xp(pontos_de(marco, "marco"))
        elif missao.get("total"):
            if missao["feitos"] >= missao["total"]:
                return ""
            missao["feitos"] += 1
            self.mudar_xp(xp.regras["unidade"])
        else:
            return "essa missão não tem marcos nem total · c conclui"
        self.celebrar()
        aviso = self.verificar_conclusao(missao)
        self.salvar("missoes", "estado")
        return aviso

    def desfazer(self, missao):
        if missao["marcos"]:
            feitos = [m for m in missao["marcos"] if m["feito"]]
            if not feitos:
                return
            feitos[-1]["feito"] = False
            self.mudar_xp(-pontos_de(feitos[-1], "marco"))
        elif missao.get("total") and missao["feitos"] > 0:
            missao["feitos"] -= 1
            self.mudar_xp(-xp.regras["unidade"])
        else:
            return
        self.salvar("missoes", "estado")

    def concluir(self, missao):
        missao["estado"] = "concluida"
        missao["encerrada_em"] = self.estado["dia"]
        self.mudar_xp(xp.regras["missao"])
        self.ativar_proxima(missao["categoria"])
        self.salvar("missoes", "estado")
        return f"missão concluída: {missao['nome']} (+{xp.regras["missao"]} xp)"

    def verificar_conclusao(self, missao):
        if missao["estado"] != "ativa" or (progresso(missao) or 0) < 1:
            return ""
        missao["estado"] = "concluida"
        missao["encerrada_em"] = self.estado["dia"]
        self.mudar_xp(xp.regras["missao"])
        self.ativar_proxima(missao["categoria"])
        return f"missão concluída: {missao['nome']} (+{xp.regras["missao"]} xp)"

    def ativar_proxima(self, categoria):
        proxima = next((m for m in self.missoes if m["categoria"] == categoria and m["estado"] == "fila"), None)
        if proxima:
            proxima["estado"] = "ativa"

    def bater_meta(self, nome, extra=0):
        missao = self.missao_por_nome(nome)
        id_marca = f"m:{nome}"
        if not missao or id_marca in self.estado["marcados"]:
            return False
        if self.estado["minutos_hoje"].get(nome, 0) + extra < missao["minutos_dia"]:
            return False
        self.estado["marcados"].append(id_marca)
        self.mudar_xp(xp.regras["habito"])
        self.celebrar()
        self.salvar("estado")
        return True

    def registrar_sessao(self, nome, minutos):
        missao = self.missao_por_nome(nome)
        minutos = round(minutos, 2)
        hoje = self.estado["minutos_hoje"]
        hoje[nome] = round(hoje.get(nome, 0) + minutos, 2)
        self.mudar_xp(int(minutos) * xp.regras["minuto"])
        if not missao:
            self.salvar("estado")
            return []
        missao["minutos"] = round(missao["minutos"] + minutos, 2)
        avisos = [f"meta do dia batida: {nome}"] if self.bater_meta(nome) else []
        avisos.append(self.verificar_conclusao(missao))
        self.salvar("missoes", "estado")
        return [aviso for aviso in avisos if aviso]

    def nome_em_uso(self, nome, ignorar=None):
        return any(h["nome"].lower() == nome.lower() and h is not ignorar for h in self.habitos)

    def adicionar_avulsa(self, texto):
        nome, pontos = sintaxe.analisar_item(texto)
        if not nome:
            return "o texto não pode ficar vazio"
        avulsa = {"texto": nome, "criada": self.estado["dia"], "feita_em": None}
        if pontos:
            avulsa["xp"] = pontos
        self.avulsas.append(avulsa)
        self.salvar("tarefas")

    def adicionar_habito(self, texto):
        habito, erro = sintaxe.analisar_habito(texto)
        if not erro and self.nome_em_uso(habito["nome"]):
            erro = "já existe um hábito com esse nome"
        if erro:
            return erro
        self.habitos.append(habito)
        self.sincronizar_vida()
        self.salvar("habitos", "estado")
        if habito.get("vida") and habito["vida"] not in ajustes.barras_vida:
            return f"nova barra de vida criada: {habito['vida']}"

    def atualizar_xp(self, novos):
        xp.regras.update(novos)
        self.salvar("xp")

    def adicionar_marco(self, missao, texto):
        nome, pontos = sintaxe.analisar_item(texto)
        if not nome:
            return "o texto não pode ficar vazio"
        missao["marcos"].append({"nome": nome, "feito": False, **({"xp": pontos} if pontos else {})})
        self.salvar("missoes")

    def adicionar_missao(self, texto):
        novos, erro = sintaxe.analisar_missao(texto)
        if erro:
            return erro
        missao = {"categoria": novos["categoria"], "nome": novos["nome"], "minutos_dia": novos["minutos_dia"],
                  "minutos": 0, "feitos": 0, "estado": "fila", "marcos": []}
        missao.update({campo: novos[campo] for campo in ("meta_horas", "total", "xp") if novos[campo]})
        self.missoes.append(missao)
        normalizar_missoes(self.missoes)
        self.salvar("missoes")
        return f"{novos['nome']} entrou na fila de {novos['categoria']}" if missao["estado"] == "fila" else ""

    def renomear(self, antigo, novo, prefixo=None):
        trocas = [(self.estado["minutos_hoje"], antigo, novo)]
        if prefixo:
            trocas.append((self.estado["contagens"], f"{prefixo}:{antigo}", f"{prefixo}:{novo}"))
            marcados = self.estado["marcados"]
            if f"{prefixo}:{antigo}" in marcados:
                marcados[marcados.index(f"{prefixo}:{antigo}")] = f"{prefixo}:{novo}"
        for registro, velho, atual in trocas:
            if velho in registro:
                registro[atual] = registro.pop(velho)

    def editar(self, linha, texto):
        if linha.tipo == "habito":
            novo, erro = sintaxe.analisar_habito(texto)
            if not erro and self.nome_em_uso(novo["nome"], linha.ref):
                erro = "já existe um hábito com esse nome"
            if erro:
                return erro
            self.renomear(linha.ref["nome"], novo["nome"], "h")
            linha.ref.clear()
            linha.ref.update(novo)
            self.sincronizar_vida()
            self.salvar("habitos", "estado")
            return
        nome, pontos = sintaxe.analisar_item(texto)
        if not nome:
            return "o texto não pode ficar vazio"
        campo = "texto" if linha.tipo == "avulsa" else "nome"
        if linha.tipo == "avulsa":
            self.renomear(linha.ref["texto"], nome)
        linha.ref[campo] = nome
        if pontos:
            linha.ref["xp"] = pontos
        else:
            linha.ref.pop("xp", None)
        self.salvar("tarefas" if linha.tipo == "avulsa" else "missoes", "estado")

    def editar_missao(self, missao, texto):
        novos, erro = sintaxe.analisar_missao(texto)
        if erro:
            return erro
        self.renomear(missao["nome"], novos["nome"], "m")
        missao.update(nome=novos["nome"], categoria=novos["categoria"], minutos_dia=novos["minutos_dia"])
        for campo in ("meta_horas", "total", "xp"):
            if novos[campo]:
                missao[campo] = novos[campo]
            else:
                missao.pop(campo, None)
        normalizar_missoes(self.missoes)
        self.salvar("missoes", "estado")

    def remover(self, linha):
        if linha.tipo == "habito":
            self.habitos.remove(linha.ref)
            if f"h:{linha.texto}" in self.estado["marcados"]:
                self.estado["marcados"].remove(f"h:{linha.texto}")
            self.estado["contagens"].pop(f"h:{linha.texto}", None)
            self.sincronizar_vida()
            self.salvar("habitos", "estado")
        elif linha.tipo == "avulsa":
            self.avulsas.remove(linha.ref)
            self.salvar("tarefas")
        elif linha.tipo == "marco":
            linha.pai["marcos"].remove(linha.ref)
            self.salvar("missoes")
        elif linha.tipo == "cabecalho":
            linha.ref["estado"] = "abandonada"
            linha.ref["encerrada_em"] = self.estado["dia"]
            self.ativar_proxima(linha.ref["categoria"])
            self.salvar("missoes")

    # virada de dia

    def virar_dias(self):
        hoje = date.today()
        dia = min(date.fromisoformat(self.estado["dia"]), hoje)
        self.estado["dia"] = dia.isoformat()
        primeiro = True
        while dia < hoje:
            self.fechar_dia(dia, ausente=not primeiro)
            primeiro = False
            dia += timedelta(days=1)
            self.estado["dia"] = dia.isoformat()
        if not primeiro:
            self.salvar("estado", "historico", "tarefas")

    def fechar_dia(self, dia, ausente):
        linhas = self.linhas_hoje()
        feitos, total, meta = self.placar(linhas)
        if not ausente or ajustes.penalizar_dias_ausentes:
            marcados = self.estado["marcados"]
            vida = self.estado["vida"]
            for habito in self.habitos:
                barra = habito.get("vida")
                if barra in vida:
                    delta = 1 if f"h:{habito['nome']}" in marcados else -1
                    vida[barra] = min(max(vida[barra] + delta, 0), ajustes.vida_maxima)
        self.historico[dia.isoformat()] = {"feitos": feitos, "total": total, "cumpriu": feitos >= meta, "ausente": ausente, "excedente": sum(l.excedente for l in linhas if l.tipo == "missao" and l.feita), "itens": [descrever(l) for l in linhas if l.feita], "faltaram": [descrever(l) for l in linhas if not l.feita]}
        self.avulsas = [a for a in self.avulsas if a["feita_em"] is None]
        self.estado["marcados"] = []
        self.estado["contagens"] = {}
        self.estado["minutos_hoje"] = {}
