import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException

# --- Настройки ---
SEARCH_QUERY = "microfiber bed sheet set"
OUTPUT_FILE = "suppliers.csv"
MINIMUM_YEARS_ON_ALIBABA = 3

# --- Основная логика ---
def scrape_suppliers():
    """
    Основная функция для скрапинга и фильтрации поставщиков с Alibaba.
    """
    service = Service()
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Раскомментируйте для запуска в фоновом режиме
    driver = webdriver.Chrome(service=service, options=options)

    print(f"Начинаю поиск по запросу: '{SEARCH_QUERY}'...")
    url = f"https://www.alibaba.com/trade/search?fsb=y&q={SEARCH_QUERY.replace(' ', '+')}"
    driver.get(url)
    time.sleep(5)  # Даем странице время на загрузку

    # Прокручиваем страницу вниз, чтобы загрузить больше результатов
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    suppliers_data = []
    
    # Примечание: селекторы Alibaba могут меняться. Этот селектор актуален на момент написания.
    supplier_cards = driver.find_elements(By.CSS_SELECTOR, "div.fy23-search-card")

    print(f"Найдено {len(supplier_cards)} потенциальных поставщиков. Начинаю фильтрацию...")

    for card in supplier_cards:
        try:
            # 1. Проверяем наличие "Verified"
            card.find_element(By.CSS_SELECTOR, "div.fy23-search-card-verified-supplier")
            
            # 2. Проверяем наличие "Trade Assurance"
            card.find_element(By.CSS_SELECTOR, "div.fy23-search-card-company-assurance-icons")

            # 3. Получаем имя и ссылку
            name_element = card.find_element(By.CSS_SELECTOR, "h2.fy23-search-card-title")
            name = name_element.text
            link = card.find_element(By.CSS_SELECTOR, "a.search-card-e-title-link").get_attribute('href')

            # 4. Получаем количество лет на платформе
            years_text = card.find_element(By.CSS_SELECTOR, "div.fy23-search-card-company-year-icon > span").text
            years = int(''.join(filter(str.isdigit, years_text)))

            # 5. Фильтруем по количеству лет
            if years >= MINIMUM_YEARS_ON_ALIBABA:
                suppliers_data.append({
                    "name": name,
                    "years_on_alibaba": years,
                    "link": link
                })
                print(f"  [+] Добавлен: {name} ({years} лет)")
            else:
                print(f"  [-] Пропущен (мало опыта): {name} ({years} лет)")

        except NoSuchElementException:
            # Пропускаем карточки, которые не соответствуют критериям (например, без "Verified")
            continue
        except Exception as e:
            print(f"Произошла ошибка при обработке карточки: {e}")

    driver.quit()

    # --- Сохранение в CSV ---
    if suppliers_data:
        print(f"\nНайдено {len(suppliers_data)} подходящих поставщиков. Сохраняю в {OUTPUT_FILE}...")
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'years_on_alibaba', 'link']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(suppliers_data)
        print("Готово!")
    else:
        print("Подходящих поставщиков не найдено.")

if __name__ == "__main__":
    scrape_suppliers()
