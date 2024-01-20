#transfer any raw text data into embeddings with index

from sentence_transformers import SentenceTransformer, util
import numpy as np
import json
import os
from datetimerange import DateTimeRange
import nlp_time_detector as nlp_time

NAME_EMBEDDING_MODEL = 'all-MiniLM-L6-v2'

class VecDataBase():
    def __init__(self, db_paths, update_db = True):
        self.cache_vector_database = {}
        self.model = SentenceTransformer(NAME_EMBEDDING_MODEL)
        if update_db and db_paths: #initalialize embeddings
            self.load_db(db_paths)

    def load_db(self, db_paths):
        for db_json_file in db_paths:
            if db_json_file in list(self.cache_vector_database.keys()): #quick load corpus_json 
                corpus_json = self.cache_vector_database[db_json_file]
                print(f"loaded json {db_json_file}")
            else:
                with open(db_json_file, 'r', encoding='utf-8') as file:
                    corpus_json = json.load(file)
                self.cache_vector_database[db_json_file] = corpus_json 
                
            db_ebd_file = self.get_embed_path(db_json_file)
            if not os.path.exists(db_ebd_file):
                self.convert_json_to_embeddings(db_json_file)
            if db_ebd_file in list(self.cache_vector_database.keys()): #quick load embeddings corpus_ebd
                corpus_ebd = self.cache_vector_database[db_ebd_file]
                print(f"loaded vdb {db_ebd_file}")
            else:
                if os.path.getsize(db_ebd_file) > 0:
                    with open(db_ebd_file, 'r', encoding='utf-8') as file:
                        try:
                            corpus_ebd = json.load(file)
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON: {e}")
                else:
                    print(f"File is empty: {db_ebd_file}")
                self.cache_vector_database[db_ebd_file] = corpus_ebd

    def convert_json_to_embeddings(self, db_paths):
        with open(db_paths, 'r') as file:
            corpus_list = json.load(file)
        
        embeddings = {}
        if type(corpus_list) == dict:
            corpus_list = [corpus_list]
        # Processing the embeddings
        for i, event in enumerate(corpus_list):
            for name, value in event.items():
                embeddings['id'+str(i)+'_'+name] = self.model.encode(value, convert_to_numpy=True).tolist()  # embedding
        
        # Writing the embeddings
        ebd_file_path = f"{db_paths}.ebd"
        with open(ebd_file_path, 'w', encoding='utf-8') as file:
            json.dump(embeddings, file, ensure_ascii=False, indent=4)
        
        print(f"Converting embeddings {db_paths} and saved to {ebd_file_path}")
        return 0

    def encode_sentences(self, corpus_dict):
        if not all(isinstance(key, str) and isinstance(value, str) for key, value in corpus_dict.items()):
            raise ValueError("All keys and values in corpus_dict must be strings")
        sentences = list(corpus_dict.values())
        embeddings = self.model.encode(sentences, convert_to_numpy=True)
        embeddings_dict = {key: embedding for key, embedding in zip(corpus_dict.keys(), embeddings)}
        return embeddings_dict
 
    def similarity(self, sentences, threshold=0.6, top_n = 2): # todo @yi
        embeddings = self.model.encode(sentences, convert_to_numpy=True)
        similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
        print(similarity.item())

    def get_embed_path(self, db_json_file):
        return db_json_file + '.ebd'

    def search_db(self, user_input, db_json_file, threshold=0.2, top_n = 2): #todo
        db_ebd_file = self.get_embed_path(db_json_file)

        if db_ebd_file not in list(self.cache_vector_database.keys()): #quick load corpus
            self.load_db([db_json_file])

        corpus_ebd = self.cache_vector_database[db_ebd_file]
        corpus_json = self.cache_vector_database[db_json_file]
        
        query_embedding = self.model.encode(user_input, convert_to_numpy=True) #user input -> query_embedding
        cosine_scores = util.pytorch_cos_sim(query_embedding, list(corpus_ebd.values()))
        top_results_index = np.argpartition(-cosine_scores[0], range(top_n))[0:top_n]

        #extracted_time = nlp_time.extract_time(user_input)
        time_based_events = None
        #if extracted_time:
        #    print(f"extracted time: {extracted_time}")
        #    time_based_events = self.search_db_by_time([t[1] for t in extracted_time], db_json_file)
        
        result = ''
        score = []
        for idx in top_results_index.tolist():
            if cosine_scores[0][idx].item() > threshold:
                #print(corpus[idx], "(Score: %.4f)" % (cosine_scores[0][idx]))
                result_id = list(corpus_ebd.keys())[idx]
                id = int(result_id.split('_')[0][2::])

                print(corpus_json)
                print(result_id)
                if time_based_events is None or id in time_based_events.keys():
                    result += json.dumps(corpus_json[int(result_id.split('_')[0][2::])])
                    score.append(cosine_scores[0][idx].item())
            else:
                print(f"searching score: {cosine_scores[0][idx].item()}")

        if result:
            print("\n most similar sentences in corpus:", result, "\n avg. score:",sum(score)/len(score),"\n")
        else:
            print("none found")
        return result, score

    def search_db_by_time(self, user_input_times, db_json_file):
        try:
            if db_json_file not in list(self.cache_vector_database.keys()): #quick load corpus
                self.load_db([db_json_file])

            corpus_json = self.cache_vector_database[db_json_file]
            events_in_range = {}
            for id, event in enumerate(corpus_json):
                time_range = self.__extract_event_time_range(event)
                for user_input_time in user_input_times:
                    if user_input_time in time_range:
                        events_in_range[id] = event
            return events_in_range
        except:
            return {}

    def __extract_event_time_range(self, event):
        event_time_str = event['event_time'].split(' | ')[0]
        parts = event_time_str.split(', ')
        date_str = ", ".join(parts[:-1])
        timestamps = parts[-1].split(' - ')
        start_time_str, end_time_str = timestamps[0], timestamps[1]
        return DateTimeRange(date_str + ', ' + start_time_str,date_str + ', ' + end_time_str)
    
if __name__ == "__main__":
    DATA_PATH={'loc1':'./db/ocp/ocp.json'} #{'loc1':'db/exhibit-info.csv', 'user1':'db/user-data.csv'}
    v = VecDataBase(DATA_PATH, False)
    
    # Test 1 starts from here: test the search by time
    ############################
    db_json_file = "./db/csv/Egyptian Museum.json"
    user_input = "hi, what's it about?"
    threshold=1.0
    top_n = 5

    v.search_db(user_input, db_json_file)

    # Test 2 starts from here 
    ############################
    ##print("Found " + str(len(v.search_db_by_time('2023-10-17 15:30:00', './db/ocp/ocp.json'))) + " events")
    #print(v.search_db_by_time('2023-10-17 15:30:00', './db/ocp/ocp.json'))
