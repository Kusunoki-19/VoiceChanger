import threading
import sys
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd

class Changer():

    T_s = 1.0/4000 # サンプリング周期[s]
    F_s = 1 / T_s # サンプリング周波数[s^-1]
    N = 4000 #fftごとのデータ数
    T_fft = T_s * N #fft を行う周期[s]
    Q_LEN = N * 4

    CHANNEL = 1 # チャンネル数（1固定）

    samplingCount = 0

    #リングQの定義。inQはマイク入力、outQは出力
    inQ = np.zeros(Q_LEN)
    outQ = np.zeros(Q_LEN)
    #各キューのfrontとrear -> F と R
    inQF = 2 * N
    inQR = 0
    outQF = N
    outQR = 0

    figInQ , axInQ = plt.subplots()
    x = np.arange(0, N , 1)
    lineInQ, = axInQ.plot(x, np.zeros(N))

    def __init__(self):

        self.stream = sd.Stream(
            channels=self.CHANNEL,
            samplerate=self.F_s,
            callback=self.audioCallback)

        aniInQ = FuncAnimation(
            self.figInQ,
            self.plotInQ,
            init_func=self.initInQGraph,
            interval=self.T_fft,
            blit=True)

        with self.stream:
            plt.show()

    def initInQGraph(self):
        self.lineInQ.set_ydata([np.nan] * self.N)
        return self.lineInQ,

    def plotInQ(self, i):
        """ボイス波形を時間領域のグラフをプロット"""
        self.lineInQ.set_ydata(self.inQ[self.inQF : self.inQF+self.N])
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
        convertedData = 1 #TODO 周波数領域のspectaclesから時間領域の波形に変換する
        return convertedData

    def audioCallback2(self):
        """T_fftごとに呼ばれるコールバック関数"""
        print("callback by a fft")
        #変換するデータの取り出し
        convertData = self.inQ[self.inQR+1 : self.inQR+self.N]
        self.inQR = (self.inQR + self.N) % self.Q_LEN
        #データの変換
#         spects = self.convertVoiceToSpects(convertData)
#         convertedSpects = self.filterSpects(spects)
#         convertedData = self.convertSpectsToVoice(convertedSpects)
        #変換したデータを出力Qに追加
#         self.outQ[self.outQF+1 : self.outQF+self.N] = convertedData[:]
#         self.outQF = (self.outQF + self.N) % self.Q_LEN

    def audioCallback(self, indata, outdata, frames, time, status):
        """サンプリングごとに呼ばれるコールバック関数"""
        self.samplingCount += 1
        print(self.samplingCount)
        if status:
            print(status, file=sys.stderr) #error status
#         print(indata)
#         print(len(indata))
#         self.stream.stop()
        #リングQに追加
        self.inQ[self.inQF] = indata[0]
        self.inQF = (self.inQF + 1) % self.Q_LEN
        #T_fftのタイミング=T_sが一定回数のタイミングで、audioCallback2を呼び出す
        if self.samplingCount == self.N:
            threadConvert = threading.Thread(target=self.audioCallback2)
            threadConvert.start()
            self.samplingCount = 0
        #リングQから取り出し
#         outdata = self.outQ[self.outQR + 1]
#         self.outQR = (self.outQR + 1) % self.Q_LEN
        outdata = indata


if __name__ == '__main__':
    Changer()