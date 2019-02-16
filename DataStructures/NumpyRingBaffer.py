import numpy as np
class NumpyRingBaffer():
    front = 0
    rear = 0
    q = np.zeros((1,1))
    def __init__(self,qLen,firstFront,firstRear):
        q = np.zeros((qLen,1))
        self.front = firstFront
        self.rear = firstRear
        
    def inqueue(self,data):
        dataLen = data.sharpe[0]
        for i in range(dataLen):
            self.p[self.front + i] = data[i]
        self.front = (self.front + dataLen) % self.dataLen
        
    def dequeue(self,dataLen):
        data = np.zeros((dataLen, 1))
        for i in range(dataLen)
        