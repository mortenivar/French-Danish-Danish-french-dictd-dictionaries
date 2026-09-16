#!/usr/bin/env python

import os
import re
import html
import subprocess
import pandas as pd

# --- Konfiguration ---
RAA_ORDBOG_FIL = "fransk-dansk-ordbog.txt"  
LEXIQUE_FILE = "Lexique383.tsv"
OUTPUT_BASE = "fra-dan"

# SAMPA til rigtig IPA tabel
SAMPA_TO_IPA = {
    "E": "ɛ", "O": "ɔ", "°": "ə", "@": "ɑ̃", "§": "ɔ̃",
    "1": "œ̃", "5": "ɛ̃", "S": "ʃ", "Z": "ʒ", "R": "ʀ",
    "8": "ɥ", "2": "ø", "9": "œ"
}

def convert_sampa_to_ipa(sampa_str):
    if not isinstance(sampa_str, str):
        return ""
    ipa_str = sampa_str
    for sampa, ipa in SAMPA_TO_IPA.items():
        ipa_str = ipa_str.replace(sampa, ipa)
    return ipa_str

def main():
    if not os.path.exists(LEXIQUE_FILE) or not os.path.exists(RAA_ORDBOG_FIL):
        print(f"Fejl: Sørg for at både '{LEXIQUE_FILE}' og '{RAA_ORDBOG_FIL}' findes.")
        return

    # 1. Indlæs udtale-indeks fra Lexique
    print("Indlæser Lexique udtale-indeks...")
    df_lex = pd.read_csv(LEXIQUE_FILE, sep="\t", usecols=["ortho", "phon"])
    df_lex = df_lex.drop_duplicates(subset=["ortho"])
    udtale_dict = dict(zip(df_lex["ortho"], df_lex["phon"].apply(convert_sampa_to_ipa)))
    del df_lex

    print(f"Parser {RAA_ORDBOG_FIL}...")
    
    with open(RAA_ORDBOG_FIL, "r", encoding="utf-8") as f:
        lines = f.readlines()

    dict_entries = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        fransk_ord = ""
        ordklasse = ""
        forklaring = ""

        # KATEGORI 1: BØJNINGSFORMER (f.eks. après-ventes (plur. af après-vente) eller acceptiez v (imparfait...))
        if " v (" in line or " (plur." in line or " (af " in line:
            # Forsøg at splitte ved første tegn på bøjningsinfo eller ordklasse
            if " v (" in line:
                parts = line.split(" v (", 1)
                ordklasse = "v"
                forklaring = "(" + parts[1].strip()
            else:
                parts = line.split(" (", 1)
                ordklasse = ""
                forklaring = "(" + parts[1].strip()
            fransk_ord = parts[0].strip()
        else:
            # KATEGORI 2: STANDARD OPSLAG
            match = re.search(r"\s+(ms|f|v|m|adj|adv|prep|conj|int|af)\s+", line)
            if match:
                pos_start = match.start()
                pos_end = match.end()
                fransk_ord = line[:pos_start].strip()
                ordklasse = match.group(1).strip()
                forklaring = line[pos_end:].strip()
            else:
                parts = line.split(" ", 1)
                fransk_ord = parts[0].strip()
                ordklasse = ""
                forklaring = parts[1].strip() if len(parts) > 1 else ""

        if not fransk_ord:
            continue

        # Hent udtale (Lexique bruger sjældent bindestreger, så vi tjekker også uden)
        clean_word = fransk_ord.replace("-", "")
        ipa = udtale_dict.get(fransk_ord, udtale_dict.get(clean_word, ""))
        
        # Opbyg toplinjen: après-ventes /udtale/
        toplinje_dele = [fransk_ord]
        if ordklasse:
            toplinje_dele.append(f"<{ordklasse}>")
        if ipa:
            toplinje_dele.append(f"/{ipa}/")
            
        toplinje = " ".join(toplinje_dele)
        formateret_forklaring = forklaring.replace("; ", "\n  - ").replace(";", "\n  - ")
        
        entry_text = f"{toplinje}\n  - {formateret_forklaring}\n"
        dict_entries.append((fransk_ord, entry_text))

    # Sorter indgangene alfabetisk efter dictds krav
    dict_entries.sort(key=lambda x: x[0].lower())

    dict_file_path = f"{OUTPUT_BASE}.dict"
    idx_file_path = f"{OUTPUT_BASE}.index"

    print("Skriver direkte til .dict og .index format med globale headere...")
    
    # Definer de magiske overskrifter dictd skal bruge for at acceptere UTF-8 og specialtegn i søgningen
    headers = "00-database-utf8\n00-database-allchars\n"
    
    with open(dict_file_path, "w", encoding="utf-8") as d_file, open(idx_file_path, "w", encoding="utf-8") as i_file:
        # Start offset efter de globale headere
        current_offset = len(headers.encode("utf-8"))
        
        # Skriv de globale headere først i .dict-filen
        d_file.write(headers)
        
        for word, body in dict_entries:
            body_bytes = body.encode("utf-8")
            body_length = len(body_bytes)
            
            # Skriv selve definitionen
            d_file.write(body)
            
            # Kodning til dictd indeksstørrelser (Base64-dictd)
            def to_base64_dictd(num):
                chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
                if num == 0:
                    return "A"
                res = ""
                while num > 0:
                    res = chars[num % 64] + res
                    num //= 64
                return res

            b64_offset = to_base64_dictd(current_offset)
            b64_length = to_base64_dictd(body_length)
            
            # Skriv ordet og dets byte-placering til indekset
            i_file.write(f"{word}\t{b64_offset}\t{b64_length}\n")
            current_offset += body_length

    # Kør dictzip på .dict filen
#    if os.path.exists(dict_file_path):
#        print(f"Komprimerer {dict_file_path} med dictzip...")
#        subprocess.run(["dictzip", "-f", dict_file_path])

    print(f"Udført!")

if __name__ == "__main__":
    main()
