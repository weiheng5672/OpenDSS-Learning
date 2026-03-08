from dss import DSS as dss_engine
import sys
import os

def run_pure_python_control(dss_file_path):
    if not os.path.exists(dss_file_path):
        print(f"錯誤: 找不到檔案 {dss_file_path}")
        return
    
    # 1. 載入腳本（這時只是把元件定義進記憶體，還沒計算）
    dss_engine.Text.Command = f"compile \"{dss_file_path}\""
    
    # 建立捷徑 (引用)
    circuit = dss_engine.ActiveCircuit
    solution = circuit.Solution

    # 2. 用 Python 指令進行求解 (代替腳本裡的 Solve)
    solution.Solve()

    # 3. 檢查是否成功收斂
    if solution.Converged:
        print("✅ 電力潮流計算成功收斂！")
    else:
        print("❌ 計算失敗，請檢查電路連接。")
        return

    # 4. 打印電壓資訊 (自定義格式，不產生 TXT)
    print(f"\n{'Bus.Node':<15} {'Voltage (V)':<15} {'Angle':<10} {'pu':<10}")
    print("-" * 50)
    
    # 取得所有節點名稱
    node_names = circuit.AllNodeNames
    # 取得複數電壓 (實部, 虛部, 實部, 虛部...)
    v_complex = circuit.AllBusVolts 
    # 取得標么值
    v_pu = circuit.AllBusVmagPu

    for i, name in enumerate(node_names):
        real = v_complex[i*2]
        imag = v_complex[i*2 + 1]
        v_mag = (real**2 + imag**2)**0.5  # 計算模值
        
        print(f"{name:<15} {v_mag:<15.2f} {v_pu[i]:<10.4f}")

    # 5. 打印特定元件的功率 (例如 Load.01)
    print(f"\n{'Element':<20} {'Total P (kW)':<15} {'Total Q (kvar)':<15}")
    print("-" * 50)
    
    # 遍歷感興趣的元件類型（例如 Loads）
    i_load = circuit.Loads.First
    while i_load > 0:
        name = circuit.ActiveElement.Name
        powers = circuit.ActiveElement.Powers # [P1, Q1, P2, Q2...]
        # 加總所有相的功率
        p_total = sum(powers[0::2])
        q_total = sum(powers[1::2])
        print(f"{name:<20} {p_total:<15.2f} {q_total:<15.2f}")
        i_load = circuit.Loads.Next

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_pure_python_control(sys.argv[1])
    else:
        print("請拖放 .dss 檔案到腳本上或提供路徑")