import objectpath
import json
import glob

class DataQuery:

    tree = None

    def __init__(self, json_data):
        self.tree = objectpath.Tree(json_data)

    def queryObjectTree(self, json_query):

        results = list(self.tree.execute(json_query))

        print("Results ", results,flush=True)
        return results

    def getObjectFilterString(self, argument_dictionary: dict):

        filter_string = ""
        i = 1

        if len(argument_dictionary.items()) > 0:
            filter_string = "["

            for k, v in argument_dictionary.items():
                if type(v) == str:
                    v = "'{v}'".format(v=v)

                filter_string = filter_string + "@.{k} is {v}".format(k=k, v=v)

                if i < len(argument_dictionary.items()):
                    filter_string = filter_string + " and "

                i += 1

            filter_string = filter_string + "]"

        return filter_string

class DataStorage:

    data = None
    dq = None

    def __init__(self):
        self.loadData()
        self.dq = DataQuery(json_data=self.data)

    def loadData(self):

        self.data = self.loadJsonFiles("patient")

    def loadJsonFiles(self, filePrefix):
        data = []
        for file in glob.glob("/code/schema/data/{filePrefix}*.json".format(filePrefix=filePrefix)):
            with open(file) as f:
                data.append(json.load(f))

        return data

    def getPatient(self, **kwargs):
        filter_string = self.dq.getObjectFilterString(
            argument_dictionary=dict(resourceType="Patient", **kwargs))
        json_query = "$.*{filters}".format(filters=filter_string)

        return self.dq.queryObjectTree(json_query=json_query)

    def getPhoto(self, **kwargs):
        filter_string = self.dq.getObjectFilterString(argument_dictionary=kwargs)

        json_query = "$.*{filters}".format(filters=filter_string)

        return self.dq.queryObjectTree(json_query=json_query)