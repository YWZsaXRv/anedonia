#
# feito por YWZsaXRv
#

import math
import struct
import wave
from pathlib import Path

taxa = 44100
pasta = Path(__file__).parent


def nota(frequencia, duracao, volume=0.35, queda=5.0):
    quadros = int(taxa * duracao)
    amostras = []
    for i in range(quadros):
        t = i / taxa
        envelope = min(t / 0.005, 1.0) * math.exp(-queda * t / duracao)
        onda = math.sin(2 * math.pi * frequencia * t) + 0.35 * math.sin(4 * math.pi * frequencia * t) + 0.12 * math.sin(6 * math.pi * frequencia * t)
        amostras.append(volume * envelope * onda / 1.47)
    return amostras


def misturar(trilhas):
    tamanho = max(inicio + len(amostras) for inicio, amostras in trilhas)
    saida = [0.0] * tamanho
    for inicio, amostras in trilhas:
        for i, valor in enumerate(amostras):
            saida[inicio + i] += valor
    return saida


def gravar(nome, amostras):
    with wave.open(str(pasta / f"{nome}.wav"), "wb") as arquivo:
        arquivo.setnchannels(1)
        arquivo.setsampwidth(2)
        arquivo.setframerate(taxa)
        arquivo.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, valor)) * 32767)) for valor in amostras))


concluir = misturar([(0, nota(659.25, 0.09, queda=3)), (int(taxa * 0.08), nota(987.77, 0.28))])
notas_nivel = (523.25, 659.25, 783.99, 1046.5, 1318.5)
nivel = misturar(
    [(int(taxa * 0.095 * i), nota(f, 0.14 if i < 4 else 0.9, queda=3 if i < 4 else 4.5)) for i, f in enumerate(notas_nivel)]
    + [(int(taxa * 0.38), nota(2093.0, 0.7, volume=0.12, queda=6))]
)
gravar("concluir", concluir)
gravar("nivel", nivel)
