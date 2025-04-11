import win32com.client

# 建立 DSS COM 物件
dssObj = win32com.client.Dispatch("OpenDSSEngine.DSS")

# 啟動 DSS 引擎
if not dssObj.Start(0):
    print("DSS 引擎啟動失敗")
    exit()

# 獲取各個子系統
dssText = dssObj.Text        # 用來執行指令
dssCircuit = dssObj.ActiveCircuit
dssSolution = dssCircuit.Solution

# 載入一個簡單的測試案例
dssText.Command = "Clear"
dssText.Command = "Redirect Example.dss"  # 這裡換成你實際的檔案路徑

# 執行潮流
dssSolution.Solve()

# 檢查解是否成功
if dssSolution.Converged:
    print("潮流收斂成功！")
else:
    print("潮流未收斂！")

# 讀取其中一個 bus 的電壓
bus = dssCircuit.Buses("sourcebus")
voltages = bus.puVmagAngle  # 取得 per-unit 電壓大小與角度
print(f"sourcebus 電壓 (p.u.): {voltages}")
