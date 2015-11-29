######################### PASS TWO #########################

'''
pass two does real translation and assembling
and writes both object and assembly listing files
'''
import util

endRecord = False
hasError = False

def assemble():
    """
    assembles each line of instructions and
    produces its object code
    """

    lines = util.linesListWithData

    # check for errors first before generating object code
    validateErrors()

    for line in lines:
        # skip if comment
        if (line[0] == "."):
            continue

        # skip if line has errors
        address = line[0].rstrip()
        if (len(util.errorsTable[address]) > 0):
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
            if directive in util.opTable:
                opCode = util.opTable[directive]

        ## get address
        if opCode is not None:
            operand = line[3].strip().lower()
            index = operand.find(",")

            # indexing is used
            if index != -1:
                temp = operand[:index]
                address = util.symTable[temp]
            # no indexing
            else:
                address = util.symTable[operand]

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

    util.linesListWithData = lines

    writeObjFile()
    writeListFile()

def fixHexString(num, limit):
    """
    makes sure that num has a length of limit
    """

    zero = "0"
    count = limit - len(num)
    num = (zero * count) + num
    return num

def writeObjFile():
    """
    writes formatted object code to file
    """

    file = open("OBJFILE", "w+")

    lines = util.linesListWithData

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

    # check if program has errors no text records are generated
    global hasError
    if hasError:
        return

    # write text records
    writeTextRecord(file, lines[1:])

    # write end record
    endRecordStr = "E" + startAdrs
    file.write(endRecordStr)
    file.close()

def writeTextRecord(file, lines):
    """
    recursive method that writes text records
    """

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

def writeListFile():
    """
    writes list file
    """

    file = open("LISFILE", "w+")

    lines = util.linesListWithData

    for line in lines:
        # if comment write as is
        if line[0] == ".":
            file.write(line + "\n")
            continue

        # if line has errors print line as is with its errors
        address = line[0]
        if (len(util.errorsTable[address]) > 0):
            address, label, directive, operand = line
            lineStr = address + (8 * " ") + label + " " + directive + " " + operand + "\n"
            file.write(lineStr)
            for msg in util.errorsTable[address]:
                file.write("\t\t******* " + msg + "\n")
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

def validateErrors():
    """
    still not done
    """

    global hasError

    lines = util.linesListWithData

    # check if anything before "start"
    if lines[0][2].strip().lower() != "start":
        util.errorsTable[lines[0][0]] = ["statement should not precede start statement",
                                         "missing or misplaced start statement"]
        hasError = True

    for line in lines:
        # skip if comment
        if line[0] == ".":
            continue

        address, label, directive, operand = line
        errorList = []

        ## check directive errors
        directive = directive.rstrip().lower()
        # directive is empty
        if (directive == "") or (directive is None):
            errorList.append("missing operation code")
        # pass if directive is a reserved operation with no hexadecimal code
        elif (directive in ["start", "byte", "word", "resw", "resb", "end"]):
            pass
        # directive isn't in operations table
        elif directive not in util.opTable.keys():
            errorList.append("unrecognized operation code")
            errorList.append("illegal operation code format")

        ## check label errors
        if (label.rstrip() != ""):
            # duplicate label found
            if moreThanOnce(label):
                errorList.append("duplicate label definition")
        # label contains spaces
        if (" " in label.rstrip()):
            errorList.append("illegal format in label field")
        # label should be defined but not
        elif (directive in ["byte", "word", "resw", "resb"]) and (label.rstrip() == ""):
            errorList.append("illegal format in label field")

        ## check operand errors
        operand = operand.rstrip().lower()
        index = operand.find(",")
        if index != -1:
            operand = operand[:index]
        # pass if operand is string
        if (operand[:2] in ["c'", "x'"]) and (operand[-1] == '\'') and (directive == "byte"):
            pass
        # operand should contain a number
        elif (not operand[0].isdigit()) and (directive in ["word", "resw", "resb"]):
            errorList.append("illegal operand field")
        # operand contains spaces or not found in symbol table or should not be a number
        elif ((" " in operand) or (operand not in util.symTable.keys()) or (operand[0].isdigit())) and \
                (directive not in ["word", "resw", "resb", "start", "end"]):
            errorList.append("missing or misplaced operand in instruction")
            errorList.append("illegal operand field")

        # check if line has errors
        if (len(errorList) > 0):
            # set global variable
            hasError = True

        util.errorsTable[address] = errorList

    # check if anything after "end"
    if lines[-1][2].strip().lower() != "end":
        util.errorsTable[lines[-1][0]] = ["statement should not follow end statement",
                                          "missing or misplaced end statement"]
        hasError = True

def moreThanOnce(symbol):
    """
    checks if label is present
    more than once in code
    """

    counter = 0
    lines = util.linesListWithData
    for line in lines:
        if line[1].strip().lower() == symbol.strip().lower():
            counter += 1

    return counter > 1
