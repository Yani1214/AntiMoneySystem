##########################################################实现追踪溯源功能############################################################
from neo4j import GraphDatabase
import networkx as nx

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

    # KBKNR算法
    def kbknr_algorithm(G):
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
        ranked_nodes = sorted(C_V.items(), key=lambda item: item[1], reverse=True)
        for node, composite_degree in ranked_nodes:
            print(f'节点: {node}, K_s: {K_s.get(node, "N/A")}, 综合度: {composite_degree}')
        
        return ranked_nodes

    # 从Neo4j加载图
    uri = "bolt://localhost:7687" 
    user = "neo4j"
    password = "XYZ67520x"  
    database = "test"
    G = load_graph_from_neo4j(uri, user, password ,database)

    # 运行KBKNR算法
    trace_data = kbknr_algorithm(G)

    return trace_data
