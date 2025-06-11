#!/usr/bin/env python3
"""
Enhanced Dash MCP Server
========================

A Model Context Protocol (MCP) server that provides Claude with intelligent access to local Dash documentation.

Overview
--------
This server bridges the gap between Claude and your locally stored Dash docsets, enabling seamless documentation
lookup during development workflows. It transforms static documentation into an interactive, searchable resource
that integrates directly with Claude's capabilities.

Key Features
------------
- **Intelligent Caching**: Multi-tier caching system (memory + disk) with configurable TTL for optimal performance
- **Content Extraction**: Extracts clean, readable content from HTML, Markdown, and text documentation files
- **Fuzzy Search Engine**: Advanced search with typo tolerance, partial matching, and intelligent ranking
- **Multiple Format Support**: Handles various documentation formats with extensible architecture
- **Enhanced Ranking**: Multi-factor scoring system considering exact matches, prefixes, types, and popularity
- **Project Context Awareness**: Analyzes project structure to provide relevant documentation
- **Implementation Guidance**: Provides best practices and patterns for specific features
- **Migration Support**: Helps with version upgrades and breaking changes
- **Latest API Reference**: Pulls current API documentation with examples

Architecture
------------
The server consists of several key components:

1. **CacheManager**: Handles both memory and disk caching with automatic expiration
2. **ContentExtractor**: Processes different file formats and extracts clean text content
3. **FuzzySearchEngine**: Provides intelligent search with scoring and ranking algorithms
4. **DashMCPServer**: Main server class orchestrating all components
5. **ProjectAwareDocumentationServer**: Adds project context and intelligent documentation selection

Supported Documentation Formats
-------------------------------
- HTML (.html, .htm) - Primary Dash format
- Markdown (.md) - Common in modern documentation
- Plain Text (.txt) - Simple documentation files

Directory Structure
-------------------
Dash docsets are expected at: ~/Library/Application Support/Dash/DocSets/
Each docset contains:
- Contents/Resources/docSet.dsidx (SQLite database with search index)
- Contents/Resources/Documents/ (actual documentation files)
- Contents/Info.plist (metadata about the docset)

Usage Examples
--------------
# Basic search across all docsets
search_dash_docs("Array.map")

# Search with full content extraction
search_dash_docs("useState", include_content=True)

# Targeted search with fuzzy matching
search_dash_docs("fetch", docset="javascript", use_fuzzy=True, limit=10)

# Project-aware documentation
get_project_relevant_docs("authentication", "/path/to/project")

# Implementation guidance
get_implementation_guidance("real-time chat", "/path/to/project")

# Migration documentation
get_migration_docs("react", "17", "18")

# Latest API reference
get_latest_api_reference("useState", "react")

Integration Workflow
-------------------
1. Install dependencies: pip install mcp beautifulsoup4 fuzzywuzzy python-levenshtein aiofiles aiohttp
2. Configure Claude to connect to this MCP server
3. Use natural language to search documentation through Claude
4. Server handles caching, ranking, and content extraction automatically

Performance Considerations
-------------------------
- First search may be slower due to docset scanning and cache building
- Subsequent searches benefit from intelligent caching
- Content extraction adds latency but provides much richer context
- Fuzzy search trades some speed for much better match quality

Cache Management
---------------
- Memory cache: Fast access for recently accessed items
- Disk cache: Persistent storage in ~/.cache/dash-mcp/
- Automatic cleanup: Items expire after 1 hour by default
- Cache keys: Generated from search parameters for optimal hit rates

Error Handling
--------------
- Graceful degradation when docsets are missing or corrupted
- Fallback to exact matching if fuzzy search fails
- Content extraction errors don't break search functionality
- Comprehensive logging for debugging and monitoring

Author: Josh (Fort Collins, CO)
Created for integration with Claude via MCP
Optimized for Python/JavaScript/React development workflows
"""
# Merge fix for Dash directory structure and database schema handling with latest version
# Fix docset discovery and add support for both Core Data and searchIndex schemas
__version__ = "1.2.12"  # Project version for SemVer and CHANGELOG automation

import asyncio
import contextlib
import logging
from logging.handlers import RotatingFileHandler
import hashlib
import json
import os
import re
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import aiofiles
import aiohttp
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz, process
from mcp.server import Server
from mcp.server.stdio import stdio_server  # Provides STDIO streams for Server.run
from mcp.types import Tool, TextContent


def configure_logging(log_level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """Configure console and optional file logging."""
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    handlers: List[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3))
    logging.basicConfig(level=log_level, format=log_format, handlers=handlers, force=True)


