
from nltk.corpus import stopwords
import sys
import math
import re
from collections import defaultdict
from collections import OrderedDict
#from ordereddefaultdict import OrderedDefaultdict
import operator
from numpy import array
import math
import nltk
from nltk import pos_tag, ne_chunk
from nltk.tokenize import sent_tokenize, word_tokenize
import pandas as pd
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk import RegexpParser
from nltk import Tree
import pandas as pd
import datefinder
from datetime import datetime
import os
import spacy
nlp = spacy.load("en_core_web_sm")
#from gensim.models import Word2Vec

def extractCoRef(file):
	dictionary = {}
	text = file.read()
	lines = text.strip().split('\n')
	line_no = 0
	sentence_dict = {}
	for line in lines:
		strings = re.findall(r'<COREF ID="(\w+)">([^<]+)<\/COREF>', line)
		temp = re.sub(r'<[^>]*>', '', line)
		sentence_dict[line_no] = temp
		if (len(strings) != 0):
			for string in strings:
				dictionary[(line_no, string[0])] = string[1]
		line_no = line_no + 1
	return dictionary,sentence_dict
	#print(dictionary)
    
def extractcoRef(file):
    scid_Coref = {}
    text = file.read()
    lines = text.strip().split('\n')
    line_no = 0
    scid_sent = {}
    for line in lines:
        cid_Corefs = re.findall(r'<COREF ID="(\w+)">([^<]+)<\/COREF>', line)
        temp = re.sub(r'<[^>]*>', '', line)
        scid_sent[line_no] = temp
        if(len(cid_Corefs) != 0):
            for cid_Coref in cid_Corefs:
                coref = cid_Coref[1]
                if(scid_sent[line_no].__contains__(coref)):
                    #print("coref:",coref)
                    #print("Before:",scid_sent[line_no])
                    scid_sent[line_no] = scid_sent[line_no].replace(coref,"",1)
                    #print("After:",scid_sent[line_no])
                scid_Coref[(line_no, cid_Coref[0])] = coref
        line_no = line_no + 1
    return scid_Coref,scid_sent

def get_continuous_chunks(text, chunk_func=ne_chunk):
    chunked = ne_chunk(pos_tag(word_tokenize(text)))
    #print("C:",chunked)
    continuous_chunk = []
    current_chunk = []

    for subtree in chunked:
        if type(subtree) == nltk.tree.Tree:            
            #print('here')
            current_chunk.append(" ".join([token for token, pos in subtree.leaves()]))
        elif current_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
                current_chunk = []
        else:
            continue
    #print(continuous_chunk)
    return continuous_chunk

## TODO: ONLY head nouns to be added
    # ex: if (wage reductions) just add "wage reductions","reductions",lemma(reductions)
def findWordNetLemitizer(coRefWord):
    wordnet_lemmatizer = WordNetLemmatizer()
    wordSet = set()
    wordSet.add(coRefWord)
    text = word_tokenize(coRefWord)
    for word in text:
        wordSet.add(word.lower())
        wordSet.add(wordnet_lemmatizer.lemmatize(word).lower())
    #print("l:",wordSet)
    return wordSet
    
def traverse_tree(input_str):
    wordSet = set()
    tree = (ne_chunk(pos_tag(word_tokenize(input_str))))
    #print("tree:", tree)
    for subtree in tree:
        if type(subtree) == nltk.tree.Tree:
            nounWord = ''
            for k in subtree:
                nounWord = nounWord + ' '+k[0]
            nounWord = nounWord.strip()
            wordSet.add(nounWord.lower())
    #print("tws:",wordSet)
    return wordSet

## TODO: same as below, if (wage reductions), just add wage reduction and
    # reductions and synonymns of reduction
def findSynHypo(word):
    wordSet = set()
    for syn in wordnet.synsets(word):
        for l in syn.lemmas(): # hyponyms, lemmas, meronyms,hypernymns, holonyms
            temp1 = l.name().lower()
            temp1 = temp1.replace("_"," ")
            wordSet.add(temp1)
#        for k in syn.hypernyms():
#            temp1 = k.name().split(".")[0].lower()
#            temp1 = temp1.replace("_"," ")
#            wordSet.add(temp1)
    return wordSet

