from queryOptimization.token import Token
from queryOptimization.cfg import *
from queryOptimization.item import Item

class Parser():
    """
    Parser类用于构造语法分析树
    """
    def __init__(self):
        self.cfg = CFG()
        self.keyword = ['SELECT','PROJECTION','JOIN','AVG','DISTINCT','ALL','FROM','WHERE']
        self.keywordTag = [Tag.SELECT,Tag.PROJECTION,Tag.JOIN,Tag.AVG]
        self.delimiter = ['[',']','(',')',',']
        self.delimiterTag = [Tag.LRP,Tag.RRP,Tag.SLP,Tag.SRP,Tag.COMMA]
        self.binaryOperator = ['&']
        self.logicalOperator = ['=','<','>','>=','<=']
        self.logicalOperatorTag = [Tag.EQ,Tag.LT,Tag.GT,Tag.GE,Tag.LE]
        self.tokens = [] # query中所有终结符集合，末尾为$
        self.currentI = -1 # 读到的当前token位置，-1为未开始分析
        self.firsts = {} # first集
        self.item_family = [] # 项目集
        self.actions = {}
        self.gotos = {}

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
            elif "'" in token or token.isdigit():
                self.tokens.append(Terminal(Tag.PATTERN,token))
            elif token in self.logicalOperator:
                self.tokens.append(Terminal(self.logicalOperatorTag[self.logicalOperator.index(token)],token))
            elif token in self.binaryOperator:
                self.tokens.append(Terminal(Tag.AND,token))
            else:
                self.tokens.append(Terminal(Tag.PROPERTY,token))
        self.tokens.append(Terminal(Tag.END,'$'))

    def doParse(self):
        #归约程序

        def reduction(nonterminal):
            print(str(nonterminal))
            flag = False
            for production in self.cfg.getProductions(nonterminal):
                print(str(production))
                body = production.body
                for symbol in body:
                    if isinstance(symbol,Nonterminal):
                        if not reduction(symbol):
                            print("执行。")
                            break
                    elif isinstance(symbol,Terminal):
                        if symbol == self.tokens[self.currentI]:
                            print('匹配')
                            print(str(symbol))
                            flag = True
                            self.stack.add(production)
                            self.tree.append(str(symbol)+'--------------终结符')
                            if self.currentI < len(self.tokens)-1:
                                self.currentI += 1
                            else:
                                return
                    elif isinstance(symbol,Empty):
                        flag = True
                        print('可以')
                    else:
                        raise None
            return flag
        self.tree.append(str(self.cfg.start))
        reduction(self.cfg.start)

    def closure(self, items) -> []:
        '''
        求项集i的闭包
        :param i:项集 列表
        :return: 项集i的闭包的一个列表 []
        '''
        first_dict = {}
        derive_list = []
        def derive_empty(a):
            '''
            输入一个非终结符，判断该非终结符是否能导出空
            :param a: 符号
            :return: 是否能够导入空
            '''
            if isinstance(a, Terminal) or isinstance(a, Empty):
                return False
            if not isinstance(a, Nonterminal):
                raise TypeError

            derive_list.append(a)
            rules = self.cfg.getProductions(a)
            for rule in rules:
                if Empty() in rule.body:
                    return True
            for rule in rules:
                body_list = rule.body
                if body_list[0] in derive_list:
                    continue
                return derive_empty(body_list[0])

        def first(a):

            '''
            获得从文法a推到得到的串的首符号的集合(a 表示alpha)
            :param a:文法符号
            :return: 终结符符号和空串集合
            '''
            if isinstance(a, Terminal):
                return [a,]
            elif isinstance(a, Empty):
                return [Empty()]
            elif not isinstance(a, Nonterminal):
                raise TypeError

            result = set()
            if a not in first_dict.keys():
                first_dict[a] = []
            rules = self.cfg.getProductions(a)
            for rule in rules:
                for s in rule.body:
                    # 说明在求first集是产生了循环
                    if s in first_dict.keys():
                        first_s = first_dict[s]
                        if derive_empty(s):
                            first_s.append(Empty())
                    else:
                        first_s = first(s)
                    result = result.union(first_s)
                    if Empty() not in first_s:
                        break
            return set(result)

        def first_beta_a(item):
            '''
            求项集item的beta_a 的first集
            :param item:
            :return:
            '''
            beta_a = item.beta_a()
            beta_a_s = []
            beta_a_s.extend(beta_a[0])
            first_set = set()
            p_is_empty = False
            for s in beta_a_s:
                if s == beta_a_s[-1]:
                    p_is_empty = True
                if s not in self.firsts.keys():
                    temp_first = first(s)
                    self.firsts[s] = temp_first
                else:
                    temp_first = first(s)
                first_set = first_set.union(temp_first)
                first_set.discard(Empty())
                if Empty() not in temp_first:
                    p_is_empty = False
                    break
            if p_is_empty:
                first_set = first_set.union(beta_a[1])
            return first_set


        # items
        # items1
        scan_items = items[:]
        set_scan_items = set(scan_items)
        for item in scan_items:
            #print(len(scan_items))
            next_symbol = item.next_symbol()
            if not isinstance(next_symbol, Nonterminal):
                continue
            first_set = first_beta_a(item)
            productions = self.cfg.getProductions(next_symbol)
            for p in productions:
                new_item = Item(p, list(first_set))
                if new_item.next_symbol() is not None:
                    if new_item in set_scan_items:
                        continue
                    scan_items.append(new_item)
                    set_scan_items.add(new_item)
                flag = True
                for i in items:
                    if i.union_symbol(new_item):
                        flag = False
                        for s in first_set:
                            if s not in i.symbols:
                                i.symbols.append(s)
                        break
                if flag:
                    items.append(new_item)
        return items

    def goto(self, i, x) -> []:
        '''
        移入x时项集i的转换 [A -> a.Xp, a]
        :param i:项集
        :param x: 文法符号
        :return: 转换后的项集
        '''
        items = []
        for a in i:
            if a.next_symbol() is None:
                continue
            if a.next_symbol() == x:
                items.append(a.next_item())
        return self.closure(items)

    def table(self, G) -> [[]]:
        '''
        求G上的项集族, 同时求的actions表和gotos表
        :param G: 增广文法
        :return:
        '''
        # 初始化项集族为[G->.p, $]
        start_production = G.getProductions(G.start)[0]
        start_items = [Item(start_production, [Terminal(Tag.END, '$')])]
        temp_family = self.closure(start_items)
        self.item_family.append(temp_family)
        index = 0
        for I in self.item_family:
            index_I =  index
            index += 1
            # 获得该项集中所有的下一个symbol
            all_symbols = []
            for i in I:
                one_symbol = i.next_symbol()
                # 如果存在某一项没有next symbol,那么以及进行规约，加入到action中
                if one_symbol is None:
                    # 设置接收状态

                    if index_I in self.actions.keys():
                        if i.production.header == self.cfg.start:
                            self.actions[index_I] = self.actions[index_I].add((i.symbols[0], -1, i.symbols))
                        else:
                            self.actions[index_I] = self.actions[index_I].union({(look_symbol, 1, i.get_production()) for look_symbol in i.symbols})
                    else:
                        if i.production.header == self.cfg.start:
                            self.actions[index_I] = {(i.symbols[0], -1, -1)}
                        else:
                            self.actions[index_I] = {(look_symbol, 1, i.get_production()) for look_symbol in i.symbols}
                if one_symbol is not None:
                    all_symbols.append(one_symbol)
            for s in all_symbols:
                new_I = self.goto(I, s)
                if new_I is not None and new_I not in self.item_family:
                    self.item_family.append(new_I)
                    index_new_I = len(self.item_family)-1
                else:
                    index_new_I = self.item_family.index(new_I)

                # 如果此时s是终结符，那么加入到actions中，并设为移入
                if isinstance(s, Terminal):

                    if index_I in self.actions.keys():
                        self.actions[index_I].add((s, 0, index_new_I))
                    else:
                        self.actions[index_I] = {(s, 0, index_new_I),}
                else:  # 如果为非终结符，那么加入到gotos中
                    if  index_I in self.gotos.keys():
                        # 设置接收状态
                        if s == self.cfg.getProductions(self.cfg.start)[0].body[0]:
                            self.gotos[index_I].add((s, -1))
                        else:
                            self.gotos[index_I].add((s, index_new_I))
                    else:
                        self.gotos[index_I] = {(s, index_new_I),}

    def program(self):
        '''
        进行语法分析
        :return:
        '''
        def move():
            nonlocal look
            if self.currentI < len(self.tokens)-1:
                self.currentI += 1
                look = self.tokens[self.currentI]

        # 2 -> A ->3 -> action token
        def error_handler():
            '''
            错误处理
            :return:
            '''
            self.errors.append((look))
            top_state = state_stack[-1]
            sub_nodes = []
            while top_state not in self.gotos.keys():
                state_stack.pop()
                sub_nodes.append(node_stack.pop())
                top_state = state_stack[-1]
            goto_actions = self.gotos[top_state]

            # 遍历当前栈顶状态下可以移入的所有非终结符
            # 这样做的目的就是尽可能少的忽略token
            while True:
                if len(state_stack) == 1:
                    state_stack[1] = 2
                    return
                move()
                for action in goto_actions:
                    restore_flag = False
                    # 对应于移入一个非终结符之后的状态
                    infer_state = action[1]
                    flag1 = False
                    if look == Terminal(Tag.END, '$'):
                        flag1 = True
                    for action_action in self.actions[infer_state]:
                        # 找到了一个可以进行回复的look
                        if action_action[0] == look:
                            restore_flag = True
                            flag1 = False
                            break
                    if flag1:
                        while top_state not in self.gotos.keys():
                            state_stack.pop()
                            node_stack.pop()
                            top_state = state_stack[-1]
                        goto_actions = self.gotos[top_state]
                    if restore_flag:
                        state_stack.append(action[1])
                        node_stack.append(Node(action[0]))
                        node_stack[-1].sub_nodes = sub_nodes
                        return


        self.table(self.cfg)
        k = 0
        for items in self.item_family:
            print("S" + str(k))
            for i in items:
                print(i)
            k += 1
        # 初始化时将0状态放入状态栈中
        state_stack = [0,]
        node_stack = []
        # look为将下一个token变成的终结符
        look = None
        move()
        while True:
            print(look)
            print(state_stack)
            state_actions =  self.actions[state_stack[-1]]
            error_flag1 = True
            for action in state_actions:
                if action[0] == look:
                    error_flag1 = False
                    #接收状态
                    if action[1] == -1:
                        if len(state_stack) != 2:
                            raise None # 规约完G之后还有问题
                        self.root_node = Node(self.cfg.start)
                        self.root_node.add_subnode(node_stack[0])
                        return

                    # 移入操作
                    elif action[1] == 0:
                        state_stack.append(action[2])
                        node_stack.append(Node(look))
                        move()
                        break
                    # 规约操作
                    else:
                        production = action[2]
                        num_of_s = production.get_num_body_smybol()
                        r_node = Node(production.header)
                        for i in range(num_of_s):
                            state_stack.pop()
                            r_node.add_subnode(node_stack.pop())
                        goto_action = self.gotos[state_stack[-1]]
                        error_flag = True
                        for action in goto_action:
                            if action[0] == production.header:
                                error_flag = False
                                state_stack.append(action[1])
                                node_stack.append(r_node)
                        if error_flag:
                            raise None
                        # 表明在该状态下该字符对应的动作为空
            if error_flag1:
                raise None

    def run(self,query):
        self.gettoken(query)
        # for token in self.tokens:
        #     print(str(token))
        for production in self.cfg.productions:
            print(str(production))
        self.program()



