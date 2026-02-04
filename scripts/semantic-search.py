#!/usr/bin/env python3
"""
Semantic Search for Memory Files
=================================

Uses OpenAI embeddings for semantic search over memory/*.md files.
Embeddings are cached locally — source markdown files are never modified.

Usage:
    python3 scripts/semantic-search.py "what did we discuss about Tencent"
    python3 scripts/semantic-search.py --rebuild          # Force rebuild embeddings
    python3 scripts/semantic-search.py --status           # Check health
    python3 scripts/semantic-search.py --update           # Update changed files only

Safeguards:
    - Source files never modified (read-only)
    - Results always show file + line number
    - Confidence scores filter low-quality matches
    - Falls back to grep if API fails
    - One command rebuild if anything breaks
"""

import os
import sys
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# Lazy imports for faster --help
def get_imports():
    global np, openai
    try:
        import numpy as np
        import openai
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Run: pip install numpy openai")
        return False

# Paths
WORKSPACE = Path.home() / '.openclaw/workspace'
MEMORY_DIR = WORKSPACE / 'memory'
MEMORY_MD = WORKSPACE / 'MEMORY.md'
EMBEDDINGS_FILE = WORKSPACE / 'memory/.embeddings-cache.json'
OPENAI_KEY_FILE = Path.home() / '.openclaw/config.yaml'

# Config
EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_SIZE = 500  # tokens approx (chars / 4)
MIN_SIMILARITY = 0.3  # Don't show results below this
TOP_K = 5  # Max results to return


def get_openai_key():
    """Extract OpenAI API key from openclaw config."""
    import yaml
    try:
        with open(OPENAI_KEY_FILE) as f:
            config = yaml.safe_load(f)
        
        # Try different config structures
        providers = config.get('providers', {})
        if 'openai' in providers:
            return providers['openai'].get('apiKey')
        
        # Fallback to env
        return os.environ.get('OPENAI_API_KEY')
    except Exception as e:
        print(f"Warning: Could not read config: {e}")
        return os.environ.get('OPENAI_API_KEY')


def get_file_hash(filepath):
    """Get MD5 hash of file contents."""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def chunk_text(text, filepath, chunk_size=CHUNK_SIZE):
    """Split text into chunks with metadata."""
    lines = text.split('\n')
    chunks = []
    current_chunk = []
    current_size = 0
    start_line = 1
    
    for i, line in enumerate(lines, 1):
        line_size = len(line) // 4  # Rough token estimate
        
        if current_size + line_size > chunk_size and current_chunk:
            chunks.append({
                'text': '\n'.join(current_chunk),
                'file': str(filepath),
                'start_line': start_line,
                'end_line': i - 1
            })
            current_chunk = [line]
            current_size = line_size
            start_line = i
        else:
            current_chunk.append(line)
            current_size += line_size
    
    # Don't forget the last chunk
    if current_chunk:
        chunks.append({
            'text': '\n'.join(current_chunk),
            'file': str(filepath),
            'start_line': start_line,
            'end_line': len(lines)
        })
    
    return chunks


def get_embedding(text, client):
    """Get embedding for text from OpenAI."""
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text[:8000]  # Truncate if too long
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding error: {e}")
        return None


def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def load_cache():
    """Load embeddings cache."""
    if EMBEDDINGS_FILE.exists():
        try:
            with open(EMBEDDINGS_FILE) as f:
                return json.load(f)
        except:
            return {'files': {}, 'chunks': [], 'embeddings': []}
    return {'files': {}, 'chunks': [], 'embeddings': []}


def save_cache(cache):
    """Save embeddings cache."""
    EMBEDDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EMBEDDINGS_FILE, 'w') as f:
        json.dump(cache, f)


def get_memory_files():
    """Get all memory files to index."""
    files = []
    
    # Main MEMORY.md
    if MEMORY_MD.exists():
        files.append(MEMORY_MD)
    
    # All .md files in memory/
    if MEMORY_DIR.exists():
        for f in MEMORY_DIR.rglob('*.md'):
            # Skip cache and very large files
            if '.embeddings' not in f.name and f.stat().st_size < 100000:
                files.append(f)
    
    return files


def rebuild_embeddings(force=False):
    """Rebuild embeddings for all memory files."""
    if not get_imports():
        return False
    
    api_key = get_openai_key()
    if not api_key:
        print("❌ No OpenAI API key found")
        return False
    
    client = openai.OpenAI(api_key=api_key)
    cache = load_cache() if not force else {'files': {}, 'chunks': [], 'embeddings': []}
    
    files = get_memory_files()
    print(f"📁 Found {len(files)} memory files")
    
    new_chunks = []
    new_embeddings = []
    files_processed = {}
    
    for filepath in files:
        file_hash = get_file_hash(filepath)
        rel_path = str(filepath.relative_to(WORKSPACE))
        
        # Check if file changed
        if not force and rel_path in cache.get('files', {}) and cache['files'][rel_path] == file_hash:
            # Keep existing embeddings for this file
            for i, chunk in enumerate(cache.get('chunks', [])):
                if chunk.get('file', '').endswith(rel_path) or rel_path in chunk.get('file', ''):
                    new_chunks.append(chunk)
                    if i < len(cache.get('embeddings', [])):
                        new_embeddings.append(cache['embeddings'][i])
            files_processed[rel_path] = file_hash
            continue
        
        # Process changed/new file
        print(f"  → Embedding: {rel_path}")
        try:
            text = filepath.read_text()
            chunks = chunk_text(text, rel_path)
            
            for chunk in chunks:
                embedding = get_embedding(chunk['text'], client)
                if embedding:
                    new_chunks.append(chunk)
                    new_embeddings.append(embedding)
            
            files_processed[rel_path] = file_hash
        except Exception as e:
            print(f"    ⚠️ Error: {e}")
    
    # Save updated cache
    cache = {
        'files': files_processed,
        'chunks': new_chunks,
        'embeddings': new_embeddings,
        'model': EMBEDDING_MODEL,
        'updated': datetime.now(timezone.utc).isoformat()
    }
    save_cache(cache)
    
    print(f"✅ Indexed {len(new_chunks)} chunks from {len(files_processed)} files")
    return True


