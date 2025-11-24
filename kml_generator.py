"""
Gerador de KML a partir de arquivos UPL
Extrai lat/lon e cria arquivo para Google Earth
"""

import os
from pathlib import Path


class KMLGenerator:
    """Gera arquivos KML a partir de coordenadas lat/lon"""
    
    def __init__(self):
        self.name = "Trajeto UPL"
        self.description = "Trajeto extraído de arquivo UPL"
    
    def generate_from_upl(self, upl_filepath, output_filepath=None):
        """
        Gera KML a partir de arquivo UPL
        
        Args:
            upl_filepath: Caminho do arquivo UPL
            output_filepath: Caminho do KML de saída (None = auto)
            
        Returns:
            Caminho do arquivo KML gerado
        """
        print(f"📍 Extraindo coordenadas de: {upl_filepath}")
        
        # Lê arquivo UPL
        try:
            with open(upl_filepath, 'r', encoding='utf-8') as f:
                linhas = [linha.strip() for linha in f if linha.strip()]
        except UnicodeDecodeError:
            with open(upl_filepath, 'r', encoding='latin-1') as f:
                linhas = [linha.strip() for linha in f if linha.strip()]
        
        # Extrai coordenadas
        coordenadas = self._extract_coordinates(linhas)
        
        if len(coordenadas) == 0:
            print("⚠️  Nenhuma coordenada lat/lon encontrada no arquivo!")
            return None
        
        # Define caminho de saída
        if output_filepath is None:
            base = Path(upl_filepath).stem
            output_filepath = str(Path(upl_filepath).parent / f"{base}.kml")
        
        # Gera KML
        self._generate_kml(coordenadas, output_filepath)
        
        print(f"✅ KML gerado: {output_filepath}")
        print(f"   {len(coordenadas)} pontos exportados")
        
        return output_filepath
    
    def _extract_coordinates(self, linhas):
        """
        Extrai coordenadas lat/lon do arquivo UPL
        
        Returns:
            Lista de dicionários com lat, lon, km, altitude
        """
        coordenadas = []
        
        i = 0
        while i < len(linhas):
            linha = linhas[i]
            
            if linha.startswith("EFVM") and "RH-" in linha:
                partes = linha.split(";")
                
                if len(partes) >= 17:
                    try:
                        # Latitude e Longitude (campos 15 e 16)
                        lat = float(partes[14].replace(',', '.'))
                        lon = float(partes[15].replace(',', '.'))
                        
                        # KM + metros (campos 12 e 13)
                        unidade = float(partes[11])
                        subunidade = float(partes[12].replace(',', '.'))
                        km = unidade + (subunidade / 1000.0)
                        
                        # Altitude (campo 17 se disponível)
                        altitude = 0.0
                        if len(partes) >= 17:
                            try:
                                altitude = float(partes[16].replace(',', '.'))
                            except:
                                pass
                        
                        # Valida coordenadas
                        if -90 <= lat <= 90 and -180 <= lon <= 180 and (lat != 0 or lon != 0):
                            coordenadas.append({
                                'lat': lat,
                                'lon': lon,
                                'km': km,
                                'altitude': altitude,
                                'descricao': f"KM {km:.3f}"
                            })
                    except (ValueError, IndexError):
                        pass
            
            i += 1
        
        return coordenadas
    
    def _generate_kml(self, coordenadas, output_filepath):
        """
        Gera arquivo KML
        
        Args:
            coordenadas: Lista de dicionários com lat, lon, km, altitude
            output_filepath: Caminho do arquivo de saída
        """
        # Calcula bounds
        lats = [c['lat'] for c in coordenadas]
        lons = [c['lon'] for c in coordenadas]
        
        lat_min, lat_max = min(lats), max(lats)
        lon_min, lon_max = min(lons), max(lons)
        
        # Centro
        lat_center = (lat_min + lat_max) / 2
        lon_center = (lon_min + lon_max) / 2
        
        # Distância aproximada para range da câmera
        lat_range = lat_max - lat_min
        lon_range = lon_max - lon_min
        range_meters = max(lat_range, lon_range) * 111000 * 2  # 2x para margem
        
        # Gera KML
        kml = []
        kml.append('<?xml version="1.0" encoding="UTF-8"?>')
        kml.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
        kml.append('  <Document>')
        kml.append(f'    <name>{self.name}</name>')
        kml.append(f'    <description>{self.description}</description>')
        
        # Estilo para linha
        kml.append('    <Style id="lineStyle">')
        kml.append('      <LineStyle>')
        kml.append('        <color>ff0000ff</color>')  # Vermelho
        kml.append('        <width>3</width>')
        kml.append('      </LineStyle>')
        kml.append('    </Style>')
        
        # Estilo para pontos
        kml.append('    <Style id="pointStyle">')
        kml.append('      <IconStyle>')
        kml.append('        <color>ff00ff00</color>')  # Verde
        kml.append('        <scale>0.5</scale>')
        kml.append('      </IconStyle>')
        kml.append('    </Style>')
        
        # LookAt inicial (visualização)
        kml.append('    <LookAt>')
        kml.append(f'      <longitude>{lon_center}</longitude>')
        kml.append(f'      <latitude>{lat_center}</latitude>')
        kml.append(f'      <altitude>0</altitude>')
        kml.append(f'      <range>{range_meters}</range>')
        kml.append('      <tilt>45</tilt>')
        kml.append('      <heading>0</heading>')
        kml.append('    </LookAt>')
        
        # Linha do trajeto
        kml.append('    <Placemark>')
        kml.append('      <name>Trajeto</name>')
        kml.append('      <description>Linha do trajeto UPL</description>')
        kml.append('      <styleUrl>#lineStyle</styleUrl>')
        kml.append('      <LineString>')
        kml.append('        <extrude>1</extrude>')
        kml.append('        <tessellate>1</tessellate>')
        kml.append('        <altitudeMode>clampToGround</altitudeMode>')
        kml.append('        <coordinates>')
        
        # Adiciona coordenadas da linha
        for coord in coordenadas:
            kml.append(f'          {coord["lon"]},{coord["lat"]},{coord["altitude"]}')
        
        kml.append('        </coordinates>')
        kml.append('      </LineString>')
        kml.append('    </Placemark>')
        
        # Pontos a cada 100m (ou menos se trajeto curto)
        step = max(1, len(coordenadas) // 50)  # Máximo 50 pontos
        
        for i in range(0, len(coordenadas), step):
            coord = coordenadas[i]
            kml.append('    <Placemark>')
            kml.append(f'      <name>KM {coord["km"]:.3f}</name>')
            kml.append(f'      <description>')
            kml.append(f'        Quilômetro: {coord["km"]:.3f}<br/>')
            kml.append(f'        Latitude: {coord["lat"]:.6f}<br/>')
            kml.append(f'        Longitude: {coord["lon"]:.6f}<br/>')
            if coord["altitude"] != 0:
                kml.append(f'        Altitude: {coord["altitude"]:.1f}m<br/>')
            kml.append(f'      </description>')
            kml.append('      <styleUrl>#pointStyle</styleUrl>')
            kml.append('      <Point>')
            kml.append('        <coordinates>')
            kml.append(f'          {coord["lon"]},{coord["lat"]},{coord["altitude"]}')
            kml.append('        </coordinates>')
            kml.append('      </Point>')
            kml.append('    </Placemark>')
        
        # Marca início e fim
        if len(coordenadas) > 0:
            # Início
            inicio = coordenadas[0]
            kml.append('    <Placemark>')
            kml.append('      <name>INÍCIO</name>')
            kml.append(f'      <description>KM {inicio["km"]:.3f}</description>')
            kml.append('      <Point>')
            kml.append('        <coordinates>')
            kml.append(f'          {inicio["lon"]},{inicio["lat"]},{inicio["altitude"]}')
            kml.append('        </coordinates>')
            kml.append('      </Point>')
            kml.append('    </Placemark>')
            
            # Fim
            fim = coordenadas[-1]
            kml.append('    <Placemark>')
            kml.append('      <name>FIM</name>')
            kml.append(f'      <description>KM {fim["km"]:.3f}</description>')
            kml.append('      <Point>')
            kml.append('        <coordinates>')
            kml.append(f'          {fim["lon"]},{fim["lat"]},{fim["altitude"]}')
            kml.append('        </coordinates>')
            kml.append('      </Point>')
            kml.append('    </Placemark>')
        
        kml.append('  </Document>')
        kml.append('</kml>')
        
        # Salva arquivo
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(kml))


def generate_kml_from_upl(upl_file, output_file=None):
    """
    Função helper para gerar KML rapidamente
    
    Args:
        upl_file: Arquivo UPL de entrada
        output_file: Arquivo KML de saída (opcional)
        
    Returns:
        Caminho do arquivo KML gerado
    """
    generator = KMLGenerator()
    return generator.generate_from_upl(upl_file, output_file)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python kml_generator.py <arquivo.upl> [saida.kml]")
        sys.exit(1)
    
    upl_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(upl_file):
        print(f"❌ Arquivo não encontrado: {upl_file}")
        sys.exit(1)
    
    kml_path = generate_kml_from_upl(upl_file, output_file)
    
    if kml_path:
        print(f"\n🌍 Abra o arquivo no Google Earth:")
        print(f"   {kml_path}")
