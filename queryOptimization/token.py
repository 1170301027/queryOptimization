
class Token():
    """
    Token类用于词法单元
    """
    def __init__(self,attribute,label):
        self.label = label
        self.attribute = attribute

    def __eq__(self, other):
        if not isinstance(other,Token):
            return False
        if self.label == other.label\
                and self.attribute == self.attribute:
            return True

    def __str__(self):
        return self.label
