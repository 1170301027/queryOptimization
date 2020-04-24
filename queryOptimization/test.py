from ui.UI import UI
from queryOptimization.parser import Parser

if __name__ == '__main__':
    parser = Parser()
    querys = []
    querys.append("SELECT [ ENAME = 'Mary' & DNAME = 'Research' ] ( EMPLOYEE JOIN DEPARTMENT )")
    querys.append("PROJECTION [ BDATE ] ( SELECT [ ENAME = 'John' & DNAME = 'Research' ] ( EMPLOYEE JOIN DEPARTMENT ) )")
    querys.append("SELECT [ ESSN = '01' ] ( PROJECTION [ ESSN , PNAME ] ( WORKS_ON JOIN PROJECT ) )")
    querys.append("PROJECTION [ ENAME ] ( SELECT [ SALARY < 3000 ] ( EMPLOYEE JOIN SELECT [ PNO = 'P1' ] ( WORKS_ON JOIN PROJECT ) ) )")
    querys.append("PROJECTION [ DNAME , SALARY ] ( AVG [ SALARY ] ( SELECT [ DNAME = 'Research' ] ( EMPLOYEE JOIN DEPARTMENT ) ) )")
    # parser.run(querys[0])
    # print('productions :')
    # for pro in parser.cfg.productions:
    #     print(str(pro))

    # 多条测试
    # ui = []
    # for i in querys:
    #     ui.append(UI(Parser(), i))
    #     ui[-1].root()
    # 单条测试
    i = 0
    ui = UI(Parser(),querys[i])
    ui.root()