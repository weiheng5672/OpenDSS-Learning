import os

# --------匯入OpenDSS引擎-------------
from dss import DSS as dss_engine
# -----------------------------------

# --------------------------------------------------------
# dss引擎兩大API: 1. Text；2. ActiveCircuit
# --------------------------------------------------------
# text 是py中的變數 他指向 dss引擎中的 Text API
# 透過 變數text 做的事情 就相當於是在向 opendss下指令
text = dss_engine.Text

print(text)

# circuit 是py中的變數 他指向 dss引擎中的 電路 ActiveCircuit
# 透過 變數circuit 做的事情 就相當於是 查看 這個電路
# 在這個階段 電路還是空的 
circuit = dss_engine.ActiveCircuit

print(circuit)

"""
和官方版本不同 社群版更簡潔 載入庫以後就直接將dss引擎作為物件使用 不需要再啟動
當頻繁和DSS腳本互動 COM就會明顯拖慢執行速度
"""


