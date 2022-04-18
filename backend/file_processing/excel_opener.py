import pandas as pd # pip3 install pandas
import openpyxl # pip3 install openpyxl
#import file_processing.comparison as comparison
import comparison

class Header:
    def __init__(self, header, datatype, necessary):
        self.header = header
        if "exclude_if" in datatype:
            self.datatype = "exclude_if"
            self.parameter = "".join(datatype.split("\"")[1:])
        else:
            self.datatype = datatype
        
        self.necessary = (necessary == 1)
    def __str__(self):
        return self.header +", " + self.datatype +", "+str(self.necessary)
    def __repr__(self):
        return self.header +", " + self.datatype +", "+str(self.necessary)
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
        headers_dict[head[0]] = Header(header, datatype, necessary)
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
    return overlap


def isLegal(overlap, headers, min_hours):
    total_hours = 0
    for key in overlap:
        this_header = headers[key]
        if this_header.datatype == "hours":
            total_hours += overlap[key]
        elif (this_header.datatype == "similar_category_one" or this_header.datatype == "different_category_one") and this_header.necessary:
            if not overlap[key]:
                return False
        elif this_header.datatype == "similar_number" and this_header.necessary:
            if overlap[key] != 0:
                return False
        elif this_header.datatype == "different_number" and this_header.necessary:
            if overlap[key] == 0:
                return False
            
    return total_hours >= min_hours

def getNameHeader(headers):
    name = None
    for header_keys in headers:
        if headers[header_keys].datatype == "name":
            name = headers[header_keys].header
    return name


def compareAllStudents(allStudents, headers, min_hours):

    name = getNameHeader(headers)
    allnames = list()
    legal = list()
    matrix = dict()
    legal_dict = dict() # 0 = same person; -1  = illegal; 1 = legal
    
    for i in range(0, len(allStudents)):
        allnames.append(allStudents[i].attributes[name])
        legal_dict[(allStudents[i].attributes[name], allStudents[i].attributes[name])] = 0
        for j in range(i + 1, len(allStudents)):
            student_one = allStudents[i]
            student_two = allStudents[j]
            name_one = student_one.attributes[name]
            name_two = student_two.attributes[name]
            overlap = compareStudents(student_one, student_two, headers)
            matrix[(name_one, name_two)] = overlap
            matrix[(name_two, name_one)] = overlap
            if isLegal(overlap, headers, min_hours):
                legal.append((name_one, name_two))
                legal_dict[(name_one, name_two)] = 1
                legal_dict[(name_two, name_one)] = 1
            else:
                legal_dict[(name_one, name_two)] = -1
                legal_dict[(name_two, name_one)] = -1
                
    #print("{" + "\n".join("{!r}: {!r},".format(k, v) for k, v in matrix.items()) + "}")
    #print("===============================")
    #print(legal)
    #print("===============================")
    #print(allnames)
    #print("===============================")
    #print(legal_dict)
    return matrix, legal, allnames, legal_dict


def get_least_paired_student(pairable_dict):
    least_paired = None
    min_pairs = float('inf')

    for student in pairable_dict:
        num_pairs = len(pairable_dict[student])
        if num_pairs < min_pairs:
            min_pairs = num_pairs
            least_paired = student
    return student


def get_least_paired_matchable_students(student_list, pairable_dict):
    possible_students = list()
    min_pairs = float('inf')

    for student in student_list:
        pair_len = len(pairable_dict[student])
        if pair_len < min_pairs:
            possible_students = list()
            possible_students.append(student)
            min_pairs = pair_len
        elif pair_len == min_pairs:
            possible_students.append(student)

    return possible_students

def compare_optional(student_to_pair, possible_pairings, overlap_matrix, headers):
    possible_students = list()
    max_num_shared = 0

    for student in possible_pairings:
        overlap = overlap_matrix[(student_to_pair, student)]
        num_shared = 0
        for key in overlap:
            this_header = headers[key]
            if not this_header.necessary:
                if this_header.datatype == "similar_category_one" or this_header.datatype == "different_category_one" and overlap[key]:
                    num_shared +=1
                elif this_header.datatype == "similar_number" and overlap[key] == 0:
                    num_shared +=1
                elif this_header.datatype == "different_number" and overlap[key] != 0:
                    num_shared +=1

        if num_shared > max_num_shared:
            possible_students = list()
            possible_students.append(student)
        elif num_shared == max_num_shared:
            possible_students.append(student)

    return possible_students
    

def get_most_hours(student_to_pair, possible_pairings, overlap_matrix, headers):
    possible_students = list()
    max_hours = float('-inf')

    for student in possible_pairings:
        overlap = overlap_matrix[(student_to_pair, student)]
        total_hours = 0
        for key in overlap:
            this_header = headers[key]
            if this_header.datatype == "hours":
                total_hours += overlap[key]

        if total_hours > max_hours:
            possible_students = list()
            possible_students.append(student)
        elif total_hours == max_hours:
            possible_students.append(student)

    return possible_students

def make_pairings_for_student(student_to_pair, pairable_dict, overlap_matrix, headers):

    possible_pairings = pairable_dict[student_to_pair]
    if len(possible_pairings) == 0:
        return None
    if len(possible_pairings) == 1:
        return possible_pairings[0]

    possible_pairings = get_least_paired_matchable_students(possible_pairings, pairable_dict)
    if len(possible_pairings) == 0:
        return None
    if len(possible_pairings) == 1:
        return possible_pairings[0]

    possible_pairings = compare_optional(student_to_pair, possible_pairings, overlap_matrix, headers)
    if len(possible_pairings) == 0:
        return None
    if len(possible_pairings) == 1:
        return possible_pairings[0]

    possible_pairings = get_most_hours(student_to_pair, possible_pairings, overlap_matrix, headers)
    if len(possible_pairings) == 0:
        return None
    else:
        return possible_pairings[0]

