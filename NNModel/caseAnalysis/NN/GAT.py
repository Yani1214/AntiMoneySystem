import os.path
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import argparse
import numpy as np
import random
import scipy.sparse as sp


def normalize_adj(mx):
    """Row-normalize sparse matrix"""
    rowsum = np.array(mx.sum(1))
    r_inv_sqrt = np.power(rowsum, -0.5).flatten()
    r_inv_sqrt[np.isinf(r_inv_sqrt)] = 0.
    r_mat_inv_sqrt = sp.diags(r_inv_sqrt)
    return mx.dot(r_mat_inv_sqrt).transpose().dot(r_mat_inv_sqrt)  # 对称归一化的操作
    # 将原始的稀疏矩阵 mx 与对角矩阵 r_mat_inv_sqrt 相乘，然后再与 r_mat_inv_sqrt 的转置矩阵相乘


def normalize(mx):
    """Row-normalize sparse matrix"""
    colsum = np.array(mx.sum(0))
    c_inv = np.power(colsum, -1).flatten()
    c_inv[np.isinf(c_inv)] = 0.  # 将无穷大的数值设为0
    c_mat_inv = sp.diags(c_inv)  # 创建对角矩阵
    mx = mx.dot(c_mat_inv)
    return mx


class GATLayer(nn.Module):
    """GAT层"""

    def __init__(self, input_feature, output_feature, dropout, alpha, concat=True):
        super(GATLayer, self).__init__()
        self.input_feature = input_feature
        self.output_feature = output_feature
        self.alpha = alpha
        self.dropout = dropout
        self.concat = concat
        self.a = nn.Parameter(torch.empty(size=(2 * output_feature, 1)))
        self.w = nn.Parameter(torch.empty(size=(input_feature, output_feature)))
        self.leakyrelu = nn.LeakyReLU(self.alpha)
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.xavier_uniform_(self.w.data, gain=1.414)
        nn.init.xavier_uniform_(self.a.data, gain=1.414)

    def forward(self, h, adj):
        Wh = torch.matmul(h, self.w.data)
        e = self._prepare_attentional_mechanism_input(Wh)
        zero_vec = -9e15 * torch.ones_like(e)
        attention = torch.where(adj > 0, e, zero_vec)  # adj>0的位置使用e对应位置的值替换，其余都为-9e15，这样设定经过Softmax后每个节点对应的行非邻居都会变为0。
        attention = F.softmax(attention, dim=1)  # 每行做Softmax，相当于每个节点做softmax
        attention = F.dropout(attention, self.dropout, training=self.training)
        h_prime = torch.matmul(attention, Wh)  # 得到下一层的输入

        if self.concat:
            return F.elu(h_prime)  # 激活
        else:
            return h_prime

    def _prepare_attentional_mechanism_input(self, Wh):

        Wh1 = torch.matmul(Wh, self.a[:self.output_feature, :])  # N*out_size @ out_size*1 = N*1

        Wh2 = torch.matmul(Wh, self.a[self.output_feature:, :])  # N*1

        e = Wh1 + Wh2.T  # Wh1的每个原始与Wh2的所有元素相加，生成N*N的矩阵
        return self.leakyrelu(e)


# class GATNet(nn.Module):
#     """GAT模型"""
#
#     def __init__(self, input_size, hidden_size, output_size, dropout, alpha, nheads):
#         super(GATNet, self).__init__()
#         self.dropout = dropout
#         self.attention = [GATLayer(input_size, hidden_size, dropout=dropout, alpha=alpha, concat=True) for _ in
#                           range(nheads)]
#         for i, attention in enumerate(self.attention):
#             self.add_module('attention_{}'.format(i), attention)
#
#         self.out_att = GATLayer(hidden_size * nheads, output_size, dropout=dropout, alpha=alpha, concat=False)
#
#     def forward(self, x, adj):
#         x = F.dropout(x, self.dropout, training=self.training)
#         x = torch.cat([att(x, adj) for att in self.attention], dim=1)
#         x = F.dropout(x, self.dropout, training=self.training)
#         x = F.elu(self.out_att(x, adj))
#
#         return F.log_softmax(x, dim=1)


