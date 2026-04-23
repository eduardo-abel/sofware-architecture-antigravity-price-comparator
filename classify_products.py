import json

def classify_products(input_file="amazon_products_local.json", output_file="amazon_classified.json"):
    with open(input_file, 'r', encoding='utf-8') as f:
        products = json.load(f)
        
    classified = {
        "Consoles": [],
        "Controles": [],
        "Volantes": [],
        "Headsets & Áudio": [],
        "Jogos": [],
        "Acessórios & Hardware": [],
        "Outros": []
    }
    
    for p in products:
        title = p.get("title", "").lower()
        
        # Novas regras de exclusão: se tiver palavras de acessórios, nunca é console
        is_accessory = any(x in title for x in ["cabo", "cable", "usb", "suporte", "base", "carregamento", "ssd", "unidade de disco", "disc drive", "disk drive", "ventilador", "cooler", "vr2", "portal remote", "lcd", "caneca", "mug", "case", "estojo", "película", "fonte"])
        is_controller = any(x in title for x in ["controle", "dualsense", "controller", "mando", "joystick", "joy-con", "pro controller"])
        is_game_title = any(x in title for x in ["jogo", "spider-man", "gran turismo", "ghost of", "resident evil", "pragmata", "mega man", "collection", "game", "mario", "zelda", "pokémon", "pokemon", "fifa", "fc 24", "halo", "forza", "nba", "mortal kombat", "street fighter", "god of war", "elden ring", "call of duty", "cod ", "battlefield", "assassin's creed", "red dead", "sonic", "crash", "hogwarts", "gta", "minecraft", "ea sports", "mídia física", "physical edition", "standard edition", "premium edition", "deluxe edition"])
        is_game = is_game_title and "console" not in title and "bundle" not in title and "pack" not in title

        # Tenta pegar o preço numérico para sanidade
        price_str = p.get("price_current", "0").replace("R$", "").replace(".", "").replace(",", ".").strip()
        try:
            price_val = float(price_str)
        except:
            price_val = 0.0

        # 1. Filtro de Acessórios e Hardware (MUITO AGRESSIVO)
        # Se tiver qualquer uma dessas palavras, é acessório, independente de ter 'console' ou 'slim' no título
        # Evitamos 'station' puro pois bate em 'playstation'. Usamos termos compostos.
        acc_terms = ["volante", "wheel", "pedal", "shifter", "pedais", "driving force", "g923", "g29", "headset", "fone", "áudio", "kinect", "unidade de disco", "disc drive", "disk drive", "cooling station", "charging station", "estação de carga", "estação de carregamento", "base de carregamento", "suporte", "base", "case", "estojo", "película", "capa", "skin", "adesivo", "faceplate", "tampa", "cover", "fonte", "power supply", "cabo", "cable", "usb", "bateria", "carregador"]
        
        if is_accessory or any(x in title for x in acc_terms):
            if any(x in title for x in ["volante", "wheel", "pedal", "shifter", "pedais", "driving force", "g923", "g29"]):
                category = "Volantes"
            elif any(x in title for x in ["headset", "fone", "áudio"]):
                category = "Headsets & Áudio"
            else:
                category = "Acessórios & Hardware"
        
        # 2. Controles
        elif is_controller:
            category = "Controles"

        # 3. Filtro de Consoles (Regra de Ouro: preço alto + plataforma = Console/Bundle)
        # Aumentamos o piso para 1000 reais para evitar peças caras sendo consoles
        elif (price_val > 1000 and any(x in title for x in ["ps5", "playstation 5", "playstation®5", "xbox series", "xbox one", "switch", "nintendo"])) or \
             any(x in title for x in ["console", "pacote", "bundle", "pack", "slim", "pro edition", "digital edition", "oled edition"]):
            
            # Sanity check: console novo por menos de 800? Extremamente improvável em 2026.
            if price_val < 800 and "console" not in title:
                if is_game_title: category = "Jogos"
                else: category = "Acessórios & Hardware"
            else:
                category = "Consoles"

        # 4. Jogos (Tudo o que restou e tem título de jogo)
        elif is_game_title:
            category = "Jogos"
            
        else:
            category = "Outros"




            
        # O usuário pediu para limpar o JSON mantendo nome, link e fotografia no segmento
        classified[category].append({
            "title": p.get("title"),
            "url": p.get("url"),
            "price": p.get("price_current"),
            "rating": p.get("rating"),
            "image": p.get("image", "")
        })
        
    # Limpa as categorias que ficaram vazias para o JSON final ficar enxuto
    classified = {k: v for k, v in classified.items() if len(v) > 0}
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(classified, f, ensure_ascii=False, indent=4)
        
    print(f"Classificação concluída com sucesso! Objeto salvo em {output_file}\n")
    print("Resumo do agrupamento:")
    for cat, items in classified.items():
        print(f" -> {cat}: {len(items)} produtos")

if __name__ == "__main__":
    classify_products()
