import os
import torch
import torch.nn as nn
import torch.utils.data as Data
import numpy as np
import torch.optim as optim
import pandas as pd
from torch.utils.data import Dataset



class MyDataset(Dataset):
    def __init__(self, x_data, y_data, z_data):
        self.features_data = x_data
        self.adjs_data = y_data
        self.labels = z_data

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, index):
        sungraphs_feature = self.features_data[index]
        sungraphs_adj = self.adjs_data[index]
        label = self.labels[index]
        return sungraphs_feature, sungraphs_adj, label


# ...定义 get_train_data 和 LSTM 类...
def get_train_data(num_train, num_total, label_path, gcn_result_path):
    num_group = len(os.listdir(gcn_result_path))  # 100个账户序列
    tensor_list = []
    for filename in os.listdir(gcn_result_path):
        with open(os.path.join(gcn_result_path, filename), 'r') as f:
            lines = f.readlines()
        num_samples = 10  # 每个账户序列划分为10个子图
        num_point = 5  # 每个子图5个节点
        feature_dim = 8  # 每个节点8维向量
        data = np.zeros((num_samples, num_point, feature_dim))
        # 逐行读取并填充数据
        for j in range(num_samples):
            for k in range(num_point):
                line = lines[j * num_point + k].strip()  # 从文件中读取一行并去除首尾空白字符
                values = [float(num) for num in line.split()]  # 将行分割为浮点数列表
                # print(len(values))
                for l in range(feature_dim):
                    data[j, k, l] = values[l]
        tensor_list.append(data)

    # 将列表中的张量合并成一个大张量
    data_all = np.stack(tensor_list)
    # 打印合并后的张量形状
    print("合并后的张量形状:", data_all.shape)

    # 构造对应的目标标签
    # 0：这是 low 参数，指定了随机整数的最小值;2：这是 high 参数，指定了随机整数的最大值（不包括该值）
    # 生成对应的目标标签
    # labels = np.random.randint(0, 2, num_group)

    # 读取 Excel 文件
    df = pd.read_excel(label_path, nrows=num_group)

    # 从DataFrame中获取label列的数据并转换为NumPy数组
    labels_column = df['label']
    labels_array = np.array(labels_column)

    # 打印或使用labels_array
    print(labels_array)

    # labels 现在是一个 (num_group, 2) 的矩阵，每一行是一个标签
    # 每一行对应一个标签，其中一个元素为 1，表示正类，另一个元素为 0，表示负类
    # labels = np.eye(2, dtype=np.float32)[np.random.randint(0, 2, num_group)]  # 每个账户对应一个 0/1 标签

    # # 构造类别权重，使得1类别和0类别的权重比例为3:1
    # class_weights = torch.tensor([1])  # 根据实际情况调整权重

    # 将数据和标签转换为PyTorch Tensor
    x = torch.tensor(data_all, dtype=torch.float32)
    y = torch.tensor(labels_array, dtype=torch.float32)

    # 获取数据的总数和打乱的索引
    num_samples = len(x)
    indices = np.arange(num_samples)
    np.random.shuffle(indices)

    # 计算train索引范围并对数据进行切分
    split_idx = int(num_train / num_total * num_samples)
    x_train = x[indices[:split_idx]]
    y_train = y[indices[:split_idx]]
    x_test = x[indices[split_idx:]]
    y_test = y[indices[split_idx:]]

    return x_train, y_train, x_test, y_test


