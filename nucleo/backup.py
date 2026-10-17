#
# feito por YWZsaXRv
#

import json
from datetime import datetime
from pathlib import Path

from nucleo import dados

arquivo_padrao = dados.pasta_backup / "anedonia_backup.json"


def exportar(destino=None):
    destino = Path(destino) if destino else arquivo_padrao
    conteudo = {
        "versao": 1,
        "criado_em": datetime.now().isoformat(timespec="seconds"),
        "dados": {nome: dados.ler(nome, None) for nome in dados.nomes if dados.caminho(nome).exists()},
    }
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(conteudo, ensure_ascii=False, indent=2), encoding="utf-8")
    return destino


def restaurar(origem=None):
    origem = Path(origem) if origem else arquivo_padrao
    conteudo = json.loads(origem.read_text(encoding="utf-8"))
    for nome, valor in conteudo["dados"].items():
        if nome in dados.nomes:
            dados.gravar(nome, valor)
    return len(conteudo["dados"])
