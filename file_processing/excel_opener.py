import pandas as pd # pip3 install pandas
import openpyxl # pip3 install openpyxl
import xlsxwriter # pip3 install xlsxwriter
import file_processing.comparison as comparison

from file_processing.constants import UPLOAD_FOLDER

# Header class for defining how to parse the headers
class Header:
    # Take in the value of the header, its datatype, and whether it is necessary
    def __init__(self, header, datatype, necessary):
        self.header = header

        # If we need to exclude a certain value of the header, extract the parameter from the exclude_if header
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

# MatchableStudent class for holding data about individual students within a dictionary
class MatchableStudent:
    def __init__(self, attributes):
        self.attributes = attributes
    def __repr__(self):
        return self.attributes.__repr__()

# Helper function for testing to convert Excel file to dataframe
def excel_to_df(filepath):
    dataframe = pd.read_excel(filepath, usecols = "A:D")
    return dataframe

# Helper function for testing to convert Excel file to dataframe, including top row
def excel_to_generic_df(filepath):
    dataframe = pd.read_excel(filepath, header=None)
    return dataframe

# Returns values from dataframe
def read_excel_file(dataframe):
    return dataframe.values

# Gets the indices of each of the headers with the given values, thus corresponding a header with its affiliated column
def getHeadersIndices(values):
    column_dict = dict()
    for i in range(len(values[0])):
        column_dict[values[0][i]] = i
    return column_dict

# Creates a headers dictionary for storing relevant information about headers given values from a dataframe
# Correlates the name of a header with all of the information that we need about it
def convertDataframeValuesToHeaders(values):
    headers_dict = dict()
    for head in values:
        try:
            header = head[0]
            datatype = head[1]
            necessary = int(head[2])
        except Exception as err:
            raise RuntimeError("Necessary header must be a number / Did you upload the right headers file and is it formatted correctly?" +
                               "... Original Exception: "+ str(type(err)) + " : " + str(err))
        headers_dict[head[0]] = Header(header, datatype, necessary)
    return headers_dict

# Given headers, the numbers of all of the columns, the parsers needed to read the values of each data point, and the dataframe, creates a list of MatchableStudent
def createStudents(headers_dict, column_dict, parser_dict, data_values):
    allStudents = list()
    for student_values in data_values:
        student_attributes = dict()
        for key in headers_dict:
            header = headers_dict[key]
            datatype = header.datatype
            try:
                parse_function = parser_dict[datatype]
            except Exception as err:
                raise RuntimeError("One of the headers in your header file does not match our predefined types... Original Exception: "+ str(type(err)) + " : " + str(err))
            try:
                student_attributes[key] = parse_function(student_values[column_dict[key]])
            except Exception as err:
                raise RuntimeError("Could not match one of the headers in the header file with the data file... Original Exception: "+ str(type(err)) + " : " + str(err))
        allStudents.append(MatchableStudent(student_attributes))
    return allStudents

# Removes students with no names / blank rows
def removeUnnamedStudents(headers_dict, allStudents):
    name = getNameHeader(headers_dict)
    output = list()
    for student in allStudents:
        if not pd.isna(student.attributes[name]):
            output.append(student)
    return output
            

# Gets the overlap between two students given the information in the headers
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

# Returns whether a given overlap between two students is Legal based on if the pairing satisfies all of the necessary criteria in the headers
# and whether the number of hours that they share is greater than or equal to the minimum number of hours
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

# Finds the header associated with the needed name column
def getNameHeader(headers):
    for header_keys in headers:
        if headers[header_keys].datatype == "name":
            return headers[header_keys].header
    raise RuntimeError("Your headers file needs to specify at least one header as the name.")

# Creates a matrix for comparing students given all of the students in the list allStudents, the headers to compare with, and
# the minimum number of hours needed for a legal pairing
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

    return matrix, legal, allnames, legal_dict

# Gets the student with the least number of legal matches given the pairable_dict 
def get_least_paired_student(pairable_dict):
    least_paired = None
    min_pairs = float('inf')

    for student in pairable_dict:
        num_pairs = len(pairable_dict[student])
        if num_pairs < min_pairs:
            min_pairs = num_pairs
            least_paired = student
    return student

# Gets the student with the least number of legal matches given that they are in student_list (which should screen for students who pair with a given student)
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

# Gets the students from possible_pairings with the most amount of shared optional criteria as student_to_pair
# Uses overlap_matrix and headers to provide data for comparison
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
    
# Gets the students from possible_pairings with the most amount of shared time as student_to_pair
# Uses overlap_matrix and headers to provide data for comparison
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

