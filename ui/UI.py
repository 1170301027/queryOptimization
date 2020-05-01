from tkinter import *
from tkinter import Tk, ttk

from queryOptimization.cfg import *
from queryOptimization.tag import Tag


class UI():
    """
    UI类用于前端显示分析树
    """
    def __init__(self,parser,query):
        self.parser = parser
        self.query = query

    def root(self):
        # 初始化窗口
        window = Tk()
        window.title('语法分析树')
        window.geometry('600x600')
        window.resizable(0, 0)

        # 菜单
        menubar = Menu(window)
        show_menu = Menu(menubar)
        show_list = ['关系代数', '查询优化']
        show_list_event = [self.gen_relation_algebra, self.query_optimization]
        for menu, event in zip(show_list, show_list_event):
            show_menu.add_command(label=menu, command=event)
        menubar.add_cascade(label='显示', menu=show_menu)
        window.config(menu=menubar)

        processTree = ttk.Treeview(window)
        processTree.pack(fill=BOTH, expand=YES)

        self.parser.run(self.query)
        # for production in self

        items = []
        nodes = [self.parser.root_node]
        items.append(processTree.insert('', 0, text=str(nodes[0].grammar_symbol),open=True))
        for pNode in nodes:
            pNodeItem = items[nodes.index(pNode)]
            subNodes = pNode.get_subnodes()
            for subNode in subNodes:
                symbol = subNode.grammar_symbol
                if isinstance(symbol, Terminal):
                    screen_show = symbol.character + ' :' + str(symbol)
                else:
                    screen_show = str(symbol)
                items.append(processTree.insert(pNodeItem, 0, text=screen_show, open=True))
            nodes.extend(subNodes)


        window.mainloop()

    def gen_relation_algebra(self):
        # 初始化窗口
        window = Tk()
        window.title('语法分析树')
        window.geometry('600x600')
        window.resizable(0, 0)

        processTree = ttk.Treeview(window)
        processTree.pack(fill=BOTH, expand=YES)

        self.parser.gen_relation_algebra()
        algebra_tree = self.parser.algebra
        nodes = [self.parser.tokens[0].show_str]
        items = []
        items.append(processTree.insert('', 0, text=str(nodes[0]), open=True))
        for pNode in nodes:
            print(pNode)
            pNodeItem = items[nodes.index(pNode)]
            if pNode in algebra_tree.keys():
                subNodes = algebra_tree[pNode]
                for symbol in subNodes:
                    items.append(processTree.insert(pNodeItem, 'end', text=symbol, open=True))
                nodes.extend(subNodes)

        window.mainloop()

    def query_optimization(self):
        # 初始化窗口
        window = Tk()
        window.title('语法分析树')
        window.geometry('600x600')
        window.resizable(0, 0)

        processTree = ttk.Treeview(window)
        processTree.pack(fill=BOTH, expand=YES)

        self.parser.do_optimization()
        algebra_tree = self.parser.optimization
        nodes = ['PROJECTION']
        items = []
        items.append(processTree.insert('', 0, text=str(nodes[0]), open=True))
        for pNode in nodes:
            print(pNode)
            pNodeItem = items[nodes.index(pNode)]
            if pNode in algebra_tree.keys():
                subNodes = algebra_tree[pNode]
                for symbol in subNodes:
                    items.append(processTree.insert(pNodeItem, 'end', text=symbol, open=True))
                nodes.extend(subNodes)

        window.mainloop()