## TODO: Do it only for head nouns
#ex: (wage reductions). find syn(wage reductions) and syn(reductions)
def findSynHypoChunking(words):
    wordSet = set()
    words = word_tokenize(words)
    
    for word in words:
        synSet = findSynHypo(word)
        for s in synSet:
            wordSet.add(s)
    
    return wordSet
        
def findIfDate(word):
    #Format: month-date-year    
    dateWord = ''
    matches = datefinder.find_dates(word)
    for match in matches:
        #print("match:",match)
        dateWord = str(match.month)+"-"+str(match.day)+"-"+str(match.year)
        #print(dateWord)
        #wordSet.add(dateStr)
    
    return dateWord
           
def mergeSets(ws1,ws2,ws3,dateWord):
    superSet = set()
    for word in ws1:
        superSet.add(word)
    for word in ws2:
        superSet.add(word)
    for word in ws3:
        superSet.add(word)
    if(len(dateWord) != 0):
        superSet.add(dateWord)
    return superSet

def extractTreeWord(text):
    split_text = text.split()
    new_text = ''
    for item in split_text:
        if item[0].isnumeric():
            new_text += item[:item.find('/')] + ' '
        elif item[0] == '(':
            pass
        else:
            new_text += item[:item.find('/')] + ' '
    return new_text

def containsPerson(sentence):
  
    flag = 0
    grammar = r"""
        NP1: {<DT>?<JJ>*<IN>*<NN>*<IN>*<NN>+}  # Chunk sequences of DT, JJ, NN
        NP2: {<ORGANIZATION>+<NNP>*}
        NP2: {<NN>} 
        NP4: {<CD>+<NP*><CD>*}
        NP5: {<NNP>*<CD>+<NNS>*<NP>?}
        NP6: {<DT>?<JJ>?<NNS>*}
        NP7: {<PERSON>+<NNP>*}
        NP8: {<GPE>?<NNP>*}
       
  """
    cp = nltk.RegexpParser(grammar)
    #result = cp.parse((ne_chunk(pos_tag(word_tokenize(sentence.lower())))))
    result = cp.parse((ne_chunk(pos_tag(word_tokenize(sentence)))))
    
    if(str(result).__contains__("PERSON")):
        flag = 1
    
    return flag

def getChunks(sentence):
    sentSet = set()
    grammar = r"""
        NP1: {<DT>?<JJ>*<IN>*<NN>*<IN>*<NN>+}  # Chunk sequences of DT, JJ, NN
        NP2: {<ORGANIZATION>+<NNP>*}
        NP2: {<NN>} 
        NP4: {<CD>+<NP*><CD>*}
        NP5: {<NNP>*<CD>+<NNS>*<NP>?}
        NP6: {<DT>?<JJ>?<NNS>*}
        NP7: {<PERSON>+<NNP>*}
        NP8: {<GPE>?<NNP>*}
       
  """
    cp = nltk.RegexpParser(grammar)
    
    result = cp.parse((ne_chunk(pos_tag(word_tokenize(sentence)))))
    
    #print(result)
    for subtree in result:
        word = ''
        if type(subtree) == nltk.tree.Tree:
            subtree = str(subtree)
            subtree = subtree.split('\n')
            subtree = " ".join(subtree)
            #print("subtree:",subtree)
            #print("==subtreeEnd====")
            word = extractTreeWord(str(subtree))
            #print("word:",word)
        if(len(word) != 0):
            sentSet.add(word.strip())
    
    return sentSet
  
#TODO: compare only between headnouns of sentenceWord with coef entity
    #Note coef head nouns already<if done> should be handled in 
    # findSynHypo, findLemmitize methods
    #word,coef
def compare(Str1,Str2):
    flag = 0
    stop_words = set(stopwords.words('english')) 
    wordnet_lemmatizer = WordNetLemmatizer()
    #For dates do direct match between strings
    #print("Str1:",Str1)
    
    dateWordSent = findIfDate(Str1)                
    dateWordCorf = findIfDate(str(Str2))
    if(len(dateWordSent) != 0 and len(dateWordCorf) != 0):
        if(compareDate(dateWordSent,dateWordCorf)):
            flag = 1
        else:
            flag = 0
            return flag;
    ##################
    #Instead of splitting Str1, just take the head noun and proceed similar
    Str1 = Str1.lower()
    Str1 = Str1.split(" ")
    Sent_length = len(Str1) -1
    word = Str1[Sent_length]
    Str2 = Str2.lower()
    Str2 = Str2.split(" ")
    #Lemmatize Str1(sentence word) before comparison
    #word = wordnet_lemmatizer.lemmatize(word)
    if(word not in stop_words):
        if(word in Str2):
            flag = 1

                
                
    return flag

