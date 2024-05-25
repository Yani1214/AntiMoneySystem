# ##########################################################实现追踪溯源功能############################################################
# from neo4j import GraphDatabase
# import networkx as nx


# # 从Neo4j加载图
# uri = "bolt://localhost:7687" 
# user = "neo4j"
# password = "XYZ67520x"  
# database = "test"

# def kbknr():
#     # Neo4j数据库连接类
#     class Neo4jConnection:
#         def __init__(self, uri, user, password, database):
#             self.driver = GraphDatabase.driver(uri, auth=(user, password), database=database)
            
#         def close(self):
#             self.driver.close()
            
#         def query(self, query, parameters=None):
#             with self.driver.session() as session:
#                 result = session.run(query, parameters)
#                 return [record for record in result]

#     # 从Neo4j读取特定查询结果并转换为NetworkX图
#     def load_graph_from_neo4j(uri, user, password, database):
#         connection = Neo4jConnection(uri, user, password, database)
        
#         # 查询具有特定属性的节点和边
#         query = """
#         MATCH (n1)-[r:TRANSACTS_TO {label: 1}]->(n2)
#         RETURN id(n1) AS source, id(n2) AS target
#         """
#         results = connection.query(query)
        
#         # 创建NetworkX图
#         G = nx.Graph()
        
#         for record in results:
#             G.add_node(record['source'])
#             G.add_node(record['target'])
#             G.add_edge(record['source'], record['target'])
        
#         connection.close()
#         return G
    
#     def get_name_and_card(uri, user, password, database, node_id):
#         connection = Neo4jConnection(uri, user, password, database)

#         # 查询节点的姓名和卡号
#         query1 = """
#         MATCH (n:Node1)
#         WHERE id(n) = $nodeId
#         RETURN n.trans_name AS name, n.trans_account AS card
#         """
#         query2 = """
#         MATCH (n:Node2)
#         WHERE id(n) = $nodeId
#         RETURN n.cp_name AS name, n.cp_card AS card
#         """
#         parameters = {"nodeId": node_id}
#         result1 = connection.query(query1, parameters)
#         result2 = connection.query(query2, parameters)
        
#         # 合并两个查询的结果
#         combined_result =  result1 + result2

#         # 将查询结果转化为列表字典
#         combined_result = [record.data() for record in combined_result]
        
#         connection.close()

#         return combined_result

#     # KBKNR算法
#     def kbknr_algorithm(G):
#         K_s = {}
#         C_V = {}
#         original_graph = G.copy()

#         # 步骤1：K-shell分层
#         k_shell_dict = nx.core_number(original_graph)

#         for V in original_graph.nodes:
#             K = k_shell_dict[V]  # 初始K值为节点的core number
            
#             # 计算所有节点的K(i)和两步邻域内的节点数N(i)
#             N_V = sum(1 for neighbor in nx.single_source_shortest_path_length(original_graph, V, cutoff=2))
            
#             # 步骤3：根据步骤1得到的K(i)和N(i)，得到各个节点的影响系数μi
#             mu = K / N_V if N_V > 0 else 0
            
#             # 步骤4：计算次邻居节点数D(i)
#             D_V = N_V - K
            
#             # 步骤5：计算节点的综合度C(V)
#             C_V[V] = K + mu * D_V

#         # 步骤6：节点按综合度C(V)排序
#         # files_info = []
#         nodes_result = []
#         ranked_nodes = sorted(C_V.items(), key=lambda item: item[1], reverse=True)
#         for node, composite_degree in ranked_nodes:
#             nodes = get_name_and_card(uri, user, password, database, node)
#             for node_result in nodes:
#                 node_result["keypoint"] = composite_degree
#                 nodes_result.append(node_result)

#             # print(f'节点: {node}, K_s: {K_s.get(node, "N/A")}, 综合度: {composite_degree}')
#             # files_info.append({"name":node, "card": composite_degree, "keypoint": composite_degree})

#         print(nodes_result)
#         return ranked_nodes,nodes_result

#     G = load_graph_from_neo4j(uri, user, password ,database)

#     # 运行KBKNR算法
#     trace_data = kbknr_algorithm(G)

#     return trace_data


##########################################################实现追踪溯源功能############################################################
from neo4j import GraphDatabase
import networkx as nx

# 从Neo4j加载图
uri = "bolt://localhost:7687" 
user = "neo4j"
password = "XYZ67520x"  
database = "test"

def kbknr():
    # Neo4j数据库连接类
    class Neo4jConnection:
        def __init__(self, uri, user, password, database):
            self.driver = GraphDatabase.driver(uri, auth=(user, password), database=database)
            
        def close(self):
            self.driver.close()
            
        def query(self, query, parameters=None):
            with self.driver.session() as session:
                result = session.run(query, parameters)
                return [record for record in result]

    # 从Neo4j读取特定查询结果并转换为NetworkX图
    def load_graph_from_neo4j(uri, user, password, database):
        connection = Neo4jConnection(uri, user, password, database)
        
        # 查询具有特定属性的节点和边
        query = """
        MATCH (n1)-[r:TRANSACTS_TO {label: 1}]->(n2)
        RETURN id(n1) AS source, id(n2) AS target
        """
        results = connection.query(query)
        
        # 创建NetworkX图
        G = nx.Graph()
        
        for record in results:
            G.add_node(record['source'])
            G.add_node(record['target'])
            G.add_edge(record['source'], record['target'])
        
        connection.close()
        return G
    
    def load_all_node_info(uri, user, password, database):
        connection = Neo4jConnection(uri, user, password, database)

        # 查询所有节点的姓名和卡号
        query = """
        MATCH (n)
        OPTIONAL MATCH (n:Node1)
        RETURN id(n) AS id, n.trans_name AS name, n.trans_account AS card
        UNION
        MATCH (n)
        OPTIONAL MATCH (n:Node2)
        RETURN id(n) AS id, n.cp_name AS name, n.cp_card AS card
        """
        results = connection.query(query)

        # 将查询结果转化为字典
        node_info = {record['id']: {"name": record['name'], "card": record['card']} for record in results if record['card'] is not None}
        
        connection.close()
        return node_info

    # KBKNR算法
    def kbknr_algorithm(G, node_info):
        K_s = {}
        C_V = {}
        original_graph = G.copy()

        # 步骤1：K-shell分层
        k_shell_dict = nx.core_number(original_graph)

        for V in original_graph.nodes:
            K = k_shell_dict[V]  # 初始K值为节点的core number
            
            # 计算所有节点的K(i)和两步邻域内的节点数N(i)
            N_V = sum(1 for neighbor in nx.single_source_shortest_path_length(original_graph, V, cutoff=2))
            
            # 步骤3：根据步骤1得到的K(i)和N(i)，得到各个节点的影响系数μi
            mu = K / N_V if N_V > 0 else 0
            
            # 步骤4：计算次邻居节点数D(i)
            D_V = N_V - K
            
            # 步骤5：计算节点的综合度C(V)
            C_V[V] = K + mu * D_V

        # 步骤6：节点按综合度C(V)排序
        nodes_result = []
        ranked_nodes = sorted(C_V.items(), key=lambda item: item[1], reverse=True)
        for node, composite_degree in ranked_nodes:
            if node in node_info:
                node_result = node_info[node]
                node_result["keypoint"] = composite_degree
                nodes_result.append(node_result)

        print(nodes_result)
        return ranked_nodes, nodes_result

    G = load_graph_from_neo4j(uri, user, password, database)
    node_info = load_all_node_info(uri, user, password, database)

    # 运行KBKNR算法
    trace_data = kbknr_algorithm(G, node_info)

    return trace_data
