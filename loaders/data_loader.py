"""
Sistema genérico de carregamento de dados para visualização 3D
Suporta múltiplos formatos de arquivo (UPL, CSV, JSON, etc)
"""

import numpy as np
import os
from abc import ABC, abstractmethod


class DataLoader(ABC):
    """Classe base abstrata para carregadores de dados"""
    
    @abstractmethod
    def load(self, filepath):
        """
        Carrega dados do arquivo
        
        Args:
            filepath: Caminho do arquivo
            
        Returns:
            Tupla (vertices, colors) onde:
                vertices: np.array shape (N, 3) com coordenadas X, Y, Z
                colors: np.array shape (N, 3) com cores R, G, B (0-1)
        """
        pass
    
    @abstractmethod
    def supports(self, filepath):
        """
        Verifica se o loader suporta este tipo de arquivo
        
        Args:
            filepath: Caminho do arquivo
            
        Returns:
            True se suporta
        """
        pass


class UPLLoader(DataLoader):
    """
    Carregador para arquivos UPL (Tunnel Inspection)
    Formato específico com cabeçalhos EFVM e dados de seção transversal
    """
    
    def __init__(self, max_points=None):
        """
        Args:
            max_points: Limite de pontos para performance (None = sem limite)
        """
        self.max_points = max_points
    
    def supports(self, filepath):
        """Suporta arquivos .upl"""
        return filepath.lower().endswith('.upl')
    
    def load(self, filepath):
        """
        Carrega arquivo UPL e retorna pontos com cores classificadas
        
        Returns:
            Tupla (vertices, colors) com dados normalizados
        """
        print(f"📂 Lendo arquivo UPL: {filepath}...")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Arquivo '{filepath}' não encontrado!")
        
        # Lê arquivo com encoding apropriado
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                linhas = [linha.strip() for linha in f if linha.strip()]
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='latin-1') as f:
                linhas = [linha.strip() for linha in f if linha.strip()]
        
        # Extrai coordenadas
        xs, ys, zs = self._parse_upl_lines(linhas)
        
        if len(xs) == 0:
            raise ValueError("Nenhum ponto válido encontrado no arquivo UPL!")
        
        print(f"✅ {len(xs):,} pontos extraídos")
        
        # Filtragem e amostragem
        xs, ys, zs = self._filter_and_sample(xs, ys, zs)
        
        # Normalização de coordenadas
        xs, ys, zs = self._normalize_coordinates(xs, ys, zs)
        
        # Calcula cores por classificação
        colors = self._calculate_colors(xs, ys, zs)
        
        # Monta arrays de retorno
        vertices = np.column_stack((xs, ys, zs)).astype(np.float32)
        
        print(f"📊 Carregamento completo: {len(vertices):,} pontos")
        return vertices, colors
    
    def _parse_upl_lines(self, linhas):
        """Extrai coordenadas X, Y, Z das linhas do arquivo"""
        xs_global = []
        ys_global = []
        zs_global = []
        
        i = 0
        while i + 1 < len(linhas):
            linha_cabecalho = linhas[i]
            
            if linha_cabecalho.startswith("EFVM") and "RH-" in linha_cabecalho:
                partes = linha_cabecalho.split(";")
                
                # Extrai coordenada Z (KM + metros)
                if len(partes) >= 13:
                    try:
                        unidade = float(partes[11])
                        subunidade = float(partes[12])
                        z_val = unidade * 1000.0 + subunidade
                    except:
                        z_val = 0.0
                else:
                    z_val = 0.0
                
                # Lê linha de dados
                linha_dados = linhas[i + 1]
                dados_raw = [p.strip() for p in linha_dados.split(';') if p.strip() != '']
                
                # Processa pares X, Y
                for j in range(0, len(dados_raw) - 1, 2):
                    try:
                        x = float(dados_raw[j].replace(',', '.'))
                        y = float(dados_raw[j + 1].replace(',', '.'))
                        
                        if not (x == 0 and y == 0):
                            xs_global.append(x / 1000.0)  # mm para metros
                            ys_global.append(y / 1000.0)
                            zs_global.append(z_val)
                    except ValueError:
                        continue
                
                i += 2
                continue
            
            i += 1
        
        return np.array(xs_global), np.array(ys_global), np.array(zs_global)
    
    def _filter_and_sample(self, xs, ys, zs):
        """Filtra outliers e reduz pontos se necessário"""
        # Filtro: remove pontos muito distantes
        mask = (np.abs(xs) <= 10.0) & (ys <= 10.0)
        xs = xs[mask]
        ys = ys[mask]
        zs = zs[mask]
        
        # Amostragem se muito grande (somente se max_points definido)
        if self.max_points is not None and len(xs) > self.max_points:
            print(f"⚠️  Arquivo muito grande ({len(xs):,} pontos)")
            print(f"   Limitando para {self.max_points:,} pontos")
            
            step = len(xs) // self.max_points
            indices = np.arange(0, len(xs), step)[:self.max_points]
            xs = xs[indices]
            ys = ys[indices]
            zs = zs[indices]
        
        return xs, ys, zs
    
    def _normalize_coordinates(self, xs, ys, zs):
        """Normaliza coordenadas Z para visualização"""
        z_min = zs.min()
        zs_norm = zs - z_min
        
        print(f"📐 Coordenadas normalizadas:")
        print(f"   X: [{xs.min():.1f}, {xs.max():.1f}] m")
        print(f"   Y: [{ys.min():.1f}, {ys.max():.1f}] m")
        print(f"   Z: [{zs_norm.min():.1f}, {zs_norm.max():.1f}] m")
        
        return xs, ys, zs_norm
    
    def _calculate_colors(self, xs, ys, zs):
        """Calcula cores por classificação de túnel (Verde/Amarelo/Vermelho)"""
        print("🎨 Calculando cores por classificação...")
        
        n = len(xs)
        colors_r = np.zeros(n, dtype=np.float32)
        colors_g = np.ones(n, dtype=np.float32)   # Verde por padrão
        colors_b = np.zeros(n, dtype=np.float32)
        
        # Cálculo vetorizado (muito mais rápido que Numba para arrays grandes)
        x_abs = np.abs(xs)
        
        # Pré-calcula distâncias para semicírculo
        dist_semicirculo = np.sqrt(xs*xs + (ys - 5.8)*(ys - 5.8))
        
        # VERMELHO: Invasão
        # Parte retangular
        mask_vermelho_ret = (x_abs <= 2.2) & (ys >= 2.5) & (ys <= 5.8)
        # Parte semicírculo
        mask_vermelho_semi = (x_abs <= 2.2) & (ys > 5.8) & (ys <= 8.0) & (dist_semicirculo <= 2.2)
        mask_vermelho = mask_vermelho_ret | mask_vermelho_semi
        
        colors_r[mask_vermelho] = 1.0
        colors_g[mask_vermelho] = 0.0
        
        # AMARELO: Alerta
        # Parte retangular
        mask_amarelo_ret = (x_abs > 2.2) & (x_abs <= 2.7) & (ys >= 2.4) & (ys <= 5.8)
        # Parte semicírculo
        mask_amarelo_semi = ((x_abs > 2.2) & (x_abs <= 2.7) & (ys > 5.8) & (ys <= 8.0) & 
                            (dist_semicirculo > 2.2) & (dist_semicirculo <= 2.7))
        # Margem base
        mask_amarelo_base = (x_abs <= 2.2) & (ys >= 2.4) & (ys < 2.5)
        
        mask_amarelo = mask_amarelo_ret | mask_amarelo_semi | mask_amarelo_base
        
        colors_r[mask_amarelo] = 1.0
        colors_g[mask_amarelo] = 1.0
        
        # Estatísticas
        n_vermelho = np.sum(mask_vermelho)
        n_amarelo = np.sum(mask_amarelo)
        n_verde = n - n_vermelho - n_amarelo
        
        print(f"📊 Classificação:")
        print(f"   🟢 SEGURO: {n_verde:,} ({n_verde/n*100:.1f}%)")
        print(f"   🟡 ALERTA: {n_amarelo:,} ({n_amarelo/n*100:.1f}%)")
        print(f"   🔴 INVASÃO: {n_vermelho:,} ({n_vermelho/n*100:.1f}%)")
        
        return np.column_stack((colors_r, colors_g, colors_b)).astype(np.float32)


