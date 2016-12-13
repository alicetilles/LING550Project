import nltk
from nltk.corpus import wordnet as wn
import math
import re
import fileinput
import collections
from requests import get
from itertools import product
import os.path

########################################################################################################################################
## TO DOWNLOAD BEFORE USE:
## Command line:
## 		pip install requests
## 		pip3 install wordfreq
## Download both the UK and the US Subtlex databases before use. Available at:
## 		US: http://www.ugent.be/pp/experimentele-psychologie/en/research/documents/subtlexus/subtlexus2.zip
## 		UK: http://crr.ugent.be/archives/1423
## Put in the same working directory and rename: "SUBTLEXUK.txt" and "SUBTLEXUS.txt"
########################################################################################################################################
## Proper use of the program:
##		python wordConversionFinal.py
########################################################################################################################################
## Two different functions that calculate the frequencies of a bunch of synonyms in subtlex data, and return a dictionary where the keys are synonyms and the values are frequencies.
## Note: SUBTLEX UK is Subtitle-based word frequencies for British English

## Make sure the files are there before starting:
if os.path.isfile('./SUBTLEXUK.txt') == False:
	print("Please make sure the subtlex UK database is in your current working directory, and named correctly (SUBTLEXUK.txt).")
	exit(0)
if os.path.isfile('./SUBTLEXUS.txt') == False:
	print("Please make sure the subtlex US database is in your current working directory, and named correctly (SUBTLEXUS.txt).")
	exit(0)



def AmericanToBritish(synonym_list):
	
	## Initialize dictionary
	outputDict = dict()

	with open('SUBTLEXUK.txt', 'r') as UKSubtlex:

		## For each synonym, check the frequency in the UKSubtlex
		for item in synonym_list:

			## Reset the file pointer/curser
			UKSubtlex.seek(0)

			## For each line,
			for line in UKSubtlex:
				line = line.lower()

				## If the item is in the line,
				if item in line:			
					## The first word is the word itself. The second 'word' is the frequency integer.
					counter = 0
					for word in line.split()[:2]:
						if counter == 0:
							subtlexWord = word
							counter = 1
						if counter == 1:
							subtlexFrequency = word
					## Compare the word from subtlex to the input word 
					## If they are equal, then we found the entry.
					if item==subtlexWord:
						outputDict[item] = int(subtlexFrequency)
	return outputDict


def BritishToAmerican(synonym_list):
	with open('SUBTLEXUS.txt', 'r') as USSubtlex:
		
		outputDict = dict()
		## For each synonym, check the frequency in the UKSubtlex
		for item in synonym_list:	
			## Initialize it to 0
			outputDict[item] = 0

			## Reset the file pointer/curser
			USSubtlex.seek(0)
			## For each line,
			for line in USSubtlex:
				line = line.lower()
				## If the item is in the line,
				if item in line:
					## The first word is the word itself. The second 'word' is the frequency integer.
					counter = 0
					for word in line.split()[:2]:
						if counter == 0:
							subtlexWord = word
							counter = 1
						if counter == 1:
							subtlexFrequency = word
				## Compare the word from subtlex to the input word 
				## If they are equal, then we found the entry.
					if item==subtlexWord:
						outputDict[item] = int(subtlexFrequency)
	return outputDict



## Takes as input the output of either of the above function output dictionaries.
## Finds how many occurances total, and the probability of each word.
## It returns a dictionary where each key is a synonym, and each value is that synonym's probability share (its frequency divided by the sum of all frequencies, of the dialect)
def MostLikelyWordProbabilities(wordFrequencyDict):
	itemRatios = dict()
	## Count up the total number of occurrences of any of the synonyms
	totalCount = 0
	for k,v in wordFrequencyDict.items():
		totalCount = totalCount + v
	## For each individual item, find the ratio. Store it in a new dictionary.
	for word in wordFrequencyDict:
		itemRatios[word] = wordFrequencyDict[word]/totalCount
	## Return the probability dictionary
	return itemRatios





## Finds the most common - simply sorting the dictionary output of MostLikelyWord.
## Returns the top n in a list of tuples. If there aren't enough, just put in the first word.
### INPUT: 	1. dictionary of probabilities (output of MostLikelyWordProbabilities)
##			2. n = the list of how many "top"s
##			3. The pretranslation dialect place - string
##			4. The posttranslation dilect place - string
##			5. Print true or false -- if they want to print the results or not
def TheMostCommon(probability_dictionaries, n, preTranslationDialect, postTranslationDialect, printResults):
	## Sort the input descending
	sortedProbabilities = sorted(probability_dictionaries.items(), key=lambda x:x[1], reverse=True)
	## Initialize output list
	output = []
	## For each item, put in the top n
	for item in sortedProbabilities[:n]:
		output.append(item)


	## If the user wanted to print the results, do that:
	if printResults == True:
		print("The most common", postTranslationDialect, "words are:")

		## Prints the top n most likely
		for pair in output:
			for word in pair[:1]:
				print("\t",word,":",pair[1]*100,"%")
		print(" ")
	return output


