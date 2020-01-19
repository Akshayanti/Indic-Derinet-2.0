#!/usr/bin/env python3

import argparse
import os
import conllu
import regex as re
import tqdm
import pickle
from inltk.inltk import setup, remove_foreign_languages
from sys import stderr


def invalid_token(given_token):
	"""
	Checks if a token is invalid, and returns boolean value accordingly
	Invalid Token:
		1. UPOS tag in list to detect function words
		2. Multi-Word Entity, detected by token_id being a tuple
		3. Numeral in the token's form or token's lemma
		4. Invalid Token in token's form or token's lemma
	:param given_token: Token to determine if it's valid or not
	:return: Bool True, Bool False
	"""
	if given_token["upostag"] in ["PROPN", "PUNCT", "SYM", "NUM", "X", "INTJ", "ADP", "AUX", "SCONJ", "CCONJ", "DET", "PART", "PRON"]:
		return True
	if type(given_token["id"]) is tuple:
		return True
	if bool(re.search(r'\d', given_token["lemma"])) or bool(re.search(r'\d', given_token["form"])):
		return True
	if bool(re.search(r'\W', given_token["lemma"])) or bool(re.search(r'\W', given_token["form"])):
		return True
	return False


def get_lemma_lexemes(sentences, dictx):
	"""
	Get a dictionary, such that the key is the lemma alongwith its lexical feature(s), and the other Inflectional Features as the value for the key
	:param sentences: Given Sentence
	:param dictx: Input dictionary to update
	:return: Updated Dictionary dictx
	"""
	for tokens in sentences:
		morph_category = (tokens["lemma"].lower(), tokens["upostag"],)
		
		if invalid_token(tokens):
			continue
		
		new_tuple = ()
		if tokens["feats"] is not None:
			for feat_field in tokens["feats"]:
				
				# For NOUN, Gender and Animacy are the lexical features
				if tokens["upostag"] == "NOUN":
					if feat_field in ["Gender", "Animacy"]:
						morph_category += (feat_field + "=" + tokens["feats"][feat_field],)
					else:
						if "," in tokens["feats"][feat_field]:
							outval = "&".join(tokens["feats"][feat_field].split(","))
							new_tuple += (feat_field + "=" + outval,)
							continue
						new_tuple += (feat_field + "=" + tokens["feats"][feat_field],)
				
				# For VERB, Aspect is the lexical feature
				elif tokens["upostag"] == "VERB":
					if feat_field == "Aspect":
						morph_category += (feat_field + "=" + tokens["feats"][feat_field],)
					else:
						if "," in tokens["feats"][feat_field]:
							outval = "&".join(tokens["feats"][feat_field].split(","))
							new_tuple += (feat_field + "=" + outval,)
							continue
						new_tuple += (feat_field + "=" + tokens["feats"][feat_field],)
				
				# For all other UPOS categories
				else:
					if "," in tokens["feats"][feat_field]:
						outval = "&".join(tokens["feats"][feat_field].split(","))
						new_tuple += (feat_field + "=" + outval,)
						continue
					new_tuple += (feat_field + "=" + tokens["feats"][feat_field],)
		
		# Create a placeholder if the key does not exist already
		if morph_category not in dictx:
			dictx[morph_category] = set()
		
		# Add the newly found value to the set
		dictx[morph_category].add(new_tuple)
	return dictx


