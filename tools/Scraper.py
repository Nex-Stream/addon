from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

# Imposta le opzioni per eseguire il browser in modalità headless
chrome_options = Options()
chrome_options.add_argument("--headless")  # Esegui senza aprire una finestra del browser
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Crea un driver per Chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# URL del sito da cui fare scraping
url = 'https://www.animesaturn.cx'

# Vai al sito
driver.get(url)

# Attendi che la pagina si carichi completamente
time.sleep(3)  # Puoi regolare il tempo di attesa in base alla velocità della pagina

# Trova gli elementi di interesse (modifica in base alla struttura del sito)
# Ad esempio, qui stiamo cercando tutti gli <h2> che potrebbero essere titoli degli anime
titles = driver.find_elements(By.TAG_NAME, 'h2')

# Scrivi i titoli in un file di testo
with open('scraped_results.txt', 'w', encoding='utf-8') as file:
    for title in titles:
        file.write(title.text + '\n')

# Chiudi il browser
driver.quit()

print("Scraping completato e risultati scritti su 'scraped_results.txt'.")