## Prompts the user for the word they want a synonym for and which sense of the word, and it generates a synonym list using wordNet.
def userPromptWordSynonymGenerator():
	# Step one: Prompt the word
	print("Please type one British or American word you'd like a synonym for: \n>> ", end="")
	for line in fileinput.input():
		## This ensures that if they wrote two or more words, only the first will be counted
		inputWords = str.split(line)
		userWord = inputWords[0]
		break
	# Step two: make sure the word is in WordNet
	# If it returns an empty list, then it isn't in WordNet.
	if(wn.synsets(userWord) == []):
		print("Sorry, that word is not available. Try another.")
		exit(0)
	# Step three: Find the wordsenses that are in wordnet and ask user to choose which they'd like
	wordSenses = wn.synsets(userWord)
	print("\nPlease choose the definition of " + userWord + " you'd like a synonym for:")
	i = 1
	senses = [];
	for item in wordSenses:
		print("\t",i,":",item.definition())
		senses.append(item)
		i+=1
	# User picks the number of the sense they're looking for
	try:
		chosenNumber = int(input("Enter a number: \n>> ")) - 1

	except:
		print("Choose a proper number please.")
		exit(0)
	if chosenNumber+1 > len(wordSenses) or chosenNumber<0:
		print("Please choose a number from the definitions above.")
		exit(0)


	## To do: write an error in case they chose an invalid number
	chosenSense = senses[chosenNumber]
	## Gather the synonyms and store into a dictionary
	lemmaSynonyms = dict()
	synonymCount=0
	while synonymCount < len(senses[chosenNumber].lemma_names()):
	        lemmaSynonyms[synonymCount]=senses[chosenNumber].lemma_names()[synonymCount]
	        synonymCount +=1
	## Save the synonyms to a list
	synonym_list = []
	for lemma in chosenSense.lemmas():
		synonym_list.append(lemma.name())

	### These are lots of possibilities from wordnet of synonyms. Based on tests for what
	### we are looking for, we found lemmas, hypernyms, and 'also sees' to have the best substitutability.
	## NOTE: Ones with +++ are good for getting synonyms, ones with ??? are sometimes good.

	"""
	print("+++ lemmas: ", chosenSense.lemmas())
	print("+++ hypernyms: ", chosenSense.hypernyms())
	print("instance hypernyms:", chosenSense.instance_hypernyms())
	print("hyponyms: ", chosenSense.hyponyms())
	print(" +++ similar tos: ", chosenSense.similar_tos())
	print(" +++ also see: ", chosenSense.also_sees())
	print("causes: ", chosenSense.causes())
	print("member_meronyms", chosenSense.member_meronyms())
	print("member_holonyms(", chosenSense.member_holonyms())
	print("mpart_meronyms(", chosenSense.part_meronyms())
	print("++ hypernyms: ", chosenSense.hypernyms())
	print("??? maybe hyponyms", chosenSense.hyponyms())
	print("instance_hypernyms", chosenSense.instance_hypernyms())
	print("instance_hyponyms", chosenSense.instance_hyponyms())
	print("member_meronyms", chosenSense.member_meronyms())
	print("member_holonyms", chosenSense.member_holonyms())
	print("mpart_meronyms", chosenSense.part_meronyms())
	print("part_holonyms", chosenSense.part_holonyms())
	print("substance_meronyms", chosenSense.substance_meronyms())
	print("substance_holonyms", chosenSense.substance_holonyms())
	print(" ?? maybe ?? entailments", chosenSense.entailments())
	print("attributes", chosenSense.attributes())
	"""

	## Adding hypernyms to the synonym list
	for item in chosenSense.hypernyms():
		synonym_list.append(item.name().split(".")[0])

	## Adding also sees to the synonym list
	for item in chosenSense.also_sees():
		synonym_list.append(item.name().split(".")[0])

	## Adding similar tos to the synonym list
	for item in chosenSense.similar_tos():
		synonym_list.append(item.name().split(".")[0])

	## If it is a proper noun, or very specific, it has no synonyms.
	if len(synonym_list) == 0:
		print("We couldn't find any synonyms for that word. Is it a proper noun?")
		exit(0)

	## Return the completed synonym list, and the inputted word
	outputList = []
	outputList.append(synonym_list)
	outputList.append(userWord)
	return outputList

## This function takes as input the pre-translation dictionary of probabilities and
## the post-translation one. It iterates through each word pair (e.g., happy british and happy American)
## and makes a ratio of original prob compared to translated prob, to find the most disproportionate.

