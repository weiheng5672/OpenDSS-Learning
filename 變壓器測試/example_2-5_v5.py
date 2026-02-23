from dss import dss
import inspect
import math
import os

def run_dss_py_three_phase(pf, mode):
    # --- 1. 參數計算 ---
    Vp_single = 2.3
    Vs_single = 0.23
    S_single = 15.0
    
    Vp_line = Vp_single * math.sqrt(3)
    Vs_line = Vs_single * math.sqrt(3)
    S_total = S_single * 3
    
    res_percent = (160 / (S_single * 1000)) * 100
    z_percent = (47 / (Vp_single * 1000)) * 100
    react_percent = math.sqrt(max(0, z_percent**2 - res_percent**2))
    
    pf_val = pf if mode == "lagging" else -pf

    # --- 2. 建立腳本 ---
    dss_script = inspect.cleandoc(f"""
    Clear
    New Circuit.ThreePhaseTest Basekv={Vp_line:.6f} phases=3
    
    ! 定義 Bus1 與電壓
    Edit Vsource.source Bus1=SourceBus Basekv={Vp_line:.6f} pu=1.0 phases=3
    ~ Z1=[0.0001, 0.0001] Z0=[0.0001, 0.0001]

    ! 定義變壓器：連接 SourceBus 到 LoadBus
    New Transformer.T1 phases=3 windings=2 
    ~ buses=[SourceBus, LoadBus]
    ~ conns=[wye, wye] kvs=[{Vp_line:.6f}, {Vs_line:.6f}] kvas=[{S_total}, {S_total}] 
    ~ XHL={react_percent:.6f} %Rs=[{res_percent:.6f}, 0]

    ! 定義負載：接在 LoadBus
    New Load.L1 Bus1=LoadBus phases=3 Kv={Vs_line:.6f} 
    ~ Kw={S_total * pf:.6f} pf={pf_val} model=1 status=fixed

    Set Voltagebases=[{Vp_line:.6f}, {Vs_line:.6f}]
    Calcvoltagebases
    Solve
    """)

    # --- 3. 執行指令 ---
    abs_path = os.path.abspath("transformer_3p_py.dss")
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(dss_script)
    
    dss.Text.Command = f"compile \"{abs_path}\""

    # --- 4. 健檢 ---
    if not dss.ActiveCircuit.Solution.Converged:
        print("警告：電力潮流未收斂！")
        return

    # --- 5. 提取結果 (修正判斷方式) ---
    dss.ActiveCircuit.SetActiveBus("LoadBus")
    v_load_pu_list = dss.ActiveCircuit.ActiveBus.puVmagAngle
    
    # 檢查長度
    if len(v_load_pu_list) == 0:
        print("錯誤：無法取得節點電壓。")
        return
        
    v_load_pu = v_load_pu_list[0] # 取得 Phase A 的標么電壓
    
    if v_load_pu == 0:
        print("錯誤：電壓值為 0。")
        return

    vr = (1.0 - v_load_pu) / v_load_pu * 100
    print(f"dss-py 三相模型 -> 功因: {pf} {mode:<7}, 電壓: {v_load_pu:.4f} pu, VR: {vr:.4f}%")

if __name__ == "__main__":
    print(f"{'功因狀況':<20} | {'標么電壓':<10} | {'電壓調整率 VR%'}")
    print("-" * 55)
    run_dss_py_three_phase(0.8, "lagging")
    run_dss_py_three_phase(1.0, "lagging")
    run_dss_py_three_phase(0.8, "leading")