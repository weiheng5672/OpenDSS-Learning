
import math

from dss import DSS as dss_engine

V_low_single = 0.48 # kV
V_high_single = 4.8 # kV
S_single = 50.0 # kVA

V_low_line = V_low_single*math.sqrt(3) # kV
V_high_line = V_high_single*math.sqrt(3) # kV
S_total = S_single * 3 # kVA

r_line = 0.18 # ohm
x_line = 0.24 # ohm

P_Load_single = 33 # kW
Q_Load_single = 25 # kvar

P_Load_total = P_Load_single*3
Q_Load_total = Q_Load_single*3

x_percent = 0.05 # pu
r_percent = 0.01 # pu


text = dss_engine.Text
circuit = dss_engine.ActiveCircuit

text.Command = "Clear"
text.Command = f"New Circuit.TransmissionExample basekv={V_low_line} phases=3"
text.Command = f"Edit Vsource.source bus1=SourceBus basekv={V_low_line} pu=1.0 Angle=0 BaseFreq=60 MVAsc3=1e12 MVASC1=1e12"

text.Command = "New Transformer.T1 phases=3 windings=2"
text.Command = "~ buses=[SourceBus, HighBus1]"
text.Command = f"~ conns=[wye, wye] kvs=[{V_low_line:.6f}, {V_high_line:.6f}] kvas=[{S_total}, {S_total}]"
text.Command = f"~ XHL={x_percent:.6f} %Rs=[{r_percent:.6f}, 0]"

text.Command = f"New Line.L12 Bus1=HighBus1 Bus2=HighBus2 Phases=3 r1={r_line} x1={x_line} length=1 units=none"

text.Command = "New Transformer.T2 phases=3 windings=2"
text.Command = "~ buses=[HighBus2, LoadBus]"
text.Command = f"~ conns=[wye, wye] kvs=[{V_high_line:.6f}, {V_low_line:.6f}] kvas=[{S_total}, {S_total}]"
text.Command = f"~ XHL={x_percent:.6f} %Rs=[{r_percent:.6f}, 0]"

text.Command = f"New Load.Load Bus1=LoadBus Phases=3 kV={V_low_line} kW={P_Load_total} kvar={Q_Load_total} model=1"
text.Command = f"Set VoltageBases = [{V_high_line}, {V_low_line}]"
text.Command = "CalcVoltageBases"
text.Command = "Solve"


# 輸出結果
print("\n" + "="*30)
print(f"{'Bus Name':<10} | {'Voltage (pu)':<12}")
print("-" * 30)

for name in circuit.AllBusNames:
    # 關鍵修正：使用 SetActiveBus 來切換目前的匯流排
    circuit.SetActiveBus(name)
    
    # puVmagAngle 會回傳一個 list: [mag1, ang1, mag2, ang2, mag3, ang3]
    # 我們取第一相 (index 0) 的幅值即可
    pu_v = circuit.Buses.puVmagAngle[0]
    
    print(f"{name:<10} | {pu_v:.6f} pu")

print("="*30)

# 將 L12 設為目前運作的元件
circuit.SetActiveElement("Line.L12")

# 取得該元件的損失 [P_loss, Q_loss] (單位為瓦特 W 和乏 var)
line_losses = circuit.ActiveElement.Losses
currents = circuit.ActiveElement.CurrentsMagAng

i_a_mag = currents[0]  # A相電流幅值 (Ampere)
i_a_ang = currents[1]  # A相電流角度 (Degree)

print(f"L12 A相電流: {i_a_mag:.2f} A, 角度: {i_a_ang:.2f}°")
print(f"線路L12每相的實功損失: {line_losses[0]/3:.4f} W")

#

tr = circuit.Transformers
print(tr)

trs = circuit.Transformers.AllNames
print(trs)

tr_capacity = circuit.Transformers.kva
print(tr_capacity)

name = circuit.Transformers.Next
print(name)

tr_name = circuit.Transformers.First
print(tr_name)

total_tr_capacity_kva = 0
while tr_name:
    total_tr_capacity_kva += circuit.Transformers.kva
    tr_name = circuit.Transformers.Next
    
print(total_tr_capacity_kva)



line = circuit.Lines
print(line)

lines = circuit.Lines.AllNames
print(lines)