def process_conllu_fused(sentences, dictx):
	"""
	TODO: Add Documentation
	Get a dictionary, such that the key is a compound_word, with details of constituent_tokens as the values
	:param sentences: Given Sentence
	:param dictx: Input dictionary to update
	:return: Updated Dictionary dictx
	"""
	from_token = -1
	to_token = -1
	compound_form = False
	combination = []
	
	for tokens in sentences:
		
		# compound_word Detected. Set placeholders
		# Use form, since lemma is not available for fused tokens
		if type(tokens["id"]) is tuple:
			compound_form = True
			from_token, _, to_token = tokens['id']
			combination = [tokens["form"].lower()]
		
		# Constituent Token of compound_word
		elif from_token <= tokens['id'] <= to_token and compound_form:
		
			# Invalid token type, discard this compound_word
			if invalid_token(tokens):
				compound_form = False
				continue
			
			# Add details of the constituents of the compound_word
			new_tuple = (tokens['lemma'].lower(), tokens["upostag"],)
			if tokens["feats"] is not None:
				for feat_field in tokens["feats"]:
					if "," in tokens["feats"][feat_field]:
						outval = "&".join(tokens["feats"][feat_field].split(","))
						new_tuple += (feat_field + "=" + outval,)
					else:
						new_tuple += (feat_field + "=" + tokens["feats"][feat_field],)
			combination.append(new_tuple)
		
			# Last constituent token in compound_word. Update dict, and reset placeholders
			if tokens['id'] == to_token and compound_form:
				from_token = -1
				to_token = -1
				compound_form = False
				compound_word = combination[0]
				if compound_word not in dictx:
					dictx[compound_word] = []
				dictx[compound_word] += [x for x in combination[1:]]
	
	return dictx
	
	
def process_conllu(givenfile, lemma_dict, fused_dict):
	"""
	Wrapper function to update the dicts for lemma-based-lexemes and compound-lexemes, as found in CONLL-U data.
	:param givenfile: Name of CONLL-U File, as string
	:param lemma_dict: The dict containing lexemes found found in conllu file.
	(lemma, mophological data) as key value
	:param fused_dict: The dict containing compound lexemes found in conllu file.
	(form) as key value
	:return: lemma_dict, fused_dict
	"""
	with open(givenfile, "r", encoding="utf-8") as datafile:
		for sentences in conllu.parse_incr(datafile):
			lemma_dict = get_lemma_lexemes(sentences, lemma_dict)
			fused_dict = process_conllu_fused(sentences, fused_dict)
	return lemma_dict, fused_dict


def is_subset(given_cand, given_items):
	"""
	TODO: Add Documentation
	:param given_cand:
	:param given_items:
	:return:
	"""
	for item in given_items:
		if len(item) >= len(given_cand) and item != given_cand:
			possible_flag = True
			cand_dict = dict()
			for cand_vals in given_cand:
				field, value = cand_vals.split("=")
				cand_dict[field] = value
				if "&" in value:
					value = set(value.split("&"))
					cand_dict[field] = value
			item_dict = dict()
			for item_vals in item:
				field, value = item_vals.split("=")
				if "&" in value:
					value = set(value.split("&"))
				item_dict[field] = value
				
			# 4 cases when the function should return False
				# 1. Both the values are string, and are not equal
				# 2. parent_candidate is not a string, and not a superset of given_value
				# 3. parent_candidate is a string, but given_value is not
				# 4. Both the values are sets, but parent_candidate is not a superset of given_value
			if all([x in item_dict.keys() for x in cand_dict.keys()]):
				for key in cand_dict:
					if type(cand_dict[key]) == type(item_dict[key]) == str and cand_dict[key] != item_dict[key]:
						possible_flag = False
						break
					elif type(cand_dict[key]) == str != type(item_dict[key]) and cand_dict[key] not in item_dict[key]:
						possible_flag = False
						break
					elif type(item_dict[key]) == str != type(cand_dict[key]):
						possible_flag = False
						break
					elif type(item_dict[key]) == type(cand_dict[key]) == set and not cand_dict[key].issubset(item_dict[key]):
						possible_flag = False
						break
				if possible_flag:
					return True
	return False
	
	
