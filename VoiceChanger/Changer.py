import threading
import sys
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd

class Changer():

    T_s = 1.0/4000 # サンプリング周期[s]
    F_s = 1 / T_s # サンプリング周波数[s^-1]
    N = 112*10 #fftごとのデータ数
    T_fft = T_s * N #fft を行う周期[s]
    Q_LEN = N * 4

    CHANNEL = 1 # チャンネル数（1固定）

    samplingCount = 0

    #リングQの定義。inQはマイク入力、outQは出力
    inQ = np.zeros((Q_LEN, 1))
    outQ = np.zeros((Q_LEN, 1))
    #各キューのfrontとrear -> F と R
    inQF = 2 * N
    inQR = 0
    outQF = N
    outQR = 0

    IN_Q_GRAPH_NUM = 112
    figInQ , axInQ = plt.subplots()
    x = np.arange(0, IN_Q_GRAPH_NUM , 1)
    lineInQ, = axInQ.plot(x, np.zeros((IN_Q_GRAPH_NUM,1)))

    def __init__(self):

        self.stream = sd.Stream(
            channels=self.CHANNEL,
            samplerate=self.F_s,
            callback=self.audioCallback)

        aniInQ = FuncAnimation(
            self.figInQ,
            self.plotInQ,
            init_func=self.initInQGraph,
            interval=self.T_s,
            blit=True)

        with self.stream:
            plt.show()

    def initInQGraph(self):
        self.axInQ.set_ylim(-1,1)
        self.axInQ.set_ylabel("digital value[-]")
        self.axInQ.set_xlabel("data index[-]")
        self.lineInQ.set_ydata([np.nan] * self.IN_Q_GRAPH_NUM)
        return self.lineInQ,

    def plotInQ(self, i):
        """ボイス波形を時間領域のグラフをプロ ット"""
        line = np.zeros((self.IN_Q_GRAPH_NUM,1))
        #inQから値の取り出し
        for i in range(self.IN_Q_GRAPH_NUM):
            line[i] = self.inQ[(self.inQF + i)%self.Q_LEN]
        self.lineInQ.set_ydata(line)
        return self.lineInQ,

    def convertVoiceToSpects(self,convertData):
        """入ってきたマイクのデータを周波数解析して、返す"""
        print("convert input voice to spectacles by fft")
        spects = np.fft.fft(convertData)
        return spects

    def filterSpects(self,spects):
        """周波数特性を変換して、output(周波数領域)のデータ配列に入れる"""
        convertedSpects = spects
        return convertedSpects

    def convertSpectsToVoice(self,convertedSpects):
        """周波数領域で変換された波形を時間領域に変換する"""
        convertedData = np.fft.ifft(convertedSpects) #TODO 周波数領域のspectaclesから時間領域の波形に変換する
        return convertedData
 
    def audioCallback2(self):
        """T_fftごとに呼ばれるコールバック関数"""
        print("callback by a fft")
        #変換するデータの取り出し
        convertData = np.zeros((self.N, 1))
        for i in range(self.N):
            convertData[i] = self.inQ[(self.inQR + 1 + i)%self.Q_LEN]
        self.inQR = (self.inQR + self.N) % self.Q_LEN
#         #データの変換
#         spects = self.convertVoiceToSpects(convertData)
#         convertedSpects = self.filterSpects(spects)
#         convertedData = self.convertSpectsToVoice(convertedSpects)
#         #変換したデータを出力Qに追加
#         for i, _ in enumerate(convertedData):
#             self.outQ[(self.outQF+i)%self.Q_LEN]  = convertedData[i]
#         self.outQF = (self.outQF + len(convertedData)) % self.Q_LEN

    def audioCallback(self, indata, outdata, frames, time, status):
        """複数のサンプリングごと呼ばれるコールバック関数"""
        """
        indata : np.array, サンプリングの結果を行ベクトルとして保持
        outdata : 出力に使う行ベクトル, indata と同じ長さと思われる
        """
        sampleLen = indata.shape[0] #行列の横の長さ
        self.samplingCount += sampleLen
        if status:
            print(status, file=sys.stderr) #error status
        #リングQに追加
        for i, _ in enumerate(indata):
            self.inQ[(self.inQF + i)%self.Q_LEN] = indata[i]
        self.inQF = (self.inQF + sampleLen) % self.Q_LEN
        #T_fftのタイミング=T_sが一定回数のタイミングで、audioCallback2を呼び出す
        if self.samplingCount >= self.N:
            threadConvert = threading.Thread(target=self.audioCallback2)
            threadConvert.start()
            self.samplingCount = self.samplingCount % self.N
        #リングQから取り出し
        for i, _ in enumerate(indata):
            outdata[i] = self.outQ[(self.outQF+i)%self.Q_LEN]
        self.outQR = (self.outQR +  sampleLen) % self.Q_LEN

        print(self.samplingCount)



if __name__ == '__main__':
    Changer()