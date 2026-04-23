import asyncio
import pandas as pd
import json
import hashlib
import os
from playwright.async_api import async_playwright
import re

# Configurações
CSV_FILE = "products_to_monitor.csv"
OUTPUT_FILE = "amazon_products_playwright.json"
HEADLESS = True

async def get_cheapest_product(page, search_query, min_threshold, expected_category):
    print(f"🔍 Pesquisando: {search_query}...")
    
    # URL de busca na Amazon
    search_url = f"https://www.amazon.com.br/s?k={search_query.replace(' ', '+')}"
    
    try:
        await page.goto(search_url, wait_until="commit", timeout=60000)
    except Exception as e:
        print(f"❌ Erro ao carregar página de busca: {e}")
        return None

    # Aguarda os resultados aparecerem
    try:
        await page.wait_for_selector('div[data-component-type="s-search-result"]', timeout=30000)
    except:
        print(f"⚠️ Nenhum resultado visual para: {search_query}")
        return None
    
    # Seleção dos cards de produto
    products = await page.query_selector_all('div[data-component-type="s-search-result"]')
    
    valid_products = []
    
    # Prepara as palavras-chave da busca para comparação
    query_clean = search_query.lower()
    query_words = set(re.findall(r'\w+', query_clean))

    # Termos Proibidos (Penalidade MASSIVA) - Coisas que confundem com o produto real
    base_forbidden = ["suporte", "cape", "capa", "case", "película", "pelicula", "protector", "skin", "adesivo", "stand", "mount", "dock", "charging", "carregador", "cabo", "cable", "adapter", "adaptador", "steering wheel", "volante", "maleta", "estojo", "cover", "faceplate", "tampa", "reparo", "peça", "part", "service", "amiibo", "cockpit", "simulator", "simulador", "frame", "wheel stand", "pedal stand", "pouch", "bag", "bolsa", "travel", "grip", "thumbstick", "keyboard", "teclado", "mouse", "caneca", "mug", "luminária", "lamp"]
    
    # Filtra da lista proibida o que estiver na query (Ex: se busco "Volante", volante não é proibido)
    active_forbidden = [f for f in base_forbidden if f not in query_clean]
    
    # Se for busca de CONSOLE, outros hardwares viram proibidos para evitar confusão
    is_console_search = "console" in query_clean
    if is_console_search:
        active_forbidden += ["controle", "controller", "joystick", "sidestick", "flight stick", "shifter", "pedal", "headset", "headphone", "pad", "remote", "volante"]

    for product in products:
        try:
            # Extração de Título
            title_el = await product.query_selector('h2 a span')
            if not title_el:
                title_el = await product.query_selector('.a-size-base-plus.a-color-base.a-text-normal')
            if not title_el:
                title_el = await product.query_selector('.a-size-medium.a-color-base.a-text-normal')
            
            title = await title_el.inner_text() if title_el else "Sem título"
            title_clean = title.lower()
            
            # Extração de URL
            url_el = await product.query_selector('h2 a')
            if not url_el:
                url_el = await product.query_selector('a.a-link-normal.s-no-outline')
            
            url_val = f"https://www.amazon.com.br{await url_el.get_attribute('href')}" if url_el else ""
            
            # Extração de Preço
            price_whole = await product.query_selector('.a-price-whole')
            price_fraction = await product.query_selector('.a-price-fraction')
            
            if price_whole:
                p_text = await price_whole.inner_text()
                p_fraction = await price_fraction.inner_text() if price_fraction else "00"
                p_clean = re.sub(r'[^\d]', '', p_text)
                price_val = float(f"{p_clean}.{p_fraction}")
            else:
                price_val = 0.0

            # Extração de Imagem
            image_el = await product.query_selector('img.s-image')
            image_url = await image_el.get_attribute('src') if image_el else ""

            # Cálculo de Relevância
            title_words_list = re.findall(r'\w+', title_clean)
            title_words = set(title_words_list)
            matches = query_words.intersection(title_words)
            relevancy = len(matches) / len(query_words) if query_words else 0
            
            # --- LÓGICA DE FILTRAGEM MASSIVA ---
            has_forbidden = any(f in title_clean for f in active_forbidden)
            
            if has_forbidden:
                 relevancy -= 2.0
            
            if any(title_clean.startswith(f) for f in ["suporte", "capa", "case", "película", "estojo", "pouch", "bag"]):
                 relevancy -= 1.0

            # Filtros de Sanidade
            if price_val >= float(min_threshold) and relevancy >= 0.35 and url_val and title != "Sem título":
                valid_products.append({
                    "title": title,
                    "url": url_val,
                    "price": price_val,
                    "image": image_url,
                    "relevancy": relevancy
                })
        except Exception:
            continue

    if not valid_products:
        print(f"⚠️ Nenhum produto RELEVANTE encontrado para: {search_query}")
        return None

    # Ordenação: Relevância Descendente, Preço Ascendente
    valid_products.sort(key=lambda x: (-x["relevancy"], x["price"]))
    
    cheapest = valid_products[0]
    print(f"✅ Encontrado (Rel: {cheapest['relevancy']:.2f}): {cheapest['title']} por R$ {cheapest['price']}")
    return cheapest

async def run_scraper():
    if not os.path.exists(CSV_FILE):
        print(f"❌ Arquivo CSV {CSV_FILE} não encontrado.")
        return

    df = pd.read_csv(CSV_FILE)
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        for index, row in df.iterrows():
            product_id = row['id']
            query = row['search_query']
            threshold = row['min_price_threshold']
            category = row['expected_category']

            monitor_hash = hashlib.md5(product_id.encode()).hexdigest()

            product_data = await get_cheapest_product(page, query, threshold, category)

            if product_data:
                results.append({
                    "monitor_id": product_id,
                    "monitor_hash": monitor_hash,
                    "category": category,
                    "title": product_data["title"],
                    "price": f"R$ {product_data['price']:.2f}".replace('.', ','),
                    "url": product_data["url"],
                    "image": product_data["image"],
                    "timestamp": pd.Timestamp.now().isoformat()
                })
            
            await asyncio.sleep(2)

        await browser.close()

    grouped_results = {}
    for item in results:
        cat = item.pop("category", "Outros")
        if cat not in grouped_results:
            grouped_results[cat] = []
        grouped_results[cat].append(item)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(grouped_results, f, indent=4, ensure_ascii=False)
    
    print(f"🏁 Scraper finalizado! Dados salvos em {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(run_scraper())
