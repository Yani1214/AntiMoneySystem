import pymysql
import numpy as np
import random
import os.path

from sklearn.metrics import precision_score, recall_score
from sklearn.metrics import f1_score
import torch
import torch.nn.functional as F
import torch.optim as optim
import argparse
import logging
import pickle

from torch.utils.data import DataLoader

from NN import GAT, lstm, Net, cut

host = '127.0.0.1'
port = 3306
user = 'root'
password = '2002104118tzq'
db = 'anti-money-v4'
charset = 'utf8mb4'
subgraph_path = r'D:\大三上\反洗钱（信安）\NNModel\data\cut_result'
# subgraph_path = '/tmp/NNModel/data/cut_result'
batch_size = 1  # 设置批次大小
filename = 'log/example_e15_s6.log'

# 配置日志记录器
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=filename,  # 将日志记录到文件中
                    filemode='w')

# 创建一个控制台处理器，并添加到日志记录器中
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# 选择GPU设备
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

card_all_trans = []


def args_net():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=int, default=2, help='the mode of model: 1 is train model ; 2 is test one card')
    parser.add_argument('--card', type=str, default='6213361128013911677', help='the card needs to test (only be set in mode 2)')
    parser.add_argument('--lr', type=float, default=0.05, help='learning rate')
    parser.add_argument('--epochs', type=int, default=20, help='Number of training epochs')
    # parser.add_argument('--device', type=int, default=30, help='Number of training epochs')
    parser.add_argument('--weight_decay', type=float, default=5e-4, help='Weight decay')
    parser.add_argument('--nheads', type=int, default=4, help='Number of head attentions')
    parser.add_argument('--dropout', type=float, default=0.2, help='Dropout rate (1 - keep probability).')
    parser.add_argument('--alpha', type=float, default=0.2, help='Alpha for the leaky_relu.')
    parser.add_argument('--patience', type=int, default=100, help='Patience')
    parser.add_argument('--seed', type=int, default=6, help='Seed number')
    parser.add_argument('--train_rate', type=float, default=0.8, help='The rate of training set')
    parser.add_argument('--input_size', type=int, default=3, help='The num of node features')
    parser.add_argument('--hidden_size_gat', type=int, default=8, help='hidden size of gat')
    parser.add_argument('--gat_out', type=int, default=8, help='Number of gat output features')
    parser.add_argument('--hidden_size_lstm', type=int, default=16, help='hidden size of lstm')
    parser.add_argument('--num_layer', type=int, default=16, help='the num of lstm layer')
    parser.add_argument('--output_size', type=int, default=1,
                        help='the num of net output, the output is a positive class probability value')
    args = parser.parse_args()
    return args


def get_all_cards():
    sql = 'SELECT person_card FROM people'
    cur.execute(sql)
    all_cards = cur.fetchall()
    # str_list = [s[0].strip() for s in all_cards if s[0].strip() != ""]
    all_cards = set(all_cards)
    return all_cards


