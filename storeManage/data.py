import random

from storeManage.extmem import Extmem


class Data():
    """
    Data类用于准备实验需要的数据
    """
    def __init__(self):
        # 元组大小8字节
        self.tuple_size = 8
        self.R = [] # 16 * 7 = 112 个元组
        self.S = [] # 32 * 7 = 224 个元组
        self.extmem = Extmem()
        self.blkSize = 64
        self.bufSize = 520
        self.buf = self.extmem.initBuffer(self.bufSize,self.blkSize)
        self.init_data()

    def init_data(self):
        # 辅助函数，在块的指定位置添加vlaue->integer
        def writeToBlock(block,integer,index):
            bytes = integer.to_bytes(4,byteorder='little',signed=True)
            block[index:index+4] = bytes[:]
            if index+4 >= 7*8-1:
                return 0
            else:
                return index+4
        # 辅助函数 按需求生成随机数据
        def init(value,firstMin,firstMax,secondMin,secondMax,relation):
            count = 0 # 块内元组个数
            self.buf.getNewBlock()
            block = bytearray(self.blkSize)
            index = 0 # 块内偏移
            for i in range(value):
                random_gen = random.Random()
                ranA = random_gen.randint(firstMin,firstMax+1)
                ranB = random_gen.randint(secondMin,secondMax+1)
                if count < 6:
                    index = writeToBlock(block, ranA, index)
                    index = writeToBlock(block, ranB, index)
                    count += 1
                else:
                    addr = relation[-1]
                    relation.append(addr+1)
                    index = self.buf.insertBlock(block,addr)
                    del block
                    block = bytearray(self.blkSize)
                    count = 0
                    self.extmem.writeBlockToDisk(index,addr,self.buf)
            return relation[:-1]

        self.R.append(1230600)
        self.R = init(112,1,40,1,1000,self.R)[:]
        self.S.append(2461200)
        self.S = init(224,20,60,1,1000,self.S)[:]
        print('init data successfully')

