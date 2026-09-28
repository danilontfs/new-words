# ---------------------------------------------
# generate-audios.py (versão com cópia do CSV)
# ---------------------------------------------
# Fluxo:
# 1) Lê planilha-anki.csv (fixo, no mesmo nível do .py).
# 2) Copia o CSV para a nova pasta "prefix" (a pasta de saída).
# 3) Gera áudios e salva na pasta "prefix".
# 4) Copia os áudios para a pasta do Anki (collection.media).
# 5) Atualiza a CÓPIA do CSV na pasta "prefix" (coluna 3 com [sound:...]).
# ---------------------------------------------

import os
import sys
import csv
import shutil
from elevenlabs import ElevenLabs

# ====== CONFIGURAÇÕES ======
base_dir = os.path.dirname(os.path.abspath(__file__))


def _load_api_key():
    key = os.environ.get("ELEVENLABS_API_KEY")
    if key:
        return key
    env_path = os.path.join(base_dir, ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("ELEVENLABS_API_KEY="):
                    return line.split("=", 1)[1].strip()
    return None


API_KEY = _load_api_key()
if not API_KEY:
    sys.exit(
        "ELEVENLABS_API_KEY não encontrada. Defina a variável de ambiente ou "
        "crie um arquivo .env (veja .env.example) com ELEVENLABS_API_KEY=sua_chave"
    )

# Caminho da pasta de mídia do Anki (Windows)
# ANKI_MEDIA_WINDOWS = r"C:\Users\Wapper\AppData\Roaming\Anki2\Usuário 1\collection.media"

# Se você roda este script NO WSL/Linux e quer copiar para o Anki do Windows:
ANKI_MEDIA_WINDOWS = r"/mnt/c/Users/Wapper/AppData/Roaming/Anki2/Usuário 1/collection.media"

# ====== CLIENTE ELEVENLABS ======
client = ElevenLabs(api_key=API_KEY)

# Nome da pasta de saída (prefixo dos arquivos), sempre dentro de lessons/
lessons_dir = os.path.join(base_dir, "lessons")
prefix = os.path.basename(sys.argv[1]) if len(sys.argv) > 1 else "news-audios"
output_dir = os.path.join(lessons_dir, prefix)
os.makedirs(output_dir, exist_ok=True)

# Arquivo CSV original (fixo)
csv_src = os.path.join(base_dir, "planilha-anki.csv")

# Cria uma cópia do CSV dentro da pasta nova
csv_copy = os.path.join(output_dir, f"{prefix}-planilha.csv")
shutil.copy2(csv_src, csv_copy)

# --- Ler a cópia do CSV ---
rows = []
phrases = []
has_header = False

with open(csv_copy, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.reader(f, delimiter=';')
    for idx, row in enumerate(reader):
        if not row:
            rows.append([])
            continue
        while len(row) < 3:
            row.append("")
        first_cell_lower = row[0].strip().lower()
        if idx == 0 and (first_cell_lower.startswith("front") or first_cell_lower.startswith("frente")):
            has_header = True
            rows.append(row)
            continue
        phrase = row[0].strip()
        rows.append(row)
        if phrase:
            phrases.append(phrase)

if not phrases:
    print("Nenhuma frase encontrada na primeira coluna do CSV.")
    sys.exit(1)

# --- Gerar áudios e atualizar a cópia do CSV ---
for i, phrase in enumerate(phrases, start=1):
    mp3_name = f"{prefix}-audio-{i:02d}.mp3"
    out_file = os.path.join(output_dir, mp3_name)

    response = client.text_to_speech.convert(
        # voice_id="56AoDkrOh6qfVPDXZ7Pt",      # Cassidy
        # voice_id="FGY2WhTYpPnrIDTdsKH5",      # Laura
        voice_id="EXAVITQu4vr4xnSDxMaL",      # Sarah
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
        voice_settings={
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0,
            "use_speaker_boost": True,
            "speed": 0.7
        },
        text=phrase
    )

    with open(out_file, "wb") as f:
        for chunk in response:
            f.write(chunk)
    print(f"Gerado: {out_file}")

    try:
        os.makedirs(ANKI_MEDIA_WINDOWS, exist_ok=True)
        shutil.copy2(out_file, os.path.join(ANKI_MEDIA_WINDOWS, mp3_name))
        print(f"  ↳ Copiado para Anki: {ANKI_MEDIA_WINDOWS}")
    except Exception as e:
        print(f"  ⚠️ Não foi possível copiar para o Anki ({ANKI_MEDIA_WINDOWS}): {e}")

    # Atualiza coluna 3 na cópia do CSV
    count_content = 0
    for r in rows:
        if not r:
            continue
        if has_header and (r is rows[0]):
            continue
        if not r[0].strip():
            continue
        count_content += 1
        if count_content == i:
            r[2] = f"[sound:{mp3_name}]"
            break

# --- Regravar a cópia do CSV ---
tmp_copy = csv_copy + ".tmp"
with open(tmp_copy, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f, delimiter=';')
    for r in rows:
        writer.writerow(r)
os.replace(tmp_copy, csv_copy)

print("\n✅ Concluído.")
print(f"   Áudios gerados em: {os.path.abspath(output_dir)}")
print(f"   CSV atualizado em: {csv_copy}")
print(f"   Cópias de áudio (se possível) em: {ANKI_MEDIA_WINDOWS}")
