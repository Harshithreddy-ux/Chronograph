import os
import tempfile
import git
from pathlib import Path
import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from services.graph_service import GraphService


class IngestionService:
    def __init__(self, graph_service: GraphService):
        self.graph_service = graph_service
        PY_LANGUAGE = Language(tspython.language())
        self.parser = Parser(PY_LANGUAGE)
    
    async def clone_repo(self, repo_url: str) -> str:
        """Clone repository to temporary directory"""
        temp_dir = tempfile.mkdtemp(prefix="chronograph_")
        git.Repo.clone_from(repo_url, temp_dir)
        return temp_dir
    
    async def parse_and_store(self, repo_path: str):
        """Parse repository and store in Neo4j"""
        repo_path = Path(repo_path)
        
        # Find all Python files
        python_files = list(repo_path.rglob("*.py"))
        
        for file_path in python_files:
            relative_path = str(file_path.relative_to(repo_path))
            await self.graph_service.create_file_node(relative_path, "python")
            
            # Parse file
            with open(file_path, 'rb') as f:
                content = f.read()
                tree = self.parser.parse(content)
                await self._extract_functions(tree.root_node, content, relative_path)
    
    async def _extract_functions(self, node, content: bytes, file_path: str):
        """Extract function definitions from AST"""
        if node.type == 'function_definition':
            name_node = node.child_by_field_name('name')
            if name_node:
                func_name = content[name_node.start_byte:name_node.end_byte].decode('utf-8')
                func_source = content[node.start_byte:node.end_byte].decode('utf-8')
                
                await self.graph_service.create_function_node(
                    name=func_name,
                    file_path=file_path,
                    start_line=node.start_point[0],
                    end_line=node.end_point[0],
                    source=func_source
                )
                
                # Extract function calls
                await self._extract_calls(node, content, func_name, file_path)
        
        # Recurse
        for child in node.children:
            await self._extract_functions(child, content, file_path)
    
    async def _extract_calls(self, node, content: bytes, caller: str, file_path: str):
        """Extract function calls from function body"""
        if node.type == 'call':
            func_node = node.child_by_field_name('function')
            if func_node and func_node.type == 'identifier':
                callee = content[func_node.start_byte:func_node.end_byte].decode('utf-8')
                await self.graph_service.create_call_relationship(caller, callee, file_path)
        
        for child in node.children:
            await self._extract_calls(child, content, caller, file_path)