#Date are <month-day-year> string
def compareDate(date1,date2):
    date1Split = date1.split("-")
    date2Split = date2.split("-")
    curDate = datetime.now()
    if( curDate.day == int(date1Split[1]) or curDate.day == int(date2Split[1]) ):
        return False
    if( (date1Split[0] == date2Split[0]) or (date1Split[1] == date2Split[1])):
        return True
    if( (int(date1Split[2]) != curDate.year) and (date1Split[2] == date2Split[2]) ):
        return True
    return False
    
def createFileList(path):
    listFiles = []
    with open(path, encoding='utf8') as f:
        for line in f:
            line = line.rstrip("\n")
            listFiles.append(line)
    return listFiles

def extractFileName(iFile):
    parts = iFile.split("/")
    fileName = parts[len(parts)-1]
    fileName = fileName.split(".")
    return fileName[0]

def minWord(sent):
    words = sent.split(' ')
    if(len(words) == 1):
        return sent
    finalWord = ''    
    finalWord = words[len(words)-1]
    #if last word starts with lower just return it
    if finalWord.islower():
        return finalWord
    
    i = len(words)-2
    while(i >= 0):
        if words[i][0].islower():
            break;
        finalWord = words[i]+' '+finalWord
        i = i-1
    return finalWord
        
def isAllCaps(word):
    i = len(word)-1
    while(i >=0):
        if(word[i].islower()):
            return False;
        i = i-1;
    return True;

def contains_Pronoun(s):
    Pnoun = ["he", "she"]
    s = s.split(" ") 
    s = set(s)
    flag = 0
    for word in s:
        if(Pnoun.__contains__(word)):
            flag = 1
            return word
    if(flag == 0):
        return ""
    
def contains_Pnoun(s):
    Pnoun = ["I","me","you"]
    s = s.split(" ") 
    s = set(s)
    flag = 0
    for word in s:
        if(Pnoun.__contains__(word)):
            flag = 1
            return word
    if(flag == 0):
        return ""
    
def containsP(sentence):
    doc = nlp(sentence)
    tag = []
    for ent in doc.ents:
         tag.append(str(ent.label_))
    if(tag.__contains__("PERSON")):
        return 1
    else:
        return 0
        

