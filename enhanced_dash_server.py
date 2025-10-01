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
__version__ = "1.3.1"  # Project version for SemVer and CHANGELOG automation

import asyncio
import contextlib
import logging
from logging.handlers import RotatingFileHandler
import hashlib
import json
import os
import re
import sqlite3
import sys
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


def is_interactive_mode() -> bool:
    """Enhanced detection of interactive vs non-interactive mode with detailed logging.
    
    Detection Sequence (in order of priority):
    1. CI Environment Detection - Check for continuous integration indicators
    2. Automation Environment Detection - Check for automated system indicators  
    3. Terminal Environment Detection - Validate terminal capabilities
    4. Shell Environment Detection - Check for interactive shell features
    5. TTY Stream Detection - Verify input/output stream capabilities
    6. Process Environment Detection - Check process hierarchy and daemon status
    7. SSH Connection Detection - Validate remote connection capabilities
    8. Session Environment Detection - Check for multiplexer sessions
    
    Logs the specific trigger that causes non-interactive mode for debugging.
    Each detection method logs both successful detection and the reasoning.
    
    Returns:
        bool: True if running in interactive mode, False if in CI/automation
    """
    logger.debug("🔍 Starting interactive mode detection sequence...")
    
    # === DETECTION PHASE 1: CI Environment Variables ===
    # These are the most reliable indicators of automated environments
    logger.debug("📋 Phase 1: Checking CI environment variables")
    ci_env_vars = [
        'CI',           # Generic CI indicator
        'CONTINUOUS_INTEGRATION',  # Alternative generic CI
        'JENKINS_URL',  # Jenkins
        'GITHUB_ACTIONS',  # GitHub Actions
        'GITLAB_CI',    # GitLab CI
        'TRAVIS',       # Travis CI
        'CIRCLECI',     # Circle CI
        'BUILDKITE',    # Buildkite
        'DRONE',        # Drone CI
        'BITBUCKET_BUILD_NUMBER',  # Bitbucket Pipelines
        'AZURE_HTTP_USER_AGENT',   # Azure DevOps
        'CODEBUILD_BUILD_ID',      # AWS CodeBuild
        'TEAMCITY_VERSION',        # TeamCity
        'BAMBOO_BUILD_NUMBER',     # Bamboo
        'TF_BUILD',     # Team Foundation Server
        'APPVEYOR',     # AppVeyor
        'WERCKER',      # Wercker
        'CONCOURSE',    # Concourse CI
        'SEMAPHORE',    # Semaphore
        'HUDSON_URL',   # Hudson
        'BUILD_ID',     # Generic build ID
        'BUILD_NUMBER', # Generic build number
    ]
    
    # === DETECTION PHASE 2: Automation Environment Variables ===
    # These indicate various forms of automated or batch processing
    logger.debug("🤖 Phase 2: Checking automation environment variables")
    automation_env_vars = [
        'AUTOMATION',   # Generic automation flag
        'AUTOMATED',    # Alternative automation flag
        'NON_INTERACTIVE',  # Explicit non-interactive mode
        'BATCH_MODE',   # Batch processing mode
        'HEADLESS',     # Headless environment
        'CRON',         # Cron job
        'SYSTEMD_EXEC_PID',  # systemd service
        'KUBERNETES_SERVICE_HOST',  # Kubernetes pod
        'DOCKER_CONTAINER',  # Docker container indicator
        'CONTAINER',    # Generic container indicator
        'AWS_EXECUTION_ENV',  # AWS Lambda/container
        'LAMBDA_RUNTIME_DIR', # AWS Lambda
        'GOOGLE_CLOUD_PROJECT',  # Google Cloud environment
        'AZURE_FUNCTIONS_ENVIRONMENT',  # Azure Functions
        'HEROKU_APP_ID',  # Heroku dyno
        'RAILWAY_ENVIRONMENT',  # Railway deployment
        'VERCEL',       # Vercel deployment
        'NETLIFY',      # Netlify build
        'CF_PAGES',     # Cloudflare Pages
    ]
    
    # Check for CI environment variables with detailed logging
    for env_var in ci_env_vars:
        env_value = os.getenv(env_var)
        if env_value:
            logger.info(f"❌ Non-interactive mode detected: CI environment variable '{env_var}' is set to '{env_value}'")
            logger.debug(f"   └─ Detection reason: CI systems set this variable to indicate automated builds")
            return False
    logger.debug("✅ Phase 1 passed: No CI environment variables detected")
    
    # Check for automation environment variables with detailed logging
    for env_var in automation_env_vars:
        env_value = os.getenv(env_var)
        if env_value:
            logger.info(f"❌ Non-interactive mode detected: Automation environment variable '{env_var}' is set to '{env_value}'")
            logger.debug(f"   └─ Detection reason: Indicates automated or batch processing environment")
            return False
    logger.debug("✅ Phase 2 passed: No automation environment variables detected")
    
    # === DETECTION PHASE 3: Terminal Environment Variables ===
    # Check terminal type and capabilities
    logger.debug("🖥️  Phase 3: Checking terminal environment")
    term = os.getenv('TERM', '').lower()
    if term in ['dumb', 'unknown', '']:
        logger.info(f"❌ Non-interactive mode detected: TERM environment variable is '{term}'")
        logger.debug(f"   └─ Detection reason: Terminal type indicates no interactive capabilities")
        return False
    logger.debug(f"✅ Phase 3a passed: TERM='{term}' indicates interactive terminal")
    
    # === DETECTION PHASE 4: Shell Environment Variables ===
    # Check shell type and interactive capabilities
    logger.debug("🐚 Phase 4: Checking shell environment")
    shell = os.getenv('SHELL', '').lower()
    if '/nologin' in shell or '/false' in shell:
        logger.info(f"❌ Non-interactive mode detected: Non-interactive shell '{shell}'")
        logger.debug(f"   └─ Detection reason: Shell configured to prevent interactive login")
        return False
    logger.debug(f"✅ Phase 4 passed: Shell '{shell}' supports interactive mode")
    
    # === DETECTION PHASE 5: TTY Stream Detection ===
    # Verify that standard streams are connected to a terminal
    logger.debug("📡 Phase 5: Checking TTY stream capabilities")
    
    # Check STDIN TTY status
    try:
        if not sys.stdin.isatty():
            logger.info("❌ Non-interactive mode detected: STDIN is not a TTY (piped/redirected input)")
            logger.debug("   └─ Detection reason: Input stream is redirected from file or pipe")
            return False
        logger.debug("✅ Phase 5a passed: STDIN is connected to a TTY")
    except (AttributeError, OSError) as e:
        logger.info(f"❌ Non-interactive mode detected: STDIN check failed ({e})")
        logger.debug(f"   └─ Detection reason: System error accessing STDIN properties")
        return False
    
    # Check STDOUT TTY status
    try:
        if not sys.stdout.isatty():
            logger.info("❌ Non-interactive mode detected: STDOUT is not a TTY (piped/redirected output)")
            logger.debug("   └─ Detection reason: Output stream is redirected to file or pipe")
            return False
        logger.debug("✅ Phase 5b passed: STDOUT is connected to a TTY")
    except (AttributeError, OSError) as e:
        logger.info(f"❌ Non-interactive mode detected: STDOUT check failed ({e})")
        logger.debug(f"   └─ Detection reason: System error accessing STDOUT properties")
        return False
    
    # Check STDERR TTY status
    try:
        if not sys.stderr.isatty():
            logger.info("❌ Non-interactive mode detected: STDERR is not a TTY (piped/redirected error output)")
            logger.debug("   └─ Detection reason: Error stream is redirected to file or pipe")
            return False
        logger.debug("✅ Phase 5c passed: STDERR is connected to a TTY")
    except (AttributeError, OSError) as e:
        logger.info(f"❌ Non-interactive mode detected: STDERR check failed ({e})")
        logger.debug(f"   └─ Detection reason: System error accessing STDERR properties")
        return False
    
    # === DETECTION PHASE 6: Process Environment Detection ===
    # Check process hierarchy and daemon indicators
    logger.debug("⚙️  Phase 6: Checking process environment")
    try:
        # Check for nohup execution
        if os.getenv('NOHUP'):
            logger.info("❌ Non-interactive mode detected: Running under nohup")
            logger.debug("   └─ Detection reason: Process started with nohup (no hangup signal handling)")
            return False
        logger.debug("✅ Phase 6a passed: Not running under nohup")
        
        # Check for daemon process characteristics
        if os.getpgrp() == os.getpid() and not os.isatty(0):
            logger.info("❌ Non-interactive mode detected: Running as daemon (no controlling terminal)")
            logger.debug("   └─ Detection reason: Process is session leader without controlling terminal")
            return False
        logger.debug("✅ Phase 6b passed: Not running as daemon process")
        
        # Check for orphaned process (parent is init)
        if os.getppid() == 1:
            logger.info("❌ Non-interactive mode detected: Parent process is init (orphaned process)")
            logger.debug("   └─ Detection reason: Process has been orphaned and adopted by init")
            return False
        logger.debug(f"✅ Phase 6c passed: Parent process ID is {os.getppid()} (not orphaned)")
        
    except (AttributeError, OSError) as e:
        logger.debug(f"⚠️  Phase 6 warning: Process environment check failed ({e})")
        logger.debug("   └─ Continuing with remaining checks...")
    
    # === DETECTION PHASE 7: SSH Connection Detection ===
    # Check for SSH connections and TTY allocation
    logger.debug("🔗 Phase 7: Checking SSH connection status")
    ssh_connection = os.getenv('SSH_CONNECTION')
    ssh_tty = os.getenv('SSH_TTY')
    
    if ssh_connection:
        if not ssh_tty:
            logger.info("❌ Non-interactive mode detected: SSH connection without TTY allocation")
            logger.debug(f"   └─ Detection reason: SSH_CONNECTION='{ssh_connection}' but SSH_TTY not set")
            return False
        else:
            logger.debug(f"✅ Phase 7 passed: SSH connection with TTY allocation (SSH_TTY='{ssh_tty}')")
    else:
        logger.debug("✅ Phase 7 passed: Not an SSH connection")
    
    # === DETECTION PHASE 8: Session Environment Detection ===
    # Check for terminal multiplexer sessions
    logger.debug("📋 Phase 8: Checking session environment")
    screen_session = os.getenv('STY')
    tmux_session = os.getenv('TMUX')
    
    if screen_session:
        logger.debug(f"✅ Phase 8a: Running in GNU Screen session (STY='{screen_session}')")
        logger.debug("   └─ Screen sessions maintain interactive capabilities")
    elif tmux_session:
        logger.debug(f"✅ Phase 8b: Running in tmux session (TMUX='{tmux_session}')")
        logger.debug("   └─ Tmux sessions maintain interactive capabilities")
    else:
        logger.debug("✅ Phase 8c: Not running in a terminal multiplexer")
    
    # === DETECTION COMPLETE ===
    # All checks passed - running in interactive mode
    logger.info("🎉 Interactive mode confirmed: All detection phases passed")
    logger.debug("   └─ Full interactive capabilities available for user interaction")
    return True


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
        # Default to Dash root directory to discover all docsets, not just DocSets subdirectory
        self.docsets_path = (
            Path(env_path)
            if env_path
            else Path.home() / "Library/Application Support/Dash"
        )

        # Resolve symlinks and handle paths that point to specific subdirectories
        adjusted_path = self.docsets_path.resolve()
        if adjusted_path.name == "DocSets" and (adjusted_path.parent / "DocSets").exists():
            # User supplied DocSets folder; use parent Dash directory for broader discovery
            adjusted_path = adjusted_path.parent
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
        """Scan for available Dash docsets with comprehensive detection and logging.
        
        Docset Detection Sequence:
        1. Cache Check - Verify if docsets are already cached
        2. Directory Existence - Ensure docsets path exists
        3. Recursive Discovery - Find all .docset directories
        4. Database Validation - Verify SQLite database exists
        5. Content Validation - Check for documentation files
        6. Metadata Extraction - Parse Info.plist for display names
        7. Category Classification - Determine docset source/type
        
        Each step logs detection progress and any issues encountered.
        """
        logger.debug("🔍 Starting docset discovery process...")
        
        # === DETECTION PHASE 1: Cache Check ===
        logger.debug("📦 Phase 1: Checking docset cache")
        cache_key = "available_docsets"
        cached = await self.cache.get(cache_key)
        if cached:
            logger.info(f"✅ Found {len(cached)} cached docsets - skipping discovery")
            logger.debug("   └─ Cache hit: Using previously discovered docsets")
            return cached
        logger.debug("❌ Phase 1: No cached docsets found - proceeding with fresh discovery")

        # === DETECTION PHASE 2: Directory Existence Check ===
        logger.debug(f"📁 Phase 2: Validating docsets directory: {self.docsets_path}")
        if not self.docsets_path.exists():
            logger.warning(f"❌ Docsets directory does not exist: {self.docsets_path}")
            logger.debug("   └─ Ensure Dash is installed or set DASH_DOCSETS_PATH environment variable")
            await self.cache.set(cache_key, [])
            return []
        logger.debug(f"✅ Phase 2 passed: Docsets directory exists")
        logger.debug(f"   └─ Scanning path: {self.docsets_path.resolve()}")

        # === DETECTION PHASE 3: Recursive Docset Discovery ===
        logger.debug("🔍 Phase 3: Scanning for .docset directories")
        docsets = []
        docset_pattern = "**/*.docset"
        docset_dirs = list(self.docsets_path.glob(docset_pattern))
        
        logger.info(f"📊 Found {len(docset_dirs)} potential docset directories")
        if not docset_dirs:
            logger.warning("❌ No .docset directories found in the search path")
            logger.debug(f"   └─ Search pattern: {docset_pattern}")
            logger.debug(f"   └─ Search root: {self.docsets_path}")
            await self.cache.set(cache_key, [])
            return []
        
        logger.debug(f"🎯 Phase 3 results: Found docset candidates")
        for i, docset_dir in enumerate(docset_dirs[:5]):  # Log first 5 for brevity
            logger.debug(f"   └─ [{i+1}] {docset_dir.name} in {docset_dir.parent.name}/")
        if len(docset_dirs) > 5:
            logger.debug(f"   └─ ... and {len(docset_dirs) - 5} more docsets")

        # === DETECTION PHASE 4: Database and Content Validation ===
        logger.debug("🗄️  Phase 4: Validating docset databases and content")
        valid_docsets = 0
        invalid_docsets = 0
        
        for docset_dir in docset_dirs:
            logger.debug(f"🔍 Examining docset: {docset_dir.name}")
            
            # Check for required database file
            db_path = docset_dir / "Contents/Resources/docSet.dsidx"
            docs_path = docset_dir / "Contents/Resources/Documents"
            
            if not db_path.exists():
                logger.debug(f"   ❌ Missing database: {db_path}")
                logger.debug(f"      └─ Skipping invalid docset: {docset_dir.name}")
                invalid_docsets += 1
                continue
                
            logger.debug(f"   ✅ Database found: {db_path}")
            
            # Check for documentation content
            has_content = docs_path.exists()
            if has_content:
                content_count = len(list(docs_path.rglob("*.*"))[:10])  # Sample first 10 files
                logger.debug(f"   ✅ Content directory found with {content_count}+ files")
            else:
                logger.debug(f"   ⚠️  No content directory found: {docs_path}")
            
            # === DETECTION PHASE 5: Metadata Extraction ===
            logger.debug(f"📋 Phase 5: Extracting metadata for {docset_dir.name}")
            
            # Extract basic docset information
            docset_name = docset_dir.name.replace(".docset", "")
            category = docset_dir.parent.name
            
            docset_info = {
                "name": docset_name,
                "db_path": str(db_path),
                "docs_path": str(docs_path),
                "has_content": has_content,
                "category": category,
            }
            
            logger.debug(f"   📊 Basic info extracted: name='{docset_name}', category='{category}'")
            
            # === DETECTION PHASE 6: Info.plist Processing ===
            info_plist = docset_dir / "Contents/Info.plist"
            if info_plist.exists():
                logger.debug(f"   📄 Processing Info.plist: {info_plist}")
                try:
                    with open(info_plist, "r") as f:
                        content = f.read()
                        if "CFBundleName" in content:
                            match = re.search(
                                r"<key>CFBundleName</key>\s*<string>([^<]+)</string>",
                                content,
                            )
                            if match:
                                display_name = match.group(1)
                                docset_info["display_name"] = display_name
                                logger.debug(f"   ✅ Display name extracted: '{display_name}'")
                            else:
                                logger.debug(f"   ⚠️  CFBundleName found but could not extract value")
                        else:
                            logger.debug(f"   ⚠️  No CFBundleName found in Info.plist")
                except Exception as e:
                    logger.debug(f"   ❌ Error parsing Info.plist: {e}")
            else:
                logger.debug(f"   ⚠️  No Info.plist found: {info_plist}")
            
            # === DETECTION PHASE 7: Category Classification ===
            logger.debug(f"🏷️  Phase 7: Classifying docset category for {docset_name}")
            
            # Enhanced category detection based on directory structure
            if "User Contributed" in str(docset_dir):
                docset_info["source"] = "user_contributed"
                logger.debug(f"   📁 Classified as: User Contributed docset")
            elif "DocSets" in str(docset_dir):
                docset_info["source"] = "official"
                logger.debug(f"   📁 Classified as: Official Dash docset")
            else:
                docset_info["source"] = "unknown"
                logger.debug(f"   📁 Classified as: Unknown source docset")
            
            docsets.append(docset_info)
            valid_docsets += 1
            logger.debug(f"   ✅ Docset validation complete: {docset_name}")
        
        # === DETECTION SUMMARY ===
        logger.info(f"📊 Docset discovery summary:")
        logger.info(f"   ├─ Total candidates found: {len(docset_dirs)}")
        logger.info(f"   ├─ Valid docsets: {valid_docsets}")
        logger.info(f"   ├─ Invalid docsets: {invalid_docsets}")
        logger.info(f"   └─ Success rate: {(valid_docsets/len(docset_dirs)*100):.1f}%")
        
        if valid_docsets > 0:
            # Log sample of discovered docsets
            sample_names = [d['name'] for d in docsets[:5]]
            logger.info(f"📚 Sample docsets: {', '.join(sample_names)}")
            if len(docsets) > 5:
                logger.info(f"   └─ ...and {len(docsets) - 5} more")
        
        # Cache the results
        await self.cache.set(cache_key, docsets)
        logger.debug(f"💾 Cached {len(docsets)} docsets for future use")
        
        return docsets

    async def search_docset(
        self,
        query: str,
        docset_name: Optional[str] = None,
        limit: int = 20,
        include_content: bool = False,
        use_fuzzy: bool = True,
    ) -> List[Dict[str, Any]]:
        """Enhanced search within Dash docsets with comprehensive logging.
        
        Search Sequence:
        1. Cache Check - Look for cached results first
        2. Docset Resolution - Identify target docsets for search
        3. Database Schema Detection - Identify SQLite table structure
        4. Query Execution - Perform database searches
        5. Entry Processing - Convert results to DocEntry objects
        6. Search Enhancement - Apply fuzzy search if enabled
        7. Content Extraction - Add documentation content if requested
        8. Result Formatting - Convert to final dictionary format
        
        Each phase logs detailed information about the search process.
        """
        logger.debug(f"🔍 Starting search for query: '{query}'")
        logger.debug(f"   ├─ Target docset: {docset_name or 'all docsets'}")
        logger.debug(f"   ├─ Result limit: {limit}")
        logger.debug(f"   ├─ Include content: {include_content}")
        logger.debug(f"   └─ Use fuzzy search: {use_fuzzy}")

        # === SEARCH PHASE 1: Cache Check ===
        logger.debug("📦 Phase 1: Checking search result cache")
        cache_key = self.cache._get_cache_key(
            f"{query}_{docset_name}_{limit}_{include_content}"
        )
        cached = await self.cache.get(cache_key)
        if cached and not include_content:  # Don't cache content results for freshness
            logger.info(f"⚡ Cache hit: Found {len(cached)} cached results for query '{query}'")
            logger.debug("   └─ Skipping database search - using cached results")
            return cached
        
        if cached:
            logger.debug("📦 Cache hit found but content extraction requested - proceeding with fresh search")
        else:
            logger.debug("📦 No cached results found - proceeding with database search")

        # === SEARCH PHASE 2: Docset Resolution ===
        logger.debug("🎯 Phase 2: Resolving target docsets for search")
        docsets = await self.get_available_docsets()
        
        if docset_name:
            original_count = len(docsets)
            docsets = [d for d in docsets if d["name"].lower() == docset_name.lower()]
            logger.info(f"🔎 Filtering to specific docset: '{docset_name}'")
            logger.debug(f"   └─ Filtered from {original_count} to {len(docsets)} docsets")
            
            if not docsets:
                logger.warning(f"❌ Specified docset '{docset_name}' not found in available docsets")
                return []
        else:
            logger.debug(f"🔎 Searching across all {len(docsets)} available docsets")
        
        all_entries = []
        successful_searches = 0
        failed_searches = 0

        # === SEARCH PHASE 3: Database Schema Detection and Query Execution ===
        logger.debug("🗄️ Phase 3: Beginning database searches across docsets")
        
        for i, docset in enumerate(docsets, 1):
            logger.debug(f"🔍 [{i}/{len(docsets)}] Searching docset: {docset['name']}")
            
            try:
                # === SEARCH PHASE 3a: Database Connection ===
                logger.debug(f"   📡 Connecting to database: {docset['db_path']}")
                conn = sqlite3.connect(docset["db_path"])
                cursor = conn.cursor()

                # === SEARCH PHASE 3b: Schema Detection ===
                logger.debug(f"   🔍 Detecting database schema for {docset['name']}")
                try:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = [row[0] for row in cursor.fetchall()]
                    logger.debug(f"   📋 Available tables: {', '.join(tables)}")

                    docset_entries = 0
                    
                    if "searchIndex" in tables:
                        # === TRADITIONAL SEARCHINDEX SCHEMA ===
                        logger.debug(f"   ✅ Using traditional searchIndex schema for {docset['name']}")
                        cursor.execute("PRAGMA table_info(searchIndex)")
                        columns = [row[1] for row in cursor.fetchall()]
                        logger.debug(f"   📊 SearchIndex columns: {', '.join(columns)}")

                        # Adapt query based on available columns
                        if "anchor" in columns:
                            sql = "SELECT name, type, path, anchor FROM searchIndex WHERE name LIKE ? LIMIT ?"
                            logger.debug(f"   🔧 Using full schema query (with anchor support)")
                        else:
                            sql = "SELECT name, type, path FROM searchIndex WHERE name LIKE ? LIMIT ?"
                            logger.debug(f"   🔧 Using basic schema query (no anchor support)")

                        # Execute search with expanded limit for fuzzy filtering
                        search_limit = limit * 2
                        logger.debug(f"   🎯 Executing search with pattern '%{query}%' (limit: {search_limit})")
                        
                        cursor.execute(sql, (f"%{query}%", search_limit))
                        rows = cursor.fetchall()
                        logger.debug(f"   📊 Found {len(rows)} raw results in {docset['name']}")

                        for row in rows:
                            entry = DocEntry(
                                name=row[0],
                                type=row[1],
                                path=row[2],
                                docset=docset["name"],
                                anchor=row[3] if len(row) > 3 else None,
                            )
                            all_entries.append(entry)
                            docset_entries += 1

                    elif "ZTOKEN" in tables and "ZTOKENTYPE" in tables:
                        # === CORE DATA SCHEMA (NEWER DASH VERSIONS) ===
                        logger.debug(f"   ✅ Using Core Data schema for {docset['name']}")
                        try:
                            # Query the Core Data schema with JOIN
                            sql = """
                            SELECT t.ZTOKENNAME as name, tt.ZTYPENAME as type, t.ZPATH as path
                            FROM ZTOKEN t
                            LEFT JOIN ZTOKENTYPE tt ON t.ZTOKENTYPE = tt.Z_PK
                            WHERE t.ZTOKENNAME LIKE ?
                            LIMIT ?
                            """
                            
                            search_limit = limit * 2
                            logger.debug(f"   🔧 Using Core Data JOIN query (limit: {search_limit})")
                            cursor.execute(sql, (f"%{query}%", search_limit))
                            rows = cursor.fetchall()
                            logger.debug(f"   📊 Core Data JOIN returned {len(rows)} results")

                            for row in rows:
                                if row[0]:  # Ensure name is not None
                                    entry = DocEntry(
                                        name=row[0],
                                        type=row[1] or "Unknown",
                                        path=row[2] or "",
                                        docset=docset["name"],
                                    )
                                    all_entries.append(entry)
                                    docset_entries += 1
                                    
                        except sqlite3.Error as e:
                            logger.warning(f"   ⚠️ Core Data JOIN query failed for {docset['name']}: {e}")
                            logger.debug(f"   🔄 Attempting fallback Core Data query...")
                            
                            # Fallback to simpler query
                            try:
                                cursor.execute("SELECT ZTOKENNAME, ZPATH FROM ZTOKEN WHERE ZTOKENNAME LIKE ? LIMIT ?", (f"%{query}%", limit))
                                rows = cursor.fetchall()
                                logger.debug(f"   📊 Core Data fallback returned {len(rows)} results")
                                
                                for row in rows:
                                    if row[0]:
                                        entry = DocEntry(
                                            name=row[0],
                                            type="Unknown",
                                            path=row[1] or "",
                                            docset=docset["name"],
                                        )
                                        all_entries.append(entry)
                                        docset_entries += 1
                            except sqlite3.Error as fallback_error:
                                logger.warning(f"   ❌ Core Data fallback also failed for {docset['name']}: {fallback_error}")

                    else:
                        logger.warning(f"   ❌ Unknown database schema for {docset['name']}")
                        logger.debug(f"   📋 Available tables: {tables}")
                        logger.debug(f"   💡 Expected 'searchIndex' or 'ZTOKEN'+'ZTOKENTYPE' tables")
                    
                    # Log results for this docset
                    if docset_entries > 0:
                        logger.debug(f"   ✅ {docset['name']} contributed {docset_entries} entries")
                        successful_searches += 1
                    else:
                        logger.debug(f"   📭 {docset['name']} returned no results")
                        successful_searches += 1  # Still successful, just no matches

                except sqlite3.Error as e:
                    logger.error(f"   ❌ Database error in {docset['name']}: {e}")
                    failed_searches += 1

                # Always close the connection
                conn.close()
                logger.debug(f"   🔌 Closed database connection for {docset['name']}")

            except Exception as e:
                logger.error(f"   ❌ Unexpected error searching {docset['name']}: {e}")
                failed_searches += 1
        
        # === SEARCH PHASE 3 SUMMARY ===
        logger.info(f"📊 Database search summary:")
        logger.info(f"   ├─ Docsets searched: {len(docsets)}")
        logger.info(f"   ├─ Successful searches: {successful_searches}")
        logger.info(f"   ├─ Failed searches: {failed_searches}")
        logger.info(f"   └─ Raw entries found: {len(all_entries)}")

        # === SEARCH PHASE 4: Search Enhancement ===
        logger.debug("🔧 Phase 4: Enhancing search results")
        
        if not all_entries:
            logger.info("📭 No entries found matching the search criteria")
            logger.debug(f"   └─ Query: '{query}' in {len(docsets)} docsets")
            # Cache empty results to avoid repeated searches
            await self.cache.set(cache_key, [])
            return []
            
        original_count = len(all_entries)
        
        # Apply fuzzy search or ranking enhancement
        if use_fuzzy and all_entries:
            logger.debug(f"🔍 Applying fuzzy search enhancement to {len(all_entries)} entries")
            all_entries = self.search_engine.fuzzy_search(query, all_entries)
            fuzzy_count = len(all_entries)
            logger.debug(f"   └─ Fuzzy search refined results: {original_count} → {fuzzy_count} entries")
        else:
            logger.debug(f"📊 Applying standard ranking to {len(all_entries)} entries")
            all_entries = self.search_engine.rank_results(all_entries, query)
            logger.debug(f"   └─ Standard ranking applied to {len(all_entries)} entries")

        # === SEARCH PHASE 5: Result Limiting ===
        logger.debug(f"✂️  Phase 5: Limiting results to top {limit} entries")
        if len(all_entries) > limit:
            logger.debug(f"   📊 Truncating {len(all_entries)} results to {limit} (as requested)")
            all_entries = all_entries[:limit]
        else:
            logger.debug(f"   📊 Returning all {len(all_entries)} results (within limit)")

        # === SEARCH PHASE 6: Content Extraction ===
        if include_content:
            logger.debug("📖 Phase 6: Extracting documentation content")
            logger.debug(f"   🔍 Processing {len(all_entries)} entries for content extraction")
            
            content_start_time = time.time()
            await self._add_content_to_entries(all_entries)
            content_duration = time.time() - content_start_time
            
            # Count entries with successfully extracted content
            entries_with_content = sum(1 for entry in all_entries if entry.content)
            logger.debug(f"   ✅ Content extraction completed in {content_duration:.2f}s")
            logger.debug(f"   📊 Successfully extracted content for {entries_with_content}/{len(all_entries)} entries")
            
            if entries_with_content < len(all_entries):
                failed_extractions = len(all_entries) - entries_with_content
                logger.debug(f"   ⚠️  {failed_extractions} entries had no extractable content")
        else:
            logger.debug("📖 Phase 6: Skipping content extraction (not requested)")

        # === SEARCH PHASE 7: Result Formatting ===
        logger.debug("🎨 Phase 7: Converting entries to dictionary format")
        results = []
        for i, entry in enumerate(all_entries):
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
                logger.debug(f"   📄 [{i+1}] {entry.name} (content: {len(entry.content)} chars)")
            else:
                logger.debug(f"   📝 [{i+1}] {entry.name} (no content)")
            results.append(result)
        
        logger.debug(f"✅ Phase 7 completed: {len(results)} results formatted")

        # === SEARCH PHASE 8: Caching ===
        if not include_content:
            logger.debug("💾 Phase 8: Caching search results")
            await self.cache.set(cache_key, results)
            logger.debug(f"   ✅ Cached {len(results)} results for future queries")
        else:
            logger.debug("💾 Phase 8: Skipping cache (content results not cached)")

        # === SEARCH COMPLETE ===
        logger.info(f"🎉 Search completed successfully for query: '{query}'")
        logger.info(f"   ├─ Docsets searched: {len(docsets)}")
        logger.info(f"   ├─ Total raw matches: {original_count}")
        logger.info(f"   ├─ Final results: {len(results)}")
        logger.info(f"   ├─ Content included: {'Yes' if include_content else 'No'}")
        logger.info(f"   └─ Cache updated: {'No' if include_content else 'Yes'}")
        
        return results

    async def _add_content_to_entries(self, entries: List[DocEntry]) -> None:
        """Add content to documentation entries with comprehensive extraction logging.
        
        Content Extraction Sequence:
        1. Docset Path Resolution - Map docset names to filesystem paths
        2. Entry Path Construction - Build full file paths for each entry
        3. File Extension Detection - Find actual files with alternative extensions
        4. Format Handler Selection - Choose appropriate content extractor
        5. Content Processing - Extract and clean content from files
        6. Error Handling - Log extraction failures and continue processing
        
        Each step logs detailed information about the extraction process.
        """
        logger.debug(f"📖 Starting content extraction for {len(entries)} entries")
        
        # === EXTRACTION PHASE 1: Docset Path Resolution ===
        logger.debug("🗂️  Phase 1: Resolving docset paths")
        docsets = await self.get_available_docsets()
        docset_paths = {d["name"]: d["docs_path"] for d in docsets if d["has_content"]}
        
        logger.debug(f"📁 Found {len(docset_paths)} docsets with content:")
        for docset_name, docs_path in list(docset_paths.items())[:5]:  # Log first 5
            logger.debug(f"   └─ {docset_name}: {docs_path}")
        if len(docset_paths) > 5:
            logger.debug(f"   └─ ...and {len(docset_paths) - 5} more docsets")
        
        # Track extraction statistics
        extraction_stats = {
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "no_docset_path": 0,
            "file_not_found": 0,
            "unsupported_format": 0,
            "extraction_errors": 0
        }
        
        # === EXTRACTION PHASE 2: Process Each Entry ===
        logger.debug("📄 Phase 2: Processing individual entries")
        
        for i, entry in enumerate(entries, 1):
            logger.debug(f"🔍 [{i}/{len(entries)}] Processing: {entry.name} ({entry.docset})")
            extraction_stats["processed"] += 1
            
            # Check if docset has content path available
            if entry.docset not in docset_paths:
                logger.debug(f"   ❌ Docset '{entry.docset}' not found in available content paths")
                extraction_stats["no_docset_path"] += 1
                continue
            
            # === EXTRACTION PHASE 3: File Path Construction ===
            docs_path = Path(docset_paths[entry.docset])
            original_file_path = docs_path / entry.path
            logger.debug(f"   📂 Base path: {original_file_path}")
            
            # === EXTRACTION PHASE 4: File Extension Detection ===
            file_path = original_file_path
            
            # Try to find the actual file with alternative extensions
            if not file_path.exists():
                logger.debug(f"   🔍 Original path not found, trying alternative extensions...")
                
                extensions_tried = []
                for ext in [".html", ".htm", ".md", ".txt"]:
                    alt_path = file_path.with_suffix(ext)
                    extensions_tried.append(ext)
                    
                    if alt_path.exists():
                        file_path = alt_path
                        logger.debug(f"   ✅ Found alternative: {file_path.name} (extension: {ext})")
                        break
                else:
                    logger.debug(f"   ❌ File not found with any extension: {extensions_tried}")
                    extraction_stats["file_not_found"] += 1
                    continue
            else:
                logger.debug(f"   ✅ Original path exists: {file_path.name}")
            
            # === EXTRACTION PHASE 5: Format Handler Selection ===
            file_ext = file_path.suffix.lower()
            logger.debug(f"   🔧 File extension detected: '{file_ext}'")
            
            if file_ext not in self.supported_formats:
                logger.debug(f"   ❌ Unsupported format: {file_ext}")
                logger.debug(f"      └─ Supported formats: {list(self.supported_formats.keys())}")
                extraction_stats["unsupported_format"] += 1
                continue
            
            handler = self.supported_formats[file_ext]
            logger.debug(f"   🛠️  Using handler: {handler.__name__}")
            
            # === EXTRACTION PHASE 6: Content Processing ===
            try:
                logger.debug(f"   📖 Extracting content from: {file_path}")
                content_start = time.time()
                content = await handler(file_path)
                content_duration = time.time() - content_start
                
                if content:
                    entry.content = content
                    content_length = len(content)
                    word_count = len(content.split())
                    
                    logger.debug(f"   ✅ Content extracted successfully in {content_duration:.3f}s")
                    logger.debug(f"      └─ Length: {content_length} chars, ~{word_count} words")
                    extraction_stats["successful"] += 1
                else:
                    logger.debug(f"   ⚠️  Handler returned empty content")
                    extraction_stats["failed"] += 1
                    
            except Exception as e:
                logger.debug(f"   ❌ Content extraction failed: {e}")
                logger.debug(f"      └─ Handler: {handler.__name__}, File: {file_path}")
                extraction_stats["extraction_errors"] += 1
        
        # === EXTRACTION SUMMARY ===
        logger.info("📊 Content extraction summary:")
        logger.info(f"   ├─ Total entries processed: {extraction_stats['processed']}")
        logger.info(f"   ├─ Successful extractions: {extraction_stats['successful']}")
        logger.info(f"   ├─ Failed extractions: {extraction_stats['failed']}")
        logger.info(f"   ├─ No docset path: {extraction_stats['no_docset_path']}")
        logger.info(f"   ├─ File not found: {extraction_stats['file_not_found']}")
        logger.info(f"   ├─ Unsupported format: {extraction_stats['unsupported_format']}")
        logger.info(f"   └─ Extraction errors: {extraction_stats['extraction_errors']}")
        
        # Calculate success rate
        if extraction_stats['processed'] > 0:
            success_rate = (extraction_stats['successful'] / extraction_stats['processed']) * 100
            logger.info(f"📈 Content extraction success rate: {success_rate:.1f}%")
            
            if success_rate < 50:
                logger.warning("⚠️  Low content extraction success rate - check file paths and formats")
            elif success_rate > 80:
                logger.debug("🎉 High content extraction success rate - system working well")


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


