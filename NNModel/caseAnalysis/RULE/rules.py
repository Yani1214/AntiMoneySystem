from datetime import datetime, timedelta, timezone
from durable.lang import *
from sqlalchemy import MetaData, Column, Integer, String, DateTime, DECIMAL
import sys

sys.path.append('..')


# 暂时没有使用
class HighRiskAccounts():
    __tablename__ = 'high_risk_accounts'
    account_id = Column(Integer, primary_key=True, autoincrement=True)  # 将account_id设为自增主键
    account = Column(String(255), unique=True, nullable=False)  # 新增账号字段，唯一且不允许为空
    risk_level = Column(Integer)  # 风险等级字段
    # 使用时区感知的 UTC 时间
    # 最后一次更新风险等级的时间戳
    last_updated = Column(DateTime, default=datetime.now(timezone.utc))  # 使用timezone.utc

    def __repr__(self):
        return f'<HighRiskAccount {self.account_id} Risk Level: {self.risk_level}>'


def get_transaction_time(trans_time):
    try:

        # 创建一个时间间隔对象
        time_delta = timedelta(seconds=trans_time)
        # 定义一个特定的日期时间对象作为基准时间，比如1970-01-01 00:00:00
        base_datetime = datetime(1970, 1, 1, 0, 0, 0)
        # 将时间间隔对象添加到基准时间中，得到新的日期时间对象
        new_datetime = base_datetime + time_delta
        return new_datetime
    except ValueError as e:
        print(f"时间格式错误: {e}")
        return None


with ruleset("large_transactions"):
    # 单笔大额交易检测
    @when_all(m.trans_amount >= 50000)
    def large_transaction(c):
        # 标记单笔交易超过50,000元的情况
        # c.m.flagged.append('LA')  # 追加标记
        c.s.result = {'flagged': 'LA'}


    @when_all(m.trans_amount < 50000)
    def not_large_transaction(c):
        pass

with ruleset("daily_transactions"):
    # 一天内累计大额交易
    @when_all(+m.trans_amount)
    def cumulative_daily(c):
        trans_time = get_transaction_time(c.m.trans_time)
        # 创建一个 timedelta 对象表示要添加的时间间隔
        # trans_time = timedelta(seconds=get_transaction_time(c.m.trans_time))
        # 确定交易时间当天的开始和结束时间
        start_of_day = datetime.combine(trans_time.date(), datetime.min.time())
        end_of_day = datetime.combine(trans_time.date(), datetime.max.time())

        transactions = [transaction for transaction in c.m.all_trans
                        if start_of_day <= get_transaction_time(transaction['trans_time']) <= end_of_day]

        if sum(t['trans_amount'] for t in transactions) > 50000:
            c.s.result = {'flagged': 'DCLA'}

