from queryOptimization.token import Token
from queryOptimization.cfg import *

class Parser():
    """
    Parser类用于构造语法分析树
    """
    def __init__(self):
        self.cfg = CFG()
        self.keyword = ['SELECT','PROJECTION','JOIN','DISTINCT','ALL','FROM','WHERE']
        self.keywordTag = [Tag.SELECT,Tag.PROJECTION,Tag.JOIN]
        self.delimiter = ['[',']','(',')',',']
        self.delimiterTag = [Tag.LRP,Tag.RRP,Tag.SLP,Tag.SRP,Tag.COMMA]
        self.binaryOperator = ['&']
        self.logicalOperator = ['=','<','>','>=','<=']
        self.logicalOperatorTag = [Tag.EQ,Tag.LT,Tag.GT,Tag.GE,Tag.LE]
        self.tree = []
        self.tokens = []
        self.currentI = 0

    def gettoken(self,query):
        '''
        用于执行解析，获取token
        :param query: 需要解析的SQL语句
        :return: tree
        '''
        query = query.split(' ')
        for i in range(len(query)):
            token = query[i]
            if token in self.keyword:
                self.tokens.append(Terminal(self.keywordTag[self.keyword.index(token)],token))
            elif token in self.delimiter:
                self.tokens.append(Terminal(self.delimiterTag[self.delimiter.index(token)],token))
            elif "'" in token:
                self.tokens.append(Terminal(Tag.PATTERN,token))
            elif token in self.logicalOperator:
                self.tokens.append(Terminal(self.logicalOperatorTag[self.logicalOperator.index(token)],token))
            elif token in self.binaryOperator:
                self.tokens.append(Terminal(Tag.BINARYOPERATOR,token))
            else:
                self.tokens.append(Terminal(Tag.PROPERTY,token))

    def doParse(self):
        def reduction(nonterminal):
            productions = self.cfg.getProductions(nonterminal)
            flag = False
            for production in productions:
                print(str(production)+str(len(productions)))
                body = production.body
                for symbol in body:
                    if isinstance(symbol,Nonterminal):
                        # print(str(symbol))
                        self.tree.append(str(symbol))
                        if not reduction(symbol):
                            print('执行')
                            break
                    elif isinstance(symbol,Terminal):
                        # print(symbol.character)
                        print(self.tokens[self.currentI].character)
                        if symbol == self.tokens[self.currentI]:
                            print('匹配')
                            flag = True
                            self.tree.append(str(symbol)+'--------')
                            if self.currentI < len(self.tokens):
                                self.currentI += 1
                            break
                    else: # 为终结符，但是不等于当前的符号，需要回溯
                        print(str(symbol))
            return flag
            # if self.currentI != len(self.tokens):
            #     print(str(nonterminal)+' : ')
            #     print('分析出错 :%s' %str(self.tokens[self.currentI]))
            #     raise None

        reduction(self.cfg.start)

    def run(self,query):
        self.gettoken(query)
        # for token in self.tokens:
        #     print(str(token))
        self.doParse()
        for i in self.tree:
            print(i)



