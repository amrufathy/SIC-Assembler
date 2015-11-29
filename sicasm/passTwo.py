
######################### PASS TWO #########################

'''
pass two does real translation and assembling
and writes both object and assembly listing files
'''

from passOne import SymTable
from utilities import opTable
from passOne import linesListWithData

endRecord = False
hasError = False

'''
assembles each line of instructions and
produces its object code
'''
def assemble():
    global linesListWithData
    lines = linesListWithData

    for line in lines:
        # skip if comment
        if (line[0] == "."):
            continue

        # initialize object code
        objCode = None

        ## get operation code
        opCode = None

        directive = line[2].strip().lower()
        # start has no object code (null)
        if directive == "start":
            opCode = line[0].strip().lower()
            line.append(objCode)
            # go to next line of instructions
            continue
        # normal directive
        else:
            # make sure operation is present in operations table
            if directive in opTable:
                opCode = opTable[directive]


        ## get address
        if opCode is not None:
            operand = line[3].strip().lower()
            index = operand.find(",")

            # indexing is used
            if index != -1:
                temp = operand[:index]
                address = SymTable[temp]
            # no indexing
            else:
                address = SymTable[operand]

            # if indexing is used add value of 'x' bit to address
            if ",x" in operand:
                address = int(address, 16)
                address += int("8000", 16)
                address = hex(address)[2:]

            # calculate object code
            objCode = opCode + address

        ## handle 'WORD' & 'BYTE'
        if opCode is None:
            if directive == "word":
                # get value and change it to hexadecimal
                operand = hex(int(line[3].strip().lower()))[2:]
                # make sure value is 6 hexadecimal digits (1 word)
                operand = fixHexString(operand, 6)
                # calculate object code
                objCode = operand

            elif directive == "byte":
                operand = line[3].strip().lower()
                # normal string
                if operand[0] == 'c':
                    operand = operand[2:-1]
                    address = ""
                    # change string characters to their ascii hexadecimal values
                    for c in operand:
                        address += str(hex(ord(c))[2:])
                # hexadecimal string
                elif operand[0] == 'x':
                    operand = operand[2:-1]
                    address = operand

                # calculate object code
                objCode = address

        ## add object code to line
        line.append(objCode)

    linesListWithData = lines

    writeObjFile()
    writeListFile()

'''
makes sure that num has a length of limit
'''
def fixHexString(num, limit):
    zero = "0"
    count = limit - len(num)
    num = (zero * count) + num
    return num


'''
writes formatted object code to file
'''
def writeObjFile():
    file = open("OBJFILE", "w+")

    lines = linesListWithData

    # write header record
    progName = lines[0][1][:-2]
    startAdrs = lines[0][0]
    if len(startAdrs) < 6:
        startAdrs = fixHexString(startAdrs, 6)

    # calculate length of program by finding the difference between last and first address
    lengthOfProg = hex(int(lines[-1][0], 16) - int(lines[0][0], 16))[2:]
    if len(lengthOfProg) < 6:
        lengthOfProg = fixHexString(lengthOfProg, 6)

    headerStr = "H" + progName + startAdrs + lengthOfProg + "\n"

    file.write(headerStr)

    # write text records
    writeTextRecord(file, lines[1:])

    # write end record
    endRecordStr = "E" + startAdrs
    file.write(endRecordStr)
    file.close()