# Environment-controlled logging configuration
LOG_LEVEL = os.getenv("DASH_MCP_LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv(
    "DASH_MCP_LOG_FILE",
    str(Path.home() / ".cache" / "dash-mcp" / "server.log"),
)
configure_logging(getattr(logging, LOG_LEVEL, logging.INFO), LOG_FILE)
logger = logging.getLogger(__name__)


@dataclass
class DocEntry:
    """Represents a documentation entry"""

    name: str
    type: str
    path: str
    docset: str
    content: Optional[str] = None
    anchor: Optional[str] = None
    score: float = 0.0


@dataclass
class ProjectContext:
    """Represents the current project context for documentation relevance"""

    language: Optional[str] = None
    framework: Optional[str] = None
    dependencies: Optional[List[str]] = None
    project_type: Optional[str] = None
    current_files: Optional[List[str]] = None


class CacheManager:
    """Handles caching of documentation content and search results"""

    def __init__(self, cache_dir: Optional[Path] = None) -> None:
        self.cache_dir = cache_dir or Path.home() / ".cache" / "dash-mcp"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache: Dict[str, Tuple[Any, float]] = {}
        self.cache_ttl = 3600  # 1 hour

    def _get_cache_key(self, data: str) -> str:
        """Generate cache key from data"""
        return hashlib.md5(data.encode()).hexdigest()

    async def get(self, key: str) -> Optional[Any]:
        """Get cached data"""
        # Check memory cache first
        if key in self.memory_cache:
            data, timestamp = self.memory_cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return data
            else:
                del self.memory_cache[key]

        # Check disk cache
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                async with aiofiles.open(cache_file, "r") as f:
                    cached_data = json.loads(await f.read())
                    if time.time() - cached_data["timestamp"] < self.cache_ttl:
                        # Update memory cache
                        self.memory_cache[key] = (
                            cached_data["data"],
                            cached_data["timestamp"],
                        )
                        return cached_data["data"]
            except Exception:
                pass

        return None

    async def set(self, key: str, data: Any) -> None:
        """Cache data"""
        timestamp = time.time()

        # Update memory cache
        self.memory_cache[key] = (data, timestamp)

        # Update disk cache
        cache_file = self.cache_dir / f"{key}.json"
        try:
            async with aiofiles.open(cache_file, "w") as f:
                await f.write(json.dumps({"data": data, "timestamp": timestamp}))
        except Exception as e:
            logger.error("Cache write error: %s", e)


class ContentExtractor:
    """Extracts and processes documentation content"""

    @staticmethod
    async def extract_html_content(file_path: Path) -> str:
        """Extract clean text content from HTML files"""
        try:
            async with aiofiles.open(
                file_path, "r", encoding="utf-8", errors="ignore"
            ) as f:
                html_content = await f.read()

            soup = BeautifulSoup(html_content, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()

            # Extract main content (try common selectors)
            main_content = (
                soup.find("main")
                or soup.find("article")
                or soup.find("div", class_=re.compile(r"content|main|body"))
                or soup.find("body")
                or soup
            )

            # Get text and clean it up
            text = main_content.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)

            return text[:5000]  # Limit content length

        except Exception as e:
            logger.error("Error extracting content from %s: %s", file_path, e)
            return ""

    @staticmethod
    async def extract_markdown_content(file_path: Path) -> str:
        """Extract content from markdown files"""
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                content = await f.read()
            return content[:5000]
        except Exception:
            return ""


class FuzzySearchEngine:
    """Enhanced search with fuzzy matching and ranking"""

    @staticmethod
    def fuzzy_search(
        query: str, entries: List[DocEntry], threshold: int = 60
    ) -> List[DocEntry]:
        """Perform fuzzy search on documentation entries"""
        if not entries:
            return []

        # Create searchable strings
        searchable = []
        for entry in entries:
            searchable.append(f"{entry.name} {entry.type} {entry.docset}")

        # Get fuzzy matches
        matches = process.extract(query, searchable, limit=len(entries))

        # Filter and score results
        results = []
        for match, score in matches:
            if score >= threshold:
                idx = searchable.index(match)
                entry = entries[idx]
                entry.score = score
                results.append(entry)

        return sorted(results, key=lambda x: x.score, reverse=True)

    @staticmethod
    def rank_results(entries: List[DocEntry], query: str) -> List[DocEntry]:
        """Advanced ranking of search results"""
        for entry in entries:
            score = 0
            query_lower = query.lower()
            name_lower = entry.name.lower()

            # Exact match bonus
            if query_lower == name_lower:
                score += 100
            elif query_lower in name_lower:
                score += 50

            # Prefix match bonus
            if name_lower.startswith(query_lower):
                score += 30

            # Type-specific bonuses
            if entry.type.lower() in ["function", "method", "class"]:
                score += 10

            # Docset popularity (you can customize this)
            popular_docsets = ["python", "javascript", "react", "nodejs"]
            if entry.docset.lower() in popular_docsets:
                score += 5

            entry.score = score

        return sorted(entries, key=lambda x: x.score, reverse=True)


