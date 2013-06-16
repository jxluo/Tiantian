import sys


class FlagType:
    (INT, FLOAT, STRING, BOOLEAN, ENUM) = range(0, 5)

    @staticmethod
    def check(type_):
        if type_ != FlagType.INT and\
            type_ != FlagType.FLOAT and\
            type_ != FlagType.STRING and\
            type_ != FlagType.BOOLEAN and\
            type_ != FlagType.ENUM:
            __handleException('%s is not a acceptable type.' % str(type_))

    @staticmethod
    def toString(type_):
        if type_ == FlagType.INT:
            return 'integer'
        elif type_ == FlagType.FLOAT:
            return 'float'
        elif type_ == FlagType.STRING:
            return 'string'
        elif type_ == FlagType.BOOLEAN:
            return 'boolean'
        elif type_ == FlagType.ENUM:
            return 'enum'


def processArguments():
    __process(sys.argv[1:])
    if isFlagSet('help'):
        __printHelpMessage()

def defineFlag(name, type_, default,
        description=None, alias=None, possibleValues=None):
    """Define a flag. 

    Arguments:
        type_ {FlagType} The type of the flag.
        name {string} The name of the flag.
        default {string|float|int|boolean} The default vale.
        alias {string} The alias, normally the short name of the flag.
        description {string} The description of the flag.
        possibleValues {list<string>} A list of possible string value.

    Notice:
        A flag can not be defined more than one time.
        The flag should be defined before {@code processArguments} called.
    """
    global __flagMap
    if __flagMap.get(name):
        __handleException('Redefined flag: ' + name)
    if alias and __flagMap.get(alias):
        __handleException('Redefined flag: ' + alias)

    flag = __Flag()
    flag.flagType = type_
    flag.name = name
    flag.value = flag.defaultValue = default
    flag.description = description
    flag.alias = alias
    if type_ == FlagType.ENUM and not possibleValues:
        __handleException('Flag type is ENUM but lack of possible values.')
    flag.possibleValues = possibleValues

    __flagMap[name] = flag
    if alias:
        __flagMap[alias] = flag
    

def setFlag(name, value):
    """Set the flag's value. The flag only can be set after defined."""
    global __flagMap
    flag = __flagMap.get(name)
    if not flag:
        __handleException('Set flag be before define: ' + name)
    __typeCheck(value, flag)
    flag.value = value

def getFlag(name):
    global __flagMap
    flag = __flagMap.get(name)
    if not flag:
        return None
    return flag.value

def isFlagSet(name):
    global __flagMap
    flag = __flagMap.get(name)
    if not flag:
        return None
    return flag.explicitlySet

############# Private stuff ##############

__flagMap = {} # A map mapping name or alias to flag element.

def __clearFlags():
    global __flagMap
    __flagMap.clear()

class __Flag:

    flagType = None # The flag type, see {@code FlagType}
    name = None # The name of the flag, a string.
    defaultValue = None # The default value of the flag.
    description = None # The description of the flag.
    alias = None # The alias of the flag, normally a short name for it.
    value = None # The current value of the flag.
    possibleValues = None # A list of possible string, if the type is ENUM.
    explicitlySet = False # If the flag is explicitly set by command.

    def getHelpString(self):
        helpString = '%s\t{%s:%s}\t%s' 
        nameString = self.name
        if self.alias:
            nameString += ', %s' % self.alias
        typeString = FlagType.toString(self.flagType)
        if self.flagType == FlagType.ENUM:
            typeString += str(self.possibleValues)
        defaultValueString = str(self.defaultValue)
        helpString = helpString %\
            (nameString, typeString, defaultValueString, str(self.description))
        return helpString
   
    @staticmethod
    def getHelpHeader():
        return '==== name\t{type:value}\tdescription ===='

