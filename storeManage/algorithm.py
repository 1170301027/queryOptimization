from storeManage.data import Data
from storeManage.extmem import Extmem,Buffer

class Algorithm():
    """
    Algorithm类用于实现查询算法
    """
    def __init__(self):
        self.data = Data() # buf and extmem are in data
        self.extmem = self.data.extmem
        self.buf = self.data.buf

    def parserBlock(self,block) -> []:
        '''
        解析一个块，取出元组
        :param block: 块结构 bytearray
        :return:
        '''
        list = []
        for i in range(7):
            offest = i * 8
            temp = block[offest:offest + 8]
            tuple = []
            tuple.append(int.from_bytes(temp[0:4], byteorder='little', signed=True))
            tuple.append(int.from_bytes(temp[4:], byteorder='little', signed=True))
            list.append(tuple)
        return list

    def writeToBlock(self, block, integer, index):
        '''
        将一个整数写入一个块，并返回下一个地址的索引
        :param block:
        :param integer:
        :param index:
        :return:
        '''
        bytes = integer.to_bytes(4, byteorder='little', signed=True)
        block[index:index + 4] = bytes[:]
        if index + 4 >= 7 * 8 - 1:
            return 0
        else:
            return index + 4

    def writeToDisk(self,firstAddr,tuples):
        '''
        将一系列元组写入磁盘
        :param firstAddr: 写入磁盘的首地址
        :param tuples: 元组属性集合
        :return: 写入磁盘位置列表
        '''
        if self.buf.isBufferFull():
            self.buf.free()
        new_block = self.buf.getNewBlock()
        count = 0
        index = 0
        addrs = []
        if not self.buf.isBufferFull():
            addrs.append(firstAddr)
            for tuple in tuples:
                for temp in tuple:
                    index = self.writeToBlock(new_block, temp, index)
                # if index % 8 != 0:
                #     index += (8 - index % 8)
                if count < 6:
                    count += 1
                    index = count*8
                else:
                    addr = addrs[-1]
                    addrs.append(addr + 1)
                    index = self.buf.insertBlock(new_block, addr)
                    del new_block
                    count = 0
                    self.extmem.writeBlockToDisk(index, addr, self.buf)
                    new_block = self.buf.getNewBlock()
                    index = 0
        if count != 0:
            index = self.buf.insertBlock(new_block, addrs[-1])
            self.extmem.writeBlockToDisk(index, addrs[-1], self.buf)
        return addrs

    def relationSelect(self,relation,choice,value,firstAddr):
        '''
        实现关系选择算法
        :param relation: 关系（此处指的是关系在磁盘块上的所有位置的列表） -> []
        :param choice:  选择条件，第几个属性， -> 1 or 2
        :param value:  属性值， -> int
        :param firstAddr: 存入磁盘的首地址
        :return:
        '''
        if not isinstance(relation,list) or not isinstance(value,int):
            return False
        if choice != 1 and choice != 2:
            return False
        result = []
        for addr in relation:
            if self.buf.isBufferFull():
                self.buf.free()
            index = self.extmem.readBlockFromDisk(addr,self.buf)
            tuples = self.parserBlock(self.buf.getBlock(index))
            for tuple in tuples:
                if tuple[choice-1] == value:
                    result.append(tuple)
        print(result)
        if len(result) != 0:
            return self.writeToDisk(firstAddr,result)
        return None

    def relationProjection(self,relation,choice,firstAddr):
        '''
        实现关系投影算法（去重）
        :param relation: 关系（此处指的是关系在磁盘块上的所有位置的列表） -> []
        :param choice:  选择条件，第几个属性， -> 1 or 2
        :param firstAddr: 存入磁盘的首地址
        :return:
        '''
        if not isinstance(relation, list):
            return False
        if choice != 1 and choice != 2:
            return False
        result = []
        for addr in relation:
            if self.buf.isBufferFull():
                self.buf.free()
            index = self.extmem.readBlockFromDisk(addr, self.buf)
            tuples = self.parserBlock(self.buf.getBlock(index))
            for tuple in tuples:
                if [tuple[choice-1]] not in result:
                    result.append([tuple[choice-1]])
        if len(result) != 0:
            result.sort()
            print(result)
            return self.writeToDisk(firstAddr, result)
        return None

    def nested_loop_join(self,r_choice,s_choice,addr):
        '''
        Nested-Loop Join 算法实现
        :param r_choice: 关系R的第几个属性
        :param s_choice: 关系S的第几个属性
        :return: 新写入块的地址
        '''
        # 参数判断阶段
        if r_choice != 1 and r_choice != 2:
            return False
        if s_choice != 1 and s_choice != 2:
            return False
        r_choice -= 1
        s_choice -= 1
        self.buf.free()
        # 执行阶段
        addrs = [addr] # 储存写入磁盘的地址，（返回值）
        write_back = self.buf.getNewBlock()  # 写回的块分配存储空间
        next_index = 0  # 存储块的下一个地址。
        # 每次用一个块存R属性的元组，六个块存S属性的元组，最后一块保留用于存储join结果
        for r_addr in self.data.R:
            r_index = self.extmem.readBlockFromDisk(r_addr,self.buf) # r的块索引
            s_index_list = [] # s的所有块索引列表
            # 遍历 S 所有块
            for s_addr in self.data.S:
                index = self.extmem.readBlockFromDisk(s_addr,self.buf)
                s_index_list.append(index)
                if len(s_index_list) != 5 and s_addr != self.data.S[-1]:
                    continue
                r_tuples = self.parserBlock(self.buf.getBlock(r_index)) # 解析数据块
                print('r_tuples')
                print(r_tuples)
                # 对S的每一个块判断关联性
                for s_index in s_index_list:
                    s_tuples = self.parserBlock(self.buf.getBlock(s_index)) # 解析一个S块
                    # join
                    # 用于判断θ条件的两层循环
                    for i in r_tuples:
                        for j in s_tuples:
                            if i[r_choice] == j[s_choice]:
                                next_index = self.writeToBlock(write_back,i[0],next_index)
                                next_index = self.writeToBlock(write_back,i[1],next_index)
                                next_index = self.writeToBlock(write_back,j[0],next_index)
                                next_index = self.writeToBlock(write_back,j[1],next_index)
                            if next_index >= 3 * 12:
                                next_index = 0
                                addr = addrs[-1]
                                addrs.append(addr+1)
                                write_back_index = self.buf.insertBlock(write_back,addr)
                                self.extmem.writeBlockToDisk(write_back_index,addr,self.buf)
                                self.buf.freeBlock(write_back_index)
                                write_back = self.buf.getNewBlock()
                # 释放掉关系S的当前所有块
                for s_index in s_index_list:
                    self.buf.freeBlock(s_index_list[0])
                s_index_list = []
            # 释放R的唯一一个块
            self.buf.freeBlock(r_index)
        if next_index != 0: # 结束若由未写入磁盘的存在，则写入
            next_index = self.buf.insertBlock(write_back,addrs[-1])
            self.extmem.writeBlockToDisk(next_index,addrs[-1],self.buf)
            self.buf.freeBlock(next_index)
        else: # 无则删除冗余地址后返回
            del addrs[-1]
        return addrs





    def hash_join(self):
        pass

    def sort_merge_join(self):
        pass