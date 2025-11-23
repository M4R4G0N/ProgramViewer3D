#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo Prático: Comparar pontos com diferentes gabaritos

Demonstra como o mesmo arquivo UPL produz diferentes resultados
dependendo do gabarito escolhido
"""

import sys
import numpy as np
from utils.tunnel_templates import TemplateRegistry, classify_points_with_template, colors_from_classification
from loaders.data_loader import UPLLoader

# Força UTF-8 para Windows
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def exemplo_1_gabaritos_basicos():
    """Exemplo 1: Testar classificação com gabaritos básicos"""
    print("\n" + "="*70)
    print("📋 EXEMPLO 1: Classificação com Gabaritos Básicos")
    print("="*70)
    
    # Pontos de teste
    test_points = np.array([
        [0.0, 3.0],      # Centro do túnel
        [2.0, 4.0],      # Lado direito
        [2.5, 4.0],      # Borda
        [3.0, 4.0],      # Fora
        [-2.0, 3.5],     # Lado esquerdo
        [0.0, 1.0],      # Baixo (fora)
        [0.0, 7.0],      # Alto
    ], dtype=np.float32)
    
    xs, ys = test_points[:, 0], test_points[:, 1]
    
    print("\n🔍 Testando pontos:")
    for i, (x, y) in enumerate(test_points):
        print(f"  {i+1}. ({x:6.1f}, {y:6.1f})", end="")
    
    # Testa cada gabarito
    for gabarit_key in TemplateRegistry.list_all():
        gabarit = TemplateRegistry.get(gabarit_key)
        print(f"\n\n📌 Gabarito: {gabarit.name}")
        print("-" * 70)
        
        # Classifica
        classifications = classify_points_with_template(xs, ys, gabarit)
        
        for i, (x, y, cls) in enumerate(zip(xs, ys, classifications)):
            status = ['🟢 SEGURO', '🟡 ALERTA', '🔴 INVASÃO'][cls]
            print(f"  Ponto {i+1} ({x:6.1f}, {y:6.1f}) → {status}")
        
        # Estatísticas
        n_seguro = np.sum(classifications == 0)
        n_alerta = np.sum(classifications == 1)
        n_invasao = np.sum(classifications == 2)
        print(f"\n  Resumo: {n_seguro} seguro, {n_alerta} alerta, {n_invasao} invasão")


def exemplo_2_carregar_upl_com_gabaritos(filepath):
    """Exemplo 2: Carregar arquivo UPL com diferentes gabaritos"""
    print("\n" + "="*70)
    print(f"📋 EXEMPLO 2: Carregar {filepath} com Diferentes Gabaritos")
    print("="*70)
    
    try:
        for gabarit_key in TemplateRegistry.list_all():
            print(f"\n📂 Carregando com gabarito: {gabarit_key}")
            
            gabarit = TemplateRegistry.get(gabarit_key)
            loader = UPLLoader(template=gabarit)
            vertices, colors = loader.load(filepath)
            
            # Conta cores
            n_seguro = np.sum((colors[:, 0] == 0) & (colors[:, 1] == 1) & (colors[:, 2] == 0))
            n_alerta = np.sum((colors[:, 0] == 1) & (colors[:, 1] == 1) & (colors[:, 2] == 0))
            n_invasao = np.sum((colors[:, 0] == 1) & (colors[:, 1] == 0) & (colors[:, 2] == 0))
            total = len(colors)
            
            print(f"   ✓ {len(vertices):,} pontos carregados")
            print(f"   🟢 SEGURO:    {n_seguro:6,} ({n_seguro/total*100:5.1f}%)")
            print(f"   🟡 ALERTA:    {n_alerta:6,} ({n_alerta/total*100:5.1f}%)")
            print(f"   🔴 INVASÃO:   {n_invasao:6,} ({n_invasao/total*100:5.1f}%)")
    
    except FileNotFoundError:
        print(f"\n❌ Arquivo não encontrado: {filepath}")
        print("   Use: python exemplo_gabaritos.py seu_arquivo.upl")


def exemplo_3_criar_gabarit_customizado():
    """Exemplo 3: Criar gabarito customizado"""
    print("\n" + "="*70)
    print("📋 EXEMPLO 3: Criar Gabarito Customizado")
    print("="*70)
    
    from utils.tunnel_templates import GabaritPersonalizado, TemplateRegistry
    
    # Define gabarito customizado
    gabarit_custom = GabaritPersonalizado(
        name="Túnel Mineiro 4m",
        safe_bounds={
            'x_min': -2.0,
            'x_max': 2.0,
            'y_min': 1.0,
            'y_max': 5.0
        },
        warning_bounds={
            'x_min': -2.5,
            'x_max': 2.5,
            'y_min': 0.5,
            'y_max': 5.5
        }
    )
    
    # Registra
    TemplateRegistry.register('mineiro_4m', gabarit_custom)
    
    print(f"\n✅ Gabarito registrado: {gabarit_custom.name}")
    
    # Testa
    test_points = np.array([
        [0.0, 3.0],
        [1.5, 3.0],
        [2.2, 3.0],
        [2.8, 3.0],
    ], dtype=np.float32)
    
    xs, ys = test_points[:, 0], test_points[:, 1]
    classifications = classify_points_with_template(xs, ys, gabarit_custom)
    
    print(f"\n🔍 Testando com novo gabarito:")
    for x, y, cls in zip(xs, ys, classifications):
        status = ['🟢 SEGURO', '🟡 ALERTA', '🔴 INVASÃO'][cls]
        print(f"  ({x:5.1f}, {y:5.1f}) → {status}")


def exemplo_4_analise_comparativa(filepath):
    """Exemplo 4: Análise comparativa (tabela)"""
    print("\n" + "="*70)
    print("📋 EXEMPLO 4: Análise Comparativa de Gabaritos")
    print("="*70)
    
    results = []
    
    for gabarit_key in TemplateRegistry.list_all():
        try:
            gabarit = TemplateRegistry.get(gabarit_key)
            loader = UPLLoader(template=gabarit)
            vertices, colors = loader.load(filepath)
            
            n_seguro = np.sum((colors[:, 0] == 0) & (colors[:, 1] == 1) & (colors[:, 2] == 0))
            n_alerta = np.sum((colors[:, 0] == 1) & (colors[:, 1] == 1) & (colors[:, 2] == 0))
            n_invasao = np.sum((colors[:, 0] == 1) & (colors[:, 1] == 0) & (colors[:, 2] == 0))
            total = len(colors)
            
            results.append({
                'gabarit': gabarit.name,
                'seguro': n_seguro,
                'alerta': n_alerta,
                'invasao': n_invasao,
                'total': total,
                'pct_invasao': n_invasao / total * 100
            })
        except:
            pass
    
    if results:
        print("\n📊 TABELA COMPARATIVA")
        print("-" * 100)
        print(f"{'Gabarito':<25} {'Seguro':>12} {'Alerta':>12} {'Invasão':>12} {'% Invasão':>12}")
        print("-" * 100)
        
        for r in results:
            print(f"{r['gabarit']:<25} {r['seguro']:>12,} {r['alerta']:>12,} {r['invasao']:>12,} {r['pct_invasao']:>11.1f}%")
        
        print("-" * 100)


def main():
    """Função principal"""
    import sys
    
    # Exemplo 1: Gabaritos básicos
    exemplo_1_gabaritos_basicos()
    
    # Exemplo 2 e 4: Se arquivo fornecido
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        exemplo_2_carregar_upl_com_gabaritos(filepath)
        exemplo_4_analise_comparativa(filepath)
    else:
        print("\n" + "="*70)
        print("💡 Para testar com arquivo UPL:")
        print("   python exemplo_gabaritos.py seu_arquivo.upl")
        print("="*70)
    
    # Exemplo 3: Customizar
    exemplo_3_criar_gabarit_customizado()
    
    print("\n✅ Exemplos concluídos!\n")


if __name__ == '__main__':
    main()
