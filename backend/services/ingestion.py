import os
import tempfile
import git
from pathlib import Path
from services.graph_service import GraphService

class IngestionService:
    def __init__(self, graph_service: GraphService):
        self.graph_service = graph_service
        # Initialize tree-sitter parser
        try:
            import tree_sitter_python as tspython
            from tree_sitter import Parser, Language
            
            # Try new API first (v0.21+)
            try:
                PY_LANGUAGE = Language(tspython.language())
            except TypeError:
                # Fallback to old API
                PY_LANGUAGE = tspython.language()
            
            self.parser = Parser(PY_LANGUAGE)
            self.use_parser = True
        except Exception as e:
            print(f"Tree-sitter not available: {e}. Using simple parsing.")
            self.use_parser = False
    
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
        
        if not python_files:
            print(f"No Python files found in {repo_path}")
            return
        
        print(f"Found {len(python_files)} Python files to parse")
        
        for file_path in python_files:
            try:
                relative_path = str(file_path.relative_to(repo_path))
                print(f"Processing: {relative_path}")
                await self.graph_service.create_file_node(relative_path, "python")
                
                # Parse file
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                if self.use_parser:
                    try:
                        tree = self.parser.parse(content)
                        if tree and tree.root_node:
                            await self._extract_functions(tree.root_node, content, relative_path)
                            print(f"  ✓ Parsed with tree-sitter")
                    except Exception as parse_error:
                        print(f"Parse error for {relative_path}: {parse_error}")
                        await self._simple_parse(content, relative_path)
                else:
                    await self._simple_parse(content, relative_path)
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        print(f"✓ Finished parsing {len(python_files)} files")
    
    async def _simple_parse(self, content: bytes, file_path: str):
        """Parse using Python AST for accurate function calls, with AI pre-analysis"""
        import ast
        import re
        
        text = content.decode('utf-8', errors='ignore')
        
        # STEP 1: Try AST parsing first
        try:
            tree = ast.parse(text)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    start_line = node.lineno
                    end_line = node.end_lineno or start_line
                    
                    # Get function source
                    lines = text.split('\n')
                    func_source = '\n'.join(lines[start_line-1:end_line])
                    
                    # CRITICAL: Use AI to detect errors/improvements
                    has_error, has_improvement, error_msg, improvement_msg = await self._analyze_with_ai(func_name, func_source)
                    
                    # Store function
                    await self.graph_service.create_function_node(
                        name=func_name,
                        file_path=file_path,
                        start_line=start_line,
                        end_line=end_line,
                        source=func_source,
                        has_error=has_error,
                        has_improvement=has_improvement,
                        error_types=error_msg,
                        improvement_types=improvement_msg
                    )
                    
                    status = ""
                    if has_error:
                        status = f" [❌ ERROR: {error_msg}]"
                    elif has_improvement:
                        status = f" [⚠️ IMPROVEMENT: {improvement_msg}]"
                    print(f"  ✓ Found function: {func_name}{status}")
                    
                    # Extract function calls from this function
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            # Get the function being called
                            if isinstance(child.func, ast.Name):
                                called_func = child.func.id
                                # Create call relationship
                                await self.graph_service.create_call_relationship(func_name, called_func, file_path)
                                print(f"    → calls: {called_func}")
                            elif isinstance(child.func, ast.Attribute):
                                # Handle method calls like obj.method()
                                called_func = child.func.attr
                                await self.graph_service.create_call_relationship(func_name, called_func, file_path)
                                print(f"    → calls: {called_func}")
            
            print(f"  ✓ Parsed with AST successfully")
                    
        except SyntaxError as e:
            print(f"  ⚠️ Syntax error in {file_path} at line {e.lineno}: {e.msg}")
            print(f"  → Using AI-powered analysis for code with syntax errors")
            await self._ai_powered_fallback(text, file_path)
        except Exception as e:
            print(f"  ⚠️ Parse error: {e}")
            print(f"  → Using AI-powered analysis")
            await self._ai_powered_fallback(text, file_path)
    
    
    async def _ai_powered_fallback(self, text: str, file_path: str):
        """AI-powered fallback that can analyze code even with syntax errors"""
        import re
        
        print(f"  🤖 Using AI to analyze code with potential syntax errors")
        
        # Use regex to extract function definitions (even if syntax is broken)
        lines = text.split('\n')
        func_pattern = r'^\s*def\s+(\w+)\s*\('
        
        for i, line in enumerate(lines):
            match = re.match(func_pattern, line)
            if match:
                func_name = match.group(1)
                func_lines = [line]
                indent = len(line) - len(line.lstrip())
                
                # Extract function body (even if malformed)
                for j in range(i + 1, min(i + 100, len(lines))):
                    next_line = lines[j]
                    if next_line.strip() and not next_line.startswith(' ' * (indent + 1)):
                        if re.match(r'^\s*(def|class)\s+', next_line):
                            break
                    func_lines.append(next_line)
                
                func_source = '\n'.join(func_lines)
                
                # AI analysis is CRITICAL here - it can detect syntax errors
                has_error, has_improvement, error_msg, improvement_msg = await self._analyze_with_ai(func_name, func_source)
                
                await self.graph_service.create_function_node(
                    name=func_name,
                    file_path=file_path,
                    start_line=i + 1,
                    end_line=i + len(func_lines),
                    source=func_source,
                    has_error=has_error,
                    has_improvement=has_improvement,
                    error_types=error_msg,
                    improvement_types=improvement_msg
                )
                
                status = ""
                if has_error:
                    status = f" [❌ ERROR: {error_msg}]"
                elif has_improvement:
                    status = f" [⚠️ IMPROVEMENT: {improvement_msg}]"
                print(f"  ✓ Found function: {func_name}{status}")
                
                # Extract calls using simple regex
                builtins = {'if', 'for', 'while', 'print', 'len', 'str', 'int', 'range', 'list', 'dict', 'set', 'tuple', 'open', 'type', 'isinstance', 'float', 'bool', 'super', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'sum', 'min', 'max', 'abs', 'all', 'any'}
                for func_line in func_lines:
                    call_matches = re.findall(r'(\w+)\s*\(', func_line)
                    for called_func in call_matches:
                        if called_func not in builtins and called_func != func_name:
                            await self.graph_service.create_call_relationship(func_name, called_func, file_path)
                            print(f"    → calls: {called_func}")
        
        print(f"  ✓ AI-powered analysis complete")
    
    async def _regex_fallback(self, text: str, file_path: str):
        """Regex fallback when AST fails - now uses AI analysis"""
        # Just call the AI-powered fallback
        await self._ai_powered_fallback(text, file_path)
    
    async def _analyze_with_ai(self, func_name: str, func_source: str):
        """Use AI to analyze function for errors and improvements"""
        try:
            import os
            from google import genai
            from google.genai import types
            
            gemini_key = os.getenv("GEMINI_API_KEY")
            if not gemini_key or gemini_key.startswith("your_"):
                # Fallback to simple detection
                return self._simple_detection(func_source)
            
            client = genai.Client(api_key=gemini_key)
            
            prompt = f"""You are an expert Python code analyzer. Analyze this function CAREFULLY and ACCURATELY.

Function: {func_name}
```python
{func_source}
```

CRITICAL RULES:
1. ERROR = ONLY actual syntax errors, runtime crashes, or critical bugs that WILL break the code
2. IMPROVEMENT = style issues, TODOs, minor optimizations, or better practices
3. If the code is VALID and WORKING, say ERROR: no
4. Be STRICT - don't flag working code as errors
5. Check for syntax errors like missing colons, invalid operators, undefined variables

Examples of ERRORS:
- Syntax errors: "return 10." (invalid), missing colons, invalid operators
- Undefined variables being used
- Type errors that will crash (e.g., int + str without conversion)
- Division by zero
- Bare except clauses (except: without exception type)
- Using eval() or exec() unsafely

Examples of IMPROVEMENTS (NOT errors):
- TODO/FIXME comments
- Debug print statements
- Could use better variable names
- Missing docstrings
- Could be more efficient
- Using deprecated methods

Respond in this EXACT format (nothing else):
ERROR: [yes/no]
ERROR_MSG: [brief description if yes, otherwise "none"]
IMPROVEMENT: [yes/no]
IMPROVEMENT_MSG: [brief description if yes, otherwise "none"]"""
            
            contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
            config = types.GenerateContentConfig(
                temperature=0.1,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                safety_settings=[
                    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
                ]
            )
            
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=contents,
                config=config
            )
            
            # Parse response
            text = response.text
            has_error = "ERROR: yes" in text
            has_improvement = "IMPROVEMENT: yes" in text
            
            error_msg = None
            improvement_msg = None
            
            if has_error:
                for line in text.split('\n'):
                    if line.startswith('ERROR_MSG:'):
                        error_msg = line.replace('ERROR_MSG:', '').strip()
                        if error_msg.lower() == 'none':
                            has_error = False
                            error_msg = None
                        break
            
            if has_improvement:
                for line in text.split('\n'):
                    if line.startswith('IMPROVEMENT_MSG:'):
                        improvement_msg = line.replace('IMPROVEMENT_MSG:', '').strip()
                        if improvement_msg.lower() == 'none':
                            has_improvement = False
                            improvement_msg = None
                        break
            
            return has_error, has_improvement, error_msg, improvement_msg
            
        except Exception as e:
            print(f"  AI analysis failed: {e}, using simple detection")
            return self._simple_detection(func_source)
    
    def _simple_detection(self, func_source: str):
        """Fallback simple detection"""
        import re
        has_error = False
        has_improvement = False
        error_msg = None
        improvement_msg = None
        
        # Errors
        if 'except:' in func_source:
            has_error = True
            error_msg = "Bare except clause"
        elif re.search(r'return\s+\d+\.(?!\d)', func_source):
            has_error = True
            error_msg = "Syntax error in return statement"
        
        # Improvements
        if 'TODO' in func_source or 'FIXME' in func_source:
            has_improvement = True
            improvement_msg = "Has TODO/FIXME"
        elif 'print(' in func_source:
            has_improvement = True
            improvement_msg = "Debug print statements"
        
        return has_error, has_improvement, error_msg, improvement_msg
    
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
