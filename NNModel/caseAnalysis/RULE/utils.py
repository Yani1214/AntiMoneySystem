from datetime import datetime, timedelta, timezone
import logging

from durable.lang import *
from collections import defaultdict, deque
from flask import current_app
from sqlalchemy import MetaData, Column, Integer, String, DateTime, DECIMAL
import sys

sys.path.append('..')


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


def create_transaction_model(table_name):
    # 动态生成类名，确保类名不包含空格和破折号
    class_name = f"Transaction_{table_name.replace(' ', '_').replace('-', '_')}"
    # 如果类名已全局定义，则直接返回该类
    if class_name in globals():
        return globals()[class_name]

    # # 从数据库中反射元数据:从数据库中读取已有的表结构信息，并将这些信息加载到 SQLAlchemy 的元数据对象中
    # meta = MetaData()
    # meta.reflect(bind=db.engine)

    # # 检查数据库表是否已有 'flagged' 字段，如果没有则添加
    # if 'flagged' not in meta.tables[table_name].c:
    #     with db.engine.connect() as connection:
    #         sql_command = text(f"ALTER TABLE {table_name} ADD COLUMN flagged VARCHAR(255) DEFAULT ''")
    #         connection.execute(sql_command)

    TransactionClass = type(class_name, (db.Model,), {
        '__module__': __name__,
        '__tablename__': table_name,
        '__table_args__': {'extend_existing': True},
        'trans_id': Column(Integer, primary_key=True),
        'trans_card': Column(String(255)),
        'trans_account': Column(String(255)),
        'trans_name': Column(String(255)),
        'id_number': Column(String(255)),
        'trans_time': Column(DateTime),
        'trans_amount': Column(DECIMAL(10, 2)),
        'trans_balance': Column(DECIMAL(10, 2)),
        'py_indicator': Column(Integer),
        'cp_card': Column(String(255)),
        'cp_name': Column(String(255)),
        'cp_id': Column(String(255)),
        'summary': Column(String(255)),
        'merchant_code': Column(String(255)),
        'trans_type': Column(String(255)),
        'label': Column(Integer),
        'is_more_median': Column(Integer),
        'is_more_mean': Column(Integer),
        'is_more_qualite25': Column(Integer),
        'is_more_qualite75': Column(Integer),
        'time_interval': Column(String(255)),
        'trans_frequency': Column(Integer),
        'trans_source': Column(String(255)),
        'flagged': Column(String(255), default=''),
        '__repr__': lambda self: f'<{class_name} {self.trans_id}>'
    })

    # 将新创建的类缓存并返回
    globals()[class_name] = TransactionClass
    return TransactionClass


