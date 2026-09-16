# French-Danish  and Danish-French dictd dictionaries
Comprehensive dictd dictionaries for French-Danish and Danish-French

This repository contains dictionaries for the command-line and server utility `dictd`. Covering approximately 227,000 French entries and 59.000 Danish entries. The difference in numbers stem from the French-Danish dictionary containing many entries that are inflected words. These dictionaries have full International Phonetic Alphabet (IPA) phonetic transcriptions for **both** French and Danish.

## Features
- **Dual Pronunciation (IPA):** Features native French pronunciation (from Lexique) and Danish pronunciation (from Udtaleordbog.dk).

---

## Prerequisites

Before building the dictionaries, ensure you have Python 3 and the `pandas` library installed on your system. You will also need `dictzip` (part of the `dictd` suite) to compress the generated `.dict` files.

On Arch Linux, you can install the dependencies using:
```bash
sudo pacman -S python-pandas dictd
```

---

## Compilation and Building

### 1. Compile the Dictionaries
To unpack the source phonetics files and execute the Python compilation scripts, simply run:
```bash
make
```
This will automatically generate the required database files: `fra-dan.dict.dz`, `fra-dan.index`, `dan-fra.dict.dz`, and `dan-fra.index`.

### 2. Clean Up Temporary Files
To remove the compiled dictionary files and keep your local directory clean, run:
```bash
make clean
```

---

## Installation (Linux)

### 1. Install the Database Files
```bash
sudo make install
```

### 2. Configure the dictd Server
Open your dictd configuration file (usually located at `/etc/dictd/dictd.conf` or `/etc/dictd.conf`):
```bash
sudo nano /etc/dictd/dictd.conf
```

Add the following database definitions to the bottom of the file:
```text
database fra-dan {
    data "/usr/share/dictd/fra-dan.dict.dz"
    index "/usr/share/dictd/fra-dan.index"
}

database dan-fra {
    data "/usr/share/dictd/dan-fra.dict.dz"
    index "/usr/share/dictd/dan-fra.index"
}
```
---

## Usage

Query the server using the standard CLI client `dict`.

**French to Danish:**
```bash
dict -d fra-dan voiture
```
*Output example:*
> voiture /vwatyʀ/
>   - bil, vogn

**Danish to French:**
```bash
dict -d dan-fra sænke
```
*Output example:*
> sænke /sɛŋgə/
>   - abaisser <v> /abese/
>   - baisser <v> /bese/

---

## Attributions, Copyrights & Licenses

This project is a data compilation (a derivative work) merging several independent academic and open-source linguistic resources. The individual source licenses are fully compatible with this aggregation and are distributed under the following terms:

### 1. French Inflected Forms (Inria LEFF)
- **Source:** [LEFF (Lexique des Formes Fléchies du Français)](https://inria.fr) developed by Inria.
- **License:** **LGPLLR** (Lesser General Public License For Linguistic Resources).
- **Terms:** Permits free redistribution and integration as a linguistic component within third-party applications and databases without enforcing its own copyleft restrictions on the broader project.

### 2. French Phonetics and Pronunciation (Lexique.org)
- **Source:** [Lexique.org](http://lexique.org) developed by Christophe Pallier and Boris New (OpenLexicon project).
- **License:** **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**.
- **Terms:** The phonetic transcription data has been included and paired in compliance with the ShareAlike provisions. Any redistribution of the French phonetic dataset requires proper attribution to the original authors.

### 3. Danish Phonetics and Pronunciation (Udtaleordbog.dk)
- **Source:** [Udtaleordbog.dk](https://udtaleordbog.dk) developed and maintained by Ruben Schachtenhaufen.
- **License:** Free Academic/Public Pronunciation Dataset.
- **Terms:** The raw list is freely available to be downloaded, modified, paired, and redistributed for any purpose, with the condition of providing proper attribution to the project.

### 4. French to Danish translations
- **Source:** Various, some of it is my own work and some of it is of unknown origin with no information about copyright or licence. If anyone recognizes anything that might constitute copyright infringement, please contact me.
- **License:** MIT License, permitting unrestricted use, modification, and sharing.

### Project Utility Scripts
The building tools included in this repository (`fransk-dansk.py`, `dansk-fransk.py`) and the `Makefile` are licensed under the **MIT License**, permitting unrestricted use, modification, and sharing.
