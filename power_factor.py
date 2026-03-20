import math
from dss import DSS as dss_engine

V_base = 161 # kV
S_base = 100 # MVA
Z_base = (V_base**2) / S_base

# OpenDSS 需要實際阻抗 (Ohm)，需要將 pu 轉為 Ohm
r12_pu = 0.02
x12_pu = 0.04
r12 = r12_pu*Z_base
x12 = x12_pu*Z_base


P_Mw = 40
Q_Mvar = 30


# 初始化 OpenDSS
text = dss_engine.Text
circuit = dss_engine.ActiveCircuit

# 1. 建立電路 (設定 Bus 1 為 SwingBus)
# BasekV 是線電壓

text.Command = "Clear"

text.Command = f"New Circuit.TransmissionExample basekv={V_base} phases=3 "

text.Command = f"Edit Vsource.source bus1=Swing_Bus basekv={V_base} pu=1.0 Angle=0 BaseFreq=60 MVAsc3=1e12 MVASC1=1e12"

# 2. 定義線路 (使用阻抗矩陣，長度設為 1)

text.Command = f"New Line.L12 Bus1=Swing_Bus Bus2=Load_Bus Phases=3 r1={r12} x1={x12} length=1 units=none"


# 3. 定義負荷 (Load)
# OpenDSS 預設是平衡三相，kV 設定為線電壓
text.Command = f"New Load.Load2 Bus1=Load_Bus Phases=3 kV={V_base} kW={P_Mw*1000} kvar={Q_Mvar*1000} model=1"

# 4. 定義電容器 (Capacitor)
# 假設加入 15 Mvar 的電容
Q_cap_Mvar = 30
text.Command = f"New Capacitor.Cap1 Bus1=Load_Bus Phases=3 kV={V_base} kvar={Q_cap_Mvar*1000}"

# 5. 執行潮流計算
text.Command = f"Set VoltageBases = [{V_base}]"
text.Command = "CalcVoltageBases"

circuit.Solution.Solve()

circuit.SetActiveBus("Load_Bus")
pu_v = circuit.Buses.puVmagAngle
print(f"電壓大小:{pu_v[0]:.6f} pu；電壓角度:{pu_v[1]:.6f} ")


circuit.SetActiveElement("Load.Load2")
# 取得複數功率 [P1, Q1, P2, Q2, P3, Q3] (單位為 kW, kvar)
powers = circuit.ActiveElement.Powers
print(f"負載實功: {powers[0]/1000:.4f} MW；負載虛功: {powers[1]/1000:.4f} Mvar")
print(f"負載功因: {circuit.Loads.PF:.4f}")

circuit.SetActiveElement("Line.L12")
line_losses = circuit.ActiveElement.Losses # 回傳 [P_loss, Q_loss]
print(f"L12 線路實功損耗: {line_losses[0]/1000:.4f} kW")
print(f"L12 線路虛功損耗: {line_losses[1]/1000:.4f} kvar")

line_powers = circuit.ActiveElement.Powers
p_in = sum(line_powers[0:6:2])
q_in = sum(line_powers[1:6:2])
pf_improved = abs(p_in) / math.sqrt(p_in**2 + q_in**2)
print(f"系統側看進去的 PF: {pf_improved:.4f}")

