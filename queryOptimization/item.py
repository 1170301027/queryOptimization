import copy

from queryOptimization.cfg import Empty


class Item:
    '''
    用于表示LR分析中的项
    [header -> body, symbols]
    '''
    def __init__(self, production, symbols):
        '''
        使用产生式产生第一个项
        即 由A -> BC生成项 [A-> .BC, a]
        '''
        self.production = production
        self.header = production.header
        self.body = production.body
        self.symbols = symbols
        # . 所在的位置
        # 0 < loc < len(body) + 1
        self.__loc = 0

    def next_symbol(self):
        '''
        获得[A->a.Bp, a]中的B，goto函数中要用到
        如果没有符号，那么返回None
        :return:
        '''
        if len(self.body) == 1 and isinstance(self.body[0], Empty):
            return None
        if self.__loc == len(self.body) :
            return None
        else:
            return self.body[self.__loc]

    def beta_a(self):
        '''
        对于A -> [a.Bp, a](a 为alpha， p为beta)
        因为在求闭包是需要求解first(p), 然后将[B->.y, b]
        加入到闭包项集中，其中b in first(pa)
        :return: 因为a可能不止一个，所以是一个二元组(p, a), 其中a是一个列表
        '''
        if self.__loc >= len(self.body) - 1:
            return [Empty(),], self.symbols
        else:
            return self.body[self.__loc + 1:], self.symbols

    def next_item(self):
        '''
        获得下一个项
        即移入符号symbol [A -> .BC, a] 变为 [A ->B.C, a]
        :param symbol: 移入的符号
        :return: 下一个项，该项是新的对象
        '''
        if self.__loc == len(self.body):
            print("无法获得下一个项")
            return None
        if len(self.body) == 1 and isinstance(self.body[0], Empty):
            return None

        new_item = copy.deepcopy(self)
        new_item.__loc += 1
        new_item.symbols = self.symbols[:]
        return new_item

    def get_production(self):
        '''
        获得该项所对应的产生式
        :return: 产生式对象
        '''
        return self.production


    def union_symbol(self, other):
        if not isinstance(other, Item):
            return False
        if self.production == other.production and self.__loc == other.__loc:
            return True



    def __str__(self):
        item_str = ''
        item_str +='[' + str(self.header) + ' -> '

        if len(self.body) == 1 and isinstance(self.body[0], Empty):
            item_str += ' . '
        else :
            i = 0
            for c in self.body:
                if self.__loc == i:
                    item_str += '.'
                item_str += str(c) + ' '
                i += 1
            if self.__loc == len(self.body):
                item_str += '.'
        item_str += ','
        for s in self.symbols:
            item_str += str(s) + " "
        item_str += ']'
        return item_str

    def __eq__(self, other):
        if not isinstance(other, Item):
            return False
        if other.symbols == self.symbols and\
                other.header == self.header and\
                other.body == self.body and\
                other.__loc == self.__loc:
            return True
    def __hash__(self):
        result = hash(self.production) + hash(str(self.symbols)) + self.__loc
        return result







