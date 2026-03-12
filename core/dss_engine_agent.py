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

    # 必須定義一個函數 去調用求解
    def solve(self):
        """
        觸發電力潮流計算（Power Flow Solution）。
        將靜態的「拓樸定義」轉化為動態的「物理平衡態」。
        """
        # -----------------------------
        self.text.Command = "Solve"
        # -----------------------------
        
        # 之所以 求解 單獨定義出來 是因為 他不總是需要
    
        """
        在 OpenDSS 中，資訊可以分為 「拓樸/定義類」 與 「狀態/解算類」，這兩者的獲取時機是不同的：

        1. 拓樸與定義類 (不需要 Solve)
        這類資訊在 Compile完成後,就已經載入記憶體並建立了索引。

        API 範例： PVSystems.Count、Loads.Count、Lines.AllNames、Circuit.Name。

        執行編譯時 OpenDSS 會掃描腳本並建立物件清單這時「有多少個 PV」是確定的事實
        不需要經過電力潮流計算 Solve 就能知道數量和名稱

        2. 狀態與解算類（通常需要 Solve)
        這類資訊涉及到電路的物理平衡，必須經過矩陣迭代計算才能得到準確值。

        API 範例： AllBusVmagPu電壓 AllElementCurrents電流 Losses損失

        雖然編譯完後這些數值可能有初始值 可能是 0 或 1.0
        
        但如果不執行 Solve 這些數值就不會反映負載壓降、線路損失或變壓器分接頭的影響。
            
        """

    # 必須定義一個函數 去調用取得電壓
    def all_voltage(self):
        """
        獲取所有節點的標么電壓 (Per-Unit Voltage Magnitude)。
        屬於【狀態類 API】：需在 solve() 後調用才有精確物理意義。
        """
        return self.circuit.AllBusVmagPu

    def has_pv_system(self):
        """
        檢查系統中是否存在 PV 系統。
        屬於【拓樸類 API】：編譯成功即可獲取，不需執行 solve()。
        """
        if self.status == "Error": return False
        return self.circuit.PVSystems.Count > 0


    def _setup_shapes(self, load_mults, pv_mults):
        """
        將 Python 列表轉換為 OpenDSS 的 LoadShape
        load_mults: 負載倍數序列 (e.g., [0.5, 0.6, ...])
        pv_mults: 太陽能倍數序列 (e.g., [0.0, 0.2, 1.0, ...])
        """
        npts = len(load_mults)
        # 定義負載曲線
        self.text.Command = f"New LoadShape.CommonLoad npts={npts} interval=1 mult=({','.join(map(str, load_mults))})"
        # 定義太陽能曲線
        self.text.Command = f"New LoadShape.CommonPV npts={npts} interval=1 mult=({','.join(map(str, pv_mults))})"

    def run_timeseries_impact_clean(self, load_profile, pv_profile):
        npts = len(load_profile)
        
        # 1. 基礎佈置 (只做一次)
        self._setup_shapes(load_profile, pv_profile)
        
        # 將所有 Load 關聯到 LoadShape
        for load_name in self.circuit.Loads.AllNames:
            self.text.Command = f"Load.{load_name}.Daily=CommonLoad"
        
        # 將所有 PV 關聯到 LoadShape (注意 PV 需要設定物件名稱)
        for pv_name in self.circuit.PVSystems.AllNames:
            self.text.Command = f"PVSystem.{pv_name}.Daily=CommonPV"

        # 準備儲存容器
        v_base_history = []  # 存無 PV 電壓
        v_pv_history = []    # 存有 PV 電壓

        # --- 第一波：純負載時序模擬 (無太陽能) ---
        for pv in self.circuit.PVSystems.AllNames:
            self.text.Command = f"PVSystem.{pv}.Irradiance=0"
        
        for i in range(npts):
            self.text.Command = f"Set Hour={i}"
            self.text.Command = "Solve"
            v_base_history.append(np.array(self.circuit.AllBusVmagPu))

        # --- 第二波：負載 + 太陽能時序模擬 ---
        for pv in self.circuit.PVSystems.AllNames:
            self.text.Command = f"PVSystem.{pv}.Irradiance=1"
        
        for i in range(npts):
            self.text.Command = f"Set Hour={i}"
            self.text.Command = "Solve"
            v_pv_history.append(np.array(self.circuit.AllBusVmagPu))

        # --- 第三波：後處理計算 ---
        max_dv_sequence = []
        for i in range(npts):
            v_no_pv = v_base_history[i]
            v_with_pv = v_pv_history[i]
            
            mask = (v_no_pv > 0.1) & (~np.isnan(v_no_pv))
            if np.any(mask):
                dv_rates = np.abs((v_with_pv[mask] - v_no_pv[mask]) / v_no_pv[mask]) * 100
                max_dv_sequence.append(np.max(dv_rates))
            else:
                max_dv_sequence.append(0.0)

        status_sequence = ["合格" if dv <= 3.0 else "不合格" for dv in max_dv_sequence]
        return max_dv_sequence, status_sequence