def DisproportionateWords(preTranslationProbabilities, postTranslationProbabilities, n, postTranslationDialect, preTranslationDialect, printResults):
	## For each item, find its match in the pre-translation data.
	## Gather the ratios of both.
	probabilityDict = dict()
	discountedItems = []
	for item in postTranslationProbabilities:
		if item not in preTranslationProbabilities:
			probabilityDict[item] = 999999
			continue
		preRatio = preTranslationProbabilities[item]

		postRatio = postTranslationProbabilities[item]

		if postRatio != 0:
			probabilityDict[item] = preRatio/postRatio

		else:
			print("Item:",item)
			probabilityDict[item] = 999999

		## If the word has a very LOW number: Then the postratio is much higher than the preratio. So this word is
		##		more like the translated dialect.
		## If the word has a very HIGH number: Then the postratio is smaller than the preratio.
		##		So this word is less like the translated dialect.

	sortedProbabilities = sorted(probabilityDict.items(), key=lambda x:x[1], reverse=True)


	## We convert the numbers to something more "English-y" to print to the user, rather than a list of long numbers.
	## If they want the results printed:
	if printResults == True:
		print("Your results for disproportionate words:")
		for word,probability in sortedProbabilities[:n]:

			if probability > 100:
				description = "much, much, much more"

			elif probability > 75:
				description = "much, much more"

			elif probability > 50:
				description  = "much more"

			elif probability > 25:
				description  = "a lot more"
			
			elif probability > 5:
				description  = "a decent amount more"
			
			elif probability > 2:
				description  = "more"
			
			elif probability > 1:
				description  = "a little bit more"

			else:
				description  = "less"


			if probability > 999998:
				print("\t\'",word.title(),"\' is ONLY used by ", postTranslationDialect," people!",sep='')

			else:

				if postTranslationDialect == "British":
					print("\t\'",word.title(),"\' is ",description," likely for a ", postTranslationDialect," person to say than an ",preTranslationDialect," person.",sep='')

				if postTranslationDialect == "American":
					print("\t\'",word.title(),"\' is ",description," likely for an ", postTranslationDialect," person to say than a ",preTranslationDialect," person.",sep='')




	return probabilityDict




## http://swoogle.umbc.edu/SimService/api.html
## The following function determines similarity between two words. The fuction is based on: 
## Lushan Han, Abhay L. Kashyap, Tim Finin, James Mayfield and Johnathan Weese, UMBC_EBIQUITY-CORE: Semantic Textual Similarity Systems, Proc. 2nd Joint Conf. on Lexical and Computational Semantics,
##			Association for Computational Linguistics, June 2013.
### sss = Semantic Similarity Service
def sss(s1, s2, type='relation', corpus='webbase'):
	try:
		response = get("http://swoogle.umbc.edu/SimService/GetSimilarity", params={'operation':'api','phrase1':s1,'phrase2':s2,'type':type,'corpus':corpus})
		return float(response.text.strip())
	
	except:
		print("Error in getting similarity.")
		exit(0)

## The following function determines similarity between synonyms, by calling function sss for each pair of words
def calcSynonymSimilarity(synonym_list,initialWord):
	similarityRatios = dict()
	similarityRatios[initialWord] = dict()

	for word in synonym_list:
		similarity_of_the_two_words=sss(word,initialWord)
		similarityRatios[initialWord][word]=similarity_of_the_two_words
#			if word1==word2:
                                ## identical words have probaility of 1: we don't want to identisy these as having the same meaning
#				similarityRatios[word1][word2]=0
	return similarityRatios
