
title = "console playstation 5".lower()
price_val = 4235.30
is_accessory = False

accessory_keywords = ["volante", "pedais", "driving force", "g923", "g29", "headset", "fone", "áudio", "drive", "unidade de disco", "station", "estação", "cooler", "ventilador", "suporte", "base", "case", "estojo", "película", "capa", "skin", "fonte", "power supply", "cabo", "cable"]

for x in accessory_keywords:
    if x in title:
        print(f"MATCHED: {x}")

if is_accessory or any(x in title for x in accessory_keywords):
    print("MATCHED ACCESSORY")
elif (price_val > 900 and any(x in title for x in ["ps5", "playstation 5", "playstation®5", "xbox series", "xbox one", "switch", "nintendo"])) or \
     any(x in title for x in ["console", "pacote", "bundle", "pack", "slim", "pro edition"]):
    print("MATCHED CONSOLE")
else:
    print("MATCHED OTHER")
