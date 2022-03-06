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

def compareStudents(student_one, student_two, headers):
    comparators = comparison.getComparators()
    overlap = dict()
    for header_keys in headers:
        this_header = headers[header_keys]
        if this_header.datatype in comparators:
            this_comparator = comparators[this_header.datatype]
            s1attribute = student_one.attributes[this_header.header]
            s2attribute = student_two.attributes[this_header.header]
            comp = this_comparator(s1attribute, s2attribute)
            overlap[this_header.header] = comp
    #print(overlap)
    return overlap

def compareAllStudents(allStudents, headers):
    name = ""
    for header_keys in headers:
        if headers[header_keys].datatype == "name":
            name = headers[header_keys].header

    matrix = dict()
    for i in range(0, len(allStudents)):
        for j in range(0, len(allStudents)):
            student_one = allStudents[i]
            student_two = allStudents[j]
            name_one = student_one.attributes[name]
            name_two = student_two.attributes[name]
            matrix[(name_one, name_two)] = compareStudents(student_one, student_two, headers)
    print("{" + "\n".join("{!r}: {!r},".format(k, v) for k, v in matrix.items()) + "}")
    return matrix

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

    #compareStudents(allStudents[0], allStudents[1], headers_dict)
    compareAllStudents(allStudents, headers_dict)
    
    
    


runner()