def make_pairable_dict(allnames, legal_dict):
    pairable_dict = dict()
    
    for n1 in allnames:
        pairable_dict[n1] = list()
        for n2 in allnames:
            if legal_dict[(n1, n2)] == 1:
                pairable_dict[n1].append(n2)

    return pairable_dict

def make_all_pairings(overlap_matrix, allnames, legal_dict, headers_dict):
    final_pairings = list()
    unpaired = list()

    while len(allnames) > 0:
        pairable_dict = make_pairable_dict(allnames, legal_dict)
        first_student = get_least_paired_student(pairable_dict)
        if first_student == None:
            return final_pairings, unpaired
        
        second_student = make_pairings_for_student(first_student, pairable_dict, overlap_matrix, headers_dict)
        if second_student == None:
            unpaired.append(first_student)
            allnames.remove(first_student)
        else:
            final_pairings.append((first_student, second_student))
            allnames.remove(first_student)
            allnames.remove(second_student)
    return final_pairings, unpaired
    

def legal_dict_to_json_dict(legal_dict, allnames):
    json_dict = dict()
    
    for n1 in allnames:
        json_dict[n1] = dict()
        for n2 in allnames:
            json_dict[n1][n2] = legal_dict[(n1, n2)]

    return json_dict

def getExclusionHeaders(headers_dict):
    excludsion_headers = list()
    for header in headers_dict:
        if headers_dict[header].datatype == "exclude_if":
            excludsion_headers.append(header)
    return excludsion_headers

def exclude_students(allnames, allStudents, headers_dict):
    excludeable = list()
    name = getNameHeader(headers_dict)
    excludsion_headers = getExclusionHeaders(headers_dict)
    
    for i in range(0, len(allStudents)):
        for header in excludsion_headers:
            parameter = headers_dict[header].parameter
            if allStudents[i].attributes[header] == parameter:
                student_name = allStudents[i].attributes[name]
                excludeable.append(student_name)
    return excludeable
        
    

def runner():
    # headers stuff
    dataframe = excel_to_df("../../data/SCIJ_MOCK_HEADERS_EXCLUDE.xlsx") # excel_to_df("../data/mock_headers.xlsx")
    values = read_excel_file(dataframe)
    headers_dict = convertDataframeValuesToHeaders(values)
    #print(headers_dict)
    #print("===============================")

    # data stuff
    data_values = read_excel_file(excel_to_generic_df("../../data/SCIJ_MOCK.xlsx")) # read_excel_file(excel_to_generic_df("../data/simple_data.xlsx"))
    column_dict = getHeadersIndices(data_values)
    min_hours = 3
    #print(column_dict)
    #print("===============================")
    parser_dict = comparison.getParserDict()
    allStudents = createStudents(headers_dict, column_dict, parser_dict, data_values[1:])
    #print(allStudents)
    #print("===============================")
    
    matrix, legal, allnames, legal_dict = compareAllStudents(allStudents, headers_dict, min_hours)
    
    json_dict = legal_dict_to_json_dict(legal_dict, allnames)
    #print(json_dict)

    # optimality stuff

    # exclusion
    students_to_exclude = exclude_students(allnames, allStudents, headers_dict)
    #print(students_to_exclude)
    paiarable_students = allnames.copy()
    paiarable_students = [x for x in paiarable_students if x not in students_to_exclude]
    
    #print(paiarable_students)
    optimal, unpaired = make_all_pairings(matrix, paiarable_students, legal_dict, headers_dict)
    #print(unpaired)
    #print(optimal)
    unpaired.extend(students_to_exclude)
    final_dict = dict()
    final_dict["optimal"] = list()

    for pair in optimal:
        p1, p2 = pair
        current_dict = dict()
        current_dict["person1"] = p1
        current_dict["person2"] = p2
        final_dict["optimal"].append(current_dict)

    final_dict["unpaired"] = unpaired
    final_dict["matrix"] = json_dict
    #print(final_dict)
    return final_dict

def makePairings(headers_dataframe, data_dataframe, min_hours):
    # extracting data
    headers_values = headers_dataframe.values
    headers_dict = convertDataframeValuesToHeaders(headers_values)
    data_values = data_dataframe.values
    column_dict = getHeadersIndices(data_values)

    parser_dict = comparison.getParserDict()
    allStudents = createStudents(headers_dict, column_dict, parser_dict, data_values[1:])
    matrix, legal, allnames, legal_dict = compareAllStudents(allStudents, headers_dict, min_hours)
    json_dict = legal_dict_to_json_dict(legal_dict, allnames)

    
    students_to_exclude = exclude_students(allnames, allStudents, headers_dict)
    paiarable_students = allnames.copy()
    paiarable_students = [x for x in paiarable_students if x not in students_to_exclude]
    optimal, unpaired = make_all_pairings(matrix, paiarable_students, legal_dict, headers_dict)

    final_dict = dict()
    final_dict["optimal"] = list()
    unpaired.extend(students_to_exclude)

    for pair in optimal:
        p1, p2 = pair
        current_dict = dict()
        current_dict["person1"] = p1
        current_dict["person2"] = p2
        final_dict["optimal"].append(current_dict)

    final_dict["unpaired"] = unpaired
    final_dict["matrix"] = json_dict
         
    return final_dict
    
if __name__ == "__main__":
    final_dict = runner()
    print(final_dict)
