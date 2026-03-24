import numpy as np

# 1. 定義基礎參數 (阻抗 z 或 直接定義 導納 y)
# 支路導納
y12 = 1 / 0.25j
y13 = 1 / 0.1j
y14 = 1 / 0.4j
y23 = 0  
y24 = 1 / 0.16j
y34 = 1 / 0.2j

# 對地導納 (Shunt Admittance)
y10 = 1 / 0.25j + 1 / -4j
y20 = 1 / 0.2j + 1 / -4j
y30 = (1 + 0.25j) + 1 / -4j
y40 = (2 + 0.5j) + 1 / -4j

# 2. 初始化 Y 矩陣 (4x4 複數矩陣)
Y = np.zeros((4, 4), dtype=complex)

# 3. 填入非對角元素 (Off-diagonal: Yij = -yij)
Y[0, 1] = Y[1, 0] = -y12
Y[0, 2] = Y[2, 0] = -y13
Y[0, 3] = Y[3, 0] = -y14
Y[1, 2] = Y[2, 1] = -y23
Y[1, 3] = Y[3, 1] = -y24
Y[2, 3] = Y[3, 2] = -y34

# 4. 填入對角元素 (Diagonal: Yii = Sum of y connected to node i)
Y[0, 0] = y10 + y12 + y13 + y14
Y[1, 1] = y20 + y12 + y23 + y24
Y[2, 2] = y30 + y13 + y23 + y34
Y[3, 3] = y40 + y14 + y24 + y34

# 5. 美化輸出
np.set_printoptions(precision=3, suppress=True)
print("Y_bus Matrix:")
print(Y)