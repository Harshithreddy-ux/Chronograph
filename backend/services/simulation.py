import os
from e2b import Sandbox


class SimulationService:
    def __init__(self):
        self.api_key = os.getenv("E2B_API_KEY")
        self.sandboxes = {}
    
    async def create_sandbox(self, repo_path: str) -> str:
        """Initialize E2B sandbox with code"""
        sandbox = Sandbox(api_key=self.api_key)
        
        # Upload code to sandbox
        sandbox.filesystem.write("/workspace", repo_path)
        
        # Install dependencies if requirements.txt exists
        if os.path.exists(os.path.join(repo_path, "requirements.txt")):
            sandbox.process.start("pip install -r /workspace/requirements.txt")
        
        self.sandboxes[sandbox.id] = sandbox
        return sandbox.id
    
    async def inject_fault(self, sandbox_id: str, fault_type: str):
        """Inject specific fault into sandboxed code"""
        sandbox = self.sandboxes.get(sandbox_id)
        if not sandbox:
            raise ValueError("Sandbox not found")
        
        # Fault injection patterns
        faults = {
            "race_condition": self._inject_race_condition,
            "memory_leak": self._inject_memory_leak,
            "deadlock": self._inject_deadlock
        }
        
        injector = faults.get(fault_type, self._inject_race_condition)
        await injector(sandbox)
    
    async def _inject_race_condition(self, sandbox: Sandbox):
        """Inject race condition by removing locks"""
        # Example: Find and comment out threading locks
        fault_script = """
import re
import os

for root, dirs, files in os.walk('/workspace'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                content = f.read()
            # Comment out lock acquisitions
            content = re.sub(r'(\\s+)(lock\\.acquire\\(\\))', r'\\1# FAULT: \\2', content)
            with open(path, 'w') as f:
                f.write(content)
"""
        sandbox.filesystem.write("/tmp/inject_fault.py", fault_script)
        sandbox.process.start("python /tmp/inject_fault.py")
    
    async def _inject_memory_leak(self, sandbox: Sandbox):
        """Inject memory leak"""
        pass  # Implement specific leak injection
    
    async def _inject_deadlock(self, sandbox: Sandbox):
        """Inject deadlock condition"""
        pass  # Implement deadlock injection
    
    async def run_load_test(self, sandbox_id: str):
        """Run k6 load test"""
        sandbox = self.sandboxes.get(sandbox_id)
        if not sandbox:
            raise ValueError("Sandbox not found")
        
        # Create k6 script
        k6_script = """
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  vus: 10,
  duration: '30s',
};

export default function() {
  let res = http.get('http://localhost:8080');
  check(res, { 'status is 200': (r) => r.status === 200 });
}
"""
        sandbox.filesystem.write("/tmp/load_test.js", k6_script)
        
        # Run k6
        result = sandbox.process.start("k6 run /tmp/load_test.js")
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.exit_code
        }