def apply_rules_to_model(Transaction):
    model_class_name = Transaction.__name__

    logger = logging.getLogger(__name__)

    def flag_transaction(trans_id, flag_type):
        print(f"尝试标记交易 {trans_id} 为 {flag_type}")  # 调试输出
        try:
            with current_app.app_context():
                transaction = Transaction.query.get(trans_id)
                if transaction:
                    if transaction.flagged and flag_type not in transaction.flagged.split(', '):
                        transaction.flagged += ', ' + flag_type  # 追加标记
                    elif not transaction.flagged:
                        transaction.flagged = flag_type  # 新建标记
                    db.session.commit()
                    print(f"交易 {trans_id} 被标记为 {flag_type}.")  # 调试输出
                else:
                    print(f"交易 {trans_id} 未找到.")  # 调试输出
        except Exception as e:
            print(f"在标记交易 {trans_id} 时发生错误: {str(e)}")  # 输出异常信息

    def get_transaction_time(trans_time):
        try:
            return datetime.strptime(trans_time, '%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            print(f"时间格式错误: {e}")
            return None

    with ruleset(f"{model_class_name}_large_transactions"):
        # 单笔大额交易检测
        @when_all(m.trans_amount >= 50000)
        def large_transaction(c):
            # 标记单笔交易超过50,000元的情况
            flag_transaction(c.m.trans_id, 'LA')
            # Large Amount

        @when_all(m.trans_amount < 50000)
        def not_large_transaction(c):
            pass

    with ruleset(f"{model_class_name}_daily_transactions"):
        # 一天内累计大额交易
        @when_all(+m.trans_amount)
        def cumulative_daily(c):
            trans_time = get_transaction_time(c.m.trans_time)
            # 确定交易时间当天的开始和结束时间
            start_of_day = datetime.combine(trans_time.date(), datetime.min.time())
            end_of_day = datetime.combine(trans_time.date(), datetime.max.time())
            # 查询当天的所有交易
            transactions = Transaction.query.filter(
                Transaction.trans_account == c.m.trans_account,
                Transaction.trans_time >= start_of_day,
                Transaction.trans_time <= end_of_day
            ).all()
            if sum(t.trans_amount for t in transactions) > 50000:
                for transaction in transactions:
                    flag_transaction(transaction.trans_id, 'DCLA')
                    # Daily Cumulative Large Amount

    with ruleset(f"{model_class_name}_weekly_transactions"):
        # 一周内累计大额交易
        @when_all(+m.trans_amount)
        def cumulative_weekly(c):
            trans_time = get_transaction_time(c.m.trans_time)
            # 确定交易时间所在周的开始和结束时间
            start_of_week = trans_time - timedelta(days=trans_time.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            # 查询本周的所有交易
            transactions = Transaction.query.filter(
                Transaction.trans_account == c.m.trans_account,
                Transaction.trans_time >= start_of_week,
                Transaction.trans_time <= end_of_week
            ).all()
            # 如果累计金额超过200,000元，则标记所有相关交易
            if sum(t.trans_amount for t in transactions) > 200000:
                for transaction in transactions:
                    flag_transaction(transaction.trans_id, 'WCLA')
                    # Weekly Cumulative Large Amount

    with ruleset(f"{model_class_name}_monthly_transactions"):
        # 一个月内累计大额交易
        @when_all(+m.trans_amount)
        def cumulative_monthly(c):
            trans_time = get_transaction_time(c.m.trans_time)
            # 确定本月的开始和结束时间
            start_of_month = trans_time.replace(day=1)
            end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            # 查询本月的所有交易
            transactions = Transaction.query.filter(
                Transaction.trans_account == c.m.trans_account,
                Transaction.trans_time >= start_of_month,
                Transaction.trans_time <= end_of_month
            ).all()
            # 如果累计金额超过200,000元，则标记所有相关交易
            if sum(t.trans_amount for t in transactions) > 200000:
                for transaction in transactions:
                    flag_transaction(transaction.trans_id, 'MCLA')
                    # Monthly Cumulative Large Amount

    with ruleset(f"{model_class_name}_frequent_transactions"):
        # 24小时内频繁交易检测
        @when_all(m.trans_amount > 0)
        def frequent_transactions(c):
            trans_time = get_transaction_time(c.m.trans_time)
            # 追踪最近24小时的所有交易
            # print(trans_time)
            transactions = Transaction.query.filter(
                Transaction.trans_account == c.m.trans_account,
                Transaction.trans_time >= (trans_time - timedelta(hours=24)),
                Transaction.trans_time <= trans_time
            ).all()
            # 如果交易次数超过10次，则标记这些交易
            if len(transactions) > 10:
                for t in transactions:
                    flag_transaction(t.trans_id, 'FT')
                    # Frequent Transactions

        @when_all(m.trans_amount <= 0)
        def not_frequent_transactions(c):
            pass

    with ruleset(f"{model_class_name}_small_amount_rapid_repeat_transactions"):
        # 小额快速重复交易检测
        @when_all(m.trans_amount < 1000)
        def small_amount_rapid_repeat_transactions(c):
            trans_time = get_transaction_time(c.m.trans_time)
            # 定义时间窗口：2小时内
            start_time_window = trans_time - timedelta(hours=2)
            end_time_window = trans_time

            # 查询同一账户在这2小时内的所有小额交易
            transactions = Transaction.query.filter(
                Transaction.trans_account == c.m.trans_account,
                Transaction.trans_amount < 1000,  # 小额交易定义为小于1000元
                Transaction.trans_time >= start_time_window,
                Transaction.trans_time <= end_time_window
            ).all()

            # 如果小额交易次数超过5次，则标记这些交易
            if len(transactions) > 5:
                for t in transactions:
                    flag_transaction(t.trans_id, 'SARRT')  # SARRT: Small Amount Rapid Repeat Transactions
                    logger.info(f"Transaction {t.trans_id} flagged for small amount rapid repeat transactions")

        @when_all(m.trans_amount >= 1000)
        def not_small_amount_rapid_repeat_transactions(c):
            pass

    with ruleset(f"{model_class_name}_circular_funding"):
        # 循环资金检测
        @when_all(+m.trans_amount)
        def detect_circular_funding(c, MIN_AMOUNT=500):
            # 从数据库获取所有交易记录，按时间排序
            # 只考虑金额大于等于MIN_AMOUNT的交易
            transactions = Transaction.query.filter(Transaction.trans_amount >= MIN_AMOUNT).order_by(
                Transaction.trans_time).all()
            graph = defaultdict(list)
            edge_info = {}

            # 构建图
            for trans in transactions:
                # 对于出账交易
                if trans.py_indicator == 1:
                    graph[trans.trans_account].append((trans.cp_card, 'out'))  # 出账
                    edge_info[(trans.trans_account, trans.cp_card, 'out')] = trans
                # 对于入账交易
                else:
                    graph[trans.cp_card].append((trans.trans_account, 'in'))  # 入账
                    edge_info[(trans.cp_card, trans.trans_account, 'in')] = trans

            # 检测所有环
            def find_cycles():
                path = []
                visited = set()
                stack = deque()

                def dfs(node, entry_type):
                    if node in visited:
                        if node in path:
                            cycle_start_idx = path.index(node)
                            cycle = path[cycle_start_idx:]
                            if len(cycle) > 1 and check_cycle(cycle):  # 验证循环的有效性
                                print(f"检测到循环资金涉及的交易: {', '.join([f'{n[0]} ({n[1]})' for n in cycle])}")
                                # 标记涉及的交易
                                for i in range(len(cycle)):
                                    curr_node, curr_type = cycle[i]
                                    next_node, next_type = cycle[(i + 1) % len(cycle)]
                                    flag_transaction(edge_info[(curr_node, next_node, curr_type)].trans_id, 'CF')
                        return
                    visited.add(node)
                    path.append((node, entry_type))
                    for neighbor, trans_type in graph[node]:
                        dfs(neighbor, trans_type)
                    path.pop()
                    visited.remove(node)

                def check_cycle(cycle):
                    # 验证循环中交易类型的合理性，例如不能全是出账或全是入账
                    types = [trans[1] for trans in cycle]
                    return 'out' in types and 'in' in types

                for node in graph:
                    dfs(node, None)  # 开始时没有交易类型

            find_cycles()

    with ruleset(f"{model_class_name}_high_risk_transactions"):
        # 检测与高风险账户频繁交易的账户
        @when_all(m.cp_card != None)
        def check_high_risk_transactions(c):
            # 查询cp_card是否在高风险名单中
            high_risk = HighRiskAccounts.query.filter_by(account=c.m.cp_card).first()
            if high_risk:
                # 使用预先计算的交易频率
                if c.m.trans_frequency > 3:  # 判断交易频率是否异常高
                    flag_transaction(c.m.trans_id, 'HRC')
                    # High-Risk Counterparty
                    logger.info(
                        f"Account {c.m.cp_card} flagged as high-risk counterparty due to frequent transactions. Frequency: {c.m.trans_frequency}")

    # 确保处理错误并提交事务
    try:
        db.session.commit()
    except Exception as e:
        logger.error(f"提交事务更改时出错: {str(e)}")
        db.session.rollback()