class DashMCPServer:
    """Enhanced Dash MCP Server with caching, content extraction, and fuzzy search"""

    def __init__(self):
        env_path = os.getenv("DASH_DOCSETS_PATH")
        self.docsets_path = (
            Path(env_path)
            if env_path
            else Path.home() / "Library/Application Support/Dash/DocSets"
        )

        # Resolve symlinks and handle paths that point to the parent "Dash" directory
        adjusted_path = self.docsets_path.resolve()
        if adjusted_path.name != "DocSets" and (adjusted_path / "DocSets").exists():
            # User supplied Dash root; use its DocSets folder instead
            adjusted_path = adjusted_path / "DocSets"
        self.docsets_path = adjusted_path

        logger.info("Using docset directory %s", self.docsets_path)
        if not self.docsets_path.exists():
            logger.warning("Docset directory %s does not exist", self.docsets_path)
        self.server = Server("dash-docs-enhanced")
        self.cache = CacheManager()
        self.extractor = ContentExtractor()
        self.search_engine = FuzzySearchEngine()

        # Supported file formats
        self.supported_formats = {
            ".html": self.extractor.extract_html_content,
            ".htm": self.extractor.extract_html_content,
            ".md": self.extractor.extract_markdown_content,
            ".txt": self.extractor.extract_markdown_content,
        }

    async def get_available_docsets(self) -> List[Dict[str, str]]:
        """Scan for available Dash docsets with caching"""
        cache_key = "available_docsets"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        docsets = []
        # Handle Dash directory structure: both direct .docset files and nested structure
        if self.docsets_path.exists():
            # Search recursively so docsets in subfolders are discovered (Dash 4 layout)
            for docset_dir in self.docsets_path.glob("**/*.docset"):
                db_path = docset_dir / "Contents/Resources/docSet.dsidx"
                docs_path = docset_dir / "Contents/Resources/Documents"

                if db_path.exists():
                    # Get docset info
                    info_plist = docset_dir / "Contents/Info.plist"
                    docset_info = {
                        "name": docset_dir.parent.name,  # Use the parent directory name
                        "db_path": str(db_path),
                        "docs_path": str(docs_path),
                        "has_content": docs_path.exists(),
                    }

                    # Try to get display name from plist
                    if info_plist.exists():
                        try:
                            # Basic plist parsing (you might want to use plistlib)
                            with open(info_plist, "r") as f:
                                content = f.read()
                                if "CFBundleName" in content:
                                    # Simple extraction
                                    match = re.search(
                                        r"<key>CFBundleName</key>\s*<string>([^<]+)</string>",
                                        content,
                                    )
                                    if match:
                                        docset_info["display_name"] = match.group(1)
                        except Exception:
                            pass

                    docsets.append(docset_info)

        await self.cache.set(cache_key, docsets)
        return docsets

    async def search_docset(
        self,
        query: str,
        docset_name: Optional[str] = None,
        limit: int = 20,
        include_content: bool = False,
        use_fuzzy: bool = True,
    ) -> List[Dict[str, Any]]:
        """Enhanced search within Dash docsets"""

        # Create cache key
        cache_key = self.cache._get_cache_key(
            f"{query}_{docset_name}_{limit}_{include_content}"
        )
        cached = await self.cache.get(cache_key)
        if cached and not include_content:  # Don't cache content results
            return cached

        docsets = await self.get_available_docsets()

        if docset_name:
            docsets = [d for d in docsets if d["name"].lower() == docset_name.lower()]

        all_entries = []

        for docset in docsets:
            try:
                conn = sqlite3.connect(docset["db_path"])
                cursor = conn.cursor()

                # Try different schema variations
                try:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = [row[0] for row in cursor.fetchall()]

                    if "searchIndex" in tables:
                        # Traditional searchIndex schema
                        cursor.execute("PRAGMA table_info(searchIndex)")
                        columns = [row[1] for row in cursor.fetchall()]

                        # Adapt query based on available columns
                        if "anchor" in columns:
                            sql = "SELECT name, type, path, anchor FROM searchIndex WHERE name LIKE ? LIMIT ?"
                        else:
                            sql = "SELECT name, type, path FROM searchIndex WHERE name LIKE ? LIMIT ?"

                        cursor.execute(
                            sql, (f"%{query}%", limit * 2)
                        )  # Get more for fuzzy filtering

                        for row in cursor.fetchall():
                            entry = DocEntry(
                                name=row[0],
                                type=row[1],
                                path=row[2],
                                docset=docset["name"],
                                anchor=row[3] if len(row) > 3 else None,
                            )
                            all_entries.append(entry)
                    
                    elif "ZTOKEN" in tables and "ZTOKENTYPE" in tables:
                        # Core Data schema (newer Dash versions)
                        try:
                            # Query the Core Data schema
                            sql = """
                            SELECT t.ZTOKENNAME as name, tt.ZTYPENAME as type, t.ZPATH as path
                            FROM ZTOKEN t
                            LEFT JOIN ZTOKENTYPE tt ON t.ZTOKENTYPE = tt.Z_PK
                            WHERE t.ZTOKENNAME LIKE ? 
                            LIMIT ?
                            """
                            
                            cursor.execute(sql, (f"%{query}%", limit * 2))
                            
                            for row in cursor.fetchall():
                                if row[0]:  # Ensure name is not None
                                    entry = DocEntry(
                                        name=row[0],
                                        type=row[1] or "Unknown",
                                        path=row[2] or "",
                                        docset=docset["name"],
                                    )
                                    all_entries.append(entry)
                        except sqlite3.Error as e:
                            logger.warning("Core Data query failed for %s: %s", docset["name"], e)
                            # Fallback to simpler query
                            try:
                                cursor.execute("SELECT ZTOKENNAME, ZPATH FROM ZTOKEN WHERE ZTOKENNAME LIKE ? LIMIT ?", (f"%{query}%", limit))
                                for row in cursor.fetchall():
                                    if row[0]:
                                        entry = DocEntry(
                                            name=row[0],
                                            type="Unknown",
                                            path=row[1] or "",
                                            docset=docset["name"],
                                        )
                                        all_entries.append(entry)
                            except sqlite3.Error:
                                logger.warning("Fallback query also failed for %s", docset["name"])
                    
                    else:
                        logger.warning("Unknown database schema for docset %s. Tables: %s", docset["name"], tables)

                except sqlite3.Error as e:
                    logger.error("Database error in %s: %s", docset['name'], e)

                conn.close()

            except Exception as e:
                logger.error("Error searching %s: %s", docset['name'], e)

        # Apply fuzzy search if enabled
        if use_fuzzy and all_entries:
            all_entries = self.search_engine.fuzzy_search(query, all_entries)
        else:
            all_entries = self.search_engine.rank_results(all_entries, query)

        # Limit results
        all_entries = all_entries[:limit]

        # Extract content if requested
        if include_content:
            await self._add_content_to_entries(all_entries)

        # Convert to dict format
        results = []
        for entry in all_entries:
            result = {
                "docset": entry.docset,
                "name": entry.name,
                "type": entry.type,
                "path": entry.path,
                "score": entry.score,
            }
            if entry.anchor:
                result["anchor"] = entry.anchor
            if entry.content:
                result["content"] = entry.content
            results.append(result)

        # Cache results (without content)
        if not include_content:
            await self.cache.set(cache_key, results)

        return results

    async def _add_content_to_entries(self, entries: List[DocEntry]) -> None:
        """Add content to documentation entries"""
        docsets = await self.get_available_docsets()
        docset_paths = {d["name"]: d["docs_path"] for d in docsets if d["has_content"]}

        for entry in entries:
            if entry.docset not in docset_paths:
                continue

            docs_path = Path(docset_paths[entry.docset])
            file_path = docs_path / entry.path

            # Try different file extensions if exact path doesn't exist
            if not file_path.exists():
                for ext in [".html", ".htm"]:
                    alt_path = file_path.with_suffix(ext)
                    if alt_path.exists():
                        file_path = alt_path
                        break

            if file_path.exists():
                file_ext = file_path.suffix.lower()
                if file_ext in self.supported_formats:
                    try:
                        content = await self.supported_formats[file_ext](file_path)
                        entry.content = content
                    except Exception as e:
                        logger.error("Error extracting content from %s: %s", file_path, e)


