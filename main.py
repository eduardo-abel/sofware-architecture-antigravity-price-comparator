import os
import sys
import json

# Garante que o projeto consegue importar o pacote explicitamente na raiz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.scrapper_amazon.local_json_adapter import LocalJsonProductAdapter
from core.application.use_cases import FindCheapestVariantsUseCase
from plugins.storage_sqlite.sqlite_adapter import SQLiteStorageAdapter

def main():
    # Caminho do JSON gerado pelo novo scraper Playwright
    json_path = "amazon_products_playwright.json"

    
    if not os.path.exists(json_path):
        print(f"Erro: O adapter está apontando para um banco que não existe: {json_path}")
        return

    # Injeção de Dependências manual (Assembler)
    repo_adapter = LocalJsonProductAdapter(filepath=json_path)
    storage_adapter = SQLiteStorageAdapter() # Porta secundária instanciada em DB
    
    compare_use_case = FindCheapestVariantsUseCase(repository=repo_adapter)
    
    # 3. Execução desacoplada
    cheapest_variants = compare_use_case.execute()
    
    # Salvar via abstração de Adapter (Sem sujar a main com DB connect ou with open)
    try:
        storage_adapter.save_cheapest_offers(cheapest_variants)
        print(f"💾 Snapshot de preços salvo com sucesso na base de dados relacional!")
    except Exception as e:
        print(f"⚠️ Erro no driver do banco ao salvar histórico: {e}")
    
    print("\n=======================================================")
    print(" 🏆 COMPARADOR COMPRADOR: OFERTAS MAIS BARATAS ATIVAS")
    print("=======================================================\n")
    
    for variant, dto in sorted(cheapest_variants.items()):
        formatted_price = f"{dto.price_value:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
        
        print(f"🕹️  {variant.upper()}")
        print(f"💰 Melhor Preço: R$ {formatted_price}")
        print(f"🏷️  Anúncio Extraído: {dto.original_title[:75]}...")
        print(f"🔗 Link Direto: {dto.url}")
        print("-" * 55)

if __name__ == "__main__":
    main()
