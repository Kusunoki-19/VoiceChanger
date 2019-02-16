import threading
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd

class Changer():
    #帯域制限周波数[s^-1] (この周波数以上はカットという周波数,本来はアナログフィルタでカット), 
    #人間の可聴域は20kHzらしいが、処理が重くなったので現段階では2.5kHz
    F_m = 4*(10**3)
    #サンプリング周波数[s^-1],
    #サンプリング定理よりT_s > 2 F_sのひつようがあるので、ぎりのサンプリング周波数(ナイキスト周波数)にする
    F_s = 2 * F_m
    #スペクトル周期[ras/s], 周波数特性の周期
    #OMEGA_s = 2 * PI * F_s
    #サンプリング周期[s]
    T_s = 1 / F_s
    #fftごとのデータ数, 現在は2.5kHzの時のindata長になってる(適当)
    N = 144*1*(10**2)
    #チャンネル数（1固定）
    CHANNEL = 1

    #リングQデータ数
    Q_LEN = N * 4
    #リングQの定義。inQはマイク入力、outQは出力
    inQ = np.zeros((Q_LEN, 1))
    outQ = np.zeros((Q_LEN, 1))
    #各キューのfrontとrear -> F と R
    inQF = 0
    inQR = 2 * N
    outQF = 0
    outQR = 2 * N

    #グラフに関する変数
    WAVE_GRAPH_VAL_NUM = Q_LEN

    fig = plt.figure()
    plt.subplots_adjust(wspace=0.6, hspace=1) # 余白を設定
    wave_x = np.arange(0, WAVE_GRAPH_VAL_NUM , 1)
    freq_x = np.fft.fftfreq(N, d=T_s)
    inFreq = np.fft.fft(np.zeros((N, 1)))
    outFreq = np.fft.fft(np.zeros((N, 1)))
    axs = [] #各グラフ
    axs.append(fig.add_subplot(221 + 0)) #左上,波(input)
    axs.append(fig.add_subplot(221 + 2)) #左下,波(output)
    axs.append(fig.add_subplot(221 + 1)) #右上,周波数特性(input)
    axs.append(fig.add_subplot(221 + 3)) #右下,周波数特性(output)
    axs.append(fig.add_subplot(221 + 0)) #左上,inQ front
    axs.append(fig.add_subplot(221 + 2)) #左下,outQ Reqr
    axs.append(fig.add_subplot(221 + 0)) #左上,inQ convert領域
    axs.append(fig.add_subplot(221 + 2)) #左下,outQ converted領域

    lines = [] #各ラインオブジェクト
    for i in [0,1]:
        lines.append(
            axs[i].plot(wave_x,[np.nan] * len(wave_x),"blue")[0])
    for i in [2,3]:
        lines.append(
            axs[i].plot(freq_x,[np.nan] * len(freq_x),"blue")[0])
    for i in [4,5]:
        lines.append(
            axs[i].plot([0,0],[-1,1],"red")[0])
    for i in [6,7]:
        lines.append(
            axs[i].plot([0,0,100,100,0],[-1,1,1,-1,-1],"green")[0])

    samplingCount = 0

    def __init__(self):

        self.stream = sd.Stream(
            channels=self.CHANNEL,
            samplerate=self.F_s,
            callback=self.audioCallback)

        self.aniInQ = FuncAnimation(
            self.fig,
            self.plotGraphs,
            init_func=self.initGraphs,
            interval=self.T_s,
            blit=True)

        with self.stream:
            plt.show()

    def initGraphs(self):
        #個別グラフ設定
        self.axs[0].set_title("Input Voice Wave")
        self.axs[1].set_title("output Voice Wave")
        self.axs[2].set_title("Input Freqency Response")
        self.axs[3].set_title("output Freqency Response")
        #波形グラフ共通設定
        for i in [0,1]:
            self.axs[i].set_ylim(-1,1)
            self.axs[i].set_xlim(0,self.WAVE_GRAPH_VAL_NUM)
            self.axs[i].set_xlabel("data index[-]")
            self.axs[i].set_ylabel("digital value[-]")
            self.lines[i].set_ydata([np.nan] * len(self.wave_x))
        #周波数特性グラフ共通設定
        for i in [2,3]:
            self.axs[i].set_ylim(-0.1,2)
            self.axs[i].set_xlim(min(self.freq_x), max(self.freq_x))
            self.axs[i].set_xlabel("Freqency[rad/s]")
            self.axs[i].set_ylabel("digital value[-]")
            self.lines[i].set_ydata([np.nan] * len(self.freq_x))
        #縦線グラフ共通設定
        for i in [4,5]:
            self.lines[i].set_data([0,0],[-1,1])
        #convert領域グラフ共通設定
        for i in [6,7]:
            self.lines[i].set_data([0,0,100,100,0],[-1,1,1,-1,-1])
        return self.lines

    def plotGraphs(self,count):
        self.plotWaves()
        self.plotFreqs()
        return self.lines


    def plotWaves(self):
        """波(input),(output)をプロ ット"""
        #波(input) inQ
        self.lines[0].set_ydata(self.inQ)
        self.lines[4].set_xdata([self.inQF,self.inQF])
        self.lines[6].set_xdata(
            np.array([self.inQR+1]*5) +
            np.array([0,0,self.N,self.N,0]))
        #波(output) outQ
        self.lines[1].set_ydata(self.outQ)
        self.lines[5].set_xdata([self.outQR,self.outQR])
        self.lines[7].set_xdata(
            np.array([self.outQF]*5) +
            np.array([0,0,self.N,self.N,0]))

    def plotFreqs(self):
        """周波数特性(input),(output)をプロ ット"""
        self.lines[2].set_ydata(abs(self.inFreq))
        self.lines[3].set_ydata(abs(self.outFreq))
        
    def inqueue(self, q, start, data):
        dataLen = len(data)
        qLen = len(q)
        for i in range(dataLen):
            index = (start + i) % qLen
            q[index] = data[i]
        start = index
        
    def dequeue(self, q, start, dataLen):
        data = []
        qLen = len(q)
        for i in range(dataLen):
            index = (start + i) % qLen
            data.append(q[index])
        start = index
        return data
        

    def convertWave(self, convertData):
        #波(input)        →周波数特性(input)
        self.inFreq = np.fft.fft(convertData)
        #周波数特性(input) →周波数特性(output) : filtering
        self.outFreq = self.inFreq * 50
        #周波数特性(output)→波(output)
        convertedData = np.fft.ifft(self.outFreq).real
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
        for i in range(sampleLen):
            self.inQ[(self.inQF + i)%self.Q_LEN] = indata[i]
        self.inQF = (self.inQF + sampleLen) % self.Q_LEN
        #T_fftのタイミング>=T_sが一定回数のタイミングで、audioCallback2を呼び出す
        if self.samplingCount >= self.N:
            threadConvert = threading.Thread(target=self.audioCallback2)
            threadConvert.start()
            self.samplingCount = self.samplingCount % self.N
        #リングQから取り出し
        for i in range(sampleLen):
            outdata[i] = self.outQ[(self.outQR+i)%self.Q_LEN]
        self.outQR = (self.outQR +  sampleLen) % self.Q_LEN

        print("sampling : %d"%(self.samplingCount))



if __name__ == '__main__':
    Changer()