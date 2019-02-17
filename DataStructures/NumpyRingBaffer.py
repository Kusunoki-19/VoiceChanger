import numpy as np

class NumpyRingBaffer():
    front = 0
    rear = 0
    length = 1
    q = np.zeros((1,1))
    def __init__(self,length,firstRear,firstFront):
        self.length = length
        self.q = np.zeros((length,1))
        self.front = firstFront
        self.rear = firstRear
    
    def printQ(self):
        print("Q length\t: {0}".format(self.length))
        print("Q Rear  \t: {0}".format(self.rear))
        print("Q Front \t: {0}".format(self.front))
        for i, datum in enumerate(self.q):
            info = ""
            if i == self.front : 
                info = info + "(front)"
            if i == self.rear : 
                info = info + "(rear)"
            print("{0}\t: {1}\t: {2}".format(i, datum, info))
            
    def enque(self,data):
        dataLen = data.shape[0]
        for i in range(dataLen):
            #rearに追加して更新
            self.q[self.rear] = data[i]
            self.rear = (self.rear + 1) % self.length
            
        
    def deque(self,dataLen):
        data = np.zeros((dataLen, 1))
        for i in range(dataLen):
            #frontから取り出して更新
            data[i] = self.q[self.front]
            self.front = (self.front + 1) % self.length
        return data
        
    def readQ(self,start,dataLen):
        data = np.zeros((dataLen, 1))
        for i in range(dataLen):
            data[i] = self.q[(start + i) % self.length]
        return data
    
        
if __name__ == '__main__':
    baffer = NumpyRingBaffer(8, 0, 4)
    a = np.array([1,2,3]).reshape(3,1)
    
    baffer.printQ()
    
    print("-----enque-----")
    baffer.enque(a)
    baffer.printQ()
    
    print("-----deque-----")
    print(baffer.deque(3))
    baffer.printQ()
    
    print("-----enque-----")
    baffer.enque(a)
    baffer.printQ()
    
    print("-----deque-----")
    print(baffer.deque(3))
    baffer.printQ()