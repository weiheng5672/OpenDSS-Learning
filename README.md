
本專案目的是
透過py 使用Opendss提供的API
熟悉相關操作

## 1.建立 Conda 環境

開啟終端機（或 Anaconda Prompt），執行：

```bash
conda create -n dss_env python=3.10
```

---

## 2.啟動環境

```bash
conda activate dss_env
```

---

## 3.安裝所需套件

```bash
pip install -r requirements.txt
```
requirements.txt 檔案內容如下

pywin32
這個是與官方opendss的COM接口的套件
使用這個套件需要額外安裝opendss軟體
只能在windoes

dss-python[all]
這個是社群版opendss
使用這個不需要再去下載官方提供的opendss
windows linux mac 皆可
[all]會下載所有相關的套件包含 可視化的matplotlib 數據處理的 pandas等
社群版opendss 沒有內建可視化功能

pyvis
另一個可視化庫 畫出的圖 可以拖曳 有互動性 並且更美觀



---

## 4.測試 COM 接口是否正常運作

在 Python 互動模式或編輯器，輸入以下測試碼：

```python
import win32com.client
dss = win32com.client.Dispatch("OpenDSSEngine.DSS")
print("OpenDSS COM 已啟動:", dss.Start(0))
```

或是



如果執行成功將結果打印出來，代表成功讓 Python 控制 OpenDSS 

## COM 僅限 Windows 平台

因為 COM 是 Windows 特有技術，這套方法只能在 **Windows** 上使用。

