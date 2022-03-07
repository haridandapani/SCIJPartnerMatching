import pandas as pd # pip3 install pandas
import openpyxl # pip3 install openpyxl

class Header:
    def __init__(self, header, datatype, necessary, similar_match):
        self.header = header
        self.datatype = datatype
        self.necessary = (necessary == 1)
        self.similar_match = (similar_match == 1)
    def __str__(self):
        return self.header +", " + self.datatype +", "+str(self.necessary)+", "+str(self.similar_match)
    def __repr__(self):
        return self.header +", " + self.datatype +", "+str(self.necessary)+", "+str(self.similar_match)
    def __hash__(self):
        return hash(self.header)
    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.header == other.header

def excel_to_df(filepath):
    dataframe = pd.read_excel(filepath, usecols = "A:D")
    return dataframe

def read_excel_file(dataframe):
    return dataframe.values

def convertDataframeValuesToHeaders(values):
    headers_dict = dict()
    for head in values:
        header = head[0]
        datatype = head[1]
        necessary = int(head[2])
        similar_match = int(head[3])
        headers_dict[head[0]] = Header(header, datatype, necessary, similar_match)
    return headers_dict

def runner():
    dataframe = excel_to_df("../data/mock_headers.xlsx")
    values = read_excel_file(dataframe)
    headers_dict = convertDataframeValuesToHeaders(values)
    print(headers_dict)

runner()
