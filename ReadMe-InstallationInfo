Read Me:
========
Team Name: VT27
Team Members : Srivathsan Gomadam Ramesh (u1208099)
                   Nikhil Ramesh (u1266557)
1)      External Sources
        a.      NLTK
                i.      Nltk.download(“all”)
        b.      Spacy
                i.      pip install -I spacy==2.2.0
                ii.     pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.2.0/en_core_web_sm-2.2.0.tar.gz
        c.      datefinder
                i.      https://github.com/akoumjian/datefinder
                (subversion of depedent packages) [other versions might cause errors]
                datefinder (0.7.0)
                ii.     pytz (from datefinder) (2019.2)
                iii.    python-dateutil>=2.4.2 (from datefinder) (2.8.0)
                iv.     regex>=2017.02.08 (from datefinder) (2019.11.1)
                v.      six>=1.5 (from python-dateutil>=2.4.2->datefinder) (1.12.0)
2)      Time to process one document: ~40 seconds at max
3)      Contribution of each team member:
        a.      Nikhil Ramesh:
                i.       Pronoun resolution and matching using customized NER based comparison and matching
                ii.     Designing the framework of the code to parse sentences and extract the coref ids, corefs as well as sentences without the tags
                iii.    Smart comparison function that doesn’t compare stop word, and ability to accommodate expanded abbreviations, comparing only the head nouns instead of the entire coref
                iv.     Dealing with capital cases and lemmatization of sentence words
        b.      Srivathsan Gomadam Ramesh:
                i.      chunking Noun Phrases using NLTK and customized regex to fit the given dataset.
                ii.     Finding data patterns and perform matching with the documents and eliminating false positive date matches
                iii.    Removing coref from the sentences
                iv.     Generating dictionary for coref using wordnet lematizer and synonyms
                v.      Custom chunking of each coref to get the head noun

4)      Any known problem or limitation: Proper versions of packages (as mentioned in 1) is required. Else it could cause problems. The packages are readily installed in the CADE virtual machine which is shared in the next section.
5)      How to RUN in CADE:
        a.      CADE machine: labx-x.eng.xxxx.edu
        b.      source /home/<uid>/env/bin/activate.csh
        c.      cd /home/<uid>/Sem3/nlp/Project/Project/code/
        d.      To Run:
                i.      (env) [uid@labx-x code]$ python3 coref.py ts1.listfile ../responses1/
                ii.     Example: python3 /home/uid/Sem3/nlp/Project/Project/code/coref.py <listFile> <Response Dir>
        e.      Scoring Program:
                i.      CADE machine: labx-x.eng.xxxx.edu
                ii.     source /home/uid/env/bin/activate.csh
                iii.    cd /home/uid/Sem3/nlp/Project/Project/scoring-program
                iv.     To execute (example):
                (env) [uid@lab1-1 scoring-program]$ python3 scorer.py -v ../tst1/ ../responses1/ ts1.listfile
                python3 scorer.py -v <keyFilesDir> <responseFileDir> <listOfFilesToScore>
