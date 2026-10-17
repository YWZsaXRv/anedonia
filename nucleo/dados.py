#
# feito por YWZsaXRv
#

import json
import shutil
from pathlib import Path

from config import ajustes

raiz = Path(__file__).resolve().parent.parent
pasta = Path(ajustes.pasta_dados) if ajustes.pasta_dados else raiz / "dados"
pasta_demo = raiz / "demo"
pasta_backup = raiz / "backup"
nomes = ("habitos", "missoes", "tarefas", "estado", "historico", "xp")


class ErroDados(Exception):
    pass


def caminho(nome):
    return pasta / f"{nome}.json"


def ler(nome, padrao):
    arquivo = caminho(nome)
    if not arquivo.exists():
        return padrao
    try:
        return json.loads(arquivo.read_text(encoding="utf-8"))
    except json.JSONDecodeError as erro:
        raise ErroDados(f"{arquivo.name}, linha {erro.lineno}: {erro.msg}") from erro


def gravar(nome, conteudo):
    pasta.mkdir(parents=True, exist_ok=True)
    arquivo = caminho(nome)
    temporario = arquivo.with_suffix(".tmp")
    temporario.write_text(json.dumps(conteudo, ensure_ascii=False, indent=2), encoding="utf-8")
    temporario.replace(arquivo)


def modificado(nome):
    arquivo = caminho(nome)
    return arquivo.stat().st_mtime_ns if arquivo.exists() else 0


def existe_algum():
    return any(caminho(nome).exists() for nome in nomes)


def copiar_demo():
    pasta.mkdir(parents=True, exist_ok=True)
    for arquivo in pasta_demo.glob("*.json"):
        shutil.copy(arquivo, pasta / arquivo.name)