class ProjectAwareDocumentationServer:
    """Extended server with project-aware documentation tools"""

    def __init__(self, dash_server: DashMCPServer):
        self.dash_server = dash_server
        self.project_context = ProjectContext()

    async def analyze_project_context(self, project_path: str) -> ProjectContext:
        """Analyze project structure to determine relevant documentation"""
        context = ProjectContext()
        project_dir = Path(project_path)

        # Check for common project files
        if (project_dir / "package.json").exists():
            try:
                async with aiofiles.open(project_dir / "package.json", "r") as f:
                    package_data = json.loads(await f.read())
                    context.language = "javascript"
                    context.dependencies = list(
                        package_data.get("dependencies", {}).keys()
                    )

                    # Detect frameworks
                    deps = context.dependencies
                    if "react" in deps:
                        context.framework = "react"
                    elif "vue" in deps:
                        context.framework = "vue"
                    elif "angular" in deps:
                        context.framework = "angular"
                    elif "next" in deps or "nextjs" in deps:
                        context.framework = "nextjs"
                    elif "express" in deps:
                        context.framework = "express"

            except Exception as e:
                logger.error("Error analyzing package.json: %s", e)

        elif (project_dir / "requirements.txt").exists() or (
            project_dir / "pyproject.toml"
        ).exists():
            context.language = "python"
            context.dependencies = []

            # Check requirements.txt
            req_file = project_dir / "requirements.txt"
            if req_file.exists():
                try:
                    async with aiofiles.open(req_file, "r") as f:
                        content = await f.read()
                        for line in content.split("\n"):
                            if line.strip() and not line.startswith("#"):
                                dep = (
                                    line.split("==")[0]
                                    .split(">=")[0]
                                    .split("<=")[0]
                                    .strip()
                                )
                                context.dependencies.append(dep)
                except Exception:
                    pass

            # Detect Python frameworks
            if context.dependencies:
                deps = [d.lower() for d in context.dependencies]
                if "django" in deps:
                    context.framework = "django"
                elif "flask" in deps:
                    context.framework = "flask"
                elif "fastapi" in deps:
                    context.framework = "fastapi"
                elif "streamlit" in deps:
                    context.framework = "streamlit"

        # Get current files for context
        try:
            context.current_files = [
                str(f.relative_to(project_dir))
                for f in project_dir.rglob("*")
                if f.is_file() and not any(part.startswith(".") for part in f.parts)
            ][
                :50
            ]  # Limit to 50 files
        except Exception:
            context.current_files = []

        return context

    async def get_relevant_documentation(
        self, query: str, project_context: ProjectContext, include_latest: bool = True
    ) -> List[Dict[str, Any]]:
        """Get documentation most relevant to current project and query"""

        # Determine relevant docsets based on project context
        relevant_docsets = []

        if project_context.language == "javascript":
            relevant_docsets.extend(["javascript", "nodejs", "mdn"])

            if project_context.framework == "react":
                relevant_docsets.extend(["react", "react_native"])
            elif project_context.framework == "vue":
                relevant_docsets.append("vue")
            elif project_context.framework == "angular":
                relevant_docsets.append("angular")
            elif project_context.framework == "nextjs":
                relevant_docsets.extend(["react", "nextjs"])

        elif project_context.language == "python":
            relevant_docsets.extend(["python", "python_3"])

            if project_context.framework == "django":
                relevant_docsets.append("django")
            elif project_context.framework == "flask":
                relevant_docsets.append("flask")
            elif project_context.framework == "fastapi":
                relevant_docsets.append("fastapi")

        # Add dependency-specific docsets
        if project_context.dependencies:
            for dep in project_context.dependencies:
                dep_lower = dep.lower()
                # Map common dependencies to docsets
                dep_mapping = {
                    "lodash": ["lodash"],
                    "axios": ["axios"],
                    "express": ["express", "nodejs"],
                    "mongoose": ["mongoose"],
                    "pandas": ["pandas"],
                    "numpy": ["numpy"],
                    "requests": ["python_requests"],
                    "tensorflow": ["tensorflow"],
                    "pytorch": ["pytorch"],
                }
                if dep_lower in dep_mapping:
                    relevant_docsets.extend(dep_mapping[dep_lower])

        # Search across relevant docsets
        all_results = []
        available_docsets = await self.dash_server.get_available_docsets()
        available_names = [d["name"].lower() for d in available_docsets]

        for docset in relevant_docsets:
            if docset.lower() in available_names:
                try:
                    results = await self.dash_server.search_docset(
                        query=query,
                        docset_name=docset,
                        limit=10,
                        include_content=include_latest,
                        use_fuzzy=True,
                    )
                    # Add relevance boost for project-specific docsets
                    for result in results:
                        result["project_relevance"] = True
                        result["score"] = (
                            result.get("score", 0) + 20
                        )  # Boost project-relevant results
                    all_results.extend(results)
                except Exception as e:
                    logger.error("Error searching %s: %s", docset, e)

        # If no project-specific results, fall back to general search
        if not all_results:
            all_results = await self.dash_server.search_docset(
                query=query, limit=15, include_content=include_latest, use_fuzzy=True
            )

        # Sort by score and return top results
        all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return all_results[:20]

    async def get_best_practices_for_feature(
        self, feature_description: str, project_context: ProjectContext
    ) -> List[Dict[str, Any]]:
        """Get best practices and patterns for implementing a specific feature"""

        # Create search queries for best practices
        queries = []

        if project_context.framework == "react":
            queries.extend(
                [
                    f"react {feature_description} best practices",
                    f"react {feature_description} patterns",
                    f"react hooks {feature_description}",
                    f"{feature_description} component patterns",
                ]
            )
        elif project_context.framework == "django":
            queries.extend(
                [
                    f"django {feature_description} best practices",
                    f"django {feature_description} patterns",
                    f"{feature_description} views models",
                ]
            )
        elif project_context.language == "python":
            queries.extend(
                [
                    f"python {feature_description} best practices",
                    f"python {feature_description} patterns",
                ]
            )
        else:
            queries.append(f"{feature_description} best practices")

        all_results = []
        for query in queries:
            results = await self.get_relevant_documentation(
                query=query, project_context=project_context, include_latest=True
            )
            all_results.extend(results)

        # Deduplicate and return top results
        seen = set()
        unique_results = []
        for result in all_results:
            key = f"{result['docset']}:{result['name']}:{result['path']}"
            if key not in seen:
                seen.add(key)
                unique_results.append(result)

        return unique_results[:15]

    async def get_migration_guidance(
        self, from_version: str, to_version: str, technology: str
    ) -> List[Dict[str, Any]]:
        """Get documentation for migrating between versions"""

        migration_queries = [
            f"{technology} migrate {from_version} {to_version}",
            f"{technology} migration guide {to_version}",
            f"{technology} upgrade {to_version}",
            f"{technology} breaking changes {to_version}",
            f"{technology} changelog {to_version}",
        ]

        all_results = []
        for query in migration_queries:
            results = await self.dash_server.search_docset(
                query=query, limit=10, include_content=True, use_fuzzy=True
            )
            all_results.extend(results)

        return all_results[:20]


