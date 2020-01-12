#!/usr/bin/sh

# Set the link for UD2.x Data here
ud_link = https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3105/ud-treebanks-v2.5.tgz
ud_version = 2.5
lang_name = Sanskrit
lang_code = sa
lang_name_lower = echo "$(lang_name)" | tr '[:upper:]' '[:lower:]'
udpipe_link = https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2998/sanskrit-ufal-ud-2.4-190531.udpipe

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
#	cd dataset; \
#		if ! [ -f sa.udpipe ]; then \
#			wget -O sa.udpipe `echo $(udpipe_link)`; \
#		fi; \
#		if ! [ -f sa.conllu ]; then \
#			udpipe --tag --input=horizontal sa.udpipe < sa.corpus > sa.conllu; \
#		fi;

#process_data:
#	python3 scripts/get_lexemes.py --lang_code `echo $(lang_code)` -id dataset;