# 調用官方程式進行分析的類別
class EngineAgentForCOM:
    def __init__(self, com_engine, dss_file_path):
        """
        初始化 COM 版分析器。
        :param com_engine: 外部傳入的 OpenDSSEngine.DSS 物件
        :param dss_file_path: Master.dss 的路徑
        """
        # 1. 基礎屬性設定
        self.engine = com_engine
        self.text = com_engine.Text
        self.circuit = com_engine.ActiveCircuit
        self.dss_error = com_engine.Error  # COM 專屬錯誤處理介面
        
        # 轉為絕對路徑以確保定位精準
        self.dss_file_path = Path(dss_file_path).absolute()
        
        self.status = "Success"
        self.error_msg = ""

        # 2. 執行編譯
        self._compile_dss()

    def _compile_dss(self):
        """私有方法：處理 COM 版專有的路徑敏感編譯"""
        original_cwd = os.getcwd()
        
        try:
            if not self.dss_file_path.exists():
                self.status = "Error"
                self.error_msg = "檔案不存在"
                return

            # A. 切換 Python 當前目錄
            dss_dir = str(self.dss_file_path.parent)
            os.chdir(dss_dir)
            
            # B. 同步 COM 引擎工作目錄 (這是 COM 版穩定的關鍵)
            self.text.Command = f"Set DataPath=\"{dss_dir}\""
            
            # C. 執行編譯
            self.text.Command = "Clear"
            self.text.Command = f"compile \"{self.dss_file_path.name}\""
            
            # D. 檢查 COM 內部編譯錯誤
            if self.dss_error.Number != 0:
                self.status = "Error"
                self.error_msg = f"DSS編譯錯誤: {self.dss_error.Description}"
        
        except Exception as e:
            self.status = "Error"
            self.error_msg = str(e).replace('\n', ' ').strip()
        finally:
            # 恢復外部環境目錄
            os.chdir(original_cwd)

    def has_pv_system(self):
        """檢查系統中是否有 PVSystems"""
        if self.status == "Error": return False
        return self.circuit.PVSystems.Count > 0

    def _distribute_load(self, feederload_kw):
        """私有方法：執行 COM 環境下的負載分配邏輯"""
        # 1. 取得變壓器二次側 Bus (115_ 系列)
        tr_buses = [bus for bus in self.circuit.AllBusNames if "115_" in bus]
        
        # 2. 統計變壓器總容量 (kVA)
        total_tr_kva = 0
        tr_exists = self.circuit.Transformers.First
        while tr_exists:
            total_tr_kva += self.circuit.Transformers.kva
            tr_exists = self.circuit.Transformers.Next

        # 3. 計算分配權重 (1% 規則)
        tr_target_kw = total_tr_kva * 0.01
        if feederload_kw <= tr_target_kw:
            tr_final_kw, sw_final_kw = feederload_kw, 0
        else:
            tr_final_kw, sw_final_kw = tr_target_kw, feederload_kw - tr_target_kw

        # 4. 取得 Switch Bus
        switch_buses = []
        for l_name in self.circuit.Lines.AllNames:
            if "switch_" in l_name.lower():
                self.circuit.Lines.Name = l_name
                switch_buses.append(self.circuit.Lines.Bus1.split('.')[0])
        switch_buses = list(set(switch_buses))

        # 5. 生成 DSS 指令掛載負載
        if tr_buses and tr_final_kw > 0:
            avg_tr = tr_final_kw / len(tr_buses)
            for bus in tr_buses:
                self.text.Command = f"New Load.TR_{bus} Bus1={bus} Phases=1 kV=0.11 kW={avg_tr} pf=0.95"

        if switch_buses and sw_final_kw > 0:
            avg_sw = sw_final_kw / len(switch_buses)
            for bus in switch_buses:
                self.text.Command = f"New Load.SW_{bus} Bus1={bus} Phases=3 kV=11.4 kW={avg_sw} pf=0.95"

    def run_voltage_impact(self, feederload_kw):
        """執行電壓變動率分析"""
        if self.status == "Error":
            return None, self.error_msg

        try:
            # A. 負載分配
            self._distribute_load(feederload_kw)

            # B. 基準計算 (無 PV)
            pv_names = self.circuit.PVSystems.AllNames
            for pv in pv_names: 
                self.text.Command = f"PVSystem.{pv}.Irradiance=0"
            
            self.text.Command = "Solve"
            if self.dss_error.Number != 0:
                return None, f"基準解算失敗: {self.dss_error.Description}"
            v_no_pv = np.array(self.circuit.AllBusVmagPu)

            # C. 併網計算 (有 PV)
            for pv in pv_names: 
                self.text.Command = f"PVSystem.{pv}.Irradiance=1"
            
            self.text.Command = "Solve"
            if self.dss_error.Number != 0:
                return None, f"併網解算失敗: {self.dss_error.Description}"
            v_with_pv = np.array(self.circuit.AllBusVmagPu)

            # D. 計算最大變動率
            mask = v_no_pv > 0.1
            if not np.any(mask):
                return None, "無有效電壓節點"

            dv_rates = np.abs((v_with_pv[mask] - v_no_pv[mask]) / v_no_pv[mask]) * 100
            max_dv = np.max(dv_rates)
            
            status = "合格" if max_dv <= 3.0 else "超過 3% 閾值"
            return max_dv, status

        except Exception as e:
            return None, f"COM 計算過程出錯: {str(e)}"
        
