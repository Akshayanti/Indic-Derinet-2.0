#!/usr/bin/sh

get_extra_data:
	if ! [ -d downloads ]; then \
		mkdir downloads; \
	fi; \
	cd downloads; \
		if ! [ -f ../tam/dataset/ta.corpus ]; then \
			if ! [ -f indic_languages_corpus.tar.gz ]; then \
				wget -c http://lotus.kuee.kyoto-u.ac.jp/WAT/indic-multilingual/indic_languages_corpus.tar.gz; \
			fi; \
			tar -xvf indic_languages_corpus.tar.gz; \
			mv indic_languages_corpus/monolingual/monolingual.ta ../tam/dataset/ta.corpus; \
			mv indic_languages_corpus/monolingual/monolingual.ur ../ur/dataset/ur.corpus; \
			rm -rf indic_languages_corpus; \
		fi; \
		if ! [ -f ../hi/dataset/hi.corpus ]; then \
			if ! [ -f prunedCorpus.tar.gz ]; then \
				wget -c http://www.cfilt.iitb.ac.in/~moses/iitb_en_hi_parallel/iitb_corpus_download/prunedCorpus.tar.gz; \
			fi; \
			tar -xvf prunedCorpus.tar.gz; \
			rm -f pruned_train.en; \
			mv pruned_train.hi ../hi/dataset/hi.corpus; \
		fi; \
		if ! [ -f ../sa/dataset/sa.corpus ]; then \
			if ! [ -d sanskrit_text_gitasupersite ]; then \
				git clone https://github.com/cltk/sanskrit_text_gitasupersite.git; \
			fi; \
			for filename in sanskrit_text_gitasupersite/bhagavadgita/*.txt; do \
				cat $$filename >> ../sa/dataset/sa.corpus; \
			done; \
			for filename in sanskrit_text_gitasupersite/yogasutra/chapter*/*.txt; do \
				cat $$filename >> ../../sa/dataset/sa.corpus; \
			done; \
		fi; \
		if ! [ -f ../mr/dataset/mr.corpus ]; then \
			if ! [ -f marathi-wikipedia-articles.zip ]; then \
				wget -c https://www.kaggle.com/disisbig/marathi-wikipedia-articles/download; \
			fi; \
			unzip marathi-wikipedia-articles.zip; \
			for filename in train/train/*.txt; do \
				cat $$filename >> ../mr/dataset/mr.corpus; \
			done; \
			for filename in valid/valid/*.txt; do \
				cat $$filename >> ../mr/dataset/mr.corpus; \
			done; \
			rm -rf train valid; \
		fi; \