with ruleset("weekly_transactions"):
    # 一周内累计大额交易
    @when_all(+m.trans_amount)
    def cumulative_weekly(c):
        trans_time = get_transaction_time(c.m.trans_time)
        # 确定交易时间当天的开始和结束时间
        start_of_week = trans_time - timedelta(days=trans_time.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        transactions = [transaction for transaction in c.m.all_trans
                        if start_of_week <= get_transaction_time(transaction['trans_time']) <= end_of_week]

        if sum(t['trans_amount'] for t in transactions) > 200000:
            c.s.result = {
                'flagged': 'WCLA'
            }

with ruleset("monthly_transactions"):
    # 一个月内累计大额交易
    @when_all(+m.trans_amount)  # @when_all(+m.trans_amount)表示存在m.trans_amount
    def cumulative_monthly(c):
        trans_time = get_transaction_time(c.m.trans_time)
        # 确定交易时间当天的开始和结束时间
        start_of_month = trans_time.replace(day=1)
        end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        transactions = [transaction for transaction in c.m.all_trans
                        if start_of_month <= get_transaction_time(transaction['trans_time']) <= end_of_month]

        if sum(t['trans_amount'] for t in transactions) > 200000:
            c.s.result = {'flagged': 'MCLA'}

with ruleset("frequent_transactions"):
    # 24小时内频繁交易检测
    @when_all(m.trans_amount > 0)
    def frequent_transactions(c):
        trans_time = get_transaction_time(c.m.trans_time)

        transactions = [transaction for transaction in c.m.all_trans
                        if (trans_time - timedelta(hours=24)) <= get_transaction_time(
                transaction['trans_time']) <= trans_time]
        # 如果交易次数超过10次，则标记这些交易
        if len(transactions) > 10:
            c.s.result = {'flagged': 'FT'}


    @when_all(m.trans_amount <= 0)
    def not_frequent_transactions(c):
        pass

with ruleset("small_amount_rapid_repeat_transactions"):
    # 小额快速重复交易检测
    @when_all(m.trans_amount < 1000)
    def small_amount_rapid_repeat_transactions(c):
        trans_time = get_transaction_time(c.m.trans_time)
        # 定义时间窗口：2小时内
        start_time_window = trans_time - timedelta(hours=2)
        end_time_window = trans_time

        transactions = [transaction for transaction in c.m.all_trans
                        if transaction['trans_amount'] < 1000 and start_time_window <= get_transaction_time(
                transaction['trans_time']) <= end_time_window]

        # 如果小额交易次数超过5次，则标记这些交易
        if len(transactions) > 5:
            c.s.result = {'flagged': 'SARRT'}


    @when_all(m.trans_amount >= 1000)
    def not_small_amount_rapid_repeat_transactions(c):
        pass

# with ruleset("circular_funding"):
#     # 循环资金检测
#     @when_all(+m.trans_amount)
#     def detect_circular_funding(c, MIN_AMOUNT=500):
#         # 从数据库获取所有交易记录，按时间排序
#         # 只考虑金额大于等于MIN_AMOUNT的交易
#         # transactions = Transaction.query.filter(Transaction.trans_amount >= MIN_AMOUNT).order_by(
#         #     Transaction.trans_time).all()
#
#         transactions_sort = sorted(Transaction, key=lambda x: x['trans_time'])
#         transactions = [transaction for transaction in transactions_sort
#                         if transaction['trans_amount'] >= MIN_AMOUNT]
#
#         graph = defaultdict(list)
#         edge_info = {}
#
#         # 构建图
#         for trans in transactions:
#             # 对于出账交易
#             if trans['py_indicator'] == 1:
#                 graph[trans['trans_card']].append((trans['cp_card'], 'out'))  # 出账
#                 edge_info[(trans['trans_card'], trans['cp_card'], 'out')] = trans
#             # 对于入账交易
#             else:
#                 graph[trans['cp_card']].append((trans['trans_card'], 'in'))  # 入账
#                 edge_info[(trans['cp_card'], trans['trans_card'], 'in')] = trans
#
#         # 检测所有环
#         def find_cycles():
#             path = []
#             visited = set()
#             stack = deque()
#
#             def dfs(node, entry_type):
#                 if node in visited:
#                     if node in path:
#                         cycle_start_idx = path.index(node)
#                         cycle = path[cycle_start_idx:]
#                         if len(cycle) > 1 and check_cycle(cycle):  # 验证循环的有效性
#                             print(f"检测到循环资金涉及的交易: {', '.join([f'{n[0]} ({n[1]})' for n in cycle])}")
#                             # 标记涉及的交易
#                             for i in range(len(cycle)):
#                                 curr_node, curr_type = cycle[i]
#                                 next_node, next_type = cycle[(i + 1) % len(cycle)]
#                                 flag_transaction(edge_info[(curr_node, next_node, curr_type)].trans_id, 'CF')
#                     return
#                 visited.add(node)
#                 path.append((node, entry_type))
#                 for neighbor, trans_type in graph[node]:
#                     dfs(neighbor, trans_type)
#                 path.pop()
#                 visited.remove(node)
#
#             def check_cycle(cycle):
#                 # 验证循环中交易类型的合理性，例如不能全是出账或全是入账
#                 types = [trans[1] for trans in cycle]
#                 return 'out' in types and 'in' in types
#
#             for node in graph:
#                 dfs(node, None)  # 开始时没有交易类型
#
#         find_cycles()

with ruleset("high_risk_transactions"):
    # 检测与高风险账户频繁交易的账户
    @when_all(m.cp_card != None)
    def check_high_risk_transactions(c):

        # 查询cp_card是否在高风险名单中

        # 加载高风险名单
        high_risk = []
        with open('../data/high_risk_cards.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                high_risk.append(line.strip())

        transactions = [transaction for transaction in c.m.all_trans if transaction['cp_card'] in high_risk]
        if len(transactions) >= 3:
            # 使用预先计算的交易频率
            if c.m.trans_frequency > 3:  # 判断交易频率是否异常高
                c.s.result = {'flagged': 'HRC'}


def check_transactions(card_trans):
    for transaction in card_trans:
        transaction['trans_amount'] = float(transaction['trans_amount'])
        # transaction['flagged']: []
        transaction.update({'flagged': []})
    new_trans = []
    for transaction in card_trans:
        event_data = {
            'trans_id': transaction['trans_id'],
            'trans_amount': float(transaction['trans_amount']),
            # 'trans_account': transaction['trans_account'],
            'trans_card': transaction['trans_card'],
            'cp_card': transaction['cp_card'],
            # 'trans_time': transaction['trans_time'].strftime('%Y-%m-%d %H:%M:%S'),  # Transaction time, 格式化为字符串
            'trans_time': transaction['trans_time'],
            'py_indicator': transaction['py_indicator'],
            'trans_frequency': transaction['trans_frequency'],
            'flagged': transaction['flagged'],
            'all_trans': card_trans
        }
        # 投递到大额交易规则集
        output = post("large_transactions", event_data)
        if output and len(output) > 3:
            result = output['result']
            if result != {}:
                transaction['flagged'].append(result['flagged'])

        # 投递到每日交易规则集
        output = post("daily_transactions", event_data)
        if output and len(output) > 3:
            result = output['result']
            if result != {}:
                transaction['flagged'].append(result['flagged'])

        # 投递到每周交易规则集
        output = post("weekly_transactions", event_data)
        if output and len(output) > 3:
            result = output['result']
            if result != {}:
                transaction['flagged'].append(result['flagged'])

        # 投递到每月交易规则集
        output = post("monthly_transactions", event_data)
        if output and len(output) > 3:
            result = output['result']
            if result != {}:
                transaction['flagged'].append(result['flagged'])

        # 投递到频繁交易规则集
        output = post("frequent_transactions", event_data)
        if output and len(output) > 3:
            result = output['result']
            if result != {}:
                transaction['flagged'].append(result['flagged'])

        # 投递到小额快速重复交易规则集
        output = post("small_amount_rapid_repeat_transactions", event_data)
        if output and len(output) > 3:
            result = output['result']
            if result != {}:
                transaction['flagged'].append(result['flagged'])

        # 投递到循环资金检测规则集
        # post("circular_funding", event_data)

        # 投递到高风险账户交易检测规则集
        # output = post("high_risk_transactions", event_data)
        # if output and len(output) > 3:
        #     result = output['result']
        #     if result != {}:
        #         transaction['flagged'].append(result['flagged'])

        new_trans.append(transaction)
    return new_trans
