import re

class ProductDomainService:
    @staticmethod
    def normalize_product_variant(title: str, category: str) -> str:
        """
        Deduze qual é o modelo base (Variação) do produto baseado no título e categoria.
        Isola as variações exatas solicitadas no Domínio.
        """
        t = title.lower()
        
        if category == "Consoles":
            # Sanity check: se na categoria Console cair algo com 'jogo', 'midia' ou 'edition' sem ter 'console'
            # vamos forçar a ser jogo genérico se o preço for baixo no futuro, mas aqui apenas refinamos o nome
            if ("edition" in t or "standard" in t or "jogo" in t) and ("console" not in t and "bundle" not in t and "pack" not in t):
                 return "Jogo Genérico (Possível erro de categoria)"

            suffix = ""
            if any(x in t for x in ["spider-man", "god of war", "astro bot", "gran turismo", "fc 24", "fifa", "battlefield", "halo", "forza"]):
                suffix = " + Jogo/Bundle"

            if "switch" in t or "nintendo" in t:
                if "oled" in t:
                    return "Console Nintendo Switch OLED" + suffix
                elif "lite" in t:
                    return "Console Nintendo Switch Lite" + suffix
                else:
                    return "Console Nintendo Switch Standard" + suffix
            elif "xbox" in t:
                if "one" in t:
                    if "s" in t:
                        return "Console Xbox One S" + suffix
                    elif "x" in t:
                        return "Console Xbox One X" + suffix
                    return "Console Xbox One Standard" + suffix
                elif "series" in t:
                    if " s" in t:
                        return "Console Xbox Series S" + suffix
                    return "Console Xbox Series X" + suffix
                return "Console Xbox Genérico" + suffix
            elif "pro" in t:
                return "Console PlayStation 5 PRO" + suffix
            elif "slim" in t:
                if "digital" in t or "edição digital" in t or "disk" not in t and "disco" not in t:
                    return "Console PlayStation 5 Slim Digital" + suffix
                return "Console PlayStation 5 Slim Standard (Disco)" + suffix
            elif "digital" in t or "edição digital" in t:
                return "Console PlayStation 5 Base Digital" + suffix
            else:
                return "Console PlayStation 5 Standard (Base/Fat)" + suffix
                
        elif category == "Controles":
            if "joy-con" in t or "joycon" in t:
                return "Controle Nintendo Joy-Con"
            elif "pro controller" in t or "switch pro" in t or ("pro" in t and ("nintendo" in t or "switch" in t)):
                return "Controle Nintendo Switch Pro"
            elif "edge" in t or ("pro " in t and "playstation" in t):
                return "Controle DualSense Edge (Pro)"
            elif "hori" in t or "luta" in t:
                return "Controle Fightpad Hori ALPHA"
            elif "dualsense" in t or "controle" in t:
                return "Controle DualSense Padrão"
            else:
                return "Controle Genérico"

        elif category == "Volantes":
            if "g29" in t:
                return "Volante Logitech G29"
            elif "g923" in t:
                return "Volante Logitech G923"
            elif "direct drive" in t or "g pro" in t or "pro wheel" in t:
                return "Volante Logitech G PRO Direct Drive"
            else:
                return "Volante Genérico"

        elif category == "Headsets & Áudio":
            if "g pro x 2" in t:
                return "Headset Logitech G PRO X 2"
            elif "g435" in t:
                return "Headset Logitech G435"
            else:
                return "Headset/Fones Diversos"

        elif category == "Acessórios & Hardware":
            if "portal" in t:
                return "PlayStation Portal"
            elif "vr2" in t:
                return "PlayStation VR2"
            elif "unidade de disco" in t or "drive" in t.replace("direct drive", ""):
                return "Leitor de Disco Avulso PS5"
            elif "base de carregamento" in t or "carregador" in t:
                return "Base de Carregamento DualSense"
            elif "cabo" in t or "cable" in t:
                return "Cabo HDMI / USB"
            elif "ssd" in t or "firecuda" in t:
                return "SSD Interno M.2"
            elif "suporte" in t:
                return "Suporte Vertical Console"
            else:
                return "Acessório Genérico"
                
        elif category == "Jogos":
            # Jogos não têm variação de hardware, mas podemos agrupar jogos iguais
            if "mario" in t:
                return "Jogo: Franquia Super Mario"
            elif "zelda" in t:
                return "Jogo: The Legend of Zelda"
            elif "pokémon" in t or "pokemon" in t:
                return "Jogo: Franquia Pokémon"
            elif "spider-man" in t:
                return "Jogo: Marvel's Spider-Man 2"
            elif "gran turismo" in t:
                return "Jogo: Gran Turismo 7"
            elif "ghost of" in t:
                return "Jogo: Ghost of Tsushima/Yōtei"
            elif "resident evil" in t:
                return "Jogo: Resident Evil"
            elif "pragmata" in t:
                return "Jogo: Pragmata"
            elif "mega man" in t:
                return "Jogo: Mega Man Collection"
            elif "ea sports" in t or "fc" in t:
                return "Jogo: EA Sports FC"
            elif "halo" in t:
                return "Jogo: Halo"
            elif "forza" in t:
                return "Jogo: Forza Horizon/Motorsport"
            else:
                return "Jogo Genérico"
                
        return f"Outros: {title[:30]}"

    @staticmethod
    def parse_price(price_text: str) -> float:
        """
        Trata e converte a string BRL (ex: 'R$ 4.199,90') para float '4199.90'.
        """
        if not price_text or "sem" in price_text.lower() or "erro" in price_text.lower():
            return 0.0
        
        clean = re.sub(r'[^\d.,]', '', price_text)
        if not clean:
            return 0.0
            
        clean = clean.replace('.', '')
        clean = clean.replace(',', '.')
        
        try:
            return float(clean)
        except ValueError:
            return 0.0
