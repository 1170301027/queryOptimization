from queryOptimization.tag import Tag


class CFG():
    """
    CFG类用于构造文法
    """
    def __init__(self):
        self.productions = []
        self.start = Nonterminal('<query>')
        self.construct()

    def construct(self):
        '''
        <query> -> <sql>
        <sql> -> SELECT [ <where> ] <fromlist>
        <where> -> <condition> | <condition> & <condition>
        <condition> -> <id> <logicalOperator> <patten>
        <condition> -> <id> | <id>,<id>
        <fromlist> -> ( <id> JOIN <id> ) | ( <id> JOIN <sql> )

        <sql> -> PROJECTION [ <where> ] ( <sql> )

        :return:
        '''
        def set(production):
            self.productions.append(production)

        set(Production(Nonterminal('<query>'),
                       [Nonterminal('<SQL>')]))

        set(Production(Nonterminal('<SQL>'),
                       [Terminal(Tag.SELECT,'SELECT'),Terminal(Tag.LRP,'['),Nonterminal('<where>'),Terminal(Tag.LRP,']')]))
        set(Production(Nonterminal('<SQL>'),
                       [Terminal(Tag.PROJECTION,'PROJECTION'),Terminal(Tag.LRP,'['),
                        Nonterminal('<where>'),Terminal(Tag.LRP,']'),Terminal(Tag.SLP,'('),Nonterminal('<SQL>'),Terminal(Tag.SRP,')')]))

        set(Production(Nonterminal('<where>'),
                       [Nonterminal('<condition>')]))
        set(Production(Nonterminal('<where>'),
                       [Nonterminal('<condition>'),Terminal(Tag.AND,'&'),Nonterminal('<condition>')]))

        set(Production(Nonterminal('<condition>'),
                       [Terminal(Tag.PROPERTY,'<id>'),Nonterminal('<logicalOperator>'),Terminal(Tag.PATTERN,'<pattern>')]))
        set(Production(Nonterminal('<condition>'),
                       [Terminal(Tag.PROPERTY,'<id>')]))
        set(Production(Nonterminal('<condition>'),
                       [Terminal(Tag.PROPERTY,'<id>'),Terminal(Tag.COMMA,','),Terminal(Tag.PROPERTY,'<id>')]))
        for i in [[Terminal(Tag.EQ,Tag.EQ)],[Terminal(Tag.LT,Tag.LT)],[Terminal(Tag.GT,Tag.GT)],[Terminal(Tag.LE,Tag.LE)],[Terminal(Tag.GE,Tag.GE)]]:
            set(Production(Nonterminal('<logicalOperator>'),i))

        set(Production(Nonterminal('fromlist'),
                       [Terminal(Tag.SLP,'('),Terminal(Tag.PROPERTY,'<id>'),Terminal(Tag.JOIN,'JOIN'),
                        Terminal(Tag.PROPERTY,'<id>'),Terminal(Tag.SRP,')')]))
        set(Production(Nonterminal('formlist'),
                       [Terminal(Tag.SLP,'('),Terminal(Tag.PROPERTY,'<id>'),Terminal(Tag.JOIN,'JOIN'),
                        Nonterminal('<SQL>'),Terminal(Tag.SRP,')')]))

    def getProductions(self,header):
        if not isinstance(header,Nonterminal):
            print(str(header)+' 参数错误')
            raise None
        result = []
        for production in self.productions:
            if header == production.header:
                result.append(production)
        return result

class Production():
    """
    Production类用于产生式
    """
    def __init__(self,header,body):
        self.header = header
        self.body = body

    def __eq__(self, other):
        if not isinstance(other,Production):
            return False
        if self.header == other.header and self.body == other.body:
            return True
        return False

    def __str__(self):
        pstr = ''
        pstr += str(self.header) + " -> "
        for c in self.body:
            pstr += str(c) + " "
        pstr += '\n'
        return pstr

class Terminal:
    '''
    终结符
    '''

    def __init__(self, character, show_str):
        # 终结符名称
        self.character = character
        self.show_str = show_str

    def __str__(self):
        return self.show_str

    def __hash__(self):
        return self.character

    def __eq__(self, other):
        if not isinstance(other, Terminal):
            return False
        return self.character == other.character


class Nonterminal:
    '''
    非终结符
    '''

    def __init__(self, character):
        # 非终结符名称
        self.character = character

    def __str__(self):
        return self.character

    def __eq__(self, other):
        if not isinstance(other, Nonterminal):
            return False
        return self.character == other.character

    def __hash__(self):
        return hash(self.character)
