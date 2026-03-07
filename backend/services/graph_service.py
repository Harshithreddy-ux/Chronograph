from neo4j import GraphDatabase
import os


class GraphService:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            auth=(
                os.getenv("NEO4J_USER", "neo4j"),
                os.getenv("NEO4J_PASSWORD", "chronograph123")
            )
        )
    
    def close(self):
        self.driver.close()
    
    async def create_file_node(self, path: str, language: str):
        """Create a File node"""
        with self.driver.session() as session:
            session.run(
                "MERGE (f:File {path: $path}) SET f.language = $language",
                path=path, language=language
            )
    
    async def create_function_node(self, name: str, file_path: str, 
                                   start_line: int, end_line: int, source: str):
        """Create a Function node and link to File"""
        with self.driver.session() as session:
            session.run("""
                MATCH (f:File {path: $file_path})
                MERGE (fn:Function {name: $name, file_path: $file_path})
                SET fn.start_line = $start_line,
                    fn.end_line = $end_line,
                    fn.source = $source
                MERGE (f)-[:CONTAINS]->(fn)
            """, name=name, file_path=file_path, start_line=start_line,
                end_line=end_line, source=source)
    
    async def create_call_relationship(self, caller: str, callee: str, file_path: str):
        """Create CALLS relationship between functions"""
        with self.driver.session() as session:
            session.run("""
                MATCH (caller:Function {name: $caller, file_path: $file_path})
                MATCH (callee:Function {name: $callee})
                MERGE (caller)-[:CALLS]->(callee)
            """, caller=caller, callee=callee, file_path=file_path)
    
    async def query_context(self, function_name: str):
        """Query graph for function context"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (f:Function {name: $name})-[r:CALLS]->(d:Function)
                RETURN f.name as function, f.source as source,
                       collect(d.name) as dependencies
            """, name=function_name)
            return [dict(record) for record in result]
    
    async def get_visualization_data(self):
        """Get nodes and edges for React Flow"""
        with self.driver.session() as session:
            # Get nodes with all properties
            nodes_result = session.run("""
                MATCH (n)
                WHERE n:File OR n:Function
                RETURN id(n) as id, labels(n)[0] as type, 
                       n.name as name, n.path as path, n.file_path as file_path,
                       n.start_line as start_line, n.end_line as end_line
            """)
            nodes = [dict(record) for record in nodes_result]
            
            # Get edges
            edges_result = session.run("""
                MATCH (a)-[r]->(b)
                RETURN id(a) as source, id(b) as target, type(r) as type
            """)
            edges = [dict(record) for record in edges_result]
            
            return {"nodes": nodes, "edges": edges}
    
    async def get_function_source(self, function_name: str, file_path: str):
        """Get source code for a specific function"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (f:Function {name: $name, file_path: $file_path})
                RETURN f.source as source, f.start_line as start_line, 
                       f.end_line as end_line
            """, name=function_name, file_path=file_path)
            record = result.single()
            if record:
                return dict(record)
            return {"source": "# Function not found", "start_line": 0, "end_line": 0}
