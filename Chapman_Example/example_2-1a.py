import dss
import math

V_low_single = 0.48 # kV

V_low_line = V_low_single*math.sqrt(3) # kV

r_line = 0.18 # ohm
x_line = 0.24 # ohm

P_Load_single = 33 # kW
Q_Load_single = 25 # kvar

P_Load_total = P_Load_single*3
Q_Load_total = Q_Load_single*3

dss_engine = dss.DSS
dss_text = dss_engine.Text
dss_circuit = dss_engine.ActiveCircuit

dss_text.Command = "Clear"
dss_text.Command = f"New Circuit.TransmissionExample basekv={V_low_line} phases=3"
dss_text.Command = f"Edit Vsource.source bus1=SwingBus basekv={V_low_line} pu=1.0 Angle=0 BaseFreq=60 MVAsc3=1e12 MVASC1=1e12"
dss_text.Command = f"New Line.L12 Bus1=SwingBus Bus2=Bus2 Phases=3 r1={r_line} x1={x_line} length=1 units=none"
dss_text.Command = f"New Load.Load Bus1=Bus2 Phases=3 kV={V_low_line} kW={P_Load_total} kvar={Q_Load_total} model=1"
dss_text.Command = f"Set VoltageBases = [{V_low_line}]"
dss_text.Command = "CalcVoltageBases"
dss_text.Command = "Solve"

# 5. 輸出結果
print("\n" + "="*30)
print(f"{'Bus Name':<10} | {'Voltage (pu)':<12}")
print("-" * 30)

for name in dss_circuit.AllBusNames:
    # 關鍵修正：使用 SetActiveBus 來切換目前的匯流排
    dss_circuit.SetActiveBus(name)
    
    # puVmagAngle 會回傳一個 list: [mag1, ang1, mag2, ang2, mag3, ang3]
    # 我們取第一相 (index 0) 的幅值即可
    pu_v = dss_circuit.Buses.puVmagAngle[0]
    
    print(f"{name:<10} | {pu_v:.6f} pu")

print("="*30)

# 將 L12 設為目前運作的元件
dss_circuit.SetActiveElement("Line.L12")

# 取得該元件的損失 [P_loss, Q_loss] (單位為瓦特 W 和乏 var)
line_losses = dss_circuit.ActiveElement.Losses
currents = dss_circuit.ActiveElement.CurrentsMagAng

i_a_mag = currents[0]  # A相電流幅值 (Ampere)
i_a_ang = currents[1]  # A相電流角度 (Degree)

print(f"L12 A相電流: {i_a_mag:.2f} A, 角度: {i_a_ang:.2f}°")
print(f"線路L12每相的實功損失: {line_losses[0]/3:.4f} W")

