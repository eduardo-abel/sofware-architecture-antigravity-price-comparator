from dataclasses import dataclass

@dataclass
class Product:
    title: str
    url: str
    price_text: str
    category: str
    image_url: str = ""
    monitor_hash: str = ""

@dataclass
class PriceVariant:
    base_model: str
    price_value: float
    original_title: str
    url: str
    image_url: str = ""
    monitor_hash: str = ""

