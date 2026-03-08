
# --------匯入介接官方OpenDSS的COM介面的庫-------------
import win32com.client
# ---------------------------------------------------

dss = win32com.client.Dispatch("OpenDSSEngine.DSS")
print("OpenDSS COM 已啟動:", dss.Start(0))
print(dss)

"""
來檢視看看 這都做了些什麼
首先 要成功執行程式 電腦必須先安裝官方的OpenDSS
win32com.client套件不包含程式本體

官方的OpenDSS有非常陽春的GUI介面
如果不使用官方的GUI介面
就要透過COM 這個官方提供的API 去調用OpenDSS的核心功能 也就是所謂的 DSS引擎
win32com.client套件 就是在py中 與COM溝通的庫

在這段程式中 dss是python中的變數 他指向 後面的那堆東西 可理解為一個物件
這個對象 代表 OpenDSS引擎

dss是python中的變數 指向 DSS引擎物件
dss.Start(0) 可以理解為 打開DSS引擎 可以將 Start(0) 看作方法 一種功能 表示啟動
成功會回傳 True

並且可以看見直接打印dss變數 結果確實是一個物件 
COMObject OpenDSSEngine.DSS

"""