if __name__ == '__main__':

    # try:
    #     device_index = torch.cuda.current_device()
    #     print("PyTorch is using GPU")
    # except RuntimeError:
    #     device_index = -1
    #     print("PyTorch is using CPU")

    # 连接数据库，属性依次为：连接名称，端口，账号，密码，数据库的名字，字符集
    connection = pymysql.connect(host=host, port=port,
                                 user=user, password=password,
                                 db=db, charset=charset)
    logging.info("success connect database!!!")
    cur = connection.cursor()
    args = args_net()

    if args.mode == 1:

        random.seed(args.seed)
        np.random.seed(args.seed)
        torch.manual_seed(args.seed)

        # 获取到所有卡号
        all_cards = get_all_cards()

        # 子图分割
        graphs_info = []  # 所有卡的子图列表的信息[[每个子图的流水数, , , ],[],[]]
        cards_label = []  # 每个卡（一系列划分好的子图）所对应的标签
        new_all_cards = []  # 对于卡号进行筛选，去除掉无流水信息的卡号
        for card_number in all_cards:
            # card_number 是一个元组形式
            card_number = card_number[0]
            person_id, card_trans, avg_amount, avg_time, card_label = cut.get_data(card_number, cur)
            # 判断调取该卡号流水时是否存在异常
            if person_id == 0:
                continue
            new_all_cards.append(card_number.strip())
            subgraphs, subgraphs_info = cut.get_subgraph(card_trans)
            graphs_info.append(subgraphs_info)
            cards_label.append(card_label)
            logging.info("The num of {}`s subgraphs is:{}".format(card_number.strip(), len(subgraphs)))
            logging.info("The info of {}`s subgraphs is:{}".format(card_number.strip(), subgraphs_info))
            cut.save(subgraph_path, card_number.strip(), subgraphs, avg_amount, avg_time, subgraphs_info)

        pro_index = []
        for i, label in enumerate(cards_label):
            if label == 1:
                pro_index.append(i)
        rate = int(len(cards_label) / len(pro_index))
        # graphs_info, cards_label, new_all_cards
        add_graphs_info = []
        add_cards_label = []
        add_new_all_cards = []
        for i in pro_index:
            add_graphs_info.append(graphs_info[i])
            add_cards_label.append(cards_label[i])
            add_new_all_cards.append(new_all_cards[i])
        graphs_info += add_graphs_info * rate
        cards_label += add_cards_label * rate
        new_all_cards += add_new_all_cards * rate

        logging.info("Read data from database have done!!!")
        # 将列表数据保存到文件中
        with open('data/intermediate_data/graphs_info.pkl', 'wb') as f:
            pickle.dump(graphs_info, f)
        with open('data/intermediate_data/cards_label.pkl', 'wb') as f:
            pickle.dump(cards_label, f)
        with open('data/intermediate_data/new_all_cards.pkl', 'wb') as f:
            pickle.dump(new_all_cards, f)
        logging.info("Have saved graphs info and cards label!!!")
        # 关闭游标与连接
        cur.close()
        connection.close()
        logging.info("Have closed connection!!!")

        # 加载文件中的列表数据
        with open('data/intermediate_data/graphs_info.pkl', 'rb') as f:
            loaded_graphs_info = pickle.load(f)
        with open('data/intermediate_data/cards_label.pkl', 'rb') as f:
            loaded_cards_label = pickle.load(f)
        with open('data/intermediate_data/new_all_cards.pkl', 'rb') as f:
            loaded_new_all_cards = pickle.load(f)
        # gat处理
        graphs_features, graphs_adj = GAT.load_data(subgraph_path, loaded_new_all_cards, loaded_graphs_info)
        # graphs_gat_out 为 列表（卡号）——>列表（子图）——>tensor(8,)（每个子图的表示）
        logging.info("Data have been transformed graphs!!!")
        # 将列表数据保存到文件中
        with open('data/intermediate_data/graphs_features.pkl', 'wb') as f:
            pickle.dump(graphs_features, f)
        with open('data/intermediate_data/graphs_adj.pkl', 'wb') as f:
            pickle.dump(graphs_adj, f)
        logging.info("Have saved graphs_features and graphs_adj!!!")

        # 加载文件中的列表数据
        with open('data/intermediate_data/graphs_features.pkl', 'rb') as f:
            loaded_graphs_features = pickle.load(f)
        with open('data/intermediate_data/graphs_adj.pkl', 'rb') as f:
            loaded_graphs_adj = pickle.load(f)
        # 创建 TensorDataset 对象
        total_num = len(loaded_cards_label)
        train_num = int(total_num * args.train_rate)
        # 将三组数据打包在一起
        zipped_lists = list(zip(loaded_graphs_features, loaded_graphs_adj, loaded_cards_label))
        # 对打包后的列表进行打乱顺序
        random.shuffle(zipped_lists)
        # 将打乱顺序后的列表解包成原始的三组数据
        loaded_graphs_features, loaded_graphs_adj, loaded_cards_label = zip(*zipped_lists)
        train_graphs_features, train_graphs_adj, train_loaded_cards_label = loaded_graphs_features[
                                                                            :train_num], loaded_graphs_adj[
                                                                                         :train_num], loaded_cards_label[
                                                                                                      :train_num]
        train_dataset = lstm.MyDataset(train_graphs_features, train_graphs_adj, train_loaded_cards_label)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        # 创建LSTM模型实例
        model = Net.GAT_LSTM_Net(input_size=args.input_size, hidden_size_gat=args.hidden_size_gat,
                                 output_size_gat=args.gat_out,
                                 dropout=args.dropout, nheads=args.nheads, alpha=args.alpha,
                                 hidden_size_lstm=args.hidden_size_lstm,
                                 num_layer=args.num_layer, output_size=args.output_size, device=device).to(device)
        criterion = F.binary_cross_entropy
        optimizer = optim.Adam(model.parameters(), lr=args.lr)
        epochs = args.epochs
        # 开始训练
        model.train()
        logging.info("Begin training!!!")
        total_train = 0
        correct = 0
        true_labels = []
        pred_labels = []
        print(device)
        for i in range(epochs):
            j = 0
            # num_0 = 0
            for features, adjs, labels in train_loader:
                # features, adjs, labels = features[0].to(device), adjs[0].to(device), labels[0].to(device)
                features = [feature.to(device) for feature in features]
                adjs = [adj.to(device) for adj in adjs]
                labels = [label.to(device) for label in labels]
                j = j + 1
                predictions = model(features, adjs).to(device)  # seq(1,20,5,8)
                labels = torch.tensor(labels).to(device)
                loss = criterion(predictions, labels.float())  # 注意将标签转换为浮点数
                # Format the loss to display more decimal places
                formatted_loss = "{:.20f}".format(loss.item())  # Adjust the number of decimal places as needed
                if j % 100 == 0:
                    logging.info("Train Step: %d loss: %s" % (i, formatted_loss))  # 损失交叉熵
                # 反向传播和优化
                optimizer.zero_grad()  # 清除之前的梯度
                loss.backward()  # 反向传播计算梯度
                optimizer.step()  # 更新模型参数
                total_train += labels.size(0)
                binary_predictions = torch.round(predictions)
                correct += (binary_predictions == labels).sum().item()
                true_labels.append(labels.tolist())
                pred_labels.append(binary_predictions.tolist())

            val_f1 = f1_score(true_labels, pred_labels)
            val_p = precision_score(true_labels, pred_labels)
            val_r = recall_score(true_labels, pred_labels)
            accuracy = correct / total_train
            logging.info("Train Step: %d ACC: %f f1: %f precision: %f recall: %f" % (i, accuracy, val_f1, val_p, val_r))

            # 保存中间结果
            if i != 0 and (i + 1) % 5 == 0:
                state_dict_dir = "data/intermediate_result"
                if not os.path.exists(state_dict_dir):
                    os.makedirs(state_dict_dir)
                torch.save(model.state_dict(), os.path.join(state_dict_dir, "model_e{}.bin".format(i + 1)))

        # 测试集代码
        model.eval()  # 切换模型到评估模式
        state_dict_dir = "data/intermediate_result"
        ckpt_acc = torch.load(os.path.join(state_dict_dir, "model_e15.bin"))
        model.load_state_dict(ckpt_acc)  # 调用 load_state_dict(ckpt) 方法时，PyTorch 会根据字典中的参数值更新模型的当前参数
        logging.info("Begin testing!!!")
        test_graphs_features, test_graphs_adj, test_loaded_cards_label = loaded_graphs_features[
                                                                         train_num:], loaded_graphs_adj[
                                                                                      train_num:], loaded_cards_label[
                                                                                                   train_num:]
        test_dataset = lstm.MyDataset(test_graphs_features, test_graphs_adj, test_loaded_cards_label)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        test_size = total_num - train_num
        logging.info("Test Dataset size: %d " % test_size)
        # 评估模型在测试集上的性能
        correct = 0
        total = 0
        y_true = []
        y_pred = []
        with torch.no_grad():  # 在测试阶段不需要计算梯度
            p = 0
            # num_0_test = 0
            for features, adjs, labels in test_loader:
                # features, adjs, labels = features.to(device), adjs.to(device), labels.to(device)
                # features, adjs, labels = features[0].to(device), adjs[0].to(device), labels[0].to(device)
                features = [feature.to(device) for feature in features]
                adjs = [adj.to(device) for adj in adjs]
                labels = [label.to(device) for label in labels]
                p = p + 1
                predictions_test = model(features, adjs).to(device)
                labels = torch.tensor(labels).to(device)
                loss_test = criterion(predictions_test, labels.float())  # 注意将标签转换为浮点数
                formatted_loss_test = "{:.20f}".format(
                    loss_test.item())  # Adjust the number of decimal places as needed
                # logging.info("p：", p, "  loss: ", formatted_loss_test)  # 损失交叉熵
                logging.info("Test Step: %d loss: %s " % (p, formatted_loss_test))
                # 将模型的预测从概率转换为0或1的标签
                binary_predictions = torch.round(predictions_test)
                total += labels.size(0)
                if binary_predictions == labels:
                    logging.info("%s\t YES\n" % p)
                else:
                    logging.info("%s\t NO\n" % p)
                correct += (binary_predictions == labels).sum().item()
                y_true.append(labels.item())
                y_pred.append(binary_predictions.item())
        accuracy = correct / total
        # y_true = torch.argmax(labels, dim=1)
        f1 = f1_score(y_true, y_pred)
        logging.info("Test Accuracy: %f  F1: %f" % (accuracy, f1))
    elif args.mode == 2:
        card_num = args.card
        person_id, card_trans, avg_amount, avg_time, card_label = cut.get_data(card_num, cur)
        # 判断调取该卡号流水时是否存在异常
        assert person_id != 0, 'CARD_TRANS ERROR!!!'
        subgraphs, subgraphs_info = cut.get_subgraph(card_trans)
        logging.info("The num of {}`s subgraphs is:{}".format(card_num, len(subgraphs)))
        logging.info("The info of {}`s subgraphs is:{}".format(card_num, subgraphs_info))
        cut.save(r'D:\大三上\反洗钱（信安）\NNModel\data\detection_cut_result', card_num, subgraphs, avg_amount, avg_time,
                 subgraphs_info)
        subgraphs_features, subgraphs_adj = GAT.load_data_detect(r'D:\大三上\反洗钱（信安）\NNModel\data\detection_cut_result', card_num, subgraphs_info)

        detect_dataset = lstm.MyDataset([subgraphs_features], [subgraphs_adj], [card_label])
        detect_loader = DataLoader(detect_dataset, batch_size=batch_size, shuffle=False, sampler=None)

        model = Net.GAT_LSTM_Net(input_size=args.input_size, hidden_size_gat=args.hidden_size_gat,
                                 output_size_gat=args.gat_out,
                                 dropout=args.dropout, nheads=args.nheads, alpha=args.alpha,
                                 hidden_size_lstm=args.hidden_size_lstm,
                                 num_layer=args.num_layer, output_size=args.output_size, device=device).to(device)
        model.eval()  # 切换模型到评估模式
        state_dict_dir = "data/intermediate_result"
        ckpt_acc = torch.load(os.path.join(state_dict_dir, "model_e15.bin"))
        model.load_state_dict(ckpt_acc)  # 调用 load_state_dict(ckpt) 方法时，PyTorch 会根据字典中的参数值更新模型的当前参数
        for features, adjs, labels in detect_loader:
            features = [feature.to(device) for feature in features]
            adjs = [adj.to(device) for adj in adjs]
            labels = [label.to(device) for label in labels]
            prediction = model(features, adjs).to(device)
            labels = torch.tensor(labels).to(device)
        logging.info('card: %s prediction: %f real_label: %d' % (card_num, prediction.item(), labels.item()))
    else:
        logging.info('MODE ERROR')
