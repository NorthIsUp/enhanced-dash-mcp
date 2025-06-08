#!/usr/bin/env python3
"""
Debug script to test Dash database access and identify issues
"""

import sqlite3
import os
from pathlib import Path

def test_dash_databases():
    """Test access to Dash databases and report findings"""
    docsets_path = Path.home() / "Library/Application Support/Dash/DocSets"
    print(f"Looking for docsets in: {docsets_path}")
    
    if not docsets_path.exists():
        print("ERROR: Docsets directory does not exist!")
        return
        
    # Look for docsets in subdirectories (Dash structure: DocSets/Name/Name.docset/)
    docset_dirs = []
    for item in docsets_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'): # Skip hidden directories
            candidate_path = item / f"{item.name}.docset"
            if candidate_path.exists():
                docset_dirs.append(candidate_path)
    
    print(f"Found {len(docset_dirs)} valid docset directories")
    
    for docset_dir in docset_dirs[:5]:  # Test first 5 docsets
        print(f"\n--- Testing {docset_dir.name} ---")
        
        db_path = docset_dir / "Contents/Resources/docSet.dsidx"
        docs_path = docset_dir / "Contents/Resources/Documents"
        
        print(f"DB Path exists: {db_path.exists()}")
        print(f"Docs Path exists: {docs_path.exists()}")
        
        if db_path.exists():
            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # Check tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                print(f"Tables: {tables}")
                
                if "searchIndex" in tables:
                    # Check schema
                    cursor.execute("PRAGMA table_info(searchIndex)")
                    columns = [row[1] for row in cursor.fetchall()]
                    print(f"SearchIndex columns: {columns}")
                    
                    # Test query
                    cursor.execute("SELECT COUNT(*) FROM searchIndex")
                    count = cursor.fetchone()[0]
                    print(f"Total entries: {count}")
                    
                    if count > 0:
                        # Sample entries
                        cursor.execute("SELECT name, type, path FROM searchIndex LIMIT 3")
                        samples = cursor.fetchall()
                        print(f"Sample entries: {samples}")
                        
                        # Test search
                        cursor.execute("SELECT name, type, path FROM searchIndex WHERE name LIKE '%python%' LIMIT 3")
                        search_results = cursor.fetchall()
                        print(f"Search results for 'python': {search_results}")
                    
                conn.close()
                print("✅ Database accessible")
                
            except Exception as e:
                print(f"❌ Database error: {e}")
        else:
            print("❌ Database file not found")
            
if __name__ == "__main__":
    test_dash_databases()