def __handleException(info):
    errorHandle = getFlag('flag_error_handle')
    if errorHandle == 'exception':
        raise Exception(info)
    elif errorHandle == 'exit':
        print info
        sys.exit(1)
    else:
        print 'Shit happen: ' + info
        sys.exit(1)


def __process(commands):
    """Process the commands"""
    for command in commands:
        if command.find('--') != 0:
            __handleException('Invalid command: ' + command)
        command = command[2:]
        pos = command.find('=')
        if pos == -1:
            # '--some_flag' is consider as:
            # name: 'some_flag', value: None
            name = command
            value = None
        else:
            # '--some_flag=' is consider as:
            # name: 'some_flag', value: ''
            name = command[:pos]
            value = command[pos+1:]
        if not name:
            __handleException('Invalid command: --' + command)
        __processSingleCommand(name, value)


def __processSingleCommand(name, valueString):
    global __flagMap
    flag = __flagMap.get(name)
    if not flag:
        __handleException('There is no flag named ' + name + '!')

    # support for boolean flag command like: --run_in_debug_mode
    if valueString == None:
        if flag.flagType != FlagType.BOOLEAN:
            __handleException('Flag have no value: ' + name)
        else:
            flag.value = True
            flag.explicitlySet = True
            return

    # Convert the value
    value = __convert(valueString, flag.flagType)

    # Check for enum flag type.
    if flag.flagType == FlagType.ENUM:
        match = False
        for possible in flag.possibleValues:
            if possible == value:
                match = True
                break
        if not match:
            __handleException("The enum flag value '%s' does not match %s." %\
                (value, str(flag.possibleValues)))
    # Set the flag.
    flag.value = value
    flag.explicitlySet = True


def __convert(valueString, type_):
    """Convert a string to value according to type_."""
    assert type(valueString) == str
    if type_ == FlagType.STRING or type_ == FlagType.ENUM:
        return valueString
    try:
        if type_ == FlagType.INT:
            value = int(valueString)
        if type_ == FlagType.FLOAT:
            value = float(valueString)
        if type_ == FlagType.BOOLEAN:
            if valueString == '0' or\
                valueString == 'false' or\
                valueString == 'False':
                value = False
            elif valueString == '1' or\
                valueString == 'true' or\
                valueString == 'True':
                value = True
            else:
                __handleException("'%s' is not a boolean." % valueString)
    except Exception, e:
        __handleException("'%s' is not a %s." %\
            (valueString, FlagType.toString(type_)))
    return value

def __typeCheck(value, flag):
    """Check whther the value is the same type as type_.
    Otherwise handle error.
    """
    type_ = flag.flagType
    fine = True
    if type_ == FlagType.INT:
        fine = (type(value) == int or type(value) == long)
    if type_ == FlagType.FLOAT:
        fine = type(value) == float
    if type_ == FlagType.BOOLEAN:
        fine = type(value) == bool
    if type_ == FlagType.STRING:
        fine = type(value) == str
    if type_ == FlagType.ENUM:
        fine = (type(value) == str and value in flag.possibleValues)
    if not fine:
        __handleException("%s is not a %s." %\
            (str(value), FlagType.toString(type_)))

def __printHelpMessage():
    global __flagMap
    print __Flag.getHelpHeader()
    pairs = __flagMap.items()
    flags = []
    for pair in pairs:
        if pair[0] != pair[1].alias and\
            pair[0] != 'help' and\
            pair[0] != 'flag_error_handle':
            flags.append(pair[1])
    flags.sort(key=lambda flag: flag.name)
    for flag in flags:
        print flag.getHelpString()
    sys.exit(0)

def __defineBasicFlag():
    defineFlag(name='help', type_=FlagType.BOOLEAN, default=False,\
        description='Whether print help message.')
    defineFlag(name='flag_error_handle', type_=FlagType.ENUM, default='exception',\
        possibleValues=['exception', 'exit'],\
        description="""The way to handle flag related error.
        \t'exception': raise a exception
        \t'exit': exit runing""")

__defineBasicFlag()