# Initialize servers
server: Server = Server("dash-docs-enhanced")
dash_server = DashMCPServer()
project_server = ProjectAwareDocumentationServer(dash_server)


# 1. Add required capabilities declaration
# 1. Add required capabilities declaration
async def list_capabilities(server):
    """Declare server capabilities per MCP spec"""
    return server.get_capabilities()


# 2. Add initialization handling
async def handle_initialize(server, request):
    """Handle initialization handshake"""
    if request.method == "initialize":
        return {
            "protocolVersion": "2025-03-26",
            "capabilities": await list_capabilities(server),
            "serverInfo": {
                "name": "Enhanced Dash Documentation Server",
                "version": "1.0.0",
            },
        }


# 3. Enhanced tool definitions with annotations
@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="search_dash_docs",
            description="Search local Dash documentation with fuzzy matching and content extraction",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for documentation",
                    },
                    "docset": {
                        "type": "string",
                        "description": "Optional specific docset to search in",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 20,
                        "description": "Maximum number of results",
                    },
                    "include_content": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether to extract and include documentation content",
                    },
                    "use_fuzzy": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to use fuzzy search matching",
                    },
                },
                "required": ["query"],
            },
            # ADD COMPLIANCE ANNOTATIONS:
            annotations={
                "safe": True,
                "title": "Search Documentation",
                "description": "Read-only search of local documentation files",
            },
        ),
        Tool(
            name="analyze_project_context",
            description="Analyze a project directory to understand its technology stack and dependencies",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to the project directory to analyze",
                    }
                },
                "required": ["project_path"],
            },
            # FILE SYSTEM ACCESS - MARK AS POTENTIALLY UNSAFE
            annotations={
                "safe": False,  # File system access
                "title": "Analyze Project",
                "description": "Reads project files to detect technology stack",
            },
        ),
        Tool(
            name="get_latest_api_reference",
            description="Get the most current API reference for a specific method or class",
            inputSchema={
                "type": "object",
                "properties": {
                    "api_name": {
                        "type": "string",
                        "description": "Name of the API, method, or class",
                    },
                    "technology": {
                        "type": "string",
                        "description": "Technology/library name",
                    },
                    "include_examples": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to include usage examples",
                    },
                },
                "required": ["api_name", "technology"],
            },
            annotations={
                "safe": True,
                "title": "API Reference Lookup",
                "description": "Retrieves API documentation without modification",
            },
        ),
        Tool(
            name="list_docsets",
            description="List all available Dash docsets with metadata",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_doc_content",
            description="Get full content for a specific documentation entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "docset": {"type": "string"},
                    "path": {"type": "string"},
                },
                "required": ["docset", "path"],
            },
        ),
        Tool(
            name="analyze_project_context",
            description="Analyze a project directory to understand its technology stack and dependencies",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to the project directory to analyze",
                    }
                },
                "required": ["project_path"],
            },
        ),
        Tool(
            name="get_project_relevant_docs",
            description="Get documentation most relevant to the current project context and query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What you're trying to implement or understand",
                    },
                    "project_path": {
                        "type": "string",
                        "description": "Path to the project directory",
                    },
                    "include_latest": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to include full content from latest documentation",
                    },
                },
                "required": ["query", "project_path"],
            },
        ),
        Tool(
            name="get_implementation_guidance",
            description="Get best practices and implementation patterns for a specific feature in your project",
            inputSchema={
                "type": "object",
                "properties": {
                    "feature_description": {
                        "type": "string",
                        "description": "Description of the feature you want to implement",
                    },
                    "project_path": {
                        "type": "string",
                        "description": "Path to the project directory",
                    },
                },
                "required": ["feature_description", "project_path"],
            },
        ),
        Tool(
            name="get_migration_docs",
            description="Get documentation for migrating or upgrading technology versions",
            inputSchema={
                "type": "object",
                "properties": {
                    "technology": {
                        "type": "string",
                        "description": "Technology being upgraded (e.g., 'react', 'django', 'nodejs')",
                    },
                    "from_version": {
                        "type": "string",
                        "description": "Current version",
                    },
                    "to_version": {"type": "string", "description": "Target version"},
                },
                "required": ["technology", "from_version", "to_version"],
            },
        ),
        Tool(
            name="get_latest_api_reference",
            description="Get the most current API reference for a specific method or class",
            inputSchema={
                "type": "object",
                "properties": {
                    "api_name": {
                        "type": "string",
                        "description": "Name of the API, method, or class",
                    },
                    "technology": {
                        "type": "string",
                        "description": "Technology/library name",
                    },
                    "include_examples": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to include usage examples",
                    },
                },
                "required": ["api_name", "technology"],
            },
        ),
    ]