class PTSLoader(DataLoader):
    """
    Carregador para arquivos PTS
    Formato: X Y Z R G B (separado por espaços)
    """
    
    def supports(self, filepath):
        """Suporta arquivos .pts"""
        return filepath.lower().endswith('.pts')
    
    def load(self, filepath):
        """
        Carrega arquivo PTS com formato: X Y Z R G B
        
        Returns:
            Tupla (vertices, colors)
        """
        print(f"📂 Lendo arquivo PTS: {filepath}...")
        
        vertices = []
        colors = []
        
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:  # Ignora linhas vazias
                    continue
                
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        # Coordenadas X, Y, Z
                        x = float(parts[0])
                        y = float(parts[1])
                        z = float(parts[2])
                        vertices.append([x, y, z])
                        
                        # Cores R, G, B (se disponíveis)
                        if len(parts) >= 6:
                            r = float(parts[3]) / 255.0  # Normaliza 0-255 para 0-1
                            g = float(parts[4]) / 255.0
                            b = float(parts[5]) / 255.0
                            colors.append([r, g, b])
                        else:
                            # Cor padrão verde se não houver cor
                            colors.append([0.0, 1.0, 0.0])
                    except ValueError:
                        continue  # Ignora linhas com erros
        
        vertices = np.array(vertices, dtype=np.float32)
        colors = np.array(colors, dtype=np.float32)
        
        print(f"✅ {len(vertices):,} pontos carregados")
        return vertices, colors


