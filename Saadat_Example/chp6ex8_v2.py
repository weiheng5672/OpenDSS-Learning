import dss

V_base = 161 # kV
S_base = 100 # MVA
Z_base = (V_base**2) / S_base

# OpenDSS 需要實際阻抗 (Ohm)，需要將 pu 轉為 Ohm
r12_pu = 0.02
x12_pu = 0.04
r12 = r12_pu*Z_base
x12 = x12_pu*Z_base

r23_pu = 0.0125
x23_pu = 0.025
r23 = r23_pu*Z_base
x23 = x23_pu*Z_base

r13_pu = 0.01
x13_pu = 0.03
r13 = r13_pu*Z_base
x13 = x13_pu*Z_base

P_Load = 400 # MW
Q_Load = 250 # Mvar

P_G = 200 # MW
V_pu_G = 1.04


# 初始化 OpenDSS
dss_engine = dss.DSS
dss_text = dss_engine.Text
dss_circuit = dss_engine.ActiveCircuit

# 1. 建立電路 (設定 Bus 1 為 SwingBus)
# BasekV 是線電壓

dss_text.Command = "Clear"

dss_text.Command = f"New Circuit.TransmissionExample basekv={V_base} phases=3 "

dss_text.Command = f"Edit Vsource.source bus1=SwingBus basekv={V_base} pu=1.05 Angle=0 BaseFreq=60 MVAsc3=1e12 MVASC1=1e12"

# 2. 定義線路 (使用阻抗矩陣，長度設為 1)

dss_text.Command = f"New Line.L12 Bus1=SwingBus Bus2=Bus2 Phases=3 r1={r12} x1={x12} length=1 units=none"

dss_text.Command = f"New Line.L23 Bus1=Bus2 Bus2=Bus3 Phases=3 r1={r23} x1={x23} length=1 units=none"

dss_text.Command = f"New Line.L13 Bus1=SwingBus Bus2=Bus3 Phases=3 r1={r13} x1={x13} length=1 units=none"

# 3. 定義負荷 (Load)
# OpenDSS 預設是平衡三相，kV 設定為線電壓
dss_text.Command = f"New Load.Load2 Bus1=Bus2 Phases=3 kV={V_base} kW={P_Load*1000} kvar={Q_Load*1000} model=1"

# 發電機指定P和V的大小是 model=3
dss_text.Command = f"New Generator.Generator Bus1=Bus3 Phases=3 kV={V_base} kW={P_G*1000} Vpu={V_pu_G} model=3"

# 4. 執行潮流計算
dss_text.Command = f"Set VoltageBases = [{V_base}]"
dss_text.Command = "CalcVoltageBases"
dss_text.Command = "Solve"

# 5. 輸出結果 (修正版)
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

test = dss_circuit.AllElementNames
print(test)

test = dss_circuit.AllElementLosses
print(test)
print(f"搖擺匯流排注入P:{-test[0]/1000:<5.2f}kW,Q:{-test[1]/1000:<5.2f}kvar")
print(f"線路1-2損耗  P:{test[2]/1000:<5.2f}kW,Q:{test[3]/1000:<5.2f}kvar")
print(f"線路2-3損耗  P:{test[4]/1000:<5.2f}kW,Q:{test[5]/1000:<5.2f}kvar")
print(f"線路1-3損耗  P:{test[6]/1000:<5.2f}kW,Q:{test[7]/1000:<5.2f}kvar")
print(f"負載損耗     P:{test[8]/1000:<5.2f}kW,Q:{test[9]/1000:<5.2f}kvar")
print(f"發電機注入   P:{-test[10]/1000:<5.2f}kW,Q:{-test[11]/1000:<5.2f}kvar")

test = dss_circuit.AllBusNames
print(test)

test = dss_circuit.AllBusVmagPu
print(test)
print(f"搖擺匯流排電壓:{test[0]:.5f} pu")
print(f"2號匯流排電壓: {test[3]:.5f} pu")
print(f"3號匯流排電壓: {test[6]:.5f} pu")


test = dss_circuit.Generators.RegisterValues
print(test)