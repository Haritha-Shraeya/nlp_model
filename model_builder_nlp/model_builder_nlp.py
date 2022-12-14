import os
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import linear_kernel
import numpy as np
import pandas as pd
from model_store.persistency.elasticSearch import ElasticSearchInterface

challenge_index = 'challenges'

class Model(object):
    def __init__(self):
        self.documents = None
        self.rawdata = None
        self.mode_data = None
        self._search_df = None
        self._count_vect = None
        self._x_train_counts = None
        self._tfidf_transformer = None
        self._x_train_tfidf = None
        self._x_new_tfidf = None
        self._text = []
        # self._results = None
        self._cosine_similarities = None
        self._results_dataframe = None
        self._final_results = None
        self.db = ElasticSearchInterface()
        self._stop_words = ["xe00", "00", "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your",
                            "yours",
                            "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself",
                            "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which",
                            "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be",
                            "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an",
                            "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for",
                            "with", "about", "against", "between", "into", "through", "during", "before", "after",
                            "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under",
                            "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all",
                            "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not",
                            "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don",
                            "should", "now"]

    def data(self):
        # self.rawdata = pd.read_csv(os.getcwd() + os.sep + "nlp.csv")
        # print("rawdata\n", self.rawdata)
        # self.mode_data = self.rawdata["text"]
        # print("modedata\n", self.mode_data)
        # problems = pd.DataFrame(self.rawdata[["challenge_id", "challenge_title"]])
        # problems["submission_type"] = "problem"
        # self._search_df = problems
        # print("_search_df\n", self._search_df)
        self.documents = self.db.get_all_docs(challenge_index)
        #self.documents = pandas.DataFrame(requests.get(self._url + "/challenges").json())  # obtains all challenges submitted to elastic search
        self.rawdata = pd.DataFrame(self.documents).T
        self.mode_data = self.rawdata["text"]
        self.mode_data = self.rawdata["text"]
        problems = pd.DataFrame(self.rawdata[["challenge_id", "challenge_title"]])
        problems["submission_type"] = "problem"
        self._search_df = problems


    def training(self):
        ## training
        self._count_vect = CountVectorizer(stop_words=self._stop_words)
        self._x_train_counts = self._count_vect.fit_transform(self.mode_data)
        # print("bag of words\n", self._x_train_counts)
        self._tfidf_transformer = TfidfTransformer()
        self._x_train_tfidf = self._tfidf_transformer.fit_transform(self._x_train_counts)
        # print("tfidf\n", self._x_train_tfidf)

    def new(self,text):
        ## new
        x_new_counts = None
        self._text.append(text)
        x_new_counts = self._count_vect.transform(self._text) # transform expects iterable object with strings
        # print("new bag of words\n", x_new_counts.toarray())
        self._x_new_tfidf = self._tfidf_transformer.transform(x_new_counts)
        # print("new tfidf\n", self._x_new_tfidf)
        self._cosine_similarities = linear_kernel(self._x_new_tfidf[0], self._x_train_tfidf).flatten()
        # cosine_similarities = linear_kernel(self._x_new_tfidf[0], self._x_train_tfidf).flatten()
        # print("linear kernel\n")
        # for i in self._cosine_similarities:
        #     print(i)
        self._results = np.argsort(self._cosine_similarities)
        # print("argsort\n", self._results)

    def sentence_similarity(self):
        # _result_list, self._results_dataframe: dataframe containing similarity with all text
        _result_list = list()
        for row in range(0, (self._search_df.shape[0])):
            # if self._cosine_similarities[self._results[row]] * 100 >= 10:
                # print("Score for record is greater than 10 ID = " + str(
                #     self._search_df.iloc[self._results[row], 0]))

            _result_list.append({
                "id": self._search_df.iloc[self._results[(row)], 0],
                "submission_type": self._search_df.iloc[self._results[(row)], 2],
                "title": self._search_df.iloc[self._results[(row)], 1],
                "score": self._cosine_similarities[self._results[(row)]] * 100
            })

        self._results_dataframe = pd.DataFrame(_result_list)
        # print(self._results_dataframe)

    def final_sentence_similarity(self):
        # _final_results, self._final_results: dataframe containing only those that have similarity with text
        _final_results = list()
        for i in range(0, min(25, self._results_dataframe.shape[0])):
            _id = self._results_dataframe.iloc[i, 0]
            _submission_type = self._results_dataframe.iloc[i, 1]
            _score = int(self._results_dataframe.iloc[i, 3])
            if _score == 0:
                continue
            _final_results.append({
                "_id": int(_id),
                "type": _submission_type,
                "score": _score,
                # "words": "[]"
            })
        self._final_results = pd.DataFrame(_final_results)
        print(self._final_results)
        return self._final_results

    def word_similarity(self):
        # word scores
        # print("get wordscore results")
        _vectors = None
        _vectors = self._x_train_tfidf.toarray() * self._x_new_tfidf[0].toarray()
        # temp1 = pd.DataFrame(self._x_train_tfidf.toarray())
        # temp1.to_csv(os.getcwd() + os.sep + "data_train.csv")
        # temp2 = pd.DataFrame(self._x_new_tfidf[0].toarray())
        # temp2.to_csv(os.getcwd() + os.sep + "data_new_tfidf.csv")
        # temp3 = pd.DataFrame(_vectors)
        # temp3.to_csv(os.getcwd() + os.sep + "data_array.csv")
        # print(_vectors)
        # print("Assinged the _vectors = " + str(_vectors.shape[0]))

        # print(self._count_vect.vocabulary_.items())
        _vocab = {v: k for k, v in sorted(self._count_vect.vocabulary_.items(), key=lambda item: item[1])}
        # print(_vocab)
        # print("Assinged the _vocab = " + str(len(_vocab)))
        _result_word_list = list()
        # print("_Vectors rows = " + str(_vectors.shape[0]))

        for vector_row in range(0, _vectors.shape[0]):
            # print("enter for loop")
            sorted_row = _vectors[vector_row].argsort()
            # print(sorted_row)
            for j in range(0, min(25, len(sorted_row))):  # top 100 words only
                _word_score = _vectors[vector_row, sorted_row[-j]]
                if _word_score >= 0.01:
                    # print(sorted_row)
                    _result_word_list.append({
                        "id": self._search_df.iloc[vector_row, 0],
                        "word": _vocab.get(sorted_row[-j]),
                        "word_score": _word_score
                    })
        self._results_word_dataframe = pd.DataFrame(_result_word_list)
        # print(self._results_word_dataframe)
        print(self._results_word_dataframe)
        return self._results_word_dataframe