## The following function prints similarity between synonyms of the topNMostCommonBeforeTranslations and topNMostCommonTranslations
def calcMostCommonSynonymSimilarity(synonym_list,topNMostCommonBeforeTranslations,topNMostCommonTranslations,goalTranslationDialect,preTranslationDialect,initialWord,disproportionateDict,printOption,topN):



	## Determine synonym similarities
	sss_url = "http://swoogle.umbc.edu/SimService/GetSimilarity"
	if printOption == True:
		similarityDict=calcSynonymSimilarity(synonym_list,initialWord)

	else:
		similarityDict=calcSynonymSimilarity(synonym_list,initialWord)

	## This prints out the results, if they want.
	if printOption == True:
		for word1,wordList in similarityDict.items():
			if word1 == initialWord:
				continue
			for innerWord,innerMeasure in wordList.items():
				if innerWord == initialWord:
					print("\t",word1,"is",innerMeasure,"similar to",initialWord,".")


	## This suggests different words if any of the words are very different.
	

	sortedProbabilities = sorted(disproportionateDict.items(), key=lambda x:x[1], reverse=True)
	print("\nNotes on similarity:")
	goodWords = []
	allGood = 0
	for word,probability in sortedProbabilities[:topN]:
		probability = similarityDict[initialWord][word]
		## TO ROSIE -- USE THIS PRINT STATEMENT TO SEE THE SIMILARITY PROBABILITY
		##print("Word:", word, "is ", probability,"similar to", initialWord)

		## Don't compare the word to itself
		if word == initialWord:
			continue

		## If it is really similar, store it to possible make a recommendation
		if round(probability, 3) > .9:
			goodWords.append(word)

		## If it is this low, it probably isn't a good match
		elif round(probability, 3) < .1:
			allGood = 1
			print("\t\'",word.title(), "\' might not at all be like \'",initialWord,"\'. We recommend you don't use it.",sep='')

			## Recommend them a better word
			if len(goodWords) != 0:
				print(" \tMaybe \'", goodWords[0],"\' would be more suitable?",sep='')
		

		elif round(probability, 3) < .2:
			allGood = 1
			print("\t\'",word.title(), "\' might be not very much like \'",initialWord,"\'. We recommend you use it use with discretion.",sep='')

		elif round(probability, 3) < .5:
			print("\t\'",word.title(), "\' might be slightly different from \'",initialWord,"\'. We recommend you use it use with discretion.",sep='')


	if allGood == 0:
		print("\tAll the synonyms are similar enough to",initialWord,"that we feel comfortable recommending them!")

	if allGood == 1:
		print("\nIf you are dissatisfied with the results, we recommend trying again but with a bigger N (words to include). If there were only a few synonyms,", initialWord, "has a specific definition, so you can probably use it.\n")








##########################################################################################
########################################################################################################################################
########################################################################################################################################

## Gets the synset synonym list.
outputList = userPromptWordSynonymGenerator()
synonym_list = outputList[0]
initialWord = outputList[1]
## Find out if the user's word is British or American.
startingWordPlace = int(input("Would you like a (1) British or (2) American translation of that? Enter 1 or 2.\n>> "))

if startingWordPlace > 2:
	print("Please type 1 or 2.")
	startingWordPlace = int(input("\n>> "))
	if startingWordPlace > 2:
		print("Not available.")
		exit(0)


## Choose the function to translate based on what they want
## If they want a British translation, do the translation.
if startingWordPlace == 1:
	goalTranslationDialect = "British"
	preTranslationDialect = "American"
	resultFrequencies = AmericanToBritish(synonym_list)

	## * problem:
	beforeTranslationFrequencies = BritishToAmerican(synonym_list)
## If they want an American translation....
if startingWordPlace == 2:
	goalTranslationDialect = "American"
	preTranslationDialect = "British"
	resultFrequencies = BritishToAmerican(synonym_list)
	beforeTranslationFrequencies = AmericanToBritish(synonym_list)

## Variable descriptions:
## 		• resultFrequences is the frequences of the translated word
##		• beforeTranslationFrequences are the frequences of the word BEFORE it gets translated



## Find the likelihood ratios, aka the percentage of each word's share out of all synonyms.
afterTranslationRatios = MostLikelyWordProbabilities(resultFrequencies)
beforeTranslationRatios = MostLikelyWordProbabilities(beforeTranslationFrequencies)

## We will take two probabilities:  (1) Which is the top n most common for the translation, and (2) which synonyms have the greatest disparity.
#1: Top N most common. We will assume that the user wants the top 3, that they want the translated results printed, and don't want the untranslated results printed, but don't want all the pre-translation results printed. These are all variables that can be edited, however.
topN = 4
## topN = int(input("How many results would you like to see? Type any integer.\n>> "))
topNMostCommonBeforeTranslations = TheMostCommon(beforeTranslationRatios,topN,goalTranslationDialect,preTranslationDialect, False)
topNMostCommonAfterTranslations = TheMostCommon(afterTranslationRatios,topN, preTranslationDialect,goalTranslationDialect, True)


#2: Which words tend to be more like the goal translation?
## They also have the option to choose if they want the results printed or not here, and the top n. We assume that they want the top 3 and they do want them printed.
## topN = int(input("How many results would you like to see for disproportionate words? Type any integer.\n>> "))
disproportionateDict = DisproportionateWords(beforeTranslationRatios,afterTranslationRatios,topN,goalTranslationDialect,preTranslationDialect, True)

## PART TWO: SIMILARITY.
## MOTIVATION: To use resources outside wordnet to guarentee we are giving the user appropriate synonyms.
########################################################################################################################################

calcMostCommonSynonymSimilarity(synonym_list,topNMostCommonBeforeTranslations,topNMostCommonAfterTranslations,goalTranslationDialect,preTranslationDialect,initialWord, disproportionateDict,False,topN)
