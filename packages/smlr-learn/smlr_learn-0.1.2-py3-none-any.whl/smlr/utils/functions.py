import numpy as np

def sigmoid(x: np.ndarray):
    return 1 / (1 + np.exp(-x))

def simplex_matrix(k: int):
    W = np.zeros((k-1, k))
    
    for j in range(k):
        if j == 0:  # j=1 的情况（Python索引从0开始）
            W[:, j] = (k-1)**(-1/2) * np.ones(k-1)
        else:  # j >= 2 的情况
            # 前 j-1 个元素
            W[:, j] = (np.ones(k-1) * ((-1-k**(0.5)) / (k-1)**(1.5)) + (k / (k-1)) ** (0.5) * np.eye(k-1)[j-1]).reshape(1,k-1)
    return W


if __name__ == "__main__":
    # 单元测试：Simplex Matrix
    print(simplex_matrix(3))