# 4. Enhanced error handling per spec
@server.call_tool()
async def call_tool(name, arguments):
    try:
        # Validate tool exists
        available_tools = [tool.name for tool in await list_tools()]
        if name not in available_tools:
            # Return proper JSON-RPC error per spec
            raise ValueError(f"Unknown tool: {name}")

        # Input validation
        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be an object")

        # Tool execution with proper error handling
        if name == "search_dash_docs":
            # Validate required arguments
            if not arguments.get("query"):
                raise ValueError("Query parameter is required")

            raw_limit = arguments.get("limit", 20)
            try:
                # Cast provided limit to int to avoid slice errors
                limit = int(float(raw_limit))
            except (TypeError, ValueError):
                raise ValueError("limit must be an integer")

            limit = max(1, min(100, limit))  # Enforce limits within range

            results = await dash_server.search_docset(
                query=arguments["query"],
                docset_name=arguments.get("docset"),
                limit=limit,
                include_content=arguments.get("include_content", False),
                use_fuzzy=arguments.get("use_fuzzy", True),
            )

            # Return compliant response with both text and structured data
            return [
                TextContent(
                    type="text",
                    text=f"Found {len(results)} documentation entries:\n"
                    + json.dumps(results, indent=2),
                )
            ]

        elif name == "list_docsets":
            docsets = await dash_server.get_available_docsets()
            return [TextContent(type="text", text=json.dumps(docsets, indent=2))]

        elif name == "get_doc_content":
            # Get specific content
            docset_name = arguments["docset"]
            doc_path = arguments["path"]

            docsets = await dash_server.get_available_docsets()
            target_docset = next((d for d in docsets if d["name"] == docset_name), None)

            if not target_docset or not target_docset["has_content"]:
                return [
                    TextContent(type="text", text="Docset not found or has no content")
                ]

            docs_path = Path(target_docset["docs_path"])
            file_path = docs_path / doc_path

            if not file_path.exists():
                for ext in [".html", ".htm"]:
                    alt_path = file_path.with_suffix(ext)
                    if alt_path.exists():
                        file_path = alt_path
                        break

            if file_path.exists():
                file_ext = file_path.suffix.lower()
                if file_ext in dash_server.supported_formats:
                    content = await dash_server.supported_formats[file_ext](file_path)
                    return [TextContent(type="text", text=content)]

            return [
                TextContent(type="text", text="Content not found or unsupported format")
            ]

        elif name == "analyze_project_context":
            context = await project_server.analyze_project_context(
                arguments["project_path"]
            )
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "language": context.language,
                            "framework": context.framework,
                            "dependencies": context.dependencies,
                            "current_files": context.current_files[
                                :10
                            ],  # Show first 10 files
                        },
                        indent=2,
                    ),
                )
            ]

        elif name == "get_project_relevant_docs":
            context = await project_server.analyze_project_context(
                arguments["project_path"]
            )
            results = await project_server.get_relevant_documentation(
                query=arguments["query"],
                project_context=context,
                include_latest=arguments.get("include_latest", True),
            )
            return [TextContent(type="text", text=json.dumps(results, indent=2))]

        elif name == "get_implementation_guidance":
            context = await project_server.analyze_project_context(
                arguments["project_path"]
            )
            results = await project_server.get_best_practices_for_feature(
                feature_description=arguments["feature_description"],
                project_context=context,
            )
            return [TextContent(type="text", text=json.dumps(results, indent=2))]

        elif name == "get_migration_docs":
            results = await project_server.get_migration_guidance(
                from_version=arguments["from_version"],
                to_version=arguments["to_version"],
                technology=arguments["technology"],
            )
            return [TextContent(type="text", text=json.dumps(results, indent=2))]

        elif name == "get_latest_api_reference":
            # Enhanced search for specific API with content extraction
            results = await dash_server.search_docset(
                query=f"{arguments['technology']} {arguments['api_name']}",
                limit=10,
                include_content=arguments.get("include_examples", True),
                use_fuzzy=True,
            )

            # Filter for API-like results (methods, functions, classes)
            api_results = [
                r
                for r in results
                if r.get("type", "").lower()
                in ["method", "function", "class", "interface", "property"]
            ]

            return [
                TextContent(
                    type="text", text=json.dumps(api_results or results, indent=2)
                )
            ]

    except ValueError as e:
        # Return proper error response per MCP spec
        return [TextContent(type="text", text=f"Error: {str(e)}", isError=True)]
    except Exception as e:
        # Log unexpected errors and return safe message
        logger.error("Unexpected error in tool %s: %s", name, e)
        return [
            TextContent(
                type="text",
                text="An unexpected error occurred. Please check server logs.",
                isError=True,
            )
        ]


