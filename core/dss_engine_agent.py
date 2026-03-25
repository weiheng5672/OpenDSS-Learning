import os
import numpy as np
from pathlib import Path
from dss import DSS as dss_engine

# ---------------三種路徑概念-----------------------

# 相對路徑 執行程式時所在的目錄 這裡是「專案主目錄」

# 絕對路徑 檔案在作業系統中的全部路徑

# 關鍵：OpenDSS 環境路徑 每個腳本資料夾的路徑
# Master.dss 裡面通常會 透過Redirect 引用同資料夾下的 Lines.dss 或 Transformers.dss
# OpenDSS 引擎在執行 Redirect 或 Compile 時，它是相對於它目前的工作目錄去找這些子檔案
# 如果 OpenDSS 引擎的「視線」沒切換到這個資料夾，它就會報錯說找不到這些組件

#------------------------------------------------------------------------------------


# 使用社群版DSS進行分析的類別
class EngineAgent:
    """
    OpenDSS 分析協作類別：
    封裝複雜的路徑切換邏輯，並提供簡潔的 API 與 OpenDSS 引擎交互。
    """
    
    def __init__(self, dss_file_path):
        """
        初始化分析器：
        1. 將輸入路徑標準化為絕對路徑，消除相對路徑的不確定性。
        2. 綁定 OpenDSS 的 Text 介面（指令輸入）與 Circuit 介面（數據提取）。
        """
        
        #---------------------------------------------------
        # 這裡將輸入路徑轉為絕對路徑
        #---------------------------------------------------
        self.dss_file_path = Path(dss_file_path).absolute()
        #---------------------------------------------------
        

        # 引擎核心組件綁定
        # self.text: 用於下達 DSS 命令（如 "New Line..."、"Solve"）
        # self.circuit: 用於讀取當前電路狀態（如電壓、電流、損耗）
        # ----------------------------------------
        self.text = dss_engine.Text
        # ----------------------------------------
        self.circuit = dss_engine.ActiveCircuit
        # ---------------------------------------- 

        self.status = "Success"
        self.error_msg = ""
        
        # 執行初始化編譯 (封裝路徑切換邏輯)
        self._compile_dss()


    def _compile_dss(self):
        """
        私有方法：處理路徑敏感的編譯流程。
        OpenDSS 的 Redirect/Compile 指令會根據當前工作目錄（CWD）尋找子檔案。
        """
        
        # 這裡的 self.dss_file_path 已經是「絕對路徑」
        
        original_cwd = os.getcwd()   # 記住「專案主目錄」
        
        try:
            if not self.dss_file_path.exists():
                self.status = "Error"
                self.error_msg = "檔案不存在"
                return

            # 切換到「腳本資料夾」
            os.chdir(self.dss_file_path.parent)
            # 清空引擎狀態
            self.text.Command = "Clear"
            # 使用絕對路徑 引導引擎編譯指定腳本
            self.text.Command = f"compile \"{self.dss_file_path.name}\""
            # 一旦編譯完 
            # 此後 在 py程式中 透過 self.text 和 self.circuit 就能夠和電路進行交互
            # 而這些功能都封裝在這個 EngineAgent類別 裡面
            # 也就是說 用這種方式雖然可以免去路徑問題 
            # 但如果我想要透過API調用 任何功能 都需要在這個類別中 再自定義相關的函數
            
            """
            透過 self.text 和 self.circuit 就能夠和電路進行交互的含意就是 
            我其實不再需要dss腳本了 只需要在py 中透過 self.text.Command 輸入字串即可
            但是 純字串的可讀性是很差的
            所以 還是需要dss腳本從外匯入 dss腳本透過vscode的拓展套件 可以顯著提高可讀性
            但是 在py 中 進行 純字串 交互的最大優點是 我可以通過格式化的輸入 在字串中嵌入變數值
            比方
            
            f"New Line.L12 Bus1=SwingBus Bus2=Bus2 Phases=3 r1={r12} x1={x12} length=1 units=none"
            
            其中 r12 x12 就是 用py 變數

            目前 應對這種兩難的方式 還是 先在 py 使用變數嵌入字串
            然後再匯出dss腳本查看 
            儘管用這種方式 其實不用匯出也能執行
            
            """
        
        except Exception as e:
            self.status = "Error"
            self.error_msg = str(e).replace('\n', ' ').strip()
        
        finally:
            os.chdir(original_cwd)


    def solve(self):
        self.circuit.Solution.Solve()


    def all_voltage(self):
        return self.circuit.AllBusVmagPu


    def _setup_shapes(self, load_mults):
        # 將 Python List 轉為 OpenDSS 字串格式
        mult_str = f"({','.join(map(str, load_mults))})"
        # 定義名為 'CommonLoad' 的 LoadShape
        self.text.Command = f"New LoadShape.CommonLoad npts={len(load_mults)} interval=1 mult={mult_str}"


    def set_load_profile(self, load_profile, shape_name="CommonLoad"):
        """
        僅負責設定 LoadShape 並將其綁定到所有負載。
        不執行 Solve。
        """
        # 1. 透過原本的私有方法定義曲線
        self._setup_shapes(load_profile)
        
        # 2. 將所有負載綁定到此曲線
        load_names = self.circuit.Loads.AllNames
        for name in load_names:
            # 這裡假設你想統一控制所有 Load，若有特定需求可再過濾名稱
            self.text.Command = f"Load.{name}.Daily={shape_name}"
            
        print(f"Successfully bound {len(load_names)} loads to {shape_name}.")


    def run_timeseries_analysis(self, steps):
            """
            專門負責執行時序求解與收集結果。
            steps: 執行的步數 (例如 len(load_profile))
            """
            results = {
                "hours": [],
                "v_min": [],
                "v_max": [],
                "losses": []
            }

            # 設定模擬模式
            self.text.Command = "Set Mode=daily Number=1 StepSize=1h"
            
            for i in range(steps):
                self.text.Command = f"Set Hour={i}"
                
                # 執行計算
                self.circuit.Solution.Solve()
                
                # 提取數據
                v_pu = np.array(self.circuit.AllBusVmagPu)
                v_pu_filtered = v_pu[v_pu > 0.1] 
                
                results["hours"].append(i)
                results["v_min"].append(np.min(v_pu_filtered))
                results["v_max"].append(np.max(v_pu_filtered))
                
                # 取實功損耗 (kW)
                loss_kw = self.circuit.Losses[0] / 1000.0
                results["losses"].append(loss_kw)

            return results



