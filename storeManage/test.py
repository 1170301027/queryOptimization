from storeManage.data import Data
from storeManage.extmem import Extmem

def testDisk():
    extmem = Extmem()
    blkSize = 64
    bufSize = 520
    buf = extmem.initBuffer(bufSize,blkSize)
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

testInitData()
# testDisk()
