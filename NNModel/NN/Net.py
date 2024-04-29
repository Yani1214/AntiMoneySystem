import torch
from torch import nn
import torch.nn.functional as F

from NN.GAT import GATLayer


class GAT_LSTM_Net(nn.Module):
    """GAT模型"""

    def __init__(self, input_size, hidden_size_gat, output_size_gat, dropout, alpha, nheads, hidden_size_lstm,
                 num_layer, output_size, device):
        super(GAT_LSTM_Net, self).__init__()
        self.dropout = dropout
        self.device = device
        self.output_size_gat = output_size_gat
        self.attention = [GATLayer(input_size, hidden_size_gat, dropout=dropout, alpha=alpha, concat=True) for _ in
                          range(nheads)]
        for i, attention in enumerate(self.attention):
            self.add_module('attention_{}'.format(i), attention)

        self.out_att = GATLayer(hidden_size_gat * nheads, output_size_gat, dropout=dropout, alpha=alpha, concat=False)

        # lstm
        self.num_layer = num_layer
        self.hidden_size_lstm = hidden_size_lstm
        self.lstm = nn.LSTM(output_size_gat, hidden_size_lstm, bidirectional=True, num_layers=num_layer)
        self.linear = nn.Linear(2 * hidden_size_lstm, output_size)  # 输出为1维，表示二分类
        self.sigmoid = nn.Sigmoid()  # 使用Sigmoid函数进行二分类

    def forward(self, xs, adjs):
        outputs_gat = []
        for x, adj in zip(xs, adjs):
            x = F.dropout(x, self.dropout, training=self.training)
            x = torch.cat([att(x, adj) for att in self.attention], dim=2)
            x = F.dropout(x, self.dropout, training=self.training)
            x = F.elu(self.out_att(x, adj))
            output_gat = F.log_softmax(x, dim=1)[0][0, :]
            outputs_gat.append(output_gat)

        hidden_cell = (torch.zeros(2 * self.num_layer, 1, self.hidden_size_lstm).to(self.device),
                       torch.zeros(2 * self.num_layer, 1, self.hidden_size_lstm).to(self.device))
        # 需要调整一下input_x的形状,将[tensor(num_subgraph, features), , ]
        input_lstm = torch.stack(outputs_gat)
        # input_lstm = torch.tensor(input_lstm, dtype=torch.float32)
        input_lstm = input_lstm.view(-1, 1, self.output_size_gat)  # (1,20,5,8)——>(L,N,H)

        lstm_out, _ = self.lstm(input_lstm, hidden_cell)
        output = self.linear(lstm_out[-1].squeeze())  # lstm_out[-1]取最后一个时间步，.squeeze()用于去除为1的维度
        predictions = self.sigmoid(output)  # 使用Sigmoid函数得到概率,表示对应样本属于正类的概率
        # binary_predictions = torch.round(predictions)  # 四舍五入为0或1的标签
        return predictions