# class BinaryClassificationLSTM(nn.Module):
#     def __init__(self, input_size=8, hidden_layer_size=32):
#         super().__init__()
#         self.hidden_layer_size = hidden_layer_size
#         self.lstm = nn.LSTM(input_size, hidden_layer_size, bidirectional=True, num_layers=4)
#         self.linear = nn.Linear(2 * hidden_layer_size, 1)  # 输出为1维，表示二分类
#         self.sigmoid = nn.Sigmoid()  # 使用Sigmoid函数进行二分类
#
#     def forward(self, input_x):
#         hidden_cell = (torch.zeros(8, 1, self.hidden_layer_size),
#                        torch.zeros(8, 1, self.hidden_layer_size))
#         # 需要调整一下input_x的形状
#         # 使用 torch.stack() 函数将 tensor 列表的列表堆叠成一个更高维度的 tensor
#         # stacked_input_x = [torch.stack(sample) for sample in input_x]
#         # 将堆叠后的 tensor 转换为 torch.float32 类型
#         # stacked_input_x = [sample.float() for sample in stacked_input_x]
#         # 可以选择进一步将列表转换为 PyTorch 张量
#         input_x = torch.stack(input_x)
#         # input_x = torch.tensor(input_x, dtype=torch.float32)
#         input_x = input_x.view(-1, 1, 8)  # (1,20,5,8)——>(L,N,H)
#
#         lstm_out, _ = self.lstm(input_x, hidden_cell)
#         output = self.linear(lstm_out[-1].squeeze())  # lstm_out[-1]取最后一个时间步，.squeeze()用于去除为1的维度
#         predictions = self.sigmoid(output)  # 使用Sigmoid函数得到概率,表示对应样本属于正类的概率
#         # binary_predictions = torch.round(predictions)  # 四舍五入为0或1的标签
#         return predictions
#
#
# if __name__ == '__main__':
#     file_name = '../RESULT/test1.txt'
#     # 获取训练数据
#     num_train = 4
#     num_total = 5
#     with open(file_name, 'a') as file:
#         message = "train / test = {} / {}\n".format(num_train, num_total - num_train)
#         file.write(message)
#     x_train, y_train, x_test, y_test = get_train_data(num_train, num_total)
#     # 创建训练数据加载器
#     train_loader = Data.DataLoader(
#         dataset=Data.TensorDataset(x_train, y_train),
#         batch_size=1,
#         shuffle=True,
#         num_workers=2,
#     )
#     dataset_size = len(train_loader.dataset)
#     with open(file_name, 'a') as file:
#         message = "Training Dataset size: {}\n".format(dataset_size)
#         file.write(message)
#     print("Training Dataset size:", dataset_size)
#
#     # 创建LSTM模型实例
#     model = BinaryClassificationLSTM()
#     criterion = nn.BCELoss()
#     optimizer = optim.Adam(model.parameters(), lr=0.00001)
#     epochs = 4
#     with open(file_name, 'a') as file:
#         message = "epochs: {}\n".format(epochs)
#         file.write(message)
#     print("epochs=", epochs)
#
#     # 开始训练
#     model.train()
#     for i in range(epochs):
#         j = 1
#         num_0 = 0
#         for seq, labels in train_loader:
#             # print(j)
#             # print(seq.size())
#             # print(labels.size())
#             j = j + 1
#
#             label_value = int(labels.item())
#             if label_value == 0:
#                 num_0 = num_0 + 1
#
#             # 将序列数据 seq 输入模型，得到模型的预测
#             predictions = model(seq)  # seq(1,20,5,8)
#             # 计算模型预测与真实标签之间的交叉熵损失
#             # 创建对应的标签（0或1）
#             target_label = torch.tensor([1])  # 你可以根据实际情况修改标签
#             loss = criterion(predictions, target_label.float())  # 注意将标签转换为浮点数
#             # Format the loss to display more decimal places
#             formatted_loss = "{:.20f}".format(loss.item())  # Adjust the number of decimal places as needed
#             if j % 100 == 0:
#                 with open(file_name, 'a') as file:
#                     message = "Train Step: {} loss: {}\n".format(i, formatted_loss)
#                     file.write(message)
#                 print("Train Step:", i, " loss: ", formatted_loss)  # 损失交叉熵
#             # 反向传播和优化
#             optimizer.zero_grad()  # 清除之前的梯度
#             loss.backward()  # 反向传播计算梯度
#             optimizer.step()  # 更新模型参数
#         with open(file_name, 'a') as file:
#             message = "train_0= {}\n".format(num_0)
#             file.write(message)
#
#     # 测试集代码
#     model.eval()  # 切换模型到评估模式
#     test_loader = Data.DataLoader(
#         dataset=Data.TensorDataset(x_test, y_test),
#         batch_size=1,
#         shuffle=False,  # 注意设置为 False，不进行数据打乱
#         num_workers=2,
#     )
#     test_size = len(test_loader.dataset)
#     print("Test Dataset size:", test_size)
#
#     # 评估模型在测试集上的性能
#     correct = 0
#     total = 0
#     with torch.no_grad():  # 在测试阶段不需要计算梯度
#         p = 0
#         num_0_test = 0
#         for seq, labels in test_loader:
#             label_value = int(labels.item())
#             if label_value == 0:
#                 num_0_test = num_0_test + 1
#             p = p + 1
#             predictions_test = model(seq)
#             target_label_test = torch.tensor([1])  # 你可以根据实际情况修改标签
#             loss_test = criterion(predictions_test, target_label_test.float())  # 注意将标签转换为浮点数
#             # Format the loss to display more decimal places
#             formatted_loss_test = "{:.20f}".format(loss_test.item())  # Adjust the number of decimal places as needed
#             print("p：", p, "  loss: ", formatted_loss_test)  # 损失交叉熵
#             # 将模型的预测从概率转换为0或1的标签
#             binary_predictions = torch.round(predictions_test)
#             total += labels.size(0)
#             if binary_predictions == labels:
#                 print(p, "\t YES\n")
#             else:
#                 print(p, "\t NO\n")
#             correct += (binary_predictions == labels).sum().item()
#
#     accuracy = correct / total
#     with open(file_name, 'a') as file:
#         test_0 = "test_0= {}\n".format(num_0_test)
#         file.write(test_0)
#         message = "Test Accuracy: {}\n\n\n\n\n\n\n\n\n\n\n".format(accuracy)
#         file.write(message)
#     print("Test Accuracy:", accuracy)
