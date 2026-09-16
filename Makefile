# --- Konfiguration ---
DICT_DIR = /usr/share/dictd
CONF_FILE = /etc/dictd/dictd.conf

# Navne på de genererede færdige filer
TARGETS = fra-dan.dict.dz fra-dan.index dan-fra.dict.dz dan-fra.index

# Standard handling
all: $(TARGETS)

# Udpakning af udtalefiler
Lexique383.tsv: Lexique383.tsv.gz
	gunzip -k Lexique383.tsv.gz

udtaleordbog-dansk.txt: udtaleordbog-dansk.txt.gz
	gunzip -k udtaleordbog-dansk.txt.gz

fransk-dansk-ordbog.txt: fransk-dansk-ordbog.txt.gz
	gunzip -k fransk-dansk-ordbog.txt.gz

# RETTET TIL &: (Grouped Target) så make ved, at begge filer spyttes ud af én kørsel
fra-dan.dict.dz fra-dan.index &: fransk-dansk.py fransk-dansk-ordbog.txt.gz Lexique383.tsv
	@echo "Building French-Danish dictd dictionary"
	python3 fransk-dansk.py
	dictzip -f fra-dan.dict

# RETTET TIL &: (Grouped Target) så make ved, at begge filer spyttes ud af én kørsel
dan-fra.dict.dz dan-fra.index &: dansk-fransk.py fransk-dansk-ordbog.txt Lexique383.tsv udtaleordbog-dansk.txt
	@echo "Building Danish-French dictd dictionary"
	python3 dansk-fransk.py
	dictzip -f dan-fra.dict

# Install target
install: all
	@echo "Installing dictionary files to $(DICT_DIR)"
	mkdir -p $(DICT_DIR)
	cp fra-dan.dict.dz fra-dan.index dan-fra.dict.dz dan-fra.index $(DICT_DIR)/
	chmod 644 $(DICT_DIR)/fra-dan.dict.dz $(DICT_DIR)/fra-dan.index
	chmod 644 $(DICT_DIR)/dan-fra.dict.dz $(DICT_DIR)/dan-fra.index
	@echo ""
	@echo "Remember to add the databases to the $(CONF_FILE)"
	systemctl restart dictd.service
	@echo "All done!"

# Clean target
clean:
	@echo "Cleaning up ..."
	rm -f $(TARGETS) fra-dan.dict dan-fra.dict Lexique383.tsv udtaleordbog-dansk.txt fransk-dansk-ordbog.txt

.PHONY: all install clean
