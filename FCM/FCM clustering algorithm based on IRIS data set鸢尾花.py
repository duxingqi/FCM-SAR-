
import numpy as np
import pandas as pd

def loadData(datapath):                                    #加载数据
    data = pd.read_csv(datapath, sep=',', header=None)    #读取数据
    data = data.sample(frac=1.0)                          # 打乱数据顺序
    dataX = data.iloc[:, :-1].values                      # 特征
    labels = data.iloc[:, -1].values                      # 标签
    # 将标签类别用 0, 1, 2表示
    labels[np.where(labels == "Iris-setosa")] = 0
    labels[np.where(labels == "Iris-versicolor")] = 1
    labels[np.where(labels == "Iris-virginica")] = 2
    return dataX, labels

def initialize_U(samples, classes):
    U = np.random.rand(samples, classes)  # 先生成随机矩阵
    sumU = 1 / np.sum(U, axis=1)   # 求每行的和
    U = np.multiply(U.T, sumU)   # 使隶属度矩阵每一行和为1
    return U.T

# 计算样本和簇中心的距离，这里使用欧氏距离
def distance(X, centroid):
    return np.sqrt(np.sum((X-centroid)**2, axis=1))

def computeU(X, centroids, m=2):
    sampleNumber = X.shape[0]  # 样本数
    classes = len(centroids)
    U = np.zeros((sampleNumber, classes))
    # 更新隶属度矩阵
    for i in range(classes):
        for k in range(classes):
            U[:, i] += (distance(X, centroids[i]) / distance(X, centroids[k])) ** (2 / (m - 1))
    U = 1 / U

    return U

def ajustCentroid(centroids, U, labels):
    newCentroids = [[], [], []]
    curr = np.argmax(U, axis=1)  # 当前中心顺序得到的标签
    for i in range(len(centroids)):
        index = np.where(curr == i)   # 建立中心和类别的映射
        trueLabel = list(labels[index])  # 获取labels[index]出现次数最多的元素，就是真实类别
        trueLabel = max(set(trueLabel), key=trueLabel.count)
        newCentroids[trueLabel] = centroids[i]
    return newCentroids

def cluster(data, labels, m, classes, EPS):
    """
    :param data: 数据集
    :param m: 模糊系数(fuzziness coefficient)
    :param classes: 类别数
    :return: 聚类中心
    """
    sampleNumber = data.shape[0]  # 样本数
    cNumber = data.shape[1]       # 特征数
    U = initialize_U(sampleNumber, classes)   # 初始化隶属度矩阵
    U_old = np.zeros((sampleNumber, classes))

    while True:
        centroids = []
        # 更新簇中心
        for i in range(classes):
            centroid = np.dot(U[:, i]**m, data) / (np.sum(U[:, i]**m))
            centroids.append(centroid)

        U_old = U.copy()
        U = computeU(data, centroids, m)  # 计算新的隶属度矩阵

        if np.max(np.abs(U - U_old)) < EPS:
            # 这里的类别和数据标签并不是一一对应的, 调整使得第i个中心表示第i类
            centroids = ajustCentroid(centroids, U, labels)
            return centroids, U
        
# 预测所属的类别
def predict(X, centroids):
    labels = np.zeros(X.shape[0])
    U = computeU(X, centroids)  # 计算隶属度矩阵
    labels = np.argmax(U, axis=1)  # 找到隶属度矩阵中每行的最大值，即该样本最大可能所属类别

    return labels

def main():
    datapath = "iris.data"                        #数据导入
    dataX, labels = loadData(datapath)            #读取数据
    #划分训练集和测试集
    ratio = 0.6                                   #训练集的比例
    trainLength = int(dataX.shape[0] * ratio)     #训练集长度
    trainX = dataX[:trainLength, :]
    trainLabels = labels[:trainLength]
    testX = dataX[trainLength:, :]
    testLabels = labels[trainLength:]
    EPS = 1e-6                                    #停止误差条件
    m = 2                                         #模糊因子
    classes = 3                                   #类别数
                                                  #得到各类别的中心
    centroids, U = cluster(trainX, trainLabels, m, classes, EPS)
    trainLabels_prediction = predict(trainX, centroids)
    testLabels_prediction = predict(testX, centroids)
    #训练集和测试集的准确率计算
    train_error = 1 - np.sum(np.abs(trainLabels_prediction - trainLabels)) / trainLength
    test_error = 1 - np.sum(np.abs(testLabels_prediction - testLabels)) / (dataX.shape[0] - trainLength)
    print("训练集上的聚类准确率为 %.2f%%" % (train_error*100))
    print("测试集上的聚类准确率为 %.2f%%" % (test_error*100))

if __name__ == "__main__":
    main()
