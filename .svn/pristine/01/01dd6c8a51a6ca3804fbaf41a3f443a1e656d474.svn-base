# this module will build a specified model
# each model_type will generate 3 files that will be stored in elastic search and meta data index in ES to enable


import os
import pickle
from datetime import datetime
from pathlib import Path

import pandas, numpy
import nltk 
#nltk.download()
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from nltk.corpus import stopwords

lemmatizer = WordNetLemmatizer()

class ModelBuilderHandle:

    def __init__(self):
        self._temp_dir = os.getcwd() + os.sep + "temp" + os.sep
        self._count_vect = None
        self._train_counts = None
        self._tfidf_transformer = None
        self._train_tfidf = None
        self._text = None
        
    def textProcessor(self, csv_file):
        df = pandas.read_csv(csv_file)  #,usecols=["text"]
        #text = df.to_pickle("./text.pkl")
        #numpy.savetxt(textFile, df.values, fmt='%s')  
        
        finalText = list()
        for paragraph_no in range(len(df['text'])): #df['text'] is list of paragraphs
            finalParagraph = ""
            sentences = nltk.sent_tokenize(df['text'][paragraph_no])
            for sentence_no in range(len(sentences)):
                words = [lemmatizer.lemmatize(word) for word in nltk.word_tokenize(sentences[sentence_no]) if word not in stopwords.words('english')]
                finalSentence = ' '.join(words)
                #print(finalSentence)
                finalParagraph += finalSentence
            finalText.append(finalParagraph)
        df['final_text'] = finalText
        #print(df['final_text'])
        return df['final_text']
         
        
    def build_model(self, text): #timestring
        # this function should build and return the model
        #print('this has entered build model' + text)
        self._text = text
        self._build_information_vectors(text=text)

        return self._count_vect, self._tfidf_transformer, self._train_tfidf

    def _build_information_vectors(self, text):
        # calculate vectors
        self._count_vect = CountVectorizer()
        self._train_counts = self._count_vect.fit_transform(text)
    
        self._tfidf_transformer = TfidfTransformer()
        self._train_tfidf = self._tfidf_transformer.fit_transform(self._train_counts)

        return

    def _save_model_vectors(self, timestring):
         timestring = str(timestring)
         # save vectors to temp directory
         p = Path(self._temp_dir + timestring + os.sep)
    
         if p.exists() == False:
             print(self._temp_dir + timestring + os.sep)
             os.makedirs(self._temp_dir + timestring + "\\")
    
         pickle.dump(self._count_vect, open(self._temp_dir + timestring + os.sep + "count_vect.pkl", 'wb'))
         pickle.dump(self._tfidf_transformer, open(self._temp_dir + timestring + os.sep + "tfidf_vect.pkl", 'wb'))
         pickle.dump(self._train_tfidf, open(self._temp_dir + timestring + os.sep + "_train_tfidf.pkl", 'wb'))
        
         return


