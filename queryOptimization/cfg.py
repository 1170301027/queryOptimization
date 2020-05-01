from queryOptimization.tag import Tag


class CFG():
    """
    CFG类用于构造文法
    """
    def __init__(self):
        self.productions = []
        self.start = Nonterminal('<query>')
        self.nonterminal_list = set()
        self.construct()
        # self.extractSameLeftFactor()

    def construct(self):
        '''
        <query> -> <sql>
        <sql> -> <keyword> [ <where> ] <relation>
        <keyword> -> SELECT | PROJECTION | AVG
        <relation> -> <fromlist> | ( <sql> )
        <where> -> <condition> | <condition> & <condition>
        <condition> -> <id> <logicalOperator> <patten>
        <condition> -> <id> | <id>,<id>
        <fromlist> -> ( <id> JOIN <id> ) | ( <id> JOIN <sql> )
        <logicalOperator> -> = | < | > | <= | >=

        :return:
        '''
        def set(production):
            self.nonterminal_list.add(production.header)
            self.productions.append(production)

        set(Production(Nonterminal('<query>'),
                       [Nonterminal('<SQL>')]))

        set(Production(Nonterminal('<SQL>'),
                       [Nonterminal('<keyword>'),Terminal(Tag.LRP,'['),Nonterminal('<where>'),Terminal(Tag.RRP,']'),Nonterminal('<relation>')]))
        set(Production(Nonterminal('<keyword>'),
                       [Terminal(Tag.SELECT,'SELECT')]))
        set(Production(Nonterminal('<keyword>'),
                       [Terminal(Tag.PROJECTION, 'PROJECTION')]))
        set(Production(Nonterminal('<keyword>'),
                       [Terminal(Tag.AVG, 'AVG')]))
        set(Production(Nonterminal('<relation>'),
                       [Nonterminal('<fromlist>')]))
        set(Production(Nonterminal('<relation>'),
                       [Terminal(Tag.SLP,'('),Nonterminal('<SQL>'),Terminal(Tag.SRP,')')]))

        set(Production(Nonterminal('<where>'),
                       [Nonterminal('<condition>'), Terminal(Tag.AND, '&'), Nonterminal('<condition>')]))
        set(Production(Nonterminal('<where>'),
                       [Nonterminal('<condition>')]))

        set(Production(Nonterminal('<condition>'),
                       [Terminal(Tag.PROPERTY,'<id>'),Nonterminal('<logicalOperator>'),Terminal(Tag.PATTERN,'<pattern>')]))
        set(Production(Nonterminal('<condition>'),
                       [Terminal(Tag.PROPERTY,'<id>'),Terminal(Tag.COMMA,','),Terminal(Tag.PROPERTY,'<id>')]))
        set(Production(Nonterminal('<condition>'),
                       [Terminal(Tag.PROPERTY,'<id>')]))
        for i in [[Terminal(Tag.EQ,Tag.EQ)],[Terminal(Tag.LT,Tag.LT)],[Terminal(Tag.GT,Tag.GT)],[Terminal(Tag.LE,Tag.LE)],[Terminal(Tag.GE,Tag.GE)]]:
            set(Production(Nonterminal('<logicalOperator>'),i))

        set(Production(Nonterminal('<fromlist>'),
                       [Terminal(Tag.SLP,'('),Terminal(Tag.PROPERTY,'<id>'),Terminal(Tag.JOIN,'JOIN'),
                        Terminal(Tag.PROPERTY,'<id>'),Terminal(Tag.SRP,')')]))
        set(Production(Nonterminal('<fromlist>'),
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
    
    def extractSameLeftFactor(self):
        def extract(production_list):
            '''
            提取公共左公因子，
            :param production_list:
            :return: （num_of_symbols,productions）
            '''
            # print(str(production_list[0].header))
            productions = []
            bodys = []
            min = 100
            for i in production_list:
                if min > len(i.body):
                    min = len(i.body)
                bodys.append(i.body)
            same = bodys[:]
            i = 0
            numofsymbols = []
            while i < min: # 小于最短长度
                list = [] # 存储每一个体的第i个字符
                num = set() # 存储重复的产生式id
                flag = False
                for body in same: # 相同产生式右部（体）集合
                    if body[i] in list:
                        flag = True
                        num.add(bodys.index(body))
                        num.add(list.index(body[i]))
                    else:
                        list.append(body[i])

                if flag:
                    numofsymbols = num.copy()
                    num.clear()
                    same = []
                    for i1 in numofsymbols:
                        same.append(bodys[i1])
                else:
                    break
                i += 1
                list.clear()
            # print(numofsymbols)
            for i1 in numofsymbols: #产生式ids
                productions.append(production_list[i1])
            return (i,productions) # i 代表有几个字符匹配

        for symbol in self.nonterminal_list:
            production_list = self.getProductions(symbol)
            length = len(production_list)
            if length == 1:
                continue
            result = extract(production_list)
            # print('result:')
            # print(result)
            if result[0] == 0:
                continue
            else:
                i = result[0]
                productions = result[1]
                for p in productions:
                    del self.productions[self.productions.index(p)]
                    pro = Production(Nonterminal(symbol.character + '_temp'),p.body[i:])
                    if pro.body == []:
                        # print('zhixing ')
                        pro = Production(pro.header,[Empty()])
                    self.productions.append(pro)
                    # print(str(pro))
                body = productions[0].body[0:i]
                body.append(Nonterminal(symbol.character + '_temp'))
                pro = Production(symbol, body=body)
                if pro.body == None:
                    pro = Production(pro.header, [Nonterminal(symbol.character + '_temp')])
                self.productions.append(pro)
                # print(str(pro))


class Production():
    """
    Production类用于产生式
    """
    def __init__(self,header,body):
        self.header = header
        self.body = body

    def get_num_body_smybol(self):
        if len(self.body) == 1 and isinstance(self.body[0], Empty):
            return 0
        return len(self.body)

    def __eq__(self, other):
        if not isinstance(other,Production):
            return False
        if self.header == other.header and self.body == other.body:
            return True
        return False

    def __hash__(self):
        return hash(str([self.header,self.body]))


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

    def set_show_str(self,show_str):
        self.show_str = show_str


    def __str__(self):
        return self.show_str

    def __hash__(self):
        return hash(self.character)

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

class Empty:
    def __init__(self):
        self.character = chr(949)

    def __eq__(self, other):
        if not isinstance(other, Empty):
            return False
        return self.character == other.character

    def __hash__(self):
        return 949

    def __str__(self):
        return self.character

class Node:
    def __init__(self, symbol, lex_line = 0):
        self.lex_line = lex_line
        self.grammar_symbol = symbol
        self.sub_nodes = []
    def add_subnode(self, node):
        '''
        增加子结点
        :param node:
        :return:
        '''
        self.sub_nodes.append(node)
    def get_subnodes(self):
        '''
        获得该结点的所有子结点
        :return:
        '''
        return self.sub_nodes
    def __str__(self):
        return str(self.grammar_symbol)