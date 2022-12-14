from flask import jsonify, make_response
from elasticsearch import Elasticsearch

cloud_id = "TestRun:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvJDFiOGQyZDVjY2MwNzQ4NGFhYmRmZDkyNWU1MTViZjdjJGJiMThjN2E2NjkxMDRiNmFiMTc4ZjhhMjI4MTRmZTNm"
es_username = "elastic"
es_password = "rl7Jt00BI7O97r3x2iKWG6Ug"
http_auth = (es_username, es_password)

#es_host = "MyFirstTry:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvJDZjOGNlOWFlNzQ0MjQ3NmI4NTNhOWUxOTYyMTYwODAwJGQzYzNmMmJmNGMzNzQxNzBhNzU4ZmI1NjljYmE2Njc1"
#es_user = "elastic"
#es_pass = "huKWasZTibML73QezrtaRACh"
#http_auth = (es_user, es_pass)

index_to_id_type = {
    'ideas': 'idea_id',
    'solutions': 'solution_id',
    'challenges': 'challenge_id',
    'models': 'model_index_number',
    'generic': 'key'
}




#connection = Elasticsearch(cloud_id=cloud_id, http_auth=http_auth)
#print(connection.info())

class ElasticSearchInterface:
    def __init__(self):
        ####print("reached init")
        self.cloud_ID = "ElasticSearch_:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyRiM2E0NmM2YTk0ZGM0M2RkYjM5MTdhODc1OTJmMjZiOSQ0ODFjOWQxMzkwZTU0MmZkOWU0Nzk2MjkyN2UzMTNhNg=="
        self.http_AUTH = ("elastic", "15FdoFfv22mqGlXbKMMomgjm")
        self.es = Elasticsearch(cloud_id=self.cloud_ID, http_auth=self.http_AUTH) #### client
        ####print(self.es.info())
        
    # create index in elastic-search
    def create_index(self, indexName):
        self.es.indices.create(index=indexName, ignore=400)

    def insert_doc(self, index, obj):
        self.es.index(index=index, body=obj)


    # insert/update document in elastic-search
    def insert_update_doc(self,index,obj):
        #print("trying to update")
        id_type = index_to_id_type[index]
        #print("step1" + str(id_type))
        search_res = self.es.search(index=index, body={"query": {"match": {id_type: obj[id_type]}}})
        #print("step2" + str(search_res))
        total_found = search_res['hits']['total']['value']
        #print("step3" + str(total_found))
        if total_found == 0:
            try:
                #print("step4")
                #value = self.es.index(index=index, body=obj)
                self.es.index(index=index, body=obj)
                #print(value)
                return "Insert successful"
            except:
                return "Insert unsuccessful"
            # return self.es.index(index=index, body=obj)

        elif total_found > 1:
            #print("step5")
            return "document id not unique"
        try:
            #print("step6")
            #return make_response(jsonify((self.es.update(index=index, id=search_res['hits']['hits'][0]['_id'], body={"doc": obj}))))
            #return jsonify({'response':(self.es.update(index=index, id=search_res['hits']['hits'][0]['_id'], body={"doc": obj}))})
            #value = self.es.update(index=index, id=search_res['hits']['hits'][0]['_id'], body={"doc": obj})
            self.es.update(index=index, id=search_res['hits']['hits'][0]['_id'], body={"doc": obj})
            #print(value)
            return "Update successful"
        except:
            return "Update unsuccessful"
         



        #self.es = connection
        #print(self.es.info())
        #self.es = Elasticsearch(cloud_id=cloud_id, basic_auth=http_auth)
        #print(self.es.info())
        # http_auth = (es_user, es_pass)
        # self.es = Elasticsearch(cloud_id=es_host, basic_auth=http_auth)
        # http_auth = (es_username, es_password)
        # self.es = Elasticsearch(cloud_id=cloud_id, http_auth=http_auth)

    def get_doc(self,index,field,field_value):
        res = self.es.search(index=index, body={"query": {"match": {field: field_value}}})
        #print(res)

        total_found = res['hits']['total']['value']
        if total_found == 0:
            return "Object not found"
        if total_found > 1:
            return "Multiple objects found"
        obj_res = res['hits']['hits'][0]['_source']
        return obj_res

    def get_all_docs(self, index):
        res = self.es.search(index=index, body={"query": {"match_all": {}}}, size=50) #default size is 10
        data_es = res['hits']['hits']
        docs = [doc['_source'] for doc in data_es]
        return {k: v for k, v in enumerate(docs)}

