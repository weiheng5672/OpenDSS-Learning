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
    circuit.SetActiveBus("Load_Bus")
    v_pu = circuit.Buses.puVmagAngle[0]
    
    # 取得線路損耗 (傳回值為 Watt, Var)
    circuit.SetActiveElement("Line.L12")
    loss = circuit.ActiveElement.Losses 
    
    # 取得系統側總功率來計算 PF
    line_powers = circuit.ActiveElement.Powers
    p_in = sum(line_powers[0:6:2])
    q_in = sum(line_powers[1:6:2])
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
