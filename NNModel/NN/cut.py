import os.path
import datetime
import logging


def deal(value):
    if type(value) == str:
        value = value.rstrip('\t')
        value = value.rstrip('\r')
    return value


def save(file_path, card_number, graphs, avg_amount, avg_time, subgraph_info):
    """
    将卡号流水子图信息保存到两个文件中，content文件中保存每个子图中 每个节点的特征信息（节点编号，金额，时间，频次）；cite文件中保存每个子图中 每条边的信息（节点，节点）
    :param file_path: 文件夹路径
    :param card_number: 文件名
    :param graphs: 子图列表
    :param avg_amount: 中心节点交易金额
    :param avg_time: 中心节点交易时间
    :param subgraph_info: 中心节点交易频次
    :return: 文件存储
    """
    contents = 'contents'
    cites = 'cites'
    card_number = card_number.strip()
    fre = sum(subgraph_info) / len(subgraph_info)
    file_name_contents = os.path.join(file_path, contents, card_number)
    file_name_cites = os.path.join(file_path, cites, card_number)
    with open(file_name_contents, 'w', encoding='utf-8') as f1, open(file_name_cites, 'w', encoding='utf-8') as f2:
        for graph in graphs:
            line = '\t'.join(['0', str(avg_amount), str(avg_time), str(fre)]) + '\n'
            f1.write(line)
            for j in graph:
                line1 = '\t'.join([str(j['trans_id']), str(j['trans_amount']), str(j['trans_time']),
                                   str(j['trans_frequency'])]) + '\n'
                f1.write(line1)
                if j.get('py_indicator') and int(j['py_indicator']):
                    line2 = '\t'.join(['0', str(j['trans_id'])]) + '\n'
                else:
                    line2 = '\t'.join([str(j['trans_id']), '0']) + '\n'
                f2.write(line2)
        print("have writen")
    f1.close()
    f2.close()


