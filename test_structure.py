#!/usr/bin/env python3
"""
Script de teste para validar a estrutura do projeto
"""

import sys
import os

# Adiciona o diretório viewer3d ao path
sys.path.insert(0, '/home/maragon/Documentos/viewer3d')

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("🧪 Testando imports...")
    
    try:
        # Core
        from core.camera import Camera3D
        print("  ✅ core.camera.Camera3D")
        
        from core.configuration import Configuration
        print("  ✅ core.configuration.Configuration")
        
        from core.application import Viewer3DApplication
        print("  ✅ core.application.Viewer3DApplication")
        
        # UI
        from ui.vector_font import VectorFont
        print("  ✅ ui.vector_font.VectorFont")
        
        from ui.components import (ColorButton, ToggleButton, Slider, Button, Panel)
        print("  ✅ ui.components (ColorButton, ToggleButton, Slider, Button, Panel)")
        
        # Loaders
        from loaders.data_loader import (DataLoader, UPLLoader, CSVLoader, DataLoaderFactory)
        print("  ✅ loaders.data_loader (DataLoader, UPLLoader, CSVLoader, DataLoaderFactory)")
        
        # Renderers
        from renderers.point_cloud import (PointCloudRenderer, AxesRenderer, AxisIndicator)
        print("  ✅ renderers.point_cloud (PointCloudRenderer, AxesRenderer, AxisIndicator)")
        
        print("\n✅ Todos os imports bem-sucedidos!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro no import: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_camera():
    """Testa funcionalidades da câmera"""
    print("🧪 Testando Camera3D...")
    
    try:
        from core.camera import Camera3D
        
        cam = Camera3D(distance=100.0, pitch=45.0, yaw=90.0)
        assert cam.distance == 100.0, "Distance incorreta"
        assert cam.pitch == 45.0, "Pitch incorreto"
        assert cam.yaw == 90.0, "Yaw incorreto"
        
        cam.rotate(10.0, 5.0)
        assert cam.yaw == 100.0, "Rotação yaw falhou"
        assert cam.pitch == 50.0, "Rotação pitch falhou"
        
        cam.zoom(50.0)
        assert cam.distance == 150.0, "Zoom falhou"
        
        cam.set_target(10, 20, 30)
        assert cam.target_x == 10, "Set target X falhou"
        
        pos = cam.get_position()
        assert len(pos) == 3, "Get position deve retornar tupla (x, y, z)"
        
        print("  ✅ Todos os testes de Camera3D passaram!\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no teste de câmera: {e}\n")
        return False


def test_configuration():
    """Testa sistema de configuração"""
    print("🧪 Testando Configuration...")
    
    try:
        from core.configuration import Configuration
        
        config = Configuration("test_config.json")
        
        # Testa get/set
        config.set("test_key", "test_value")
        assert config.get("test_key") == "test_value", "Get/Set falhou"
        
        # Testa métodos específicos
        config.set_point_size(5.0)
        assert config.get_point_size() == 5.0, "Point size falhou"
        
        config.set_show_axes(False)
        assert config.get_show_axes() == False, "Show axes falhou"
        
        # Limpa arquivo de teste
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
        
        print("  ✅ Todos os testes de Configuration passaram!\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no teste de configuração: {e}\n")
        return False


def test_vector_font():
    """Testa sistema de fontes"""
    print("🧪 Testando VectorFont...")
    
    try:
        from ui.vector_font import VectorFont
        
        font = VectorFont()
        
        # Verifica dicionário de strokes
        assert 'A' in font.strokes, "Falta caractere 'A' no dicionário"
        assert '0' in font.strokes, "Falta caractere '0' no dicionário"
        assert ' ' in font.strokes, "Falta espaço no dicionário"
        
        # Testa medição de texto
        width = font.measure_text("HELLO", font_size=1.0)
        assert width > 0, "Medição de texto falhou"
        
        # Testa adicionar caractere customizado
        font.add_custom_char('©', [(0, 0, 1, 1)])
        assert '©' in font.strokes, "Adicionar caractere customizado falhou"
        
        print("  ✅ Todos os testes de VectorFont passaram!\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no teste de fonte: {e}\n")
        return False


def test_point_cloud_renderer():
    """Testa renderizador de nuvens de pontos"""
    print("🧪 Testando PointCloudRenderer...")
    
    try:
        from renderers.point_cloud import PointCloudRenderer
        import numpy as np
        
        renderer = PointCloudRenderer()
        
        # Cria dados de teste
        vertices = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]], dtype=np.float32)
        colors = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
        
        renderer.set_data(vertices, colors)
        
        assert renderer.n_vertices == 3, "Número de vértices incorreto"
        
        # Testa bounds
        mins, maxs = renderer.get_bounds()
        assert mins[0] == 0 and maxs[0] == 2, "Bounds incorretos"
        
        # Testa center
        center = renderer.get_center()
        assert abs(center[0] - 1.0) < 0.01, "Centro incorreto"
        
        # Testa point size
        renderer.set_point_size(5.0)
        assert renderer.get_point_size() == 5.0, "Point size falhou"
        
        print("  ✅ Todos os testes de PointCloudRenderer passaram!\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no teste de renderer: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("🧪 TESTES DO VIEWER3D")
    print("="*60 + "\n")
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Camera", test_camera()))
    results.append(("Configuration", test_configuration()))
    results.append(("VectorFont", test_vector_font()))
    results.append(("PointCloudRenderer", test_point_cloud_renderer()))
    
    print("="*60)
    print("📊 RESULTADOS")
    print("="*60)
    
    for name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"  {name:20s} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print("="*60)
    print(f"Total: {passed}/{total} testes passaram")
    print("="*60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
