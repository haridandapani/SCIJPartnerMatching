import pandas as pd # pip3 install pandas
import openpyxl # pip3 install openpyxl
import comparison

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

class MatchableStudent:
    def __init__(self, attributes):
        self.attributes = attributes
    def __repr__(self):
        return self.attributes.__repr__()


def excel_to_df(filepath):
    dataframe = pd.read_excel(filepath, usecols = "A:D")
    return dataframe

def excel_to_generic_df(filepath):
    dataframe = pd.read_excel(filepath, header=None)
    return dataframe

def read_excel_file(dataframe):
    return dataframe.values


def getHeadersIndices(values):
    column_dict = dict()
    for i in range(len(values[0])):
        column_dict[values[0][i]] = i
    return column_dict


def convertDataframeValuesToHeaders(values):
    headers_dict = dict()
    for head in values:
        header = head[0]
        datatype = head[1]
        necessary = int(head[2])
        similar_match = int(head[3])
        headers_dict[head[0]] = Header(header, datatype, necessary, similar_match)
    return headers_dict


def createStudents(headers_dict, column_dict, parser_dict, data_values):
    allStudents = list()
    for student_values in data_values:
        student_attributes = dict()
        for key in headers_dict:
            header = headers_dict[key]
            datatype = header.datatype
            parse_function = parser_dict[datatype]
            student_attributes[key] = parse_function(student_values[column_dict[key]])
        allStudents.append(MatchableStudent(student_attributes))
    return allStudents
    
        

def runner():
    # headers stuff
    dataframe = excel_to_df("../data/mock_headers.xlsx")
    values = read_excel_file(dataframe)
    headers_dict = convertDataframeValuesToHeaders(values)
    print(headers_dict)
    print("===============================")

    # data stuff
    data_values = read_excel_file(excel_to_generic_df("../data/simple_data.xlsx"))
    #print(values)
    column_dict = getHeadersIndices(data_values)
    print(column_dict)
    print("===============================")
    parser_dict = comparison.getParserDict()
    allStudents = createStudents(headers_dict, column_dict, parser_dict, data_values[1:])
    print(allStudents)
    
    
    


runner()
