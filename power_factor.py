import math
from dss import DSS as dss_engine

"""
透過opendss演示 加入電容 改善功率因數的習題
最後可以看到投入電容能夠明顯改善功因
減少電流 提升電壓 減少線損
"""

# --- 參數設定 ---
V_base = 161 
S_base = 100 
Z_base = (V_base**2) / S_base 

r12_pu, x12_pu = 0.02, 0.04
r12, x12 = r12_pu * Z_base, x12_pu * Z_base

P_Mw, Q_Mvar = 40, 30
Q_cap_kvar = 25000  # 假設投入25 Mvar

# --- 初始化 OpenDSS ---
text = dss_engine.Text
circuit = dss_engine.ActiveCircuit

def build_circuit():
    text.Command = "Clear"
    text.Command = f"New Circuit.TransmissionExample basekv={V_base} phases=3"
    text.Command = f"New Line.L12 Bus1=SourceBus Bus2=Load_Bus Phases=3 r1={r12} x1={x12} length=1 units=none"
    text.Command = f"New Load.Load2 Bus1=Load_Bus Phases=3 kV={V_base} kW={P_Mw*1000} kvar={Q_Mvar*1000} model=1"
    # 定義電容，但初始狀態設為關閉 (enabled=no)
    text.Command = f"New Capacitor.Cap1 Bus1=Load_Bus Phases=3 kV={V_base} kvar={Q_cap_kvar} enabled=no"
    text.Command = f"Set VoltageBases = [{V_base}]"
    text.Command = "CalcVoltageBases"

def run_and_report(case_name):
    circuit.Solution.Solve()
    
    # 取得負載端電壓 (取第一相 pu 值)
    """
    這邊的 SetActiveBus 是 opendss的API
    circuit 是 py變數 可以理解成 指向 DSS引擎物件的一個變數
    對circuit這個變數 使用 . 算符 就是透過 circuit這個變數 調用opendss提供的API

    SetActiveBus 字面上意思是 設定主動匯流排 但他的意思是說 當我們進行完潮流計算之後
    我們把注意力放在 其中一個 指定的匯流排的意思 
    """
    circuit.SetActiveBus("Load_Bus")  # 這一行 設定 潮流計算之後 我們關注的匯流排

    v_pu = circuit.Buses.puVmagAngle[0] # 這裡的Buses的電壓標么值和角度 就是前一行指定的匯流排的

    # 當然 opendss 也有API 可以直接回傳所有節點的電壓
    # 這邊沒有使用那種看似更單純的方式 是因為 那種方式在opendss才是特例
    

    # 取得線路損耗 (傳回值為 Watt, Var)
    """
    這邊的 SetActiveElement 是 opendss的API
    circuit 是 py變數 可以理解成 指向 DSS引擎物件的一個變數
    對circuit這個變數 使用 . 算符 就是透過 circuit這個變數 調用opendss提供的API

    SetActiveElement 字面上意思是 設定主動元件 這容易引起誤會 他不是電子學中的主動元件
    他的意思是 當我們進行完潮流計算之後
    我們把注意力放在 其中一個 指定的元件的意思 
    """
    circuit.SetActiveElement("Line.L12") # 這一行 設定 潮流計算之後 我們關注的元件
    loss = circuit.ActiveElement.Losses  # 這裡的元件的losses 就是前一行指定的元件的
    print(loss)
    # 所謂潮流 就是 所有節點的電壓 和所有支路的功率
    # 節點就是 bus
    # 支路就是 元件

    # opendss 也有API 可以直接回傳所有元件的losses
    # 這邊沒有使用那種看似更單純的方式 是因為 那種方式在opendss才是特例


    # 取得系統側總功率來計算 PF
    line_powers = circuit.ActiveElement.Powers
    print(line_powers)
    # 這邊的元件 還是 Line.L12
    # 但這次透過 Powers API 取得 這個支路的功率

    # 先對於 Powers API 回傳的信息有所了解
    # Line.L12 有流進 流出 兩個端點 每個端點都有 a b c 三相 
    # 每端點的每相 都有P和Q 
    # a相 流進的PQ 流出的PQ
    # b相 流進的PQ 流出的PQ
    # b相 流進的PQ 流出的PQ
    # 所以 Powers API 回傳的信息 會有12個數字
    # 這12個數字的前6個數字就代表流進 後6個數字就代表流出
    # 並且 從直接打印結果可以看出 後面 6個數字 是負的
    # 負號就是流出的意思
    # opendss元件的參照方向 預設流入為正 負值代表流出

    # 對比回傳losses的API
    # 根據直接打印結果 回傳lose的API就回傳兩個數字
    # 分別是P的總損耗 和Q的總損耗 
    
    p_in = sum(line_powers[0:6:2]) 
    # line_powers[0] + line_powers[2] + line_powers[4]
    # line_powers[0] 流入a相的P
    # line_powers[2] 流入b相的P
    # line_powers[4] 流入c相的P

    q_in = sum(line_powers[1:6:2]) 
    # line_powers[1] + line_powers[3] + line_powers[5] 
    # line_powers[1] 流入a相的Q
    # line_powers[3] 流入b相的Q
    # line_powers[5] 流入c相的Q

    # 這邊能驗證看看 
    # 這些數字相加 就是線損
    losses_P_check = sum(line_powers[0:12:2]) 
    losses_Q_check = sum(line_powers[1:12:2]) 
    print(losses_P_check)
    print(losses_Q_check)


    pf = abs(p_in) / math.sqrt(p_in**2 + q_in**2 + 1e-9)

    print(f"--- {case_name} ---")
    print(f"負載電壓: {v_pu:.4f} pu")
    print(f"線路損耗: {loss[0]/1000:.2f} kW / {loss[1]/1000:.2f} kvar")
    print(f"系統側功率因數 (PF): {pf:.4f}\n")

# --- 執行流程 ---
build_circuit()

# 1. 執行未投切電容的情況
run_and_report("未投入電容 (Baseline)")

# 2. 投入電容並重新計算
text.Command = "Capacitor.Cap1.enabled=yes"
run_and_report("已投入 15 Mvar 電容 (Improved)")