# Makes the pairings for a given studen given the people they could possibly pair with, the overlap statisics, and the headers
def make_pairings_for_student(student_to_pair, pairable_dict, overlap_matrix, headers):

    # Get all legal pairings for the student
    possible_pairings = pairable_dict[student_to_pair]
    if len(possible_pairings) == 0:
        return None
    if len(possible_pairings) == 1:
        return possible_pairings[0]

    # Find the legal pairing that has the smallest number of other people that they could pair with
    possible_pairings = get_least_paired_matchable_students(possible_pairings, pairable_dict)
    if len(possible_pairings) == 0:
        return None
    if len(possible_pairings) == 1:
        return possible_pairings[0]

    # Compare students on optional criteria, returning the students that satisfy the most optional criteria
    possible_pairings = compare_optional(student_to_pair, possible_pairings, overlap_matrix, headers)
    if len(possible_pairings) == 0:
        return None
    if len(possible_pairings) == 1:
        return possible_pairings[0]

    # Return the students with the most amount of shared time with the student to pair 
    possible_pairings = get_most_hours(student_to_pair, possible_pairings, overlap_matrix, headers)
    if len(possible_pairings) == 0:
        return None
    else:
        return possible_pairings[0]

# Makess the pairable dictionary for all students given the legality of all pairings and all students' names
# Returns a dictionary correlating each student to a list of students they could legally pair with
def make_pairable_dict(allnames, legal_dict):
    pairable_dict = dict()
    for n1 in allnames:
        pairable_dict[n1] = list()
        for n2 in allnames:
            if legal_dict[(n1, n2)] == 1:
                pairable_dict[n1].append(n2)

    return pairable_dict

# Makes all of the pairings for all of the students given in allnames
# Returns a list of pairings and all people left unpaired
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
    
# Converts legal_dict to something usable by the frontend
def legal_dict_to_json_dict(legal_dict, allnames):
    json_dict = dict()
    
    for n1 in allnames:
        json_dict[n1] = dict()
        for n2 in allnames:
            json_dict[n1][n2] = legal_dict[(n1, n2)]

    return json_dict

# Gets the headers used for excluding students
def getExclusionHeaders(headers_dict):
    exclusion_headers = list()
    for header in headers_dict:
        if headers_dict[header].datatype == "exclude_if":
            exclusion_headers.append(header)
    return exclusion_headers

# Returns the list of students to exclude based on allStudents, which contains data about each student and headers_dict
def exclude_students(allnames, allStudents, headers_dict):
    excludeable = list()
    name = getNameHeader(headers_dict)
    exclusion_headers = getExclusionHeaders(headers_dict)
    
    for i in range(0, len(allStudents)):
        for header in exclusion_headers:
            parameter = headers_dict[header].parameter
            if allStudents[i].attributes[header] == parameter:
                student_name = allStudents[i].attributes[name]
                excludeable.append(student_name)
    return excludeable
        
    

def runner():
    # headers stuff
    dataframe = excel_to_df("../data/h1.xlsx") # excel_to_df("../data/mock_headers.xlsx")
    values = read_excel_file(dataframe)
    headers_dict = convertDataframeValuesToHeaders(values)
    #print(headers_dict)
    #print("===============================")

    # data stuff
    data_values = read_excel_file(excel_to_generic_df("../data/d1.xlsx")) # read_excel_file(excel_to_generic_df("../data/simple_data.xlsx"))
    column_dict = getHeadersIndices(data_values)
    min_hours = 3
    #print(column_dict)
    #print("===============================")
    parser_dict = comparison.getParserDict()
    allStudents = createStudents(headers_dict, column_dict, parser_dict, data_values[1:])
    allStudents = removeUnnamedStudents(headers_dict, allStudents)
    #for student in allStudents: print(str(student) + '\n')
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

# Makes the pairings given the headers dataframe, the student data dataframe, and the minimum number of hours needed for legality
def makePairings(headers_dataframe, data_dataframe, min_hours):
    final_dict = dict()

    try:
        # extracting data from uploaded files
        headers_values = headers_dataframe.values
        headers_dict = convertDataframeValuesToHeaders(headers_values)
        data_values = data_dataframe.values
        column_dict = getHeadersIndices(data_values)
        parser_dict = comparison.getParserDict()
        allStudents = createStudents(headers_dict, column_dict, parser_dict, data_values[1:])
        allStudents = removeUnnamedStudents(headers_dict, allStudents)

        # Makes the legal pairings and converts to JSON for returning to frontend
        matrix, legal, allnames, legal_dict = compareAllStudents(allStudents, headers_dict, min_hours)
        json_dict = legal_dict_to_json_dict(legal_dict, allnames)

        # Makes the optimal pairings by excluding students, pairing all students, and then finding unpaired students
        students_to_exclude = exclude_students(allnames, allStudents, headers_dict)
        paiarable_students = allnames.copy()
        paiarable_students = [x for x in paiarable_students if x not in students_to_exclude]
        optimal, unpaired = make_all_pairings(matrix, paiarable_students, legal_dict, headers_dict)
        unpaired.extend(students_to_exclude)

        # Formats final data for sending to frontend
        
        final_dict["optimal"] = list()

        for pair in optimal:
            p1, p2 = pair
            current_dict = dict()
            current_dict["person1"] = p1
            current_dict["person2"] = p2
            final_dict["optimal"].append(current_dict)

        final_dict["unpaired"] = unpaired
        final_dict["matrix"] = json_dict
        filename = data_to_excel_file(final_dict)
        final_dict["success"] = True
        final_dict["message"] = "Successfully created pairs!"
        final_dict["filename"] = filename
        print(filename)
        

    except Exception as err:
        final_dict["success"] = False
        final_dict["message"] = str(err)
         
    return final_dict

