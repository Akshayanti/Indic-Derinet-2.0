#!/usr/bin/sh

# Set the link for UD2.x Data here
ud_link = https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3105/ud-treebanks-v2.5.tgz
ud_version = 2.5
lang_name = Marathi
lang_code = mr
lang_name_lower = echo "$(lang_name)" | tr '[:upper:]' '[:lower:]'
udpipe_link = https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2998/marathi-ufal-ud-2.4-190531.udpipe

get_data:
	if ! [ -f dataset/ud_`echo lang_code`.conllu ]; then \
		if ! [ -d $(HOME)/ud-treebanks-v`echo $(ud_version)` ]; then \
			cd $(HOME); \
				wget -c `echo $(ud_link)`; \
				tar -xf ud-treebanks-v`echo $(ud_version)`.tgz; \
		fi; \
		for conllufile in $(HOME)/ud-treebanks-v`echo $(ud_version)`/UD_`echo $(lang_name)`-*/*.conllu; do \
			cat $$conllufile >> dataset/ud_`echo $(lang_code)`.conllu; \
		done; \
	fi;
	cd dataset; \
		if ! [ -f mr.udpipe ]; then \
			wget -O mr.udpipe `echo $(udpipe_link)`; \
		fi; \
		if ! [ -f mr.conllu ]; then \
			udpipe --tag --tokenize mr.udpipe < mr.corpus > mr.conllu; \
		fi;
