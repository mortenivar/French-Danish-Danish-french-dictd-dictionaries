#!/usr/bin/env python

import os
import re
import subprocess
import pandas as pd

# --- Konfiguration ---
RAA_ORDBOG_FIL = "fransk-dansk-ordbog.txt"  
LEXIQUE_FILE = "Lexique383.tsv"
DANSK_UDTALE_FIL = "udtaleordbog-dansk.txt"  
OUTPUT_BASE = "dan-fra"  

# SAMPA til rigtig IPA tabel (til fransk Lexique)
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

def rense_dansk_ord(ord_str):
    # 1. Fjern forklarende parenteser i selve ordet f.eks. "sænke (en handling)" -> "sænke"
    rent_ord = re.sub(r"\(.*?\)", "", ord_str)
    # 2. Fjern punktummer, kommaer og andre skilletegn til sidst eller i starten af ordet (f.eks. "bil." -> "bil")
    rent_ord = rent_ord.strip(".,;:!? ")
    return rent_ord.lower()

def main():
    if not os.path.exists(LEXIQUE_FILE) or not os.path.exists(RAA_ORDBOG_FIL) or not os.path.exists(DANSK_UDTALE_FIL):
        print(f"Fejl: Sørg for at både '{LEXIQUE_FILE}', '{RAA_ORDBOG_FIL}' og '{DANSK_UDTALE_FIL}' findes i mappen.")
        return

    # 1. Indlæs udtale-indeks fra fransk Lexique
    print("Indlæser fransk Lexique udtale-indeks...")
    df_lex = pd.read_csv(LEXIQUE_FILE, sep="\t", usecols=["ortho", "phon"])
    df_lex = df_lex.drop_duplicates(subset=["ortho"])
    fransk_udtale_dict = dict(zip(df_lex["ortho"], df_lex["phon"].apply(convert_sampa_to_ipa)))
    del df_lex

    # 2. Indlæsning av Dansk Udtaleordbog (Semikolon-separeret CSV format)
    print("Indlæser Dansk Udtaleordbog...")
    dansk_udtale_dict = {}
    
    with open(DANSK_UDTALE_FIL, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("Based on") or line.startswith("The list") or line.startswith("Orthography;"):
                continue
                
            if ";" in line:
                parts = line.split(";")
                if len(parts) >= 2:
                    da_word = parts[0].strip().lower()
                    da_ipa = parts[1].strip()
                    
                    if ";" in da_ipa:
                        da_ipa = da_ipa.split(";")[0].strip()
                        
                    da_ipa_clean = da_ipa.strip("[]//")
                    
                    if da_word not in dansk_udtale_dict:
                        dansk_udtale_dict[da_word] = da_ipa_clean

    print(f"Inverterer {RAA_ORDBOG_FIL} til Dansk-Fransk og fletter udtaler...")
    
    with open(RAA_ORDBOG_FIL, "r", encoding="utf-8") as f:
        lines = f.readlines()

    fra_dan_mappe = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        fransk_ord = ""
        ordklasse = ""
        forklaring = ""

        # KATEGORI 1: BØJNINGSFORMER (Springes over i den omvendte)
        if " v (" in line or " (plur." in line or " (af " in line:
            continue

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

        if not fransk_ord or not forklaring:
            continue

        # Hent fransk udtale
        clean_word = fransk_ord.replace("-", "")
        fransk_ipa = fransk_udtale_dict.get(fransk_ord, fransk_udtale_dict.get(clean_word, ""))
        
        # Formater den franske destination
        fransk_target = fransk_ord
        if ordklasse:
            fransk_target += f" <{ordklasse}>"
        if fransk_ipa:
            fransk_target += f" /{fransk_ipa}/"

        # Split forklaringen op i individuelle danske ord
        danske_ord = re.split(r"[;,]\s*", forklaring)

        for d_ord in danske_ord:
            rent_dansk = rense_dansk_ord(d_ord)
            # Ignorer hvis ordet blev tomt eller er for kort
            if not rent_dansk or len(rent_dansk) < 2:
                continue
            
            if rent_dansk not in fra_dan_mappe:
                fra_dan_mappe[rent_dansk] = set()
            
            fra_dan_mappe[rent_dansk].add(fransk_target)

    # Byg dictd-indgange
    dict_entries = []
    for dansk_opslag, franske_oversaettelser in fra_dan_mappe.items():
        dansk_ipa = dansk_udtale_dict.get(dansk_opslag, "")
        
        toplinje = dansk_opslag
        if dansk_ipa:
            toplinje += f" /{dansk_ipa}/"
            
        oversaettelser_streng = "\n  - ".join(sorted(franske_oversaettelser))
        entry_text = f"{toplinje}\n  - {oversaettelser_streng}\n"
        dict_entries.append((dansk_opslag, entry_text))

    dict_entries.sort(key=lambda x: x[0].lower())

    dict_file_path = f"{OUTPUT_BASE}.dict"
    idx_file_path = f"{OUTPUT_BASE}.index"

    print(f"Genererer {dict_file_path} og {idx_file_path}...")
    headers = "00-database-utf8\n00-database-allchars\n"
    
    with open(dict_file_path, "w", encoding="utf-8") as d_file, open(idx_file_path, "w", encoding="utf-8") as i_file:
        current_offset = len(headers.encode("utf-8"))
        d_file.write(headers)
        
        for word, body in dict_entries:
            body_bytes = body.encode("utf-8")
            body_length = len(body_bytes)
            
            d_file.write(body)
            
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
            
            i_file.write(f"{word}\t{b64_offset}\t{b64_length}\n")
            current_offset += body_length

#    if os.path.exists(dict_file_path):
#        print(f"Komprimerer {dict_file_path} med dictzip...")
#        subprocess.run(["dictzip", "-f", dict_file_path])

    print(f"\nFærdig! Genstart din dictd-service.")

if __name__ == "__main__":
    main()