def get_data(card_number, cur):
    """
    流程：获取到可疑流水——>获取到可疑交易卡号——>从person表中调取卡号相关的人员信息——>得到用户的person_number
        ——>根据person_number找到对应的表——>从表中找到该卡号所有的可以交易信息
    :param card_number: 输入需要检测的卡号
    :return:一个字典列表，每条流水都以字典键值对的形式表示，列表包含一个卡号的所有流水记录
    """
    # 构建 SQL 语句
    sql_get_person_id = 'select person_number, label from ' + 'people' + ' where person_card = {}'.format(card_number)
    # print(sql_get_person_id)
    # 执行 SQL 语句
    cur.execute(sql_get_person_id)
    # 获取数据
    data_person = cur.fetchall()    # 元组列表

    # 是否存在在people表中无法找到卡号信息的情况
    if len(data_person) == 0:
        logging.info("{}该卡号信息无法在people表中找到".format(card_number))
        return 0, 0, 0, 0, 0

    person_id = data_person[0][0].split('.0')[0]
    card_label = data_person[0][1]
    # print("person_id: {}".format(person_id))
    table_name = 'person_' + str(person_id)

    # 用于计算中心节点的属性
    amount = 0
    time = 0

    sql_get_card_data1 = 'SELECT * FROM ' + table_name + ' WHERE trans_card = ' + card_number
    cur.execute(sql_get_card_data1)
    data_trans1 = cur.fetchall()
    card_trans1 = []
    colum_index = ['trans_id', 'trans_card', 'trans_account', 'trans_name', 'id_number', 'trans_time', 'trans_amount',
                   'trans_balance',
                   'py_indicator', 'cp_card', 'cp_name', 'cp_id', 'summary', 'merchant_code', 'trans_type', 'label',
                   'is_more_median',
                   'is_more_mean', 'is_more_qualite25', 'is_more_qualite75', 'time_interval', 'trans_frequency',
                   'trans_source']
    for data_tuple in data_trans1:
        data_dict = dict((colum_index[index], deal(value)) for index, value in enumerate(data_tuple))
        amount += data_dict['trans_amount']
        data_dict['trans_time'] = (data_dict['trans_time'] - datetime.datetime(1970, 1, 1)).total_seconds()
        time += data_dict['trans_time']
        card_trans1.append(data_dict)
    # print("num_trans1: {}".format(len(card_trans1)))

    sql_get_card_data2 = 'SELECT * FROM ' + table_name + ' WHERE cp_card = ' + card_number
    cur.execute(sql_get_card_data2)
    data_trans2 = cur.fetchall()
    card_trans2 = []
    colum_index = ['trans_id', 'trans_card', 'trans_account', 'trans_name', 'id_number', 'trans_time', 'trans_amount',
                   'trans_balance',
                   'py_indicator', 'cp_card', 'cp_name', 'cp_id', 'summary', 'merchant_code', 'trans_type', 'label',
                   'is_more_median',
                   'is_more_mean', 'is_more_qualite25', 'is_more_qualite75', 'time_interval', 'trans_frequency',
                   'trans_source']
    for data_tuple in data_trans2:
        data_dict = dict((colum_index[index], deal(value)) for index, value in enumerate(data_tuple))
        amount += data_dict['trans_amount']
        data_dict['trans_time'] = (data_dict['trans_time'] - datetime.datetime(1970, 1, 1)).total_seconds()
        # data_dict['trans_time'] = data_dict['trans_time'].replace(year=1970, month=1, day=1).timestamp()
        time += data_dict['trans_time']
        temp_id = data_dict['id_number']
        data_dict['id_number'] = data_dict['cp_id']
        data_dict['cp_id'] = temp_id

        temp_card = data_dict['trans_card']
        data_dict['trans_card'] = data_dict['cp_card']
        data_dict['cp_card'] = temp_card

        temp_name = data_dict['trans_name']
        data_dict['trans_name'] = data_dict['cp_name']
        data_dict['cp_name'] = temp_name

        if data_dict.get('py_indicator') and int(data_dict['py_indicator']) == 1:
            # 如果 data_dict['py_indicator'] 不为空且等于 1
            # 进行相应的操作
            data_dict['py_indicator'] = 0
        else:
            data_dict['py_indicator'] = 1
        card_trans2.append(data_dict)

    # 判断是否存在person表中无法找到该卡号相关交易记录的情况
    if len(data_trans1) + len(data_trans2) == 0:
        logging.info("{}该卡号流水无法在person_{}表中找到".format(card_number, person_id))
        return 0, 0, 0, 0, 0

    # print("num_trans2: {}".format(len(card_trans2)))
    card_trans = card_trans1 + card_trans2
    avg_amount = amount / (len(data_trans1) + len(data_trans2))
    avg_time = time / (len(data_trans1) + len(data_trans2))
    return person_id, card_trans, avg_amount, avg_time, card_label


def get_subgraph(card_trans):
    """
    对一个卡号的所有交易流水进行划分，使划分后的每个子图都为简单图
    :param card_trans: 一个列表，包含一个卡号的所有交易信息
    :return: 一个列表的列表，元素是子图列表，子图列表中包含子图里面包含的每条流水信息；
            一个整数的列表，元素是每个子图中流水信息的条数
    """
    sorted_card_trans = sorted(card_trans, key=lambda x: x['trans_time'])
    node_num = {}
    graphs = []
    subgraph_info = []
    subgraph = []
    last_trans = 0
    for i in sorted_card_trans:
        key = str(i['cp_card'])
        py = i['py_indicator']
        # 判断是否合并交易
        if last_trans and key == last_trans['cp_card'] and py == last_trans['py_indicator']:
            print("have a merge")
            last_trans['trans_balance'] = i['trans_balance']
            last_trans['trans_amount'] = last_trans['trans_amount'] + i['trans_amount']
            last_trans['summary'] = last_trans['summary'] + i['summary']
            last_trans['trans_frequency'] = i['trans_frequency']
        else:
            # 不发生合并才添加
            if last_trans != 0:
                subgraph.append(last_trans)

            last_trans = i
            node_num.setdefault(key, 0)
            if node_num[key] < 1:
                node_num[key] += 1
                # subgraph.append(i)
            else:
                graphs.append(subgraph)
                subgraph_info.append(len(subgraph))
                # 更新子图
                subgraph = []
                # 更新子图节点统计
                for x in node_num.keys():
                    node_num[x] = 0
                node_num[key] = 1
    subgraph.append(last_trans)
    graphs.append(subgraph)
    subgraph_info.append(len(subgraph))
    return graphs, subgraph_info