async def amain() -> None:
    """Run the server with STDIO streams and handle cancellation."""
    # Enhanced startup with interactive mode detection and detailed logging
    logger.info("Enhanced Dash MCP server starting (logs: %s)", LOG_FILE)
    
    # Detect and log interactive mode status with detailed reasoning
    interactive = is_interactive_mode()
    if interactive:
        logger.info("🖥️  Running in INTERACTIVE mode - full functionality enabled")
    else:
        logger.info("🤖 Running in NON-INTERACTIVE mode (CI/automation detected)")
    
    # Log environment summary for debugging
    env_summary = {
        "TERM": os.getenv('TERM', 'not set'),
        "CI": os.getenv('CI', 'not set'),
        "GITHUB_ACTIONS": os.getenv('GITHUB_ACTIONS', 'not set'),
        "GITLAB_CI": os.getenv('GITLAB_CI', 'not set'),
        "JENKINS_URL": os.getenv('JENKINS_URL', 'not set'),
        "TRAVIS": os.getenv('TRAVIS', 'not set'),
        "SHELL": os.getenv('SHELL', 'not set'),
        "SSH_CONNECTION": os.getenv('SSH_CONNECTION', 'not set'),
        "SSH_TTY": os.getenv('SSH_TTY', 'not set'),
        "TMUX": os.getenv('TMUX', 'not set'),
        "STY": os.getenv('STY', 'not set'),
    }
    logger.debug("Environment summary: %s", env_summary)
    
    # Log STDIN/STDOUT/STDERR TTY status
    try:
        tty_status = {
            "stdin_isatty": sys.stdin.isatty(),
            "stdout_isatty": sys.stdout.isatty(),
            "stderr_isatty": sys.stderr.isatty(),
        }
        logger.debug("TTY status: %s", tty_status)
    except (AttributeError, OSError) as e:
        logger.debug("TTY status check failed: %s", e)
    
    # Log process information for automation detection
    try:
        process_info = {
            "pid": os.getpid(),
            "ppid": os.getppid(),
            "pgrp": os.getpgrp(),
            "session_id": os.getsid(0) if hasattr(os, 'getsid') else 'not available',
        }
        logger.debug("Process info: %s", process_info)
    except (AttributeError, OSError) as e:
        logger.debug("Process info check failed: %s", e)
    
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
            if interactive:
                logger.info("🛑 Received interrupt signal in interactive mode")
            else:
                logger.info("🛑 Received interrupt signal in non-interactive mode")
            await _cancel_task(server_task)
        except Exception as exc:  # pragma: no cover - sanity
            # Log unexpected errors to help diagnose failures
            logger.exception("Error running server: %s", exc)
            await _cancel_task(server_task)
            raise
        finally:
            # Indicate shutdown regardless of cancellation reason
            if interactive:
                logger.info("Enhanced Dash MCP server stopped (was running in interactive mode)")
            else:
                logger.info("Enhanced Dash MCP server stopped (was running in non-interactive mode)")
            return

