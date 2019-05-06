import pickle
import json
import math
import os
#returns None if no models exist for cow_id; otherwise return a tuple of length-4
#the tuple represents the predicted (yield, fat, protein, lactose) respectively
def GetModelAndPredict(cow_id, temperature, humidity):
    #see if there are models existing for cow_id
    # print(sys)
    path = str(os.getcwd())
    # print(path)
    # print("--end---")
    with open(path + "/models/model_meta.txt", 'r' ,encoding='utf-8') as meta_file:
        data_limit = json.load(meta_file)['data_limit']
        print(data_limit)
        
    with open(path + "/models/model_stats.txt", 'r' ,encoding='utf-8') as stats_file:
        data_stats = json.load(stats_file)
        
    if str(cow_id) not in data_stats or data_stats[str(cow_id)] < data_limit: 
        return None
    else:
        minimum = math.floor(data_stats[str(cow_id)] / 5) * 5
    
    #if there are models for cow_id, return predicted result
    fields = ['yield', 'fat','protein','lactose']
    results = []
    filename = path + "/models/models/"+str(minimum)+"/"+str(cow_id)+".pkl"
    with open(filename, 'rb') as model_file:
        for field in fields:
            loaded_model = pickle.load(model_file)
            results.append(loaded_model.predict([[temperature,humidity]])[0])
    return tuple(results)

# print(GetModelAndPredict(4400, 10, 53))