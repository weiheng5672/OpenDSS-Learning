import win32com.client
import inspect
import math
import os

def run_dss_three_phase_fixed(pf, mode):
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

    # --- 2. 建立腳本：確保編法完全符合三相規範 ---
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
    
    # 上述的電路是三相的 新增電路的部分 按照慣例 Basekv要填入的是線電壓
    # 以上電路 只有一個變壓器 變壓器兩端的 匯流排1就是 SourceBus 匯流排2就是 LoadBus
    # 但為計算電壓調整率 在LoadBus 掛上一個負載
    # 在 OpenDSS 中，pf的正負號用來表示相位關係：正值代表滯後，負值代表領先。
    # 短路試驗（高壓側加壓，低壓側短路）測得的功率損耗 Psc，是變壓器在額定電流下一次和二次繞組電阻產生的總銅損。
    # 它是一個整體的、不可分割的實測值。 OpenDSS允許為每個繞組獨立設定 %R，但在絕大多數情況下，只有總的 Psc資料。
    # 此時，一種標準的簡化處理就是將全部損耗歸算到一次側（高壓側）

    # --- 3. 啟動與執行 ---
    try:
        dss_obj = win32com.client.Dispatch("OpenDSSEngine.DSS")
        dss_obj.Start(0)
        dss_text = dss_obj.Text
        dss_circuit = dss_obj.ActiveCircuit
    except Exception as e:
        print(f"啟動 OpenDSS 失敗: {e}")
        return

    abs_path = os.path.abspath("transformer_3p_win.dss")
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(dss_script)
    
    dss_text.Command = f"compile \"{abs_path}\""

    # --- 4. 健檢：確認是否 Solve 成功 ---
    if not dss_circuit.Solution.Converged:
        print("警告：電力潮流未收斂！請檢查電路連接。")
        return

    # --- 5. 提取結果 ---
    # 這裡我們換一個更穩定的方式：取得 LoadBus 的標么電壓
    dss_circuit.SetActiveBus("LoadBus")
    v_load_pu_list = dss_circuit.ActiveBus.puVmagAngle
    
    if not v_load_pu_list or len(v_load_pu_list) == 0:
        print("錯誤：無法取得節點電壓。")
        return
        
    v_load_pu = v_load_pu_list[0] # 取 Phase A
    
    if v_load_pu == 0:
        print("錯誤：電壓值為 0，請檢查電壓基準 (Voltagebases) 設定。")
        return

    vr = (1.0 - v_load_pu) / v_load_pu * 100
    print(f"三相模型 -> 功因: {pf} {mode}, 電壓: {v_load_pu:.4f} pu, VR: {vr:.4f}%")

if __name__ == "__main__":
    run_dss_three_phase_fixed(0.8, "lagging")
    run_dss_three_phase_fixed(1.0, "lagging")
    run_dss_three_phase_fixed(0.8, "leading")