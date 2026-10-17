<div align="center">

# Anedonia

![Vim](https://img.shields.io/badge/vim-019733?logo=vim&logoColor=white&height=24)
![Python](https://img.shields.io/badge/python-3776AB?logo=python&logoColor=white&height=24)
![Windows](https://img.shields.io/badge/windows-0078D6?height=24)
![Linux](https://img.shields.io/badge/linux-e95420?logo=linux&logoColor=white&height=24)

Gerenciador de tarefas TUI.

</div>

## Demo

<img width="1911" height="1051" alt="demo-0" src="https://github.com/user-attachments/assets/fd5ade71-a7ec-49fe-a302-ebf6c496d749" />


## Atalhos

| Tecla | Ação |
|-------|------|
| j k | descer / subir |
| h l | trocar de painel |
| espaço | marcar (hábito xN: +1; título de missão: avança 1) |
| t | cronômetro do item sob o cursor |
| a | nova tarefa (no painel missão: novo marco) |
| n | novo hábito |
| m | nova missão |
| e | editar o item sob o cursor |
| x | remover / abandonar missão |
| u | -1 num contador |
| c | concluir missão |
| v | histórico (árvore por dia) · tab alterna para concluídas |
| p | regras de xp |
| b | backup |
| q | sair |

## XP

| Item | Valor |
|------|-------|
| Hábito feito | 10 |
| Tarefa avulsa | 5 |
| Marco concluído | 50 |
| Aula/unidade | 15 |
| Missão concluída | 200 |
| Minuto cronometrado | 1 |
| XP por nível | 100 |

mude com `p` no app ou em `dados/xp.json`.

## Instalação Windows

```powershell
.\anedonia.ps1 -install     # cria o venv, instala as deps e cria o path
.\anedonia.ps1 -uninstall   # remove venv e path
```

## Instalação Linux

Em breve criarei um instalador. Por enquanto, crie o `.venv` manualmente, instale os requirements e rode o `anedonia.py`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python anedonia.py
```

## Backup

o backup é gravado ao sair, na virada do dia e com a tecla `b`.

na máquina nova: extraia o zip, ponha o `anedonia_backup.json` em `backup/` e rode normalmente:
sem `dados/`, ele restaura sozinho.

- `python anedonia.py --backup` grava o backup e sai
- `python anedonia.py --restaurar [arq]` restaura e sai
- `python anedonia.py --demo` reinicia com a demo (faz backup antes)

---

<div align="center">

Cuide de você.

</div>