def main() -> None:
    """Entry point for the console script."""
    asyncio.run(amain())

if __name__ == "__main__":
    import sys
    
    # Check for test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test mode: validate setup without starting server
        print("🧪 Enhanced Dash MCP Server - Test Mode")
        print(f"📍 Docsets path: {DashMCPServer().docsets_path}")
        print(f"📊 Log file: {LOG_FILE}")
        
        # Quick validation
        try:
            server_instance = DashMCPServer()
            print(f"✅ Server initialized successfully")
            
            # Test docset discovery
            import asyncio
            async def test_docsets():
                docsets = await server_instance.get_available_docsets()
                print(f"📚 Found {len(docsets)} docsets")
                if docsets:
                    print("   Sample docsets:", [d['name'] for d in docsets[:3]])
                return len(docsets) > 0
            
            has_docsets = asyncio.run(test_docsets())
            if has_docsets:
                print("🎉 Server test completed successfully - ready for MCP client connection")
                sys.exit(0)
            else:
                print("⚠️ No docsets found - check DASH_DOCSETS_PATH or Dash installation")
                print("ℹ️  Server can still be used for testing - this is expected on non-macOS systems")
                # Don't exit with error code since server initialization was successful
                sys.exit(0)
                
        except Exception as e:
            print(f"❌ Server test failed: {e}")
            sys.exit(1)
    
    # Normal mode: Run the server using asyncio and stdio_server for stream wiring
    main()
