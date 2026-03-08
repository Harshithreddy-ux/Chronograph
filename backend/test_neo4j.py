"""Test Neo4j connection and query data"""
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    """Test Neo4j connection"""
    try:
        driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            auth=(
                os.getenv("NEO4J_USER", "neo4j"),
                os.getenv("NEO4J_PASSWORD", "chronograph123")
            )
        )
        
        with driver.session() as session:
            # Test connection
            result = session.run("RETURN 1 as test")
            print("✓ Neo4j connection successful!")
            
            # Count nodes
            result = session.run("MATCH (n) RETURN labels(n)[0] as type, count(n) as count")
            print("\nNodes in database:")
            for record in result:
                print(f"  {record['type']}: {record['count']}")
            
            # Get all functions
            result = session.run("""
                MATCH (f:Function)
                RETURN f.name as name, f.file_path as file
                LIMIT 10
            """)
            print("\nFunctions found:")
            functions = list(result)
            if functions:
                for record in functions:
                    print(f"  - {record['name']} in {record['file']}")
            else:
                print("  No functions found!")
            
            # Get all files
            result = session.run("MATCH (f:File) RETURN f.path as path")
            print("\nFiles found:")
            files = list(result)
            if files:
                for record in files:
                    print(f"  - {record['path']}")
            else:
                print("  No files found!")
        
        driver.close()
        
    except Exception as e:
        print(f"✗ Neo4j connection failed: {e}")
        print("\nMake sure Neo4j is running:")
        print("  docker run -d -p 7474:7474 -p 7687:7687 \\")
        print("    -e NEO4J_AUTH=neo4j/chronograph123 \\")
        print("    neo4j:latest")

if __name__ == "__main__":
    test_connection()