#Command line args: python3 coref <ListFile> <ResponseDir>
if __name__ == '__main__':
#    if(len(sys.argv) != 3):
#        print('Expected: python3 coref <ListFile> <ResponseDir>')
#        sys.exit(-1)
        
    listFilePath = sys.argv[1]
    responseFileDir = sys.argv[2]
    testing = 0
    if(testing == 1):
        print('here')
        #line = 'Aeroflot general manager for Hong Kong Vassili Tkatchenko said on Tuesday he was unaware the writ had been filed.'
        line = 'Aviation consultant Steve Miller, the managing director of Trinity Aviation, said he was unaware of any aviation court settlements in Hong Kong.'
        
        print(getChunks(line))
        line = 'Aviation consultant Steve Miller'
        line = 'An outbreak of what is suspected to be winter vomiting disease forced the closure of Sunnybrook Hospital\'s emergency department on Monday morning.'
        line = 'Outbreaks in the UK and Ireland have occurred throughout the year in hospitals, health care facilities, and schools.'
        line = 'John Smith said Outbreaks in the UK'
        line = 'FAMILIES SUE OVER AREOFLOT CRASH DEATHS'
        line = 'U.S. airlines have received an antitrust exemption to negotiate an agreement, which would be subject to government approval.'
        print(getChunks(line))
        
       
        sys.exit(0)
    
    
   # listFilePath = 'E:/Courses/Semester3/NLP/Project/code/tst1.listfile'
   # responseFileDir = 'E:/Courses/Semester3/NLP/Project/resTest'
    
   
    print(listFilePath)
    print(responseFileDir)
    listFiles = createFileList(listFilePath)
    #print("listFiles:",listFiles)
    for iFile in listFiles:
        inputFile = open(iFile,'r')
        fileName = extractFileName(iFile)
        #print("ofn:",fileName)
        #inputFile = open('E:/Courses/Semester3/NLP/Project/dev/a9.input', 'r')
        #outputFile = 'E:/Courses/Semester3/NLP/Project/responses/a9.response'
        outputFile = responseFileDir+"/"+fileName+'.response'
        print("outfile:",outputFile)
        print("Processing input file:",inputFile)
    

        fwrite = open(outputFile, "w+")
        sidCid_word,sidSent = extractcoRef(inputFile)
        #print("sidCid_word:",sidCid_word)
        #print("sidSent:",sidSent)
        #build cid_sentences for each coreferrence
        sidCid_set = defaultdict(set)
        for index in sidCid_word:
            wordSets = set()
            coRefWord = sidCid_word[index]
            #check if the coRefWord is all caps if yes, just pass the end split
            splitCoref = coRefWord.split(' ')
            if isAllCaps(splitCoref[len(splitCoref)-1]):
                coRefWord = splitCoref[len(splitCoref)-1]
            wordSet1 = findWordNetLemitizer(coRefWord)
            wordSet2 = traverse_tree(coRefWord)
            wordSet3 = findSynHypo(coRefWord)
            #wordSet3 = findSynHypoChunking(coRefWord)
            dateWord = findIfDate(coRefWord)
            wordSets = mergeSets(wordSet1,wordSet2,wordSet3,dateWord)
            wordSets.add(coRefWord)
            sidCid_set[index] = wordSets
        print(sidCid_set)
        #fwrite.write(str(sidCid_set))
        
    
        l = len(sidSent)
        for x,y in sidCid_set.items():
            sidCid_ans = defaultdict(set)
            coref = sidCid_word[x]
            sentNo = x[0]
            #print("i:",i)
            print()
            headStr = "<COREF ID="+'"'+x[1]+'"'+">"+coref+"</COREF>"        
            print(headStr)
            fwrite.write(headStr+"\n")
          
            cntr = sentNo+1
            #cntr = sentNo
            # TODO: Uncomment below for pronoun in CADE
            Pronoun2 = contains_Pronoun(sidSent[sentNo])
            Person_flag = containsP(coref)
            if(len(Pronoun2) != 0 and Person_flag == 1):
                sidCid_ans[sentNo].add(Pronoun2)
            if(cntr < l):
                Pronoun1 = contains_Pronoun(sidSent[cntr])
                if(len(Pronoun1) != 0 and Person_flag == 1 and (sentNo+1) == cntr):
                    sidCid_ans[cntr].add(Pronoun1)
            
                
            while (cntr < l):
                Coef_Pnoun = contains_Pnoun(sidCid_word[x])
                if(len(Coef_Pnoun) != 0):
                   # Prnoun = contains_Pnoun(sidSent[cntr])
                   # if(Prnoun == Coef_Pnoun):
                    #    sidCid_ans[cntr].add(Coef_Pnoun)  
                    cntr = cntr + 1
                    continue

                if(len(sidSent[cntr]) == 0):
                    cntr = cntr + 1
                    continue;
                sentence = getChunks(sidSent[cntr])
                
                matchCntr = 0
                for word in sentence:

                    for coef in y:
                        if(compare(word,coef)):
                            #To minimize the word
                            endWord = minWord(word)
                            #Check if its date then remove NYT
                            if len(findIfDate(word)) > 1 and word[0].isalpha():
                                endWord = endWord[4:len(endWord)]
                            sidCid_ans[cntr].add(endWord)
                            #sidCid_ans[cntr].add(word)                            
                cntr = cntr + 1
                
                
            for k,j in sidCid_ans.items():
                temp_string = "{"+str(k)+"}"
                for temp in j:
                    if(len(temp) != 0):
                        newWord = temp_string +" "+"{"+ temp +"}"
                        print(newWord)
                        fwrite.write(newWord+"\n")
            fwrite.write("\n")
                    
    
    

    
    

    
    
 
    
  
    
    