class CSVLoader(DataLoader):
    """
    Carregador genérico para arquivos CSV
    Formato esperado: X, Y, Z, [R, G, B]
    """
    
    def supports(self, filepath):
        """Suporta arquivos .csv"""
        return filepath.lower().endswith('.csv')
    
    def load(self, filepath):
        """
        Carrega CSV com colunas X, Y, Z e opcionalmente R, G, B
        
        Returns:
            Tupla (vertices, colors)
        """
        print(f"📂 Lendo arquivo CSV: {filepath}...")
        
        data = np.loadtxt(filepath, delimiter=',', skiprows=1)
        
        # Primeiras 3 colunas são coordenadas
        vertices = data[:, :3].astype(np.float32)
        
        # Se tem 6 colunas, últimas 3 são cores
        if data.shape[1] >= 6:
            colors = data[:, 3:6].astype(np.float32)
            # Normaliza cores se estão em 0-255
            if colors.max() > 1.0:
                colors = colors / 255.0
        else:
            # Cor padrão verde
            colors = np.ones((len(vertices), 3), dtype=np.float32) * [0, 1, 0]
        
        print(f"✅ {len(vertices):,} pontos carregados")
        return vertices, colors


class DataLoaderFactory:
    """
    Factory para criar loaders apropriados baseado no tipo de arquivo
    """
    
    def __init__(self):
        """Inicializa factory com loaders disponíveis"""
        self.loaders = [
            UPLLoader(),
            PTSLoader(),
            CSVLoader(),
        ]
    
    def get_loader(self, filepath):
        """
        Retorna loader apropriado para o arquivo
        
        Args:
            filepath: Caminho do arquivo
            
        Returns:
            DataLoader apropriado
            
        Raises:
            ValueError se formato não suportado
        """
        for loader in self.loaders:
            if loader.supports(filepath):
                return loader
        
        raise ValueError(f"Formato de arquivo não suportado: {filepath}")
    
    def load(self, filepath):
        """
        Carrega arquivo automaticamente com loader apropriado
        
        Args:
            filepath: Caminho do arquivo
            
        Returns:
            Tupla (vertices, colors)
        """
        loader = self.get_loader(filepath)
        return loader.load(filepath)
