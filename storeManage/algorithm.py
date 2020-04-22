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

    def writeToDisk(self,firstAddr,tuples):
        '''
        将一系列元组写入磁盘
        :param firstAddr: 写入磁盘的首地址
        :param tuples: 元组属性集合
        :return: 写入磁盘位置列表
        '''
        def writeToBlock(block, integer, index):
            bytes = integer.to_bytes(4, byteorder='little', signed=True)
            block[index:index + 4] = bytes[:]
            if index + 4 >= 7 * 8 - 1:
                return 0
            else:
                return index + 4

        new_block = self.buf.getNewBlock()
        count = 0
        index = 0
        addrs = []
        if not self.buf.isBufferFull():
            addrs.append(firstAddr)
            for tuple in tuples:
                for temp in tuple:
                    index = writeToBlock(new_block, temp, index)
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

    def nested_loop_join(self):
        ''''''


    def hash_join(self):
        pass

    def sort_merge_join(self):
        pass