def search(query, top_k=TOP_K):
    """Search memory files semantically."""
    if not get_imports():
        return fallback_grep(query)
    
    cache = load_cache()
    
    if not cache.get('embeddings'):
        print("⚠️ No embeddings found. Building index...")
        if not rebuild_embeddings():
            return fallback_grep(query)
        cache = load_cache()
    
    api_key = get_openai_key()
    if not api_key:
        print("⚠️ No API key, falling back to grep")
        return fallback_grep(query)
    
    try:
        client = openai.OpenAI(api_key=api_key)
        query_embedding = get_embedding(query, client)
        
        if not query_embedding:
            return fallback_grep(query)
        
        # Calculate similarities
        similarities = []
        for i, emb in enumerate(cache['embeddings']):
            sim = cosine_similarity(query_embedding, emb)
            if sim >= MIN_SIMILARITY:
                similarities.append((sim, i))
        
        # Sort by similarity
        similarities.sort(reverse=True)
        
        # Format results
        results = []
        for sim, idx in similarities[:top_k]:
            chunk = cache['chunks'][idx]
            results.append({
                'score': round(sim, 3),
                'file': chunk['file'],
                'lines': f"{chunk['start_line']}-{chunk['end_line']}",
                'preview': chunk['text'][:200] + '...' if len(chunk['text']) > 200 else chunk['text']
            })
        
        return results
    
    except Exception as e:
        print(f"⚠️ Search error: {e}, falling back to grep")
        return fallback_grep(query)


def fallback_grep(query):
    """Fallback to grep if semantic search fails."""
    print(f"🔍 Grep fallback for: {query}")
    results = []
    
    try:
        # Simple grep through memory files
        cmd = f'grep -rn -i "{query}" {MEMORY_DIR} {MEMORY_MD} 2>/dev/null | head -10'
        output = subprocess.check_output(cmd, shell=True, text=True)
        
        for line in output.strip().split('\n'):
            if line:
                parts = line.split(':', 2)
                if len(parts) >= 3:
                    results.append({
                        'score': 0.5,  # Unknown confidence
                        'file': parts[0],
                        'lines': parts[1],
                        'preview': parts[2][:200],
                        'fallback': True
                    })
    except:
        pass
    
    return results


def status():
    """Check health of semantic search system."""
    print("🔍 Semantic Search Status\n")
    
    cache = load_cache()
    
    # Cache status
    if EMBEDDINGS_FILE.exists():
        size = EMBEDDINGS_FILE.stat().st_size / 1024
        print(f"📦 Cache: {size:.1f} KB")
        print(f"   Model: {cache.get('model', 'unknown')}")
        print(f"   Updated: {cache.get('updated', 'unknown')}")
        print(f"   Chunks: {len(cache.get('chunks', []))}")
        print(f"   Files: {len(cache.get('files', {}))}")
    else:
        print("📦 Cache: Not found (run --rebuild)")
    
    # File coverage
    print(f"\n📁 Memory files:")
    files = get_memory_files()
    cached_files = set(cache.get('files', {}).keys())
    
    stale = 0
    for f in files:
        rel = str(f.relative_to(WORKSPACE))
        current_hash = get_file_hash(f)
        cached_hash = cache.get('files', {}).get(rel)
        
        if cached_hash is None:
            print(f"   ❌ {rel} — not indexed")
            stale += 1
        elif cached_hash != current_hash:
            print(f"   ⚠️ {rel} — stale")
            stale += 1
    
    if stale == 0:
        print(f"   ✅ All {len(files)} files up to date")
    else:
        print(f"\n   Run --update to refresh {stale} files")
    
    # API check
    print(f"\n🔑 API:")
    api_key = get_openai_key()
    if api_key:
        print(f"   ✅ OpenAI key found")
    else:
        print(f"   ❌ No OpenAI key")
    
    return stale == 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    arg = sys.argv[1]
    
    if arg == '--rebuild':
        rebuild_embeddings(force=True)
    
    elif arg == '--update':
        rebuild_embeddings(force=False)
    
    elif arg == '--status':
        status()
    
    else:
        # Search query
        query = ' '.join(sys.argv[1:])
        results = search(query)
        
        if not results:
            print(f"No results for: {query}")
            return
        
        print(f"🔍 Results for: {query}\n")
        for r in results:
            confidence = "🟢" if r['score'] > 0.5 else "🟡" if r['score'] > 0.35 else "🔴"
            fallback = " (grep)" if r.get('fallback') else ""
            print(f"{confidence} [{r['score']}] {r['file']}:{r['lines']}{fallback}")
            print(f"   {r['preview']}")
            print()


if __name__ == '__main__':
    main()
