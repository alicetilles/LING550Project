import nltk
from nltk.corpus import wordnet as wn
import math
import re
import fileinput
import LinThesaurusCorpusReader as Lin
import BNCreadertest as BNC


"""
Proper use of the program:
python wordConversion.py
Program prompts a word to convert, user enters it
Program prompts which place the word is from, America or Britain, user enters that
Program spits out a 'synonym'
"""




##BNC.readEntireBritCorpus()

#exit(0)

# Step one: Prompt the word

userWord = " "

print("Please type one word you'd like a synonym for.")

for line in fileinput.input():

	## This ensures that if they wrote two words, only the first will be counted
	inputWords = str.split(line)
	userWord = inputWords[0]
	break



# Step two: make sure the word is in WordNet
# If it returns an empty list, then it isn't in WordNet.

if(wn.synsets(userWord) == []):
	print("Sorry, that word is not available. Try another.")
	exit(0)


# Step three: Find the wordsenses that is in wordnet and ask user to choose which they'd like
wordSenses = wn.synsets(userWord)

print("\nPlease choose the definition of " + userWord + " you'd like a synonym for:\n")



i = 1
senses = [];
for item in wordSenses:

	print("\t",i,":",item.definition(),"\n")

	senses.append(item)

	i+=1



# User picks the number of the sense they're looking for

chosenNumber = int(input("Enter a number: ")) - 1

## To do: write an error in case they chose an invalid number


print("You chose: ",senses[chosenNumber].definition())

chosenSense = senses[chosenNumber]

print("\nCHOSEN SENSE:",chosenSense)





## Gather the synonyms and store into a dictionary

lemmaSynonyms = dict()

synonymCount=0

while synonymCount < len(senses[chosenNumber].lemma_names()):

        lemmaSynonyms[synonymCount]=senses[chosenNumber].lemma_names()[synonymCount]

        synonymCount +=1

print("FIRST SET OF SYNONYMS: ",lemmaSynonyms)

print("\n\n\n")

for lemma in chosenSense.lemmas():
	print (lemma.name())

for hypernym in chosenSense.hypernyms():
		print(hypernym.name())


## Initially use only British Corpus and American Corpus: later, for a more complete script, prompt user for location (American, Scottish, British, Australian) 



## Import appropriate Corpus for searching:

## British National Corpus (BNC) -- ** INITIAL http://inmyownterms.com/get-to-know-and-use-your-english-corpora-bnc-glowbe-coca-coha-and-more/

#### BNC contd. http://www.nltk.org/_modules/nltk/corpus/reader/bnc.html

#### BNC contd. http://www.nltk.org/api/nltk.corpus.reader.html#module-nltk.corpus.reader.bnc

## Open American National Corpus (OANC) -- ** INITIAL (http://www.anc.org/data/oanc/download/)

## Corpus of Contemporary American English (COCA)

## Scottish Corpus of Texts & Speech (SCOTS)

## Australian National Corpus (AusNC)

## International Corpus of English (ICE)



## Search chosen corpus for each synonym of each word in firstGroupSynonyms and the frequency of occurrence of each synonyms in the chosen corpus

## A) select the most frequently used synonym and return this "translation" to the user??? AND/OR

## B) compile a set of words that are in BOTH (or 2nd as 1st is in firstGroupSynonyms??) categories then use Subtlex(-UK) to assign word frequencies for each word. Then assign a frequency rank.











"""

for item in chosenSense:

	print(item)











"""