def generateRandomName(length = 8):
    import random
    import string
    return(''.join(random.choices(string.ascii_lowercase, k=length)))

def data_to_excel_file(final_dict):
    df_optimal = pd.DataFrame.from_dict(final_dict["optimal"])
    df_optimal.name = "Optimal Pairings"
    # print(df_optimal)

    df_unpaired = pd.DataFrame.from_dict(final_dict["unpaired"])
    df_unpaired.name = "Unpaired Students"
    # print(df_unpaired)

    df_matrix = pd.DataFrame.from_dict(final_dict["matrix"])
    df_matrix.name = "Students Matrix"
    # print(df_matrix)

    folder = UPLOAD_FOLDER + "/"
    name = generateRandomName(8) + ".xlsx"
    filename = folder + name
    
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    workbook = writer.book
    worksheet = workbook.add_worksheet('SCIJ Student Pairings')
    writer.sheets['SCIJ Student Pairings'] = worksheet
    worksheet.write_string(0, 0, df_optimal.name)

    df_optimal.to_excel(writer, sheet_name='SCIJ Student Pairings', startrow=1, startcol=0)
    worksheet.write_string(df_optimal.shape[0] + 4, 0, df_unpaired.name)
    # print("optimal shape 0", df_optimal.shape[0])
    df_unpaired.to_excel(writer, sheet_name='SCIJ Student Pairings', startrow=df_optimal.shape[0] + 5, startcol=0)
    # print("unpaired shape 0", df_unpaired.shape[0])
    # print("matrix shape 0", df_matrix.shape[0])
    worksheet.write_string(df_optimal.shape[0] + 4 + df_unpaired.shape[0] + 4, 0, df_matrix.name)
    df_matrix.to_excel(writer, sheet_name='SCIJ Student Pairings', startrow=df_matrix.shape[0] + 5, startcol=0)
    
    # Conditional Formatting of Colors (Green = Legal, Gray = Self, Red = Illegal)
    # This is the row number of the upper leftmost corner cell of the matrix (used for specifying cell range for conditional formatting).
    # The column number would just be 1 as it is Column 2 in the spreadsheet.
    row_upper_left_corner = df_optimal.shape[0] + 4 + df_unpaired.shape[0] + 4 + 2
    # This is the row number of the lower rightmost corner cell of the matrix (used for specifying cell range for conditional formatting).
    row_lower_right_corner = row_upper_left_corner + len(df_matrix) - 1
    col_lower_right_corner = len(df_matrix.columns)

    # First parameter – in order: row number of the upper leftmost corner cell, its column number, row number of the lower rightmost corner cell, its column number
    # Conditional Formatting (Green = Legal)
    green_format = workbook.add_format({'bg_color': '#C6EFCE',
                                        'font_color': '#006100'})
    worksheet.conditional_format(row_upper_left_corner, 1, row_lower_right_corner, col_lower_right_corner, {'type': 'cell',
                                                                                                            'criteria': '=',
                                                                                                            'value': 1,
                                                                                                            'format': green_format})
    
    # Conditional Formatting (Gray = Self)
    gray_format = workbook.add_format({'bg_color': '#D3D3D3',
                                        'font_color': '#3D3D3D'})
    worksheet.conditional_format(row_upper_left_corner, 1, row_lower_right_corner, col_lower_right_corner, {'type': 'cell',
                                                                                                            'criteria': '=',
                                                                                                            'value': 0,
                                                                                                            'format': gray_format})

    # Conditional Formatting (Red = Illegal)
    red_format = workbook.add_format({'bg_color': '#FFC7CE',
                                        'font_color': '#9C0006'})
    worksheet.conditional_format(row_upper_left_corner, 1, row_lower_right_corner, col_lower_right_corner, {'type': 'cell',
                                                                                                            'criteria': '=',
                                                                                                            'value': -1,
                                                                                                            'format': red_format})

    worksheet.set_column(0, col_lower_right_corner, 20)

    writer.save()

    # df = pd.DataFrame.from_dict(final_dict, orient='index')
    # df = df.transpose()

    # df = (df.T)
    # print(df)
    # df = pd.DataFrame({'Name': ['A', 'B', 'C', 'D'],
    #                'Age': [10, 0, 30, 50]})

    # writer = pd.ExcelWriter('demo.xlsx', engine='xlsxwriter')
    # df.to_excel(writer, sheet_name='Sheet1', index=False)
    # writer.save()
    return name
    
if __name__ == "__main__":
    final_dict = runner()
    #data_to_excel_file(final_dict)
    print(final_dict)
