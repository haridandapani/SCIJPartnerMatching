import pandas as pd

# Takes a string that might have a number in it and extracts the first number, as separated by spaces
def processNumber(numberString):
    numberString = str(numberString)
    if pd.isna(numberString):
        return -1
    for s in numberString.split():
        if s.isdigit():
            return int(s)

    return -1

# Given a name, returns that same name
def generateName(name):
    if pd.isna(name):
        return ""
    return name

# Given a single category, returns the value of that category for comparison
def generateCategoryFromCategoryOne(category):
    if pd.isna(category):
        return ""
    return category

# Given a list of hour-long timeslots separated by ; , returns the distinct hours slots
def generateListFromHours(hours):
    if pd.isna(hours):
        return list()
    if hours != hours:
        return list()
    semicolonsplit = hours.split(";")
    commassplit = hours.split(", ")
    if len(semicolonsplit) > len(commassplit):
        return semicolonsplit
    else:
        return commassplit

# Compares the amount of overlap between two sets of hours
def compareHours(hours_1, hours_2):
    def intersection(lst1, lst2):
        lst3 = [value for value in lst1 if value in lst2]
        return lst3
    overlap = intersection(hours_1, hours_2)
    return len(overlap)

# Returns a comparator that compares to single categories
# If similar is true, then we return a comparator checking for sameness. Otherwise, we return a comparator checking for difference.
def compareCategoryOne(similar : bool):
    if similar:
        return lambda cat_1, cat_2: cat_1 == cat_2
    else:
        return lambda cat_1, cat_2: cat_1 != cat_2

# Comparator for two numbers
def compareNumbers(num1, num2):
    return abs(num1 - num2)

# Dictionary that tells us how to extract data from all of the different possible header types
def getParserDict():
    parser_dict = {"hours": generateListFromHours, "similar_category_one": generateCategoryFromCategoryOne, "name": generateName,
                   "different_category_one": generateCategoryFromCategoryOne, "similar_number": processNumber, "different_number": processNumber,
                   "exclude_if": generateName}
    return parser_dict

# Dictionary of comparators for all comparable header types
def getComparators():
    compare_dict = {"hours": compareHours, "similar_category_one": compareCategoryOne(True), "different_category_one": compareCategoryOne(False),
                    "similar_number": compareNumbers, "different_number": compareNumbers}
    return compare_dict

def runner():
    hours_1 = "10 AM - 11 AM;11 AM - 12 PM;12 PM - 1 PM"
    hours_2 = "11 AM - 12 PM;12 PM - 1 PM;2 PM - 3 PM;3 PM - 4 PM"
    parser_dict = getParserDict()
    comp_hours_1 = parser_dict["hours"](hours_1)
    comp_hours_2 = parser_dict["hours"](hours_2)
    comparison = compareHours(comp_hours_1, comp_hours_2)
    print(comparison)


if __name__ == "__main__":
    runner()
