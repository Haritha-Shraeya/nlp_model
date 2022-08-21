from .elasticSearch import ElasticSearchInterface


challenges_index = 'challenges'
models_index = 'models'


class Challenge_esi:
    def __init__(self):
        #print("reached persistencyyy")
        self.esi = ElasticSearchInterface()
        #print("inside persistency" + str(self.esi))
        #print(self.esi.es.info())

    def insert_update_challenge(self, data): 
        #creating document to insert into ElasticSearch
        challenge_data_doc = {
            "challenge_id": data["challenge_id"],
            "challenge_title": data["challenge_title"],
            "text": data["text"]
        }  
        #### print(challenge_data_doc)
        #print(self.esi.insert_update_doc(challenges_index, challenge_data_doc))
        ##self.esi.create_index("challenge1")
        #print("index created")
        #print("print here" + self.esi.insert_update_doc("challenge1", challenge_data_doc))
        #return self.esi.insert_update_doc(challenges_index, challenge_data_doc)  #do i create challenges_index?
        return self.esi.insert_update_doc(challenges_index, challenge_data_doc)

        #indexes
        #chllng3
        #challenge
        #challenge1

    def get_challenge(self, challenge_id):
        return self.esi.get_doc(challenges_index, "challenge_id", challenge_id)

    def get_all_challenges(self):
        return self.esi.get_all_docs(challenges_index)


class Model_esi:
    def __init__(self):
        self.esi = ElasticSearchInterface()

    def insert_model(self, model_index, model_doc):
        self.esi.insert_doc(model_index, model_doc)

    def get_all_models(self):
        return self.esi.get_all_docs(models_index)