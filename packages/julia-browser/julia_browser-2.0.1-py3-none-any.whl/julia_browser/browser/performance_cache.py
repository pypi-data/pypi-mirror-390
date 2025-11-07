"""
Performance & Caching System - Asynchronous execution, content caching, and optimization
Handles large websites with lazy loading and intelligent caching strategies
"""

import asyncio
import aiohttp
import hashlib
import json
import time
import gzip
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, urlparse
import sqlite3
import threading

@dataclass
class CacheEntry:
    """Represents a cached page or resource"""
    url: str
    content: str
    content_type: str
    headers: Dict[str, str]
    timestamp: float
    size: int
    compression: str = 'none'
    etag: Optional[str] = None
    last_modified: Optional[str] = None

class PerformanceCache:
    """High-performance caching system with async support"""
    
    def __init__(self, cache_dir: str = ".browser_cache", max_size_mb: int = 500):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache_db_path = self.cache_dir / "cache.db"
        self.memory_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'total_size': 0,
            'entries': 0
        }
        self._lock = threading.RLock()
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for cache metadata"""
        with sqlite3.connect(self.cache_db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache_entries (
                    url TEXT PRIMARY KEY,
                    content_hash TEXT,
                    content_type TEXT,
                    headers TEXT,
                    timestamp REAL,
                    size INTEGER,
                    compression TEXT,
                    etag TEXT,
                    last_modified TEXT,
                    access_count INTEGER DEFAULT 0,
                    last_access REAL
                )
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp ON cache_entries(timestamp)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_last_access ON cache_entries(last_access)
            ''')
            conn.commit()
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key from URL"""
        return hashlib.sha256(url.encode()).hexdigest()
    
    def _compress_content(self, content: str) -> Tuple[bytes, str]:
        """Compress content for storage"""
        try:
            compressed = gzip.compress(content.encode('utf-8'))
            if len(compressed) < len(content.encode('utf-8')) * 0.8:  # Only if significant compression
                return compressed, 'gzip'
            else:
                return content.encode('utf-8'), 'none'
        except:
            return content.encode('utf-8'), 'none'
    
    def _decompress_content(self, data: bytes, compression: str) -> str:
        """Decompress cached content"""
        try:
            if compression == 'gzip':
                return gzip.decompress(data).decode('utf-8')
            else:
                return data.decode('utf-8')
        except:
            return str(data)
    
    async def get(self, url: str) -> Optional[CacheEntry]:
        """Get cached entry for URL"""
        with self._lock:
            cache_key = self._get_cache_key(url)
            
            # Check memory cache first
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                if self._is_valid(entry):
                    self.cache_stats['hits'] += 1
                    self._update_access_stats(url)
                    return entry
                else:
                    del self.memory_cache[cache_key]
            
            # Check disk cache
            try:
                with sqlite3.connect(self.cache_db_path) as conn:
                    cursor = conn.execute(
                        'SELECT * FROM cache_entries WHERE url = ?', (url,)
                    )
                    row = cursor.fetchone()
                    
                    if row:
                        url_db, content_hash, content_type, headers_json, timestamp, size, compression, etag, last_modified, access_count, last_access = row
                        
                        # Load content from file
                        content_file = self.cache_dir / f"{cache_key}.content"
                        if content_file.exists():
                            with open(content_file, 'rb') as f:
                                content_data = f.read()
                            
                            content = self._decompress_content(content_data, compression)
                            headers = json.loads(headers_json) if headers_json else {}
                            
                            entry = CacheEntry(
                                url=url,
                                content=content,
                                content_type=content_type,
                                headers=headers,
                                timestamp=timestamp,
                                size=size,
                                compression=compression,
                                etag=etag,
                                last_modified=last_modified
                            )
                            
                            if self._is_valid(entry):
                                # Add to memory cache
                                self.memory_cache[cache_key] = entry
                                self.cache_stats['hits'] += 1
                                self._update_access_stats(url)
                                return entry
                            else:
                                # Remove expired entry
                                self._remove_cache_entry(url)
            except Exception as e:
                logging.warning(f"Cache read error for {url}: {e}")
            
            self.cache_stats['misses'] += 1
            return None
    
    async def set(self, url: str, content: str, content_type: str = 'text/html', 
                  headers: Dict[str, str] = None, ttl: int = 3600) -> bool:
        """Cache content for URL"""
        if not content:
            return False
        
        headers = headers or {}
        cache_key = self._get_cache_key(url)
        
        try:
            with self._lock:
                # Compress content
                compressed_data, compression = self._compress_content(content)
                
                # Create cache entry
                entry = CacheEntry(
                    url=url,
                    content=content,
                    content_type=content_type,
                    headers=headers,
                    timestamp=time.time(),
                    size=len(compressed_data),
                    compression=compression,
                    etag=headers.get('etag'),
                    last_modified=headers.get('last-modified')
                )
                
                # Save to disk
                content_file = self.cache_dir / f"{cache_key}.content"
                with open(content_file, 'wb') as f:
                    f.write(compressed_data)
                
                # Save metadata to database
                with sqlite3.connect(self.cache_db_path) as conn:
                    conn.execute('''
                        INSERT OR REPLACE INTO cache_entries 
                        (url, content_hash, content_type, headers, timestamp, size, compression, etag, last_modified, last_access)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        url, cache_key, content_type, json.dumps(headers), 
                        entry.timestamp, entry.size, compression, 
                        entry.etag, entry.last_modified, time.time()
                    ))
                    conn.commit()
                
                # Add to memory cache
                self.memory_cache[cache_key] = entry
                
                # Update stats
                self.cache_stats['entries'] += 1
                self.cache_stats['total_size'] += entry.size
                
                # Clean up if necessary
                await self._cleanup_if_needed()
                
                return True
                
        except Exception as e:
            logging.error(f"Cache write error for {url}: {e}")
            return False
    
    def _is_valid(self, entry: CacheEntry, max_age: int = 3600) -> bool:
        """Check if cache entry is still valid"""
        age = time.time() - entry.timestamp
        return age < max_age
    
    def _update_access_stats(self, url: str):
        """Update access statistics for URL"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                conn.execute('''
                    UPDATE cache_entries 
                    SET access_count = access_count + 1, last_access = ?
                    WHERE url = ?
                ''', (time.time(), url))
                conn.commit()
        except Exception as e:
            logging.warning(f"Failed to update access stats: {e}")
    
    def _remove_cache_entry(self, url: str):
        """Remove cache entry completely"""
        cache_key = self._get_cache_key(url)
        
        try:
            # Remove from memory
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                self.cache_stats['total_size'] -= entry.size
                del self.memory_cache[cache_key]
            
            # Remove from disk
            content_file = self.cache_dir / f"{cache_key}.content"
            if content_file.exists():
                content_file.unlink()
            
            # Remove from database
            with sqlite3.connect(self.cache_db_path) as conn:
                conn.execute('DELETE FROM cache_entries WHERE url = ?', (url,))
                conn.commit()
            
            self.cache_stats['entries'] -= 1
            
        except Exception as e:
            logging.warning(f"Failed to remove cache entry {url}: {e}")
    
    async def _cleanup_if_needed(self):
        """Clean up cache if it exceeds size limits"""
        if self.cache_stats['total_size'] > self.max_size_bytes:
            await self._cleanup_cache()
    
    async def _cleanup_cache(self):
        """Clean up old cache entries using LRU strategy"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                # Get least recently used entries
                cursor = conn.execute('''
                    SELECT url, size FROM cache_entries 
                    ORDER BY last_access ASC 
                    LIMIT 100
                ''')
                
                entries_to_remove = cursor.fetchall()
                
                # Remove oldest entries until under size limit
                bytes_freed = 0
                for url, size in entries_to_remove:
                    if self.cache_stats['total_size'] - bytes_freed < self.max_size_bytes * 0.8:
                        break
                    
                    self._remove_cache_entry(url)
                    bytes_freed += size
                
                logging.info(f"Cache cleanup: freed {bytes_freed} bytes, removed {len(entries_to_remove)} entries")
                
        except Exception as e:
            logging.error(f"Cache cleanup failed: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = self.cache_stats['hits'] / (self.cache_stats['hits'] + self.cache_stats['misses']) if (self.cache_stats['hits'] + self.cache_stats['misses']) > 0 else 0
        
        return {
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'hit_rate': f"{hit_rate:.2%}",
            'entries': self.cache_stats['entries'],
            'total_size_mb': self.cache_stats['total_size'] / (1024 * 1024),
            'cache_dir': str(self.cache_dir),
            'memory_entries': len(self.memory_cache)
        }

class AsyncBrowserEngine:
    """Asynchronous browser engine with performance optimizations"""
    
    def __init__(self, max_concurrent: int = 10, enable_caching: bool = True):
        self.max_concurrent = max_concurrent
        self.cache = PerformanceCache() if enable_caching else None
        self.session = None
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.process_pool = ProcessPoolExecutor(max_workers=2)
        
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent,
            limit_per_host=5,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        timeout = aiohttp.ClientTimeout(
            total=30,
            connect=10,
            sock_read=10
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
        
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
    
    async def fetch_page(self, url: str, use_cache: bool = True) -> Tuple[bool, str, Optional[BeautifulSoup], Dict]:
        """Asynchronously fetch a web page with caching"""
        
        # Check cache first
        if use_cache and self.cache:
            cached = await self.cache.get(url)
            if cached:
                soup = await self._parse_html_async(cached.content)
                return True, cached.content, soup, {'from_cache': True, 'content_type': cached.content_type}
        
        # Fetch from network
        async with self.semaphore:
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        content_type = response.headers.get('content-type', 'text/html')
                        headers = dict(response.headers)
                        
                        # Cache the result
                        if use_cache and self.cache:
                            await self.cache.set(url, content, content_type, headers)
                        
                        # Parse HTML asynchronously
                        soup = await self._parse_html_async(content)
                        
                        return True, content, soup, {
                            'from_cache': False,
                            'content_type': content_type,
                            'status': response.status,
                            'headers': headers
                        }
                    else:
                        return False, f"HTTP {response.status}", None, {'status': response.status}
                        
            except Exception as e:
                return False, str(e), None, {'error': str(e)}
    
    async def fetch_multiple_pages(self, urls: List[str], use_cache: bool = True) -> List[Tuple[str, bool, str, Optional[BeautifulSoup], Dict]]:
        """Fetch multiple pages concurrently"""
        tasks = []
        for url in urls:
            task = asyncio.create_task(self._fetch_with_url(url, use_cache))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append((urls[i], False, str(result), None, {'error': str(result)}))
            else:
                url, success, content, soup, metadata = result
                processed_results.append((url, success, content, soup, metadata))
        
        return processed_results
    
    async def _fetch_with_url(self, url: str, use_cache: bool) -> Tuple[str, bool, str, Optional[BeautifulSoup], Dict]:
        """Wrapper to include URL in result"""
        success, content, soup, metadata = await self.fetch_page(url, use_cache)
        return url, success, content, soup, metadata
    
    async def _parse_html_async(self, content: str) -> Optional[BeautifulSoup]:
        """Parse HTML content asynchronously"""
        if not content:
            return None
        
        try:
            # Use thread pool for CPU-intensive parsing
            loop = asyncio.get_event_loop()
            soup = await loop.run_in_executor(
                self.thread_pool,
                lambda: BeautifulSoup(content, 'html.parser')
            )
            return soup
        except Exception as e:
            logging.error(f"HTML parsing error: {e}")
            return None
    
    async def extract_links_async(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract links from page asynchronously"""
        if not soup:
            return []
        
        try:
            loop = asyncio.get_event_loop()
            links = await loop.run_in_executor(
                self.thread_pool,
                self._extract_links_sync,
                soup, base_url
            )
            return links
        except Exception as e:
            logging.error(f"Link extraction error: {e}")
            return []
    
    def _extract_links_sync(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Synchronous link extraction for thread pool"""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href:
                absolute_url = urljoin(base_url, href)
                text = link.get_text(strip=True) or href
                links.append({
                    'url': absolute_url,
                    'text': text,
                    'type': 'link'
                })
        
        # Also extract other resource links
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src:
                absolute_url = urljoin(base_url, src)
                alt = img.get('alt', 'Image')
                links.append({
                    'url': absolute_url,
                    'text': alt,
                    'type': 'image'
                })
        
        return links

class LazyLoader:
    """Lazy loading system for large websites"""
    
    def __init__(self, async_engine: AsyncBrowserEngine):
        self.async_engine = async_engine
        self.loaded_sections = set()
        self.pending_sections = {}
        
    async def load_section_on_demand(self, section_id: str, url: str) -> Optional[str]:
        """Load page section only when requested"""
        if section_id in self.loaded_sections:
            return self.pending_sections.get(section_id)
        
        try:
            success, content, soup, metadata = await self.async_engine.fetch_page(url)
            if success and soup:
                # Extract specific section
                section = soup.find(id=section_id) or soup.find(class_=section_id)
                if section:
                    section_content = str(section)
                    self.pending_sections[section_id] = section_content
                    self.loaded_sections.add(section_id)
                    return section_content
        except Exception as e:
            logging.error(f"Lazy loading error for section {section_id}: {e}")
        
        return None
    
    async def preload_critical_sections(self, url: str, critical_selectors: List[str]):
        """Preload critical page sections"""
        try:
            success, content, soup, metadata = await self.async_engine.fetch_page(url)
            if success and soup:
                tasks = []
                for selector in critical_selectors:
                    task = asyncio.create_task(self._extract_section_async(soup, selector))
                    tasks.append(task)
                
                sections = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, section_content in enumerate(sections):
                    if not isinstance(section_content, Exception) and section_content:
                        selector = critical_selectors[i]
                        self.pending_sections[selector] = section_content
                        self.loaded_sections.add(selector)
                        
        except Exception as e:
            logging.error(f"Preloading error: {e}")
    
    async def _extract_section_async(self, soup: BeautifulSoup, selector: str) -> Optional[str]:
        """Extract section content asynchronously"""
        try:
            elements = soup.select(selector)
            if elements:
                return str(elements[0])
        except Exception as e:
            logging.error(f"Section extraction error for {selector}: {e}")
        
        return None

class PerformanceMonitor:
    """Monitor and report performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'page_load_times': [],
            'cache_performance': {},
            'memory_usage': [],
            'concurrent_requests': 0,
            'total_requests': 0,
            'failed_requests': 0
        }
        self.start_time = time.time()
    
    def record_page_load(self, url: str, load_time: float, from_cache: bool = False):
        """Record page load performance"""
        self.metrics['page_load_times'].append({
            'url': url,
            'time': load_time,
            'from_cache': from_cache,
            'timestamp': time.time()
        })
        self.metrics['total_requests'] += 1
    
    def record_request_start(self):
        """Record start of concurrent request"""
        self.metrics['concurrent_requests'] += 1
    
    def record_request_end(self, success: bool = True):
        """Record end of request"""
        self.metrics['concurrent_requests'] -= 1
        if not success:
            self.metrics['failed_requests'] += 1
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.metrics['page_load_times']:
            return {'status': 'No performance data available'}
        
        load_times = [entry['time'] for entry in self.metrics['page_load_times']]
        cached_requests = sum(1 for entry in self.metrics['page_load_times'] if entry['from_cache'])
        
        avg_load_time = sum(load_times) / len(load_times)
        min_load_time = min(load_times)
        max_load_time = max(load_times)
        
        cache_hit_rate = cached_requests / len(self.metrics['page_load_times']) if self.metrics['page_load_times'] else 0
        
        success_rate = (self.metrics['total_requests'] - self.metrics['failed_requests']) / self.metrics['total_requests'] if self.metrics['total_requests'] > 0 else 0
        
        uptime = time.time() - self.start_time
        
        return {
            'total_requests': self.metrics['total_requests'],
            'failed_requests': self.metrics['failed_requests'],
            'success_rate': f"{success_rate:.2%}",
            'avg_load_time': f"{avg_load_time:.3f}s",
            'min_load_time': f"{min_load_time:.3f}s",
            'max_load_time': f"{max_load_time:.3f}s",
            'cache_hit_rate': f"{cache_hit_rate:.2%}",
            'concurrent_requests': self.metrics['concurrent_requests'],
            'uptime': f"{uptime:.1f}s",
            'requests_per_second': self.metrics['total_requests'] / uptime if uptime > 0 else 0
        }