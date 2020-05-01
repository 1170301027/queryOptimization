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

    def nest_loop_join(self,r_choice,s_choice,addr):
        '''
        Nest-Loop Join 算法实现
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
        '''for r_addr in self.data.R:
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
            self.buf.freeBlock(r_index)'''
        r_index_list = []  # r的所有块索引列表
        for r_addr in self.data.R:
            r_index = self.extmem.readBlockFromDisk(r_addr,self.buf) # r的块索引
            r_index_list.append(r_index)
            if len(r_index_list) != 6 and r_addr != self.data.R[-1]:
                continue
            for s_addr in self.data.S:
                s_index = self.extmem.readBlockFromDisk(s_addr,self.buf)
                s_tuples = self.parserBlock(self.buf.getBlock(s_index))
                for r_index in r_index_list:
                    r_tuples = self.parserBlock(self.buf.getBlock(r_index))
                    # 用于判断θ条件的两层循环
                    for i in r_tuples:
                        for j in s_tuples:
                            if i[r_choice] == j[s_choice]:
                                next_index = self.writeToBlock(write_back, i[0], next_index)
                                next_index = self.writeToBlock(write_back, i[1], next_index)
                                next_index = self.writeToBlock(write_back, j[0], next_index)
                                next_index = self.writeToBlock(write_back, j[1], next_index)
                            if next_index >= 3 * 12:
                                next_index = 0
                                addr = addrs[-1]
                                addrs.append(addr + 1)
                                write_back_index = self.buf.insertBlock(write_back, addr)
                                self.extmem.writeBlockToDisk(write_back_index, addr, self.buf)
                                self.buf.freeBlock(write_back_index)
                                write_back = self.buf.getNewBlock()
                # 释放掉S的当前块
                self.buf.freeBlock(s_index)
            # 释放掉R的所有块5
            for i in range(len(r_index_list)):
                self.buf.freeBlock(r_index_list[0])
            r_index_list.clear()

        if next_index != 0: # 结束若由未写入磁盘的存在，则写入
            next_index = self.buf.insertBlock(write_back,addrs[-1])
            self.extmem.writeBlockToDisk(next_index,addrs[-1],self.buf)
            self.buf.freeBlock(next_index)
        else: # 无则删除冗余地址后返回
            del addrs[-1]
        return addrs

    def hash_join(self, r_choice, s_choice, addr):
        '''
        Hash-Join 算法实现
        用两个表中较小的表利用join key 在内存中建立散列表， 扫描较大的表并探测散列表，
        找出与hash表匹配的行
        :param r_choice:
        :param s_choice:
        :param addr: 要存储的首地址（块名）
        :return: 磁盘上的位置列表
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
        # 制 r_hash_table
        r_hash_table = {} # dict {hash_func(integer):{integer:[tuple]}}
        for r_addr in self.data.R:
            index = self.extmem.readBlockFromDisk(r_addr,self.buf)
            if index == None: # 读完所有R的块
                break
            tuples = self.parserBlock(self.buf.getBlock(index)) # 解析块
            # 加入hash_table
            for tuple in tuples:
                integer = tuple[r_choice]
                key = hash(integer)
                if key not in r_hash_table.keys():
                    r_hash_table[key] = []
                r_hash_table[key].append(tuple)
            self.buf.freeBlock(index)

        print(r_hash_table)
        # 制 s_hash_table
        s_hash_table = {}
        for s_addr in self.data.S:
            index = self.extmem.readBlockFromDisk(s_addr,self.buf)
            if index == None:
                break
            tuples = self.parserBlock(self.buf.getBlock(index))  # 解析块
            # 加入hash_table
            for tuple in tuples:
                integer = tuple[s_choice]
                key = hash(integer)
                if key not in s_hash_table.keys():
                    s_hash_table[key] = []
                s_hash_table[key].append(tuple)
            self.buf.freeBlock(index)

        print()
        print(s_hash_table)
        # join
        addrs = [addr] # 写入地址列表，返回值
        next_index = 0 # 块内索引
        write_back = self.buf.getNewBlock() # 初始化写回块
        for r_key in r_hash_table.keys():
            if r_key in s_hash_table.keys():
                r_tuples = r_hash_table[r_key]
                s_tuples = s_hash_table[r_key]
                for r_tuple in r_tuples:
                    for s_tuple in s_tuples:
                        next_index = self.writeToBlock(write_back, r_tuple[0], next_index)
                        next_index = self.writeToBlock(write_back, r_tuple[1], next_index)
                        next_index = self.writeToBlock(write_back, s_tuple[0], next_index)
                        next_index = self.writeToBlock(write_back, s_tuple[1], next_index)
                        if next_index >= 3 * 12:
                            next_index = 0
                            addr = addrs[-1]
                            addrs.append(addr + 1)
                            write_back_index = self.buf.insertBlock(write_back, addr)
                            self.extmem.writeBlockToDisk(write_back_index, addr, self.buf)
                            self.buf.freeBlock(write_back_index)
                            write_back = self.buf.getNewBlock()
        if next_index != 0: # 结束若由未写入磁盘的存在，则写入
            next_index = self.buf.insertBlock(write_back,addrs[-1])
            self.extmem.writeBlockToDisk(next_index,addrs[-1],self.buf)
            self.buf.freeBlock(next_index)
        else: # 无则删除冗余地址后返回
            del addrs[-1]
        return addrs

    def sort_merge_join(self,r_choice,s_choice,addr):
        def mergesort(seq,choice):
            """归并排序"""
            if len(seq) <= 1:
                return seq
            mid = len(seq) / 2  # 将列表分成更小的两个列表
            # 分别对左右两个列表进行处理，分别返回两个排序好的列表
            left = mergesort(seq[:mid],choice)
            right = mergesort(seq[mid:],choice)
            # 对排序好的两个列表合并，产生一个新的排序好的列表
            return merge(left, right, choice)

        def merge(left, right, choice):
            """合并两个已排序好的列表，产生一个新的已排序好的列表"""
            result = []  # 新的已排序好的列表
            i = 0  # 下标
            j = 0
            # 对两个列表中的元素 两两对比。
            # 将最小的元素，放到result中，并对当前列表下标加1
            while i < len(left) and j < len(right):
                if left[i][choice] <= right[j][choice]:
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1
            result += left[i:]
            result += right[j:]
            return result

        def outer_sort(addrs,choice):
            '''
            内存二分之一的归并处理
            :param addrs: 块所在的地址
            :return:
            '''
            A_addrs = addrs[0:7][:]
            B_addrs = addrs[8:15][:]
            self.buf.free()
            data_list = []
            for addr in A_addrs:
                index = self.extmem.readBlockFromDisk(addr)
                data_list.extend(self.parserBlock(index))
            data_list = mergesort(data_list,choice)


        # 参数判断阶段
        if r_choice != 1 and r_choice != 2:
            return False
        if s_choice != 1 and s_choice != 2:
            return False
        r_choice -= 1
        s_choice -= 1
        self.buf.free()
        # 执行阶段
        addrs = [addr]
