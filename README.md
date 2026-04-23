# 🕹️ Antigravity Price Comparator

Um rastreador e comparador de preços inteligente para consolas, jogos e acessórios, construído com **Arquitetura Hexagonal** e **CQRS**. O sistema utiliza **Playwright** para capturar ofertas dinâmicas da Amazon com base em uma lista customizada de monitoramento.

---

## 🚀 Como Rodar o Projeto

### 1. Requisitos e Ambiente
- **Python 3.x** instalado.
- Ambiente virtual configurado:
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  pip install playwright pandas
  playwright install chromium
  ```

### 2. Fluxo de Execução (Novo Pipeline Playwright)

O sistema agora permite monitorar produtos específicos via CSV:

1. **Configuração da Lista:** Edite o arquivo `products_to_monitor.csv` com os produtos exatos que deseja rastrear.
   
2. **Captura Inteligente (Playwright):** O scraper percorre o CSV, busca na Amazon e identifica automaticamente a oferta mais barata para cada item, gerando um hash único de referência.
   ```bash
   python scraper_playwright.py
   ```

3. **Geração de Histórico:** Salva os resultados no banco SQLite para análise temporal.
   ```bash
   python main.py
   ```

### 3. Visualização

*   **Dashboard Web (Recomendado):** `python presentation/web_dashboard/app.py` -> `http://localhost:8080`
*   **Dashboard CLI:** `python presentation/cli_dashboard.py`

---

## 📂 Estrutura de Dados
- `products_to_monitor.csv`: Lista de entrada (ID, Busca, Categoria, Preço Mínimo).
- `amazon_products_playwright.json`: Resultado da captura dinâmica.
- `amazon_offers_history.db`: Banco de dados temporal (SQLite).
- `monitor_hash`: Identificador único no JSON que linka o produto capturado ao item do seu CSV.

