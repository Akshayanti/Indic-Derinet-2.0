#!/usr/bin/sh

# Set the link for UD2.x Data here
ud_link = https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3105/ud-treebanks-v2.5.tgz
udpipe_link = https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2998/hindi-hdtb-ud-2.4-190531.udpipe
ud_version = 2.5
lang_name = Hindi
lang_code = hi
lang_name_lower = echo "$(lang_name)" | tr '[:upper:]' '[:lower:]'

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
		if ! [ -f pruned_train.hi ]; then \
			if ! [ -f prunedCorpus.tar.gz ]; then \
				wget -c http://www.cfilt.iitb.ac.in/~moses/iitb_en_hi_parallel/iitb_corpus_download/prunedCorpus.tar.gz; \
			fi; \
			tar -xvf prunedCorpus.tar.gz; \
			rm -f pruned_train.en; \
		fi; \
		if ! [ -f hi.udpipe ]; then \
			wget -O hi.udpipe `echo $(udpipe_link)`; \
		fi; \
		if ! [ -f hi.conllu ]; then \
			udpipe --tag --input=horizontal hi.udpipe < pruned_train.hi > hi.conllu; \
		fi;
