def generateName(name):
    return name

def generateCategoryFromCategoryOne(category):
    return category

def generateListFromHours(hours):
    return hours.split(";")

def compareHours(hours_1, hours_2):
    def intersection(lst1, lst2):
        lst3 = [value for value in lst1 if value in lst2]
        return lst3
    overlap = intersection(hours_1, hours_2)
    return len(overlap)

def compareCategoryOne(cat_1, cat_2):
    return cat_1 == cat_2

def getParserDict():
    parser_dict = {"hours": generateListFromHours, "category_one": generateCategoryFromCategoryOne, "name": generateName}
    return parser_dict

def getComparators():
    compare_dict = {"hours": compareHours, "category_one": compareCategoryOne}
    return compare_dict

def runner():
    hours_1 = "10 AM - 11 AM;11 AM - 12 PM;12 PM - 1 PM"
    hours_2 = "11 AM - 12 PM;12 PM - 1 PM;2 PM - 3 PM;3 PM - 4 PM"
    parser_dict = getParserDict()
    comp_hours_1 = parser_dict["hours"](hours_1)
    comp_hours_2 = parser_dict["hours"](hours_2)
    comparison = compareHours(comp_hours_1, comp_hours_2)
    print(comparison)
