"""
Gerenciador de cache para carregamento rápido de nuvens de pontos
Salva dados processados em formato binário NumPy para acesso instantâneo
"""

import numpy as np
import os
import hashlib
import json
from pathlib import Path


class CacheManager:
    """
    Gerencia cache de nuvens de pontos para carregamento rápido
    
    Funcionalidades:
    - Salva vertices e cores em formato binário .npy
    - Usa hash MD5 do arquivo original para detectar mudanças
    - Cache automático em diretório .cache/
    - Limpeza de cache antigo
    """
    
    def __init__(self, cache_dir=".cache"):
        """
        Inicializa gerenciador de cache
        
        Args:
            cache_dir: Diretório para armazenar cache (padrão: .cache/)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Metadados do cache
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self):
        """Carrega metadados do cache"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_metadata(self):
        """Salva metadados do cache"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _get_file_hash(self, filepath):
        """
        Calcula hash MD5 do arquivo para detectar mudanças
        
        Args:
            filepath: Caminho do arquivo
            
        Returns:
            String com hash MD5
        """
        hash_md5 = hashlib.md5()
        
        # Para arquivos muito grandes, lê apenas partes (primeiro 1MB + último 1MB + tamanho)
        file_size = os.path.getsize(filepath)
        
        with open(filepath, 'rb') as f:
            if file_size > 2 * 1024 * 1024:  # > 2MB
                # Lê primeiro 1MB
                hash_md5.update(f.read(1024 * 1024))
                # Pula para último 1MB
                f.seek(-1024 * 1024, 2)
                hash_md5.update(f.read(1024 * 1024))
                # Adiciona tamanho do arquivo ao hash
                hash_md5.update(str(file_size).encode())
            else:
                # Arquivos pequenos: lê tudo
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    
    def _get_cache_path(self, filepath):
        """
        Gera caminho do cache para um arquivo
        
        Args:
            filepath: Caminho do arquivo original
            
        Returns:
            Tupla (cache_path, cache_key)
        """
        # Usa nome do arquivo + hash como chave única
        file_hash = self._get_file_hash(filepath)
        basename = Path(filepath).stem
        
        cache_key = f"{basename}_{file_hash}"
        cache_path = self.cache_dir / f"{cache_key}.npz"
        
        return cache_path, cache_key
    
    def has_cache(self, filepath):
        """
        Verifica se existe cache válido para o arquivo
        
        Args:
            filepath: Caminho do arquivo original
            
        Returns:
            True se cache existe e é válido
        """
        if not os.path.exists(filepath):
            return False
        
        cache_path, cache_key = self._get_cache_path(filepath)
        
        # Verifica se arquivo de cache existe
        if not cache_path.exists():
            return False
        
        # Verifica se metadados existem
        if cache_key not in self.metadata:
            return False
        
        # Verifica se arquivo original não foi modificado
        current_mtime = os.path.getmtime(filepath)
        cached_mtime = self.metadata[cache_key].get('mtime', 0)
        
        # Cache válido se mtime não mudou
        return abs(current_mtime - cached_mtime) < 1.0  # Tolerância de 1 segundo
    
    def load_from_cache(self, filepath):
        """
        Carrega dados do cache
        
        Args:
            filepath: Caminho do arquivo original
            
        Returns:
            Tupla (vertices, colors) ou None se cache inválido
        """
        if not self.has_cache(filepath):
            return None
        
        cache_path, cache_key = self._get_cache_path(filepath)
        
        try:
            print(f"⚡ Carregando do cache: {Path(filepath).name}")
            
            # Carrega arquivo .npz com múltiplos arrays
            data = np.load(cache_path)
            vertices = data['vertices']
            colors = data['colors']
            
            # Atualiza estatísticas de uso
            if cache_key in self.metadata:
                self.metadata[cache_key]['last_access'] = os.path.getmtime(filepath)
                self.metadata[cache_key]['access_count'] = self.metadata[cache_key].get('access_count', 0) + 1
                self._save_metadata()
            
            return vertices, colors
        except Exception as e:
            print(f"⚠️  Erro ao carregar cache: {e}")
            return None
    
    def save_to_cache(self, filepath, vertices, colors):
        """
        Salva dados no cache em um único arquivo comprimido
        
        Args:
            filepath: Caminho do arquivo original
            vertices: Array NumPy (N, 3) com coordenadas
            colors: Array NumPy (N, 3) com cores RGB
        """
        cache_path, cache_key = self._get_cache_path(filepath)
        
        try:
            # Salva ambos arrays em um único arquivo .npz comprimido
            np.savez_compressed(cache_path, vertices=vertices, colors=colors)
            
            # Atualiza metadados
            self.metadata[cache_key] = {
                'original_file': str(filepath),
                'mtime': os.path.getmtime(filepath),
                'file_size': os.path.getsize(filepath),
                'num_points': len(vertices),
                'created': os.path.getmtime(filepath),
                'last_access': os.path.getmtime(filepath),
                'access_count': 1
            }
            self._save_metadata()
            
            # Mostra tamanho do cache criado
            cache_size_mb = cache_path.stat().st_size / (1024 * 1024)
            print(f"💾 Cache salvo: {cache_key} ({cache_size_mb:.1f} MB)")
        except Exception as e:
            print(f"⚠️  Erro ao salvar cache: {e}")
    
    def clear_cache(self, older_than_days=None):
        """
        Limpa cache antigo
        
        Args:
            older_than_days: Remove cache não acessado há X dias (None = limpa tudo)
        """
        import time
        
        if older_than_days is None:
            # Remove tudo
            for file in self.cache_dir.glob("*.npz"):
                file.unlink()
            self.metadata.clear()
            self._save_metadata()
            print("🗑️  Cache totalmente limpo")
        else:
            # Remove por idade
            cutoff_time = time.time() - (older_than_days * 24 * 60 * 60)
            removed = 0
            
            for cache_key, meta in list(self.metadata.items()):
                if meta.get('last_access', 0) < cutoff_time:
                    # Remove arquivo
                    cache_file = self.cache_dir / f"{cache_key}.npz"
                    
                    if cache_file.exists():
                        cache_file.unlink()
                    
                    del self.metadata[cache_key]
                    removed += 1
            
            self._save_metadata()
            print(f"🗑️  Removidos {removed} caches antigos")
    
    def get_cache_stats(self):
        """
        Retorna estatísticas do cache
        
        Returns:
            Dicionário com estatísticas
        """
        total_files = len(self.metadata)
        total_size = 0
        total_points = 0
        
        for cache_key in self.metadata:
            cache_file = self.cache_dir / f"{cache_key}.npz"
            
            if cache_file.exists():
                total_size += cache_file.stat().st_size
            
            total_points += self.metadata[cache_key].get('num_points', 0)
        
        return {
            'total_files': total_files,
            'total_size_mb': total_size / (1024 * 1024),
            'total_points': total_points,
            'cache_dir': str(self.cache_dir)
        }
    
    def print_stats(self):
        """Imprime estatísticas do cache"""
        stats = self.get_cache_stats()
        print("\n📊 Estatísticas do Cache:")
        print(f"   Arquivos em cache: {stats['total_files']}")
        print(f"   Tamanho total: {stats['total_size_mb']:.2f} MB")
        print(f"   Pontos totais: {stats['total_points']:,}")
        print(f"   Diretório: {stats['cache_dir']}\n")