def remove_subset_values(given_dict):
	"""
	TODO: Add documentation for the new condition introduced
	For values in a given key, select the longest subsequence values.
	:param given_dict: A dict with all key, values
	:return new_dict: A dict with only the values such that no two are subsets of each other, for any given key
	"""
	new_dict = dict()
	for given_key in given_dict:
		if given_dict[given_key] == {()} and given_key[1] in ["VERB", "NOUN"] and len([x for x in given_dict.keys() if x[:2] == given_key[:2] and x != given_key]) == 0:
			continue
		for given_value in given_dict[given_key]:
			superset_present = is_subset(given_value, given_dict[given_key])
			if not superset_present:
				if given_key not in new_dict:
					new_dict[given_key] = set()
				new_dict[given_key].add(given_value)
	return new_dict
	
	
def split_ambiguous_entries(given_lemmas_dict):
	"""
	Checks for items in param1, and classifies into 2 dicts.
	Dict1: Requires Manual Evaluation.
		Criteria:
			Key length < 3
			Key length >= 3 and "&" in key value
	Dict2: Does Not Require Manual Evaluation
		Criteria:
			Not in Dict1
	:param given_lemmas_dict: A dict that contains the preliminary list of lexemes.
	:return: Dict1, Dict2
	"""
	requires_manual_check = dict()
	automatic_check = dict()
	for key in given_lemmas_dict.keys():
		if key[1] in ["VERB", "NOUN"]:
			if len(key) < 3:
				requires_manual_check[key] = given_lemmas_dict[key]
				continue
			elif any(["&" in x for x in key[2:]]):
				requires_manual_check[key] = given_lemmas_dict[key]
				continue
		automatic_check[key] = given_lemmas_dict[key]
	return automatic_check, requires_manual_check
	
	
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	group0 = parser.add_mutually_exclusive_group(required=True)
	group0.add_argument("-i", "--input", nargs="+", help="Input files to read data from, in CONLL-U format. Multiple values possible.")
	group0.add_argument("-id", "--input_directory", type=str, help="Parent directory to read CONLL-U files from. Reads .conllu files recursively.")
	parser.add_argument("--lang_code", type=str, help="ISO Language Code for which CONLL-U files would be opened", required=True)
	parser.add_argument("--error_check_file", type=str, help="Output file for ambiguous lexemes in TSV format")
	args = parser.parse_args()
	
	input_files = []
	if args.input:
		for i in args.input:
			input_files.append(i)
	elif args.input_directory:
		for root, dirs, files in os.walk(args.input_directory):
			for filename in files:
				if filename.endswith(".conllu") and args.lang_code in filename.split(".conllu")[0].split("_"):
					input_files.append(os.path.join(root, filename))
	
	global lang_code
	lang_code = args.lang_code
	try:
		setup(lang_code)
	except PermissionError:
		print("Downloading Models Failed. Please make sure you have enough privileges to create a directory.\n"
		      "For debugging, run the Language Code Setup using python interpreter.\n"
		      "Useful Links- \n"
		      "1. https://inltk.readthedocs.io/en/latest/api_docs.html#setup-the-language\n"
		      "2. https://github.com/caffe2/models/issues/16\n", file=stderr)
		exit(1)
	
	all_lexemes = dict()
	compound_lexemes = dict()
	for infile in tqdm.tqdm(input_files):
		all_lexemes, compound_lexemes = process_conllu(infile, all_lexemes, compound_lexemes)
	all_lexemes = remove_subset_values(given_dict=all_lexemes)
	no_check_required, check_required = split_ambiguous_entries(all_lexemes)
	
	# print(len(no_check_required), file=stderr)
	
	if args.error_check_file:
		with open(args.error_check_file, "w", encoding="utf-8") as outfile:
			for key in sorted(check_required.keys()):
				outfile.write("\t".join([x for x in key]) + "\n")

	with open("dataset/lexemes.pickle", "wb") as outfile:
		pickle.dump(no_check_required, outfile)


# TODO:
# 	1. Add check for combos that don't occur more than a small threshold
#   2. Remove subsets for the compound lemmas dict
