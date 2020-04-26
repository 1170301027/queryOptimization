import os


class Extmem():
    """
    Extmem类用于模拟外存磁盘块存储和存取程序
    """
    def __init__(self):
        self.diskPath = 'disk/'
        self.numIO = 0

    def initBuffer(self,bufSize,blkSize):
        return Buffer(bufSize,blkSize)

    # def freeBuffer(self,buf):
    #     buf.free()
    #
    # def getNewBlockInBuffer(self,buf):
    #     index = buf.getNewBlock()
    #     return index

    def dropBlockOnDisk(self,addr):
        file = self.diskPath + str(addr)
        if os.path.exists(file):
            os.remove(file)

    def readBlockFromDisk(self,addr,buf):
        def writeToBlock(block,integer,index):
            bytes = integer.to_bytes(4,byteorder='little',signed=True)
            block[index:index+4] = bytes[:]
            if index+4 >= 7*8-1:
                return 0
            else:
                return index+4

        if not isinstance(buf,Buffer):
            print('param error')
            raise None
        file = self.diskPath + str(addr)
        if os.path.exists(file):
            self.numIO += 1
            with open(file, 'r') as f:
                if not buf.isBufferFull():
                    block = buf.getNewBlock()
                    list = f.readlines()
                    index = 0
                    for tuple in list:
                        first = int(tuple.split(' ')[0])
                        second = int(tuple.split(' ')[1])
                        index = writeToBlock(block, first, index)
                        index = writeToBlock(block, second, index)
                    return buf.insertBlock(block,addr) # index

    def writeBlockToDisk(self,blockIndex,addr,buf):
        if not isinstance(buf,Buffer):
            return False
        file = self.diskPath+str(addr)
        block = buf.getBlock(blockIndex)
        buf.freeBlock(blockIndex)
        if block != None:
            block = block[0 : buf.blockSize - 4]
        with open(file,'w+') as f:
            self.numIO += 1
            for i in range(7):
                offest = i*8
                temp = block[offest:offest+8]
                first_value = int.from_bytes(temp[0:4],byteorder='little',signed=True)
                second_value = int.from_bytes(temp[4:],byteorder='little',signed=True)
                if first_value == 0 and second_value == 0:
                    continue
                if first_value == 0:
                    first_value = ''
                if second_value == 0:
                    second_value = ''
                f.write(str(first_value) + ' ' + str(second_value) + '\n')

    def __str__(self):
        return 'number of I/O : %d' %self.numIO

class Block():
    """
    Block类用于块结构
    """
    def __init__(self,addr,data,next):
        self.addr = addr
        self.data = data
        self.next = next




class Buffer():
    """
    Buffer类用于
    """
    def __init__(self,bufSize,blockSize):
        # 外存I/O次数
        self.numIO = 0
        # 缓冲区大小（byte）
        self.bufSize = bufSize
        # 块大小（byte）-> 后四个字节存放磁盘块的地址
        self.blockSize = blockSize
        self.suffixBlockAddressIndex = self.blockSize - 4
        # 缓冲区可存放的最大块数
        self.numAllBlock = int(bufSize / (blockSize + 1))
        # 缓冲区可用块数
        self.numFreeBlock = self.numAllBlock
        # 数据 (存放块,每一个块为一个list？)
        self.data = []
        self.currentIndex = (0,0)

    def free(self):
        self.numFreeBlock = self.numAllBlock
        del self.data
        self.data = []
        
    def isBufferFull(self):
        return self.numFreeBlock == 0

    def isIndexInData(self,index):
        return index < len(self.data)

    def getNewBlock(self): # 获取一个新块的地址
        '''
        获取一个新块的索引
        :return:
        '''
        if self.isBufferFull():
            return None
        return bytearray(self.blockSize)
    
    def freeBlock(self, index): # 删除，修改上一个块的地址字段为当前块下一个块的地址
        '''
        删除块
        :param index: buf内索引
        :return: 成功返回true，失败返回false
        '''
        if self.isIndexInData(index):
            if index != 0:
                self.data[index - 1][self.suffixBlockAddressIndex:] = self.data[index][self.suffixBlockAddressIndex:]
            del self.data[index]
            self.numFreeBlock += 1
            return True
        return False
    
    def insertBlock(self, data, addr): # 插入，修改上一个块的地址字段为0，成功返回该块的地址索引
        '''
        插入块。
        :param data: 块数据
        :param addr: 块名（地址） int
        :return: 成功返回插入块在buf中的索引，失败返回False
        '''
        if not self.isBufferFull():
            index = len(self.data)
            if index != 0:
                self.data[index - 1][self.suffixBlockAddressIndex:] = addr.to_bytes(4,byteorder='little',signed=True)[:]
            self.data.append(data)
            next_addr = 0
            self.data[-1][self.suffixBlockAddressIndex:] = next_addr.to_bytes(4,byteorder='little',signed=True)[:]
            self.numFreeBlock -= 1
            self.numIO += 1
            return len(self.data)-1
        return False

    def getBlock(self, index): # 获取指定块
        if self.isIndexInData(index):
            data = self.data[index]
            self.numIO += 1
            return data
        return None

    
    def __str__(self):
        result = 'buf size :' + str(self.bufSize) + \
                 '\nblock size :' + str(self.blockSize) + \
                 '\nnum of I/O :' + str(self.numIO) + \
                 '\nnum of free blocks :' + str(self.numFreeBlock) + \
                 '\nnum of all blocks : ' + str(self.numAllBlock) + \
                 '\ndata : '
        for data in self.data:
            result += '\n block---:' + str(data)
        return result
        
