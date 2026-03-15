from core.dss_engine_agent import EngineAgent
import matplotlib.pyplot as plt

def run_test(dss_file_path):
    
    # 數據
    mult = [
        0.4, 0.3, 0.2, 0.2, 0.3, 0.5, 
        0.7, 0.8, 0.9, 1.0, 1.0, 0.9, 
        0.8, 0.7, 0.8, 0.9, 1.0, 1.2, 
        1.3, 1.1, 0.9, 0.7, 0.6, 0.5
    ]
      
    hours = list(range(24))
    
    agent = EngineAgent(dss_file_path)
    
    results = agent.run_timeseries_load(mult)

    # --- 開始繪圖 ---
    # 建立一個包含三個子圖的畫布 (3列1行)
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

    # 1. 繪製原始負載曲線 (Input)
    ax1.plot(hours, mult, marker='o', color='b', label='Load Multiplier')
    ax1.set_ylabel("Load (pu)")
    ax1.set_title("Input: LoadShape Profile")
    ax1.grid(True, linestyle='--')
    ax1.legend()

    # 2. 繪製系統最低電壓變化 (Voltage Output)
    # 這裡假設 results 有存 v_min
    if "v_min" in results:
        ax2.plot(hours, results["v_min"], marker='s', color='r', label='Min Bus Voltage')
        # 畫出一條 0.95 pu 的警告線
        ax2.axhline(y=0.95, color='gray', linestyle=':', label='0.95 pu Limit')
        ax2.set_ylabel("Voltage (pu)")
        ax2.set_title("Output: Minimum System Voltage")
        ax2.grid(True, linestyle='--')
        ax2.legend()

    # 3. 繪製系統總損耗 (Loss Output)
    if "losses" in results:
        ax3.plot(hours, results["losses"], marker='^', color='g', label='Total Losses')
        ax3.set_ylabel("Losses (kW)")
        ax3.set_xlabel("Time (Hour)")
        ax3.set_title("Output: System Power Losses")
        ax3.grid(True, linestyle='--')
        ax3.legend()

    plt.tight_layout() # 自動調整佈局避免文字重疊
    plt.show()
    
    
if __name__ == "__main__":
    
    case1 = "dss_script/case1.dss"
    
    run_test(case1)
    
