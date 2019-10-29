import numpy as np
import re
from nltk.tokenize import sent_tokenize, word_tokenize






def custom_sentence_tokenizer(text, tokenizer, testing = False, verbose = False):
	"""
	Description: Splits a piece of text, should be an entire note, into sentences. Relies on 
		the NLTK sentence tokenizer, and then runs checks on each split sentence. If a sentence
		is found to be over 400 tokens, it's assumed to be a list of clinical terms, in which case
		split_medical_list() is run on this text. If this doesn't work, then it's assumed to be a
		paragraph of text with headers and no significant new lines. This is then split using a
		regular expression.
		Note that this does not accurately split text up into sentences, and tends to create 
		longer 'sentences', but these 'sentences' usually stop at what can be considered proper
		sentence boundaries. So we aim for longer 'sentences' over shorter spans of text which
		run the risk of splitting up proper sentences.
	Usage:
				my_text = re.sub("â€|™|˜", "", my_text)
				# I think these are single quote characters that got messed up.
				my_text = re.sub("\xa0+", " ", my_text)
				# These take up a lot of space in the text and messup the tokenizer
				my_text = re.sub("\r\n", "\n", my_text)
				# replacing Windows new line with just new line
				text = re.sub('\\\\.br\\\\', "\n", text)
				# I think this are weird html leftovers
				sentences = custom_sentence_tokenizer(text = my_text, tokenizer = bert_tokenizer)

	Input:
		text (str): A string of text from a clinical note. No processing is performed in this
			function so all pre-processing needs to happen before sentence tokenization.
			See usage above for suggestions.
		tokenizer (BERT Tokenizer): Can be any tokenizer, but should be BERT tokenizer. Used to
			determine if there are too many tokens in a sentence.
				from transformers.tokenization_bert import BertTokenizer
				tokenizer = BertTokenizer.from_pretrained('bert-large-uncased', do_lower_case=True)
		testing (boolean): If True then extra information is returned. See below.
		verbose (boolean): Just prints more about what's going on
	Output:
		sentences_final (list(str)): A list of sentences.
		sents_not_split (int): optionally returned if testing is True. This is the number of
			sentences which could not be split.
	TODO
		1) This wil return single sentences if nltk looks at a text and only extracts one sentence
			out that is under the max_sentence_toks. Can happen if the whole input is a list.
	"""
	sentences = sent_tokenize(text)
	sentences_custom_tokenized = []
	max_sentence_toks = 400# max number of tokens in a sentence otherwise we assume it's a list.
	sents_not_split = 0
	for sentence in sentences:
		toks = tokenizer.tokenize(sentence)
		if len(toks) >= max_sentence_toks or len(sentences) == 1:
			if verbose:
				print("Splitting a medical list")
			sub_sentences = split_medical_list(sentence)
			if len(sub_sentences) == 1:
				# This code assumes that if we're here we hit a sentence
				# which isn't a list, but a large paragraph of headers
				# with no new lines that separate them. 
				# the regex below looks for single or multi word headers
				# all capitalized that ends with a colon.
				# and it assumes that the sentence could not be split at all
				if verbose:
					print("could not split the string\n" + sentence)
					print("Assuming this text is is a large paragraph and splitting")
					print("LET'S KICK IT INTO OVERDRIVE")
				# splitting by headers in a string.
				sub_sentences = re.split(r'([A-Z0-9][A-Z0-9. ]*:)', sentence)
			sentences_custom_tokenized.extend(sub_sentences)
			if len(sub_sentences) == 1:
				sents_not_split += 1
			if verbose:
				print("original length: {}".format(len(toks)))
				for split_sent in sub_sentences:
					print("\t{}".format(len(tokenizer.tokenize(split_sent))))
		else:
			sentences_custom_tokenized.append(sentence)
	assert len(sentences_custom_tokenized) >= len(sentences)
	sentences_final = []
	for elem in sentences_custom_tokenized:
		if elem.strip() != "":# removing empty tokens.
			sentences_final.append(elem)
	if testing:
		return(sentences_final, sents_not_split)
	else:
		return(sentences_final)


def split_medical_list(text):
	"""
	Description: Splits a piece of text up using some heuristics for columbia data.
		The text is split based on new lines. Then some lines are combined if they are not
		the beginnings of a new list. A list often starts with " " or "·", but if a line is
		empty of has an alphanumeric character in the first character then it is the start
		of a new list element, and thus its on sentence.
	Input:
		text (str): A string which is the result of using nltk on a larger chunk of text, and
			finding that this particular input could not be parsed down to a good length.
	Output:
		sentences_fix_split_list_item (list(str)): A list of sentences.
	TODO:
		1)
	"""
	sentences_new_line_split = text.split("\n")
	sentences_fix_split_list_item = []
	curr_sentence = ""
	for idx, elem in enumerate(sentences_new_line_split):
		if idx == 0:
			curr_sentence = elem
		elif elem == "" or begins_list_element(my_text = elem):
			# above checks if we've reached end or are about to start a new element in the list.
			if curr_sentence.strip() != "":# don't append empty lines.
				sentences_fix_split_list_item.append(curr_sentence)
			curr_sentence = elem
		else:# guessing that this line should be joined with the previous line
			if curr_sentence == "":
				curr_sentence = elem
			else:
				curr_sentence += " " + elem
	if curr_sentence.strip() != "":
		sentences_fix_split_list_item.append(curr_sentence)


	# check to make sure all original lines made it into the data
	for line in sentences_new_line_split:# This will slow down the tokenizer, but is a good idea
		# to make sure we're not losing any information.
		text_found = False
		if line.strip() != "":
			for fixed_line in sentences_fix_split_list_item:
				if line in fixed_line:
					text_found = True
					break
			assert text_found, "missing original string: {}".format(line)
	return(sentences_fix_split_list_item)



def begins_list_element(my_text):
	"""
	Description: Returns true when an piece of text is the beginning of a new list elemnt
		usually starting with " " or "·". This is CUIMC specific.
	Input:
		my_text (str): Piece of text from splitting on new line.
	Output: Boolean whether or not my_text is the beginning of a list element.
	TODO:
	"""
	if my_text.startswith("·") or my_text.startswith(" "):
		return(True)
	else:
		return(False)