# 5. Add security input validation
def validate_file_path(path: str) -> bool:
    """Validate file paths for security"""
    try:
        resolved_path = Path(path).resolve()
        # Ensure path is within allowed directories
        allowed_dirs = [
            Path.home() / "Projects",
            Path.cwd(),
            Path.home() / "Development",
        ]
        return any(
            str(resolved_path).startswith(str(allowed_dir))
            for allowed_dir in allowed_dirs
        )
    except Exception:
        return False


def sanitize_search_query(query: str) -> str:
    """Sanitize search queries"""
    if not query or len(query.strip()) == 0:
        raise ValueError("Query cannot be empty")
    if len(query) > 500:
        raise ValueError("Query too long (max 500 characters)")
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"|&;$`\\]', "", query)
    return sanitized.strip()


# 6. Add proper tool change notifications
async def notify_tools_changed():
    """Notify clients when tool list changes"""
    # This would be called when tools are dynamically added/removed
    await server.send_notification("notifications/tools/list_changed", {})


# 7. Add rate limiting (basic implementation)
from collections import defaultdict
import time


class RateLimiter:
    def __init__(self, max_calls=100, window_seconds=60):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.calls = defaultdict(list)

    def is_allowed(self, client_id="default"):
        now = time.time()
        # Clean old calls
        self.calls[client_id] = [
            call_time
            for call_time in self.calls[client_id]
            if now - call_time < self.window_seconds
        ]

        if len(self.calls[client_id]) >= self.max_calls:
            return False

        self.calls[client_id].append(now)
        return True


