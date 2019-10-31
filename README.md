# Medical Sentence Tokenizer
This is my work on tokenizing clinical text into sentences for [BERT](https://arxiv.org/abs/1810.04805) pre-training. We needed to split a large corpus of clinical notes from Columbia University Irving Medical Center into sentences with minimal goal of not splitting up sentences, and allowing for multiple actual sentences to be packed into one sentence while limiting the number of overly long sentences. The reasoning behind this is that for next sentence prediction it's important that the two segments are split between sentences making the task more difficult.


## Determining a baseline tokenizer
The first step was to determine a baseline tokenizer from [nltk](https://www.nltk.org/_modules/nltk/tokenize.html#sent_tokenize), [spaCy](https://spacy.io/), and [scispacy](https://allenai.github.io/scispacy/). This was more of an informal comparison as I randomly sampled and compared the sentences identified by the three sentence tokenizers. I found that scispacy and spaCy performed similarly and were thrown off by \n characters in the text. This can be good and bad depending on the note and how it was processed before. Often clinicians will use new lines as a kind of sentence delimiter, however line wrapping can introduce erroneous new line characters that don't actually signify a new sentence. NLTK was not thrown off be new lines and often ignored them so removing or keeping wrapped lines made little difference.
One of the major differences between the spaCy-like tokenizers and nltk is that nltk would tokenize longer chunks by combining true sentences together while not splitting true sentences up very often. The spaCy-like tokenizers would often tokenizer sentences into smaller chunks, but would also split true sentences up while doing this. For this reason I chose to use the nltk tokenizer as it was more important to have tokenized chunks that did not span sentences at the expense of some chunks being longer. The next section discusses handling the individual, overly long chunks, and not the entire piece of text as nltk was run before this.


## Catching overly long sentences

Having overly long sentences still has the potential to throw off pre-training a BERT model, as in the [corpus generation step](https://github.com/ncbi-nlp/NCBI_BERT/blob/master/tokenizer/run_tokenization.py) it was decided that if a sentence was longer than the max allowed length the next segment would always be random. If this happens too often the balance between random and following segment could be thrown off, furthermore many tokens would be discarded during the truncation step for the two segments. After looking through what kind of chunks were overly long (greater than 400 word piece tokens) the most common examples were lists of medical concepts such as medications, vitals, past medical history, etc. with little to no proper punctuation, and long paragraphs that contain subject headings but no new lines. 

### Medical lists
Medical lists were fairly easy to handle, and I think my code handled a majority of the cases. The form of medical lists was often a large chunk of text with new lines after every element in a list, and two new lines between lists or headers. Elements in the list often started with a space or dot signifying that it was a new element and under the current list header. I made the decision that headers could be their own sentences, as combining them with another sentence seem arbitrary, and that each element in a list was its own sentence as well. 

Example:

CURRENT MEDICATIONS:

  * Medication 1
  * Medication 2
  * Medication 3 for x weeks at y dosage
and then z weeks at 2 dosage.

In the example below it's obvious that the third element in the list is on two lines, and should be condensed into one sentence, while the rest of the elements are easily split by new lines into their own sentences.


### Long paragraphs containing subject headings
The next case that occurred less often was a large chunk of text with no new lines and no reliable sentence boundary punctuation. However, these chunks of text did often contain headers with the form of capital letters, possibly with spaces, followed by a colon. I decided that each header was its own sentence, and then the following information was also its own sentence and only ended at the next reliable header.

Example:

PAST MEDICAL HISTORY: The patient has a history of x but has been well controled in the past with proper nutrition and medication FAMILY HISTORY: No significant family history social history: p.t smokes two packs a week, and drinks with dinner as well as socially denies elicit drug use lives with wife in the Bronx Chief Complaint: p.t. presented with radiating chest pain.

In the above example there is no punctuation to help discern sentences but headers can be used to split the text up. However headers are not always reliable and may contain all capital letters, or just a few. 
