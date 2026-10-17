#
# feito por YWZsaXRv
#

import shutil
import subprocess
import sys
from pathlib import Path

from config import ajustes

pasta = Path(__file__).resolve().parent.parent / "sons"
players = (["afplay"], ["paplay"], ["pw-play"], ["aplay", "-q"], ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"])


def tocar(nome):
    arquivo = pasta / f"{nome}.wav"
    if not ajustes.sons_ativos or not arquivo.exists():
        return
    try:
        if sys.platform == "win32":
            import winsound

            winsound.PlaySound(str(arquivo), winsound.SND_FILENAME | winsound.SND_ASYNC)
            return
        for player in players:
            if shutil.which(player[0]):
                subprocess.Popen(player + [str(arquivo)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
    except Exception:
        pass