rate_limiter = RateLimiter()


# Apply rate limiting in tool calls
async def rate_limited_call_tool(name, arguments):
    if not rate_limiter.is_allowed():
        return [
            TextContent(
                type="text",
                text="Rate limit exceeded. Please wait before making more requests.",
                isError=True,
            )
        ]

    return await call_tool(name, arguments)


async def _cancel_task(task: asyncio.Task) -> None:
    """Cancel a task and wait for it to finish."""
    # Centralizes task cancellation to prevent duplicate cleanup logic.
    task.cancel()
    # The server task may have already raised KeyboardInterrupt which should
    # not propagate further during cleanup.
    with contextlib.suppress(asyncio.CancelledError, KeyboardInterrupt):
        await task


async def main() -> None:
    """Run the server with STDIO streams and handle cancellation."""
    # Log startup so users know the server is running
    logger.info("Enhanced Dash MCP server starting (logs: %s)", LOG_FILE)
    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        server_task = asyncio.create_task(
            # stdio_server provides untyped streams that satisfy the expected
            # asyncio.StreamReader/StreamWriter interface
            server.run(read_stream, write_stream, init_options)
        )
        try:
            await server_task
        except (asyncio.CancelledError, KeyboardInterrupt):
            await _cancel_task(server_task)
        except Exception as exc:  # pragma: no cover - sanity
            # Log unexpected errors to help diagnose failures
            logger.exception("Error running server: %s", exc)
            await _cancel_task(server_task)
            raise
        finally:
            # Indicate shutdown regardless of cancellation reason
            logger.info("Enhanced Dash MCP server stopped")
            return


if __name__ == "__main__":
    # Run the server using asyncio and stdio_server for stream wiring
    asyncio.run(main())
