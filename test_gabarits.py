#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Rápido do Sistema de Gabaritos

Valida se todos os componentes estão funcionando corretamente
"""

import sys
import numpy as np

def test_imports():
    """Testa se todos os imports funcionam"""
    print("\n[1/5] Testando imports...")
    try:
        from utils.tunnel_templates import TemplateRegistry, FerroviaTunel, RodoviaDupla, TuneloAqued
        from utils.tunnel_templates import GabaritPersonalizado, classify_points_with_template, colors_from_classification
        from ui.gabarit_selector_menu import GabaritSelectorMenu
        from ui.train_model_selector_menu import TrainModelSelectorMenu
        from loaders.data_loader import UPLLoader
        print("    [OK] Todos os imports OK")
        return True
    except Exception as e:
        print(f"    [ERRO] {e}")
        return False


def test_gabarits():
    """Testa funcionamento dos gabaritos"""
    print("\n[2/5] Testando gabaritos...")
    try:
        from utils.tunnel_templates import TemplateRegistry
        
        # Lista gabaritos
        gabarits = TemplateRegistry.list_all()
        print(f"    Gabaritos disponíveis: {len(gabarits)}")
        for key in gabarits:
            gabarit = TemplateRegistry.get(key)
            print(f"      - {key}: {gabarit.name}")
        
        # Testa um ponto com cada gabarito
        test_point = (0.0, 3.0)
        for key in gabarits:
            gabarit = TemplateRegistry.get(key)
            cls = gabarit.classify_point(*test_point)
            status = ['SEGURO', 'ALERTA', 'INVASAO'][cls]
            print(f"      - {key} @ {test_point}: {status}")
        
        print("    [OK] Gabaritos OK")
        return True
    except Exception as e:
        print(f"    [ERRO] {e}")
        return False


def test_classification():
    """Testa classificação de múltiplos pontos"""
    print("\n[3/5] Testando classificação de pontos...")
    try:
        from utils.tunnel_templates import TemplateRegistry, classify_points_with_template, colors_from_classification
        
        # Pontos de teste
        xs = np.array([0.0, 2.0, 2.5, 3.0], dtype=np.float32)
        ys = np.array([3.0, 4.0, 4.0, 4.0], dtype=np.float32)
        
        gabarit = TemplateRegistry.get('ferrovia')
        
        # Classifica
        classifications = classify_points_with_template(xs, ys, gabarit)
        print(f"    Pontos: {len(xs)}")
        print(f"    Classificacoes: {classifications}")
        
        # Converte para cores
        colors = colors_from_classification(classifications)
        print(f"    Cores: shape={colors.shape}, dtype={colors.dtype}")
        
        print("    [OK] Classificacao OK")
        return True
    except Exception as e:
        print(f"    [ERRO] {e}")
        return False


def test_data_loader():
    """Testa carregador UPL com gabarito"""
    print("\n[4/5] Testando carregador UPL...")
    try:
        from loaders.data_loader import UPLLoader
        from utils.tunnel_templates import TemplateRegistry
        
        # Testa com arquivo real se existir
        import os
        arquivo = 'RLT_NE__20250227_00 1.upl'
        
        if os.path.exists(arquivo):
            print(f"    Arquivo encontrado: {arquivo}")
            
            # Carrega com gabarito
            gabarit = TemplateRegistry.get('ferrovia')
            loader = UPLLoader(template=gabarit)
            vertices, colors = loader.load(arquivo)
            
            print(f"    Vertices: {len(vertices):,} pontos")
            print(f"    Cores: shape={colors.shape}")
            print(f"    [OK] Carregador OK")
        else:
            print(f"    [AVISO] Arquivo nao encontrado ({arquivo}) - pulando")
            print(f"    [OK] Carregador OK (sem arquivo)")
        
        return True
    except Exception as e:
        print(f"    [ERRO] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_registry():
    """Testa registro de novo gabarito"""
    print("\n[5/5] Testando registro de gabarito customizado...")
    try:
        from utils.tunnel_templates import GabaritPersonalizado, TemplateRegistry
        
        # Cria novo gabarito
        novo = GabaritPersonalizado(
            name="Teste",
            safe_bounds={'x_min': -1, 'x_max': 1, 'y_min': 0, 'y_max': 2},
            warning_bounds={'x_min': -2, 'x_max': 2, 'y_min': -1, 'y_max': 3}
        )
        
        # Registra
        TemplateRegistry.register('teste_novo', novo)
        
        # Recupera
        retrieved = TemplateRegistry.get('teste_novo')
        print(f"    Gabarito registrado: {retrieved.name}")
        
        # Testa
        cls = retrieved.classify_point(0.0, 1.0)
        status = ['SEGURO', 'ALERTA', 'INVASAO'][cls]
        print(f"    Classificacao de (0, 1): {status}")
        
        print("    [OK] Registro OK")
        return True
    except Exception as e:
        print(f"    [ERRO] {e}")
        return False


def main():
    """Função principal"""
    print("="*70)
    print("TESTE RAPIDO: Sistema de Gabaritos de Tunel v2.0")
    print("="*70)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Gabaritos", test_gabarits()))
    results.append(("Classificacao", test_classification()))
    results.append(("Data Loader", test_data_loader()))
    results.append(("Registry", test_registry()))
    
    # Resumo
    print("\n" + "="*70)
    print("RESULTADO DOS TESTES")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASSOU]" if result else "[FALHOU]"
        print(f"{name:20} {status}")
    
    print("="*70)
    print(f"Total: {passed}/{total} testes passaram")
    print("="*70)
    
    if passed == total:
        print("\n[OK] TUDO OK! Sistema esta funcional.\n")
        return 0
    else:
        print(f"\n[AVISO] {total - passed} teste(s) falharam.\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
