import os


class Extmem():
    """
    Extmem类用于模拟外存磁盘块存储和存取程序
    """
    def __init__(self):
        self.diskPath = 'disk/'

    def initBuffer(self,bufSize,blkSize):
        return Buffer(bufSize,blkSize)

    def freeBuffer(self,buf):
        buf.free()

    def dropBlockOnDisk(self,addr):
        file = self.diskPath + addr
        if os.path.exists(file):
            os.remove(file)

    def readBlockFromDisk(self,addr,buf):
        file = self.diskPath + addr
        if os.path.exists(file):
            with open(file, 'r') as f:
                return buf.insertBlock(f.read()) # index



    def writeBlockToDisk(self,blockIndex,addr,buf):
        file = self.diskPath+addr
        with open(file,'wb') as f:
            f.write(buf.getBlock(blockIndex))







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
        self.numAllBlock = bufSize / (blockSize + 1)
        # 缓冲区可用块数
        self.numFreeBlock = self.numAllBlock
        # 数据 (存放块,每一个块为一个list？)
        self.data = []
        for i in range(self.numAllBlock):
            self.data.append(bytearray(self.blockSize))
        self.currentIndex = (0,0)

    def free(self):
        # self.numAllBlock = 0
        # self.numFreeBlock = 0
        # self.bufSize = 0
        # self.numIO = 0
        # self.blockSize = 0
        self.data = []
        
    def isBufferFull(self):
        return self.numFreeBlock == 0

    def isIndexInData(self,index):
        return index < len(self.data)

    def getNewBlock(self):
        if self.isBufferFull():
            return None
        return len(self.data)
    
    def freeBlock(self, index):
        if self.isIndexInData(index):
            del self.data[index]
            self.numFreeBlock += 1
            return True
        return False
    
    def insertBlock(self, data):
        if not self.isBufferFull():
            self.data.append(data)
            self.numFreeBlock -= 1
            self.numIO += 1
            return len(self.data)-1
        return False

    def getBlock(self, index):
        if self.isIndexInData(index):
            data = self.data[index]
            del self.data[index]
            self.numIO += 1
            return data
        return None

    
    def __str__(self):
        result = 'buf size :' + str(self.bufSize) + \
                 'block size :' + str(self.blockSize) + \
                 '\nnum of I/O :' + str(self.numIO) + \
                 '\nnum of free blocks :' + str(self.numFreeBlock) + \
                 '\nnum of all blocks' + str(self.numAllBlock) + \
                 '\ndata : ' + str(self.data)
        return result
        
