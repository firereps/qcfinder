# backend.py (Wersja 10 - Gotowa na wdrożenie na serwer Render)

import re
import os # Dodajemy bibliotekę os
from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)
CORS(app)

# ... (cała reszta kodu od get_product_info do końca find_qc_endpoint pozostaje bez zmian)
def get_product_info(url):
    product_id = None
    platform = None
    id_match = re.search(r'\d{10,19}', url)
    if id_match: product_id = id_match.group(0)
    if '1688.com' in url: platform = 'ali1688'
    elif 'weidian.com' in url: platform = 'weidian'
    elif 'taobao.com' in url: platform = 'taobao'
    elif 'tmall.com' in url: platform = 'tmall'
    return platform, product_id

@app.route('/find_qc', methods=['POST'])
def find_qc_endpoint():
    agent_url = request.json.get('product_url')
    print(f"Otrzymano zapytanie dla: {agent_url}")
    if not agent_url: return jsonify({"error": "Brak linku"}), 400

    guessed_platform, product_id = get_product_info(agent_url)
    if not product_id: return jsonify({"images": [], "error": "Nie znaleziono ID produktu."})

    print(f"Znaleziono ID: {product_id}, Zgadnięta platforma: {guessed_platform}")

    platforms_to_check = []
    if guessed_platform: platforms_to_check.append(guessed_platform)
    for p in ['weidian', 'taobao', 'ali1688', 'tmall']:
        if p not in platforms_to_check: platforms_to_check.append(p)
    print(f"Kolejność sprawdzania platform: {platforms_to_check}")

    image_urls = []
    options = webdriver.ChromeOptions()
    # Ważne: Render sam sobie radzi ze ścieżkami, nie potrzebujemy Brave
    # Użyjemy domyślnego Chrome'a, który jest na serwerze Render
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage') # To jest BARDZO ważne na serwerach
    options.add_argument('log-level=3')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    try:
        with webdriver.Chrome(options=options) as driver:
            for platform in platforms_to_check:
                if image_urls: break
                qc_search_url = f"https://finds.ly/product/{platform}/{product_id}"
                print(f"Próbuję otworzyć: {qc_search_url}")

                try:
                    driver.get(qc_search_url)
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".grid-container img"))
                    )
                    
                    print("  -> Strona i zdjęcia załadowane. Pobieram linki...")
                    gallery_images = driver.find_elements(By.CSS_SELECTOR, ".grid-container img")
                    
                    for img_tag in gallery_images:
                        src = img_tag.get_attribute('src')
                        if src: image_urls.append(src)
                    
                    print(f"  ✅ Znaleziono {len(image_urls)} zdjęć na platformie {platform}!")
                except Exception as e:
                    print(f"  -> Nie znaleziono zdjęć na {platform} w ciągu 30 sekund lub wystąpił inny błąd.")
                    continue
    except Exception as e:
        print(f"KRYTYCZNY BŁĄD podczas działania Selenium: {e}")
        return jsonify({"images": [], "error": str(e)})

    print(f"Zakończono. Znaleziono łącznie {len(image_urls)} zdjęć.")
    return jsonify({"images": image_urls})

# ========================================================================
# ===== ZMIANA NA POTRZEBY SERWERA RENDER ================================
# ========================================================================
if __name__ == '__main__':
    # To jest potrzebne, żeby Render wiedział, na jakim porcie ma działać
    port = int(os.environ.get('PORT', 5000))
    # Uruchamiamy aplikację w trybie produkcyjnym
    app.run(host='0.0.0.0', port=port)
# ========================================================================