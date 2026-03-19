import dss

V_base = 161 # kV
S_base = 100 # MVA
Z_base = (V_base**2) / S_base

# OpenDSS 需要實際阻抗 (Ohm)，需要將 pu 轉為 Ohm
r12_pu = 0.12
x12_pu = 0.16
r12 = r12_pu*Z_base
x12 = x12_pu*Z_base

P_Mw = 100 
Q_Mvar = 50


# 初始化 OpenDSS
dss_engine = dss.DSS
text = dss_engine.Text
circuit = dss_engine.ActiveCircuit

# 1. 建立電路 (設定 Bus 1 為 SwingBus)
# BasekV 是線電壓

text.Command = "Clear"

text.Command = f"New Circuit.Question_6_11 basekv={V_base} phases=3 "

text.Command = f"Edit Vsource.source bus1=Swing_Bus basekv={V_base} pu=1.0 Angle=0 BaseFreq=60 MVAsc3=1e12 MVASC1=1e12"

# 2. 定義線路 (使用阻抗矩陣，長度設為 1)

text.Command = f"New Line.L12 Bus1=Swing_Bus Bus2=Load_Bus Phases=3 r1={r12} x1={x12} length=1 units=none"


# 3. 定義負荷 (Load)
# OpenDSS 預設是平衡三相，kV 設定為線電壓
text.Command = f"New Load.Load2 Bus1=Load_Bus Phases=3 kV={V_base} kW={P_Mw*1000} kvar={Q_Mvar*1000} model=1"

text.Command = f"Set VoltageBases = [{V_base}]"
text.Command = "CalcVoltageBases"

circuit.Solution.Solve()

# 5. 輸出結果
bus_names = circuit.AllBusNames

print(bus_names)

circuit.SetActiveBus("Load_Bus")

v_pu = circuit.ActiveBus.puVmagAngle

print(v_pu[0])
print(v_pu[1])


