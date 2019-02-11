import threading
import sys
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd

class Changer():
    #サンプリング周期[s]
    T_s = 1.0/4000
    #サンプリング周波数[s^-1]
    F_s = 1 / T_s
    #fftごとのデータ数
    N = 112*10
    #fftを行う周期[s]
    T_fft = T_s * N
    #チャンネル数（1固定）
    CHANNEL = 1

    #リングQデータ数
    Q_LEN = N * 4
    #リングQの定義。inQはマイク入力、outQは出力
    inQ = np.zeros((Q_LEN, 1))
    outQ = np.zeros((Q_LEN, 1))
    #各キューのfrontとrear -> F と R
    inQF = 2 * N
    inQR = 0
    outQF = N
    outQR = 0

    #グラフに関する変数
    IN_Q_GRAPH_NUM = 112
    fig , ax = plt.subplots(2,2,figsize=(10,5))
    x = np.arange(0, IN_Q_GRAPH_NUM , 1)
    lineInQ, = ax[0,0].plot(x, np.zeros((IN_Q_GRAPH_NUM,1)))

    samplingCount = 0

    def __init__(self):

        self.stream = sd.Stream(
            channels=self.CHANNEL,
            samplerate=self.F_s,
            callback=self.audioCallback)

        self.aniInQ = FuncAnimation(
            self.fig,
            self.plotInQ,
            init_func=self.initInQGraph,
            interval=self.T_s,
            blit=True)

        with self.stream:
            plt.show()

    def initInQGraph(self):
        self.ax[0,0].set_title("Input Voice Wave")
        self.ax[0,0].set_ylim(-1,1)
        self.ax[0,0].set_ylabel("digital value[-]")
        self.ax[0,0].set_xlabel("data index[-]")
        self.lineInQ.set_ydata([np.nan] * self.IN_Q_GRAPH_NUM)
        return self.lineInQ,

    def initInFreqGraph(self):
        self.ax[0,1].set_title("Input Freqency ")
        self.ax[0,1].set_ylim(-1,1)
        self.ax[0,1].set_ylabel("digital value[-]")
        self.ax[0,1].set_xlabel("Freqency[rad/s]")
        self.ax[0,1].set_xscale("log")
        self.lineInQ.set_ydata([np.nan] * self.IN_Q_GRAPH_NUM)
        return self.lineInQ,

    def plotInQ(self, count):
        """ボイス波形を時間領域のグラフをプロ ット"""
        line = np.zeros((self.IN_Q_GRAPH_NUM,1))
        #inQから値の取り出し
        for i in range(self.IN_Q_GRAPH_NUM):
            line[i] = self.inQ[(self.inQF + i)%self.Q_LEN]
        self.lineInQ.set_ydata(line)
        return self.lineInQ,

    def convertWave(self, convertData):
        #波(input)        →周波数特性(input)
        self.inFreq = np.fft.fft(convertData)
        #周波数特性(input) →周波数特性(output) : filtering
        self.outFreq = self.inFreq
        #周波数特性(output)→波(output)
        convertedData = np.fft.ifft(self.outFreq)
        return convertedData

    def audioCallback2(self):
        """T_fftごとに呼ばれるコールバック関数"""
        print("callback by a convertion")
        #変換するデータの取り出し
        convertData = np.zeros((self.N, 1))
        for i in range(self.N):
            convertData[i] = self.inQ[(self.inQR + 1 + i)%self.Q_LEN]
        #inQ Rear の更新
        self.inQR = (self.inQR + self.N) % self.Q_LEN
        #データの変換
        convertedData = self.convertWave(convertData)
        #変換したデータを出力Qに追加
        for i, _ in enumerate(convertedData):
            self.outQ[(self.outQF+i)%self.Q_LEN]  = convertedData[i]
        #outQ Front の更新
        self.outQF = (self.outQF + len(convertedData)) % self.Q_LEN

    def audioCallback(self, indata, outdata, frames, time, status):
        """複数のサンプリングごと呼ばれるコールバック関数"""
        """
        indata : np.array, サンプリングの結果を行ベクトルとして保持
        outdata : 出力に使う行ベクトル, indata と同じ長さと思われる
        """
        sampleLen = indata.shape[0] #行列の横の長さ
        self.samplingCount += sampleLen

        #リングQに追加
        for i, _ in enumerate(indata):
            self.inQ[(self.inQF + i)%self.Q_LEN] = indata[i]
        self.inQF = (self.inQF + sampleLen) % self.Q_LEN
        #T_fftのタイミング>=T_sが一定回数のタイミングで、audioCallback2を呼び出す
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