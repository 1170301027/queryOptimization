
class Tag():
    """
    Tag类用于记录标记
    """

    AND = '<AND>'
    KEYWORD = '<keyword>' # SQL keyword
    SELECT = '<select>'
    PROJECTION = '<projection>'
    AVG = '<avg>'
    JOIN = '<binaryOperator>'

    SELLIST = '<selList>'
    FROMLIST = '<fromList>'


    LOGICALOPERATOR = '<logicalOperator>' # join condition e.g :<>=
    PROPERTY = '<id>' # property in table(column), or name of table
    PATTERN = '<pattern>' # value of some property, with "'"
    DELIMITER = '<delimiter>' # e.g : ()[]
    LRP = '<LRP>'
    RRP = '<RRP>'
    SLP = '<SLP>'
    SRP = '<SRP>'
    COMMA = '<COMMA>'

    BINARYOPERATOR = '<binaryOperator>'
    EQ = '='
    LT = '<'
    GT = '>'
    LE = '<='
    GE = '>='

    END = '$'
