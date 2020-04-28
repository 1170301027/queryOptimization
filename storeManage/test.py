from storeManage.data import Data
from storeManage.extmem import Extmem
from storeManage.algorithm import Algorithm
extmem = Extmem()
blkSize = 64
bufSize = 520
buf = extmem.initBuffer(bufSize,blkSize)
algorithm = Algorithm()

def testWriteToDisk():
    blkIndex = buf.getNewBlock()
    addrs = []

    for i in range(buf.numAllBlock):
        addr = 'block_%d' %i
        # addr = int(addr)
        addrs.append(hash(addr).to_bytes(8,byteorder='little',signed=True))
    for addr in addrs:
        new_bytearray = bytearray(blkSize)
        data = b'abcdefg'
        new_bytearray[0:len(data)] = data[:]
        buf.insertBlock(new_bytearray,addr)
        _addr = int.from_bytes(addr,byteorder='little',signed=True)
        extmem.writeBlockToDisk(0,_addr,buf)
    print(str(buf))

def testInitData():
    data = Data()
    data.init_data()

def testReadFromDisk():
    extmem.readBlockFromDisk(1230600,buf)
    print(str(buf))

def testRelationSelect():
    # R.A = 40 -> 从 10000 开始存
    addrs = algorithm.relationSelect(algorithm.data.R, 1, 40, 10000)
    print(addrs)

def testRelationProjection():
    addrs = algorithm.relationProjection(algorithm.data.R, 1, 20000)
    print(addrs)

def testNestLoopJoin():
    # R.A == S.C
    addrs = algorithm.nest_loop_join(1,1,30000)
    print(addrs)

def testHashJoin():
    # R.A == S.C
    addrs = algorithm.hash_join(1,1,40000)
    print(addrs)

def testSortMergeJoin():
    pass

# testInitData()
# testWriteToDisk()
# testReadFromDisk()

# testRelationSelect()
# testRelationProjection()
testNestLoopJoin()
testHashJoin()
