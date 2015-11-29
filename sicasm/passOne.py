
######################### PASS ONE #########################

'''
pass one assigns address to each instruction
and constructs a symbol table
'''

linesListWithData = []
SymTable = {}

'''
this function splits an instruction string and returns it
as list of strings
input: "PROG    START    1000"
return: ["PROG", "START", "1000"]
'''
def stringInstructionsToLists(instruction):
    return [instruction[0:8], instruction[9:17], instruction[17:36]]

'''
this function reads the srcfile, saves all the code
as lists of string using the function 'stringInstructionsToLists'
then calls 'assignAddresses'
'''
def readFromFile():
    file = open("SRCFILE", "r+")

    #get line by line
    lines = [line.rstrip('\n') for line in file]

    linesList = []

    for line in lines:
        #if line is comment put as is
        if line[0] == ".":
            linesList.append(line)
        #process normal line
        else:
            linesList.append(stringInstructionsToLists(line))

    assignAddresses(linesList)

'''
this function assigns an address to each instruction
'''
def assignAddresses(linesList):

    #get start address as hex number
    startingAddress = int(linesList[0][2], 16)
    currentAddress = startingAddress

    for line in linesList:
        #skip if comment
        if line[0] == ".":
            continue

        #if "start" put address as is
        if line[1].strip().lower() == "start":
            line.insert(0, hex(currentAddress)[2:])
        else:
            line.insert(0, hex(currentAddress)[2:])

            #calculate reserved bytes and add to address
            if line[2].strip().lower() == "resb":
                currentAddress += int(line[3].strip())
            #calculate reserved words(each of length 3) and add to address
            elif line[2].strip().lower() == "resw":
                currentAddress += 3 * int(line[3].strip())
            #calculate length of string and add length to address
            elif line[2].strip().lower() == "byte":
                operand = line[3].strip().lower()[2:-1]
                currentAddress += len(operand)
            #normal address calculation
            else:
                currentAddress += 3

    #update global list to be used later
    global linesListWithData
    linesListWithData = linesList

    makeSymTable()


def makeSymTable():
    global SymTable
    lines = linesListWithData

    for line in lines:
        address = line[0]
        label = line[1].strip().lower()
        #if symbol not empty and not already present in symbol table
        #then add
        if (label != '') and (label not in SymTable.keys):
            SymTable[label] = address
