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
    
    def __init__(self, max_points=None, template=None):
        """
        Args:
            max_points: Limite de pontos para performance (None = sem limite)
            template: Gabarito para classificação (None = usa padrão ferrovia)
        """
        self.max_points = max_points
        self.template = template
    
    def supports(self, filepath):
        """Suporta arquivos .upl"""
        return filepath.lower().endswith('.upl')
    
    def load(self, filepath):
        """
        Carrega arquivo UPL e retorna pontos com cores classificadas
        
        Returns:
            Tupla (vertices, colors) com dados normalizados
        """
        print(f"[LENDO] Lendo arquivo UPL: {filepath}...")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Arquivo '{filepath}' não encontrado!")
        
        # Verifica se existe cache
        cache_path = self._get_cache_path(filepath)
        if os.path.exists(cache_path):
            try:
                print(f"[CACHE] Carregando do cache: {cache_path}")
                cached = np.load(cache_path)
                vertices = cached['vertices']
                colors = cached['colors']
                print(f"📊 Carregamento completo (cache): {len(vertices):,} pontos")
                return vertices, colors
            except Exception as e:
                print(f"⚠️  Erro ao carregar cache, reprocessando: {e}")
        
        # Lê arquivo com encoding apropriado
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                linhas = [linha.strip() for linha in f if linha.strip()]
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='latin-1') as f:
                linhas = [linha.strip() for linha in f if linha.strip()]
        
        # Extrai coordenadas
        xs, ys, zs, desvios_laterais = self._parse_upl_lines(linhas)
        
        if len(xs) == 0:
            raise ValueError("Nenhum ponto válido encontrado no arquivo UPL!")
        
        print(f"[OK] {len(xs):,} pontos extraidos")
        
        # Filtragem e amostragem
        xs, ys, zs, desvios_laterais = self._filter_and_sample(xs, ys, zs, desvios_laterais)
        
        # Normalização de coordenadas
        xs, ys, zs_norm = self._normalize_coordinates(xs, ys, zs)
        
        # Calcula cores por classificação (usando X relativo - sem desvio lateral)
        colors = self._calculate_colors(xs, ys, zs_norm, desvios_laterais)
        
        # Monta arrays de retorno
        vertices = np.column_stack((xs, ys, zs_norm)).astype(np.float32)
        
        # Salva cache
        self._save_cache(cache_path, vertices, colors)
        
        print(f"📊 Carregamento completo: {len(vertices):,} pontos")
        return vertices, colors
    
    def _get_cache_path(self, filepath):
        """Gera caminho para arquivo de cache"""
        cache_dir = ".cache"
        os.makedirs(cache_dir, exist_ok=True)
        
        base_name = os.path.basename(filepath)
        cache_name = os.path.splitext(base_name)[0] + ".npz"
        return os.path.join(cache_dir, cache_name)
    
    def _save_cache(self, cache_path, vertices, colors):
        """Salva dados processados em cache"""
        try:
            np.savez_compressed(cache_path, vertices=vertices, colors=colors)
            print(f"[CACHE] Dados salvos em: {cache_path}")
        except Exception as e:
            print(f"⚠️  Não foi possível salvar cache: {e}")
    
    def _parse_upl_lines(self, linhas):
        """Extrai coordenadas X, Y, Z e lat/lon das linhas do arquivo"""
        xs_global = []
        ys_global = []
        zs_global = []
        lats = []  # Latitude de cada seção
        lons = []  # Longitude de cada seção
        
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
                
                # Extrai latitude e longitude (campos 15 e 16 = índices 14 e 15)
                lat, lon = 0.0, 0.0
                try:
                    if len(partes) >= 16:
                        lat = float(partes[14].replace(',', '.'))
                        lon = float(partes[15].replace(',', '.'))
                except:
                    pass
                
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
                            lats.append(lat)
                            lons.append(lon)
                    except ValueError:
                        continue
                
                i += 2
                continue
            
            i += 1
        
        xs = np.array(xs_global)
        ys = np.array(ys_global)
        zs = np.array(zs_global)
        lats = np.array(lats)
        lons = np.array(lons)
        
        # Aplica transformação lateral no eixo X baseado em lat/lon
        # Retorna também os desvios aplicados
        xs, desvios_laterais = self._apply_lateral_transform(xs, ys, zs, lats, lons)
        
        return xs, ys, zs, desvios_laterais
    
    def _apply_lateral_transform(self, xs, ys, zs, lats, lons):
        """
        Aplica desvio lateral no eixo X baseado em latitude/longitude
        
        Lógica:
        1. Lê todas as seções com lat/lon
        2. Pega primeira e última seção
        3. Cria linha reta imaginária (referência)
        4. Para cada seção, calcula desvio perpendicular à linha reta
        5. Adiciona esse desvio no eixo X de todos os pontos da seção
        
        Args:
            xs, ys, zs: Coordenadas originais
            lats, lons: Latitude e longitude de cada ponto
            
        Returns:
            xs_new: Coordenadas X transformadas
        """
        # Fator de escala para desvio lateral (ajustável)
        # Valores pequenos (0.001 - 0.1) para não distorcer muito
        # 0.01 = 1% do desvio real
        FATOR_ESCALA = 1
        # Se não há lat/lon válido, retorna X original
        if len(lats) == 0 or np.all(lats == 0) or np.all(lons == 0):
            print("⚠️  Lat/Lon não disponível, mantendo coordenadas originais")
            desvios = np.zeros_like(xs)
            return xs, desvios
        
        # Agrupa por seção (Z único)
        unique_z = np.unique(zs)
        
        if len(unique_z) < 2:
            print("⚠️  Menos de 2 seções, mantendo coordenadas originais")
            desvios = np.zeros_like(xs)
            return xs, desvios
        
        # 1. Coleta lat/lon de cada seção
        secoes = []
        for z_val in unique_z:
            mask = zs == z_val
            lat_media = np.mean(lats[mask])
            lon_media = np.mean(lons[mask])
            secoes.append({
                'z': z_val,
                'lat': lat_media,
                'lon': lon_media,
                'mask': mask
            })
        
        # 2. Primeira e última seção
        primeira = secoes[0]
        ultima = secoes[-1]
        
        lat_start = primeira['lat']
        lon_start = primeira['lon']
        lat_end = ultima['lat']
        lon_end = ultima['lon']
        
        print(f"📍 Transformação lateral baseada em GPS:")
        print(f"   Início: lat={lat_start:.6f}, lon={lon_start:.6f}")
        print(f"   Fim: lat={lat_end:.6f}, lon={lon_end:.6f}")
        
        # 3. Converte lat/lon para metros (aproximação plana local)
        # 1° lat ≈ 111 km
        # 1° lon ≈ 111 km × cos(latitude)
        lat_mid = (lat_start + lat_end) / 2
        
        # Vetor da linha reta imaginária (início → fim)
        dx_reta = (lon_end - lon_start) * 111000 * np.cos(np.radians(lat_mid))
        dy_reta = (lat_end - lat_start) * 111000
        
        dist_reta = np.sqrt(dx_reta**2 + dy_reta**2)
        
        if dist_reta < 0.001:  # Linha muito curta (< 1mm)
            print("⚠️  Trajeto muito curto, mantendo coordenadas originais")
            desvios = np.zeros_like(xs)
            return xs, desvios
        
        # Normaliza vetor da linha reta
        dx_reta_norm = dx_reta / dist_reta
        dy_reta_norm = dy_reta / dist_reta
        
        # Vetor perpendicular à linha reta (rotação 90° anti-horário)
        perp_x = -dy_reta_norm
        perp_y = dx_reta_norm
        
        print(f"   Linha reta: ({dx_reta:.1f}m, {dy_reta:.1f}m) - {dist_reta:.1f}m")
        print(f"   Vetor perpendicular: ({perp_x:.3f}, {perp_y:.3f})")
        
        # 4. Para cada seção, calcula desvio lateral
        xs_new = xs.copy()
        desvios = np.zeros_like(xs)  # Armazena desvio de cada ponto
        
        for secao in secoes:
            lat_secao = secao['lat']
            lon_secao = secao['lon']
            mask = secao['mask']
            
            # Posição real da seção em relação ao início (metros)
            dx_real = (lon_secao - lon_start) * 111000 * np.cos(np.radians(lat_mid))
            dy_real = (lat_secao - lat_start) * 111000
            
            # Desvio perpendicular = produto escalar com vetor perpendicular
            # Isso dá a distância lateral da seção em relação à linha reta
            desvio_lateral = dx_real * perp_x + dy_real * perp_y
            
            # 5. Adiciona desvio lateral ao eixo X (com fator de escala)
            xs_new[mask] += desvio_lateral * FATOR_ESCALA
            desvios[mask] = desvio_lateral * FATOR_ESCALA
        
        print(f"   ✅ Desvio lateral aplicado (escala={FATOR_ESCALA})!")
        print(f"   X original: [{xs.min():.1f}, {xs.max():.1f}] m")
        print(f"   X com desvio: [{xs_new.min():.1f}, {xs_new.max():.1f}] m")
        print(f"   Desvio aplicado: ±{abs(desvios).max():.2f} m")
        
        return xs_new, desvios
    
    def _filter_and_sample(self, xs, ys, zs, desvios_laterais):
        """Filtra outliers e reduz pontos se necessário"""
        # Filtro: remove pontos muito distantes apenas no eixo Y
        # X não tem limite (pode variar com desvio lateral GPS)
        mask = (ys <= 10.0)
        xs = xs[mask]
        ys = ys[mask]
        zs = zs[mask]
        desvios_laterais = desvios_laterais[mask]
        
        # Amostragem se muito grande (somente se max_points definido)
        if self.max_points is not None and len(xs) > self.max_points:
            print(f"⚠️  Arquivo muito grande ({len(xs):,} pontos)")
            print(f"   Limitando para {self.max_points:,} pontos")
            
            step = len(xs) // self.max_points
            indices = np.arange(0, len(xs), step)[:self.max_points]
            xs = xs[indices]
            ys = ys[indices]
            zs = zs[indices]
            desvios_laterais = desvios_laterais[indices]
        
        return xs, ys, zs, desvios_laterais
    
    def _normalize_coordinates(self, xs, ys, zs):
        """Normaliza coordenadas Z para visualização"""
        z_min = zs.min()
        zs_norm = zs - z_min
        
        print(f"[NORMALIZAR] Coordenadas normalizadas:")
        print(f"   X: [{xs.min():.1f}, {xs.max():.1f}] m")
        print(f"   Y: [{ys.min():.1f}, {ys.max():.1f}] m")
        print(f"   Z: [{zs_norm.min():.1f}, {zs_norm.max():.1f}] m")
        
        return xs, ys, zs_norm
    
    def _calculate_colors(self, xs, ys, zs, desvios_laterais):
        """Calcula cores por classificação de túnel (Verde/Amarelo/Vermelho)"""
        from utils.tunnel_templates import FerroviaTunel, classify_points_with_template, colors_from_classification
        
        # Se não fornecido um gabarito, usa o padrão (ferrovia)
        template = self.template if self.template is not None else FerroviaTunel()
        
        # Calcula X relativo (sem desvio lateral) para classificação correta
        # O gabarito está sempre centrado em X=0
        xs_relative = xs - desvios_laterais
        
        # Classifica pontos: 0=seguro, 1=alerta, 2=invasão
        classifications = classify_points_with_template(xs_relative, ys, template)
        
        # Converte classificações para cores RGB
        colors = colors_from_classification(classifications)
        
        # Estatísticas
        n_seguro = np.sum(classifications == 0)
        n_alerta = np.sum(classifications == 1)
        n_invasao = np.sum(classifications == 2)
        total = len(classifications)
        
        print(f"[STATS] Classificacao (gabarito: {template.name}):")
        print(f"   [SEGURO] {n_seguro:,} ({n_seguro/total*100:.1f}%)")
        print(f"   [ALERTA] {n_alerta:,} ({n_alerta/total*100:.1f}%)")
        print(f"   [INVASAO] {n_invasao:,} ({n_invasao/total*100:.1f}%)")
        print(f"   Classificação usa X relativo (descontando desvio lateral)")
        
        return colors.astype(np.float32)


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