def load_data(path, all_cards, graphs_info):
    print('Loading dataset...')
    # graphs_gat_out = []
    graphs_features = []
    graphs_adj = []
    i = 0
    for card_number, subgraph_info in zip(all_cards, graphs_info):
        i += 1
        print('epoch:{}'.format(i))
        # 判断是否存在该卡号子图信息文件
        if not os.path.exists(os.path.join(path, 'contents', card_number)):
            continue
        idx_features_labels = np.genfromtxt(os.path.join(path, 'contents', card_number),
                                            dtype=np.dtype(str))  # 使用numpy读取.txt文件
        begin_edge, begin_node = 0, 0
        # subgraph_gat_out = []
        subgraphs_features = []
        subgraphs_adj = []
        # 对每个卡号中的每个子图进行操作
        for num_edge in subgraph_info:
            num_node = num_edge + 1  # num_node：该子图的节点数；num_edge：该子图的边数
            features = sp.csr_matrix(idx_features_labels[begin_node:begin_node + num_node, 1:],
                                     dtype=np.float32)  # 获取特征矩阵
            # build graph
            idx = np.array(idx_features_labels[begin_node:begin_node + num_node, 0], dtype=np.int32)
            idx_map = {j: i for i, j in enumerate(idx)}
            edges_unordered = np.genfromtxt(os.path.join(path, 'cites', card_number), dtype=np.int32)
            # 只有一条边的情况
            if edges_unordered.ndim == 1:
                edges_unordered = edges_unordered.reshape(1, 2)
            edges_unordered = edges_unordered[begin_edge:begin_edge + num_edge, :]
            edges = np.array(list(map(idx_map.get, edges_unordered.flatten())), dtype=np.int32).reshape(
                edges_unordered.shape)
            adj = sp.coo_matrix((np.ones(edges.shape[0]), (edges[:, 0], edges[:, 1])), shape=(num_node, num_node),
                                dtype=np.float32)
            features = normalize(features)
            adj = normalize_adj(adj + sp.eye(
                adj.shape[0]))  # 邻接矩阵中加上自连接（self-connections），以确保每个节点都至少有一个邻居。在图神经网络中，这种操作通常有助于提高模型的稳定性和泛化性能。
            features = torch.FloatTensor(np.array(features.todense()))  # todense() 方法将稀疏矩阵转换为其稠密表示形式

            ######################
            adj = torch.FloatTensor(np.array(adj.todense()))

            begin_edge += num_edge
            begin_node += num_node

            subgraphs_features.append(features)

            # # 对adj进行操作
            # # 将稀疏矩阵转换为密集数组
            # dense_adj = adj.toarray()
            # # 创建单位矩阵
            # eye = sp.eye(adj.shape[0])
            # # 将单位矩阵转换为密集数组
            # dense_eye = eye.toarray()
            # # 将稀疏矩阵与单位矩阵相加并进行归一化处理
            # normalized_adj = dense_adj + dense_eye
            # normalized_adj /= normalized_adj.sum(1, keepdims=True)
            # # 将归一化后的密集数组转换为张量
            # tensor_adj = torch.tensor(normalized_adj, dtype=torch.float32)
            subgraphs_adj.append(adj)

        graphs_features.append(subgraphs_features)
        graphs_adj.append(subgraphs_adj)

    return graphs_features, graphs_adj


def load_data_detect(path, card_number, subgraph_info):
    print('Loading dataset...')
    idx_features_labels = np.genfromtxt(os.path.join(path, 'contents', card_number),
                                        dtype=np.dtype(str))  # 使用numpy读取.txt文件
    begin_edge, begin_node = 0, 0
    subgraphs_features = []
    subgraphs_adj = []
    # 对每个卡号中的每个子图进行操作
    for num_edge in subgraph_info:
        num_node = num_edge + 1  # num_node：该子图的节点数；num_edge：该子图的边数
        features = sp.csr_matrix(idx_features_labels[begin_node:begin_node + num_node, 1:],
                                 dtype=np.float32)  # 获取特征矩阵
        # build graph
        idx = np.array(idx_features_labels[begin_node:begin_node + num_node, 0], dtype=np.int32)
        idx_map = {j: i for i, j in enumerate(idx)}
        edges_unordered = np.genfromtxt(os.path.join(path, 'cites', card_number), dtype=np.int32)
        # 只有一条边的情况
        if edges_unordered.ndim == 1:
            edges_unordered = edges_unordered.reshape(1, 2)
        edges_unordered = edges_unordered[begin_edge:begin_edge + num_edge, :]
        edges = np.array(list(map(idx_map.get, edges_unordered.flatten())), dtype=np.int32).reshape(
            edges_unordered.shape)
        adj = sp.coo_matrix((np.ones(edges.shape[0]), (edges[:, 0], edges[:, 1])), shape=(num_node, num_node),
                            dtype=np.float32)
        features = normalize(features)
        adj = normalize_adj(adj + sp.eye(
            adj.shape[0]))  # 邻接矩阵中加上自连接（self-connections），以确保每个节点都至少有一个邻居。在图神经网络中，这种操作通常有助于提高模型的稳定性和泛化性能。
        features = torch.FloatTensor(np.array(features.todense()))  # todense() 方法将稀疏矩阵转换为其稠密表示形式
        adj = torch.FloatTensor(np.array(adj.todense()))
        begin_edge += num_edge
        begin_node += num_node
        subgraphs_features.append(features)
        subgraphs_adj.append(adj)

    return subgraphs_features, subgraphs_adj
