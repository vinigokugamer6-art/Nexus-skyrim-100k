
import os
import time
import requests
from pathlib import Path

API_KEY = os.environ.get("NEXUS_API_KEY", "")
JOGO = "skyrimspecialedition"
PASTA = Path("resultados")
PASTA.mkdir(exist_ok=True)

if not API_KEY:
    raise RuntimeError("Configure NEXUS_API_KEY nos Secrets do GitHub.")

sessao = requests.Session()
sessao.headers.update({
    "apikey": API_KEY,
    "User-Agent": "CatalogoNexusMods/1.0"
})

registros = {}

# Listas oficiais disponíveis na API
for tipo in ["latest_added", "latest_updated", "trending"]:
    url = f"https://api.nexusmods.com/v1/games/{JOGO}/mods/{tipo}.json"
    resposta = sessao.get(url, timeout=30)
    print(tipo, resposta.status_code)
    resposta.raise_for_status()

    for mod in resposta.json():
        mid = mod.get("mod_id")
        nome = mod.get("name")
        if mid and nome:
            registros[int(mid)] = nome

    restante = resposta.headers.get("x-rl-daily-remaining")
    if restante is not None and int(restante) < 5:
        print("Limite da API próximo. Parando.")
        break
    time.sleep(2)

ordenados = sorted(
    registros.items(),
    key=lambda item: (item[1].casefold(), item[0])
)

for extensao in ["txt", "md"]:
    caminho = PASTA / f"Skyrim_SE_Parte_001.{extensao}"
    with caminho.open("w", encoding="utf-8") as arquivo:
        for numero, (mid, nome) in enumerate(ordenados, 1):
            link = f"https://www.nexusmods.com/skyrimspecialedition/mods/{mid}"
            if extensao == "md":
                arquivo.write(f"{numero}. [{nome}]({link})\n")
            else:
                arquivo.write(f"{numero}. {nome} | {link}\n")

print("Mods reais coletados:", len(ordenados))
print("Arquivos salvos em resultados/")

