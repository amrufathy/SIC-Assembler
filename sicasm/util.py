'''
operations table
stores supported SIC operations with their hexadecimal representation
'''

opTable = {
    "add": "18",
    "and": "40",
    "comp": "28",
    "div": "24",
    "j": "3c",
    "jeq": "30",
    "jgt": "34",
    "jlt": "38",
    "jsub": "48",
    "lda": "00",
    "ldch": "50",
    "ldl": "08",
    "ldx": "04",
    "mul": "20",
    "or": "44",
    "rd": "d8",
    "rsub": "4c",
    "sta": "0c",
    "stch": "54",
    "stl": "14",
    "stx": "10",
    "sub": "1c",
    "td": "e0",
    "tix": "2c",
    "wd": "dc"
}

'''
symbol table
contains each label found in code
with its corresponding address
'''

symTable = {}

'''
list that contains formatted instruction lines
'''

linesListWithData = []

'''
errors table
contains each address with its errors if any
'''

errorsTable = {}