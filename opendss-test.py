import win32com.client

dss = win32com.client.Dispatch("OpenDSSEngine.DSS")
print("OpenDSS COM 已啟動:", dss.Start(0))