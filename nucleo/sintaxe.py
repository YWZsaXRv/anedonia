#
# feito por YWZsaXRv
#

import re

from config import ajustes

padroes = (
    ("vezes", r"x(\d+)"),
    ("xp", r"xp(\d+)"),
    ("vida", r"@(\w+)"),
    ("minutos", r"(\d+(?:[.,]\d+)?)min"),
    ("horas", r"(\d+(?:[.,]\d+)?)h"),
    ("total", r"/(\d+)"),
    ("categoria", r"#(\w+)"),
)


def numero(texto):
    return float(texto.replace(",", "."))


def analisar(texto, permitidos):
    nome, campos = [], {}
    for palavra in texto.split():
        for campo, padrao in padroes:
            achado = re.fullmatch(padrao, palavra, re.I) if campo in permitidos else None
            if achado:
                campos[campo] = achado.group(1)
                break
        else:
            nome.append(palavra)
    return " ".join(nome), campos


def vezes_do(habito):
    return max(1, int(habito.get("vezes", 1)))


def analisar_item(texto):
    nome, campos = analisar(texto, {"xp"})
    return nome, int(campos["xp"]) if "xp" in campos else None


def analisar_habito(texto):
    nome, campos = analisar(texto, {"vezes", "xp", "vida"})
    habito = {"nome": nome}
    if int(campos.get("vezes", 1)) > 1:
        habito["vezes"] = int(campos["vezes"])
    if "xp" in campos:
        habito["xp"] = int(campos["xp"])
    if "vida" in campos:
        habito["vida"] = campos["vida"].lower()
    return habito, "" if nome else "o nome não pode ficar vazio"


def analisar_missao(texto):
    nome, campos = analisar(texto, {"minutos", "horas", "total", "categoria", "xp"})
    categoria = campos.get("categoria", ajustes.categorias_missao[0]).lower()
    if not nome:
        return {}, "o nome não pode ficar vazio"
    if categoria not in ajustes.categorias_missao:
        return {}, f"categoria deve ser: {' ou '.join(ajustes.categorias_missao)}"
    minutos = numero(campos["minutos"]) if "minutos" in campos else ajustes.minutos_padrao
    return {
        "nome": nome,
        "categoria": categoria,
        "minutos_dia": max(1, int(minutos)),
        "meta_horas": numero(campos["horas"]) if "horas" in campos else None,
        "total": int(campos["total"]) if "total" in campos else None,
        "xp": int(campos["xp"]) if "xp" in campos else None,
    }, ""


def escrever_item(nome, pontos):
    return nome + (f" xp{pontos}" if pontos else "")


def escrever_habito(habito):
    partes = [habito["nome"]]
    if habito.get("vezes"):
        partes.append(f"x{habito['vezes']}")
    if habito.get("vida"):
        partes.append(f"@{habito['vida']}")
    if habito.get("xp"):
        partes.append(f"xp{habito['xp']}")
    return " ".join(partes)


def escrever_missao(missao):
    partes = [missao["nome"], f"#{missao['categoria']}", f"{missao['minutos_dia']}min"]
    if missao.get("meta_horas"):
        partes.append(f"{missao['meta_horas']:g}h")
    if missao.get("total"):
        partes.append(f"/{missao['total']}")
    if missao.get("xp"):
        partes.append(f"xp{missao['xp']}")
    return " ".join(partes)
