import numpy
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import linear_kernel
import numpy as np
import pandas as pd
from model_store.persistency.persistency import Model_esi

challenge_index = 'challenges'
models_index = 'models'


class Model(object):
    def __init__(self):
        self.text = []
        self._search_df = pd.DataFrame()
        self._count_vect = None
        self._x_train_counts = None
        self._tfidf_transformer = None
        self._x_train_tfidf = None
        self._x_new_tfidf = None
        self._new_text = []
        self.models = pd.DataFrame()
        self.trained_model = pd.DataFrame()
        self._cosine_similarities = None
        self._results = None
        self._results_dataframe = None
        self._final_results = None
        self._results_word_dataframe = None
        self.db = Model_esi()
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

    def model_data(self, challenge_entry):
        text = (challenge_entry["text"])
        self.text.append(text)

        new_row = {"challenge_id": challenge_entry["challenge_id"], "challenge_title": challenge_entry["challenge_title"], "submission_type": "problem"}
        self._search_df = self._search_df.append(new_row, ignore_index=True)

        self._count_vect = CountVectorizer(stop_words=self._stop_words)
        self._x_train_counts = self._count_vect.fit_transform(self.text)
        self._tfidf_transformer = TfidfTransformer()
        self._x_train_tfidf = self._tfidf_transformer.fit_transform(self._x_train_counts)
        print(type(self._x_train_counts))
        print(type(self._x_train_tfidf))
        counts = self._x_train_counts.tolil(copy=False).data
        counts_list = counts.tolist()
        tfidf = self._x_train_tfidf.tolil(copy=False).data
        tfidf_list = tfidf.tolist()
        print(type(counts_list))
        print(type(tfidf_list))
        model_data = {
            "model_type": "challenges",
            "challenge_id": challenge_entry["challenge_id"],
            "x_train_counts": counts_list,
            "x_train_tfidf": tfidf_list
        }
        self.db.insert_model(models_index, model_data)

    def new(self, inp_text):
        self._new_text.append(inp_text)
        self._count_vect = CountVectorizer(stop_words=self._stop_words)
        x_new_counts = self._x_train_counts.transform(self._new_text) # transform expects iterable object with strings
        self._tfidf_transformer = TfidfTransformer()
        self._x_new_tfidf = self._x_train_tfidf.transform(x_new_counts)
        self.models = pd.DataFrame(self.db.get_all_models()).T
        self.trained_model = self.models["x_train_tfidf"]
        self._cosine_similarities = linear_kernel(self._x_new_tfidf[0], self.trained_model).flatten()
        self._results = np.argsort(self._cosine_similarities)

    def sentence_similarity(self):
        _result_list = list()
        for row in range(0, (self._search_df.shape[0])):
            _result_list.append({
                "id": self._search_df.iloc[self._results[(row)], 0],
                "submission_type": self._search_df.iloc[self._results[(row)], 2],
                "title": self._search_df.iloc[self._results[(row)], 1],
                "score": self._cosine_similarities[self._results[(row)]] * 100
            })

        self._results_dataframe = pd.DataFrame(_result_list)

    def final_sentence_similarity(self):
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
                "score": _score
            })
        self._final_results = pd.DataFrame(_final_results)
        print(self._final_results)
        return self._final_results

    def word_similarity(self):
        _vectors = None
        _vectors = self._x_train_tfidf.toarray() * self._x_new_tfidf[0].toarray()
        _vocab = {v: k for k, v in sorted(self._count_vect.vocabulary_.items(), key=lambda item: item[1])}
        _result_word_list = list()

        for vector_row in range(0, _vectors.shape[0]):
            sorted_row = _vectors[vector_row].argsort()
            for j in range(0, min(25, len(sorted_row))):  # top 100 words only
                _word_score = _vectors[vector_row, sorted_row[-j]]
                if _word_score >= 0.01:
                    _result_word_list.append({
                        "id": self._search_df.iloc[vector_row, 0],
                        "word": _vocab.get(sorted_row[-j]),
                        "word_score": _word_score
                    })
        self._results_word_dataframe = pd.DataFrame(_result_word_list)
        return self._results_word_dataframe

