import win32com.client
import sys

def run_dss_script(dss_file_path):
    dss_engine = win32com.client.Dispatch("OpenDSSEngine.DSS")
    if not dss_engine.Start(0):
        print("OpenDSS 啟動失敗")
        return

    dss_engine.Text.Command = f"compile {dss_file_path}"

if __name__ == "__main__":
    run_dss_script(sys.argv[1])
