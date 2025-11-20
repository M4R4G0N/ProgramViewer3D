#!/usr/bin/env python3
"""
Script principal para executar o visualizador 3D
"""

import sys
from core.application import Viewer3DApplication


def main():
    """Função principal"""
    # Cria aplicação
    app = Viewer3DApplication()
    
    # Carrega arquivo se fornecido como argumento
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        app.load_file(filepath)
    else:
        print("\n💡 Uso:")
        print("   python3 main.py [arquivo]")
        print("\n   Exemplos:")
        print("   python3 main.py data.upl")
        print("   python3 main.py points.csv")
        print("\n   Sem argumentos: Abre visualizador vazio")
        print("="*60)
    
    # Inicia loop principal
    app.run()


if __name__ == "__main__":
    main()