'''
recursive method that writes text records
'''
def writeTextRecord(file, lines):
    # finished writing records
    if lines == []:
        # set global boolean and return
        global endRecord
        endRecord = True
        return

    startAdrs = lines[0][0]
    if len(startAdrs) < 6:
        startAdrs = fixHexString(startAdrs, 6)

    # start writing new text record
    textRecordStr = "T" + startAdrs

    # string to accumulate object code of the record in
    objCodeStr = ""

    # loop on each line of instructions
    for i in range(0, (len(lines))):

        currentObjCode = lines[i][4]
        # before last line
        if i == (len(lines) - 1):
            nextObjCode = None
        else:
            nextObjCode = lines[i + 1][4]

        # current line doesn't have object code
        # must terminate and start a new record
        if currentObjCode is None:
            # get length of record
            length = hex(len(objCodeStr) / 2)[2:]
            if len(length) < 2:
                length = fixHexString(length, 2)
            # get object code of record
            textRecordStr += length + objCodeStr + "\n"
            file.write(textRecordStr)
            # terminate and start a new record
            writeTextRecord(file, lines[i + 1:])

        # return when finished writing
        if endRecord:
            return

        # accumulate object code to terminate in next loop
        if nextObjCode is None:
            objCodeStr += currentObjCode
            continue

        if currentObjCode is not None:
            objCodeStr += currentObjCode

        # length of record bigger than 60
        # must terminate and start a new record
        if len(objCodeStr) + len(nextObjCode) > 60:
            # get length of record
            length = hex(len(objCodeStr) / 2)[2:]
            if len(length) < 2:
                length = fixHexString(length, 2)
            # get object code of record
            textRecordStr += length + objCodeStr + "\n"
            file.write(textRecordStr)
            # terminate and start a new record
            writeTextRecord(file, lines[i + 1:])

'''
writes list file
'''
def writeListFile():
    file = open("LISFILE", "w+")

    lines = linesListWithData

    for line in lines:

        # if comment write as is
        if line[0] == ".":
            file.write(line + "\n")
            continue

        # get parts of line
        address, label, directive, operand, objCode = line

        # set object code spaces
        if objCode is None:
            objCode = "      "

        # increase length to 6 digits
        if len(objCode) < 6:
            diff = 6 - len(objCode)
            objCode = objCode + (" " * diff)

        # print multi-line object code
        if len(objCode) > 6:
            length = len(objCode)
            temp = objCode
            temp = temp[0:6]
            # print first normal line
            lineStr = address + " " + temp + " " + label + " " + directive + " " + operand + "\n"
            file.write(lineStr)
            # loop on remaining object code with limit of 6 as step
            for i in range(6, length, 6):
                # set space before string
                str = (" " * len(address)) + " "
                temp = objCode
                # if object code has more than 6 remaining digits print only 6
                if i + 6 < len(objCode):
                    str += temp[i:i + 6] + "\n"
                # if object code has less than 6 remaining digits print the remaining
                else:
                    diff = (i + 6) - len(objCode)
                    str += temp[i:i + (6 - diff)] + "\n"
                file.write(str)

        # object code has length of 6
        else:
            lineStr = address + " " + objCode + " " + label + " " + directive + " " + operand + "\n"
            file.write(lineStr)

    file.close()

'''
still not done
'''
def validateError():
    errorsTable = {}

    lines = linesListWithData

    if lines[0][2].strip().lower() != "start":
        errorsTable[lines[0][0]] = ["statement should not precede start statement",
                                    "missing or misplaced start statement"]

    for line in lines:
        address, label, directive, operand, objCode = line
        errorList = []
        if (directive == "") or (directive is None):
            errorList.append("missing operation code")
        elif directive not in opTable.keys():
            errorList.append("unrecognized operation code")
            errorList.append("illegal operation code format")
        if moreThanOnce(label):
            errorList.append("duplicate label definition")
        if " " in operand.rstrip() or operand not in SymTable.keys:
            errorList.append("missing or misplaced operand in instruction")
            errorList.append("illegal operand field")

        errorsTable[address] = errorList

    if lines[-1][2].strip().lower() != "end":
        errorsTable[lines[-1][0]] = ["statement should not follow end statement", "missing or misplaced end statement"]

'''
still not done
'''
def moreThanOnce(symbol):
    counter = 0
    lines = linesListWithData
    for line in lines:
        if line[1].strip().lower() == symbol:
            counter += 1

    return counter > 1
