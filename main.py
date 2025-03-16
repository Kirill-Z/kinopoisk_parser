import re
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

def _convert_to_yyyy_mm_dd(date: str) -> str:
    if date == "Не найдено":
        return date
    date_part = date.split(",")[0]
    date_obj = datetime.strptime(date_part, "%d.%m.%Y")
    return date_obj.strftime("%Y-%m-%d")

# Настройка Selenium
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
base_url = "https://www.kinopoisk.ru/user/32108041/votes/list/vs/novote/page/{}/#list"
first_page_url = "https://www.kinopoisk.ru/user/32108041/votes/list/vs/novote/perpage/200/#list"
all_items = []

login_url = "https://passport.yandex.ru/auth?origin=kinopoisk&retpath=https%3A%2F%2Fsso.passport.yandex.ru%2Fpush%3Fretpath%3Dhttps%253A%252F%252Fwww.kinopoisk.ru%252Fapi%252Fprofile-pending%252F%253Fretpath%253Dhttps%25253A%25252F%25252Fwww.kinopoisk.ru%25252Fuser%25252F32108041%25252Fvotes%25252Flist%25252Fvs%25252Fnovote%25252Fperpage%25252F200%25252F%26uuid%3D9c03ad32-110d-49e8-a0ef-139cdd88a0e0%26reason%3Dlogin%26session-status%3D"
driver.get(login_url)
print("Войди в аккаунт в открывшемся окне (введи логин и пароль)...")
time.sleep(60)
time.sleep(3)

soup = BeautifulSoup(driver.page_source, 'html.parser')
navigator = soup.find('div', class_='navigator')
if navigator:
    pagination = navigator.find('ul', class_='list')
    if pagination:
        last_page_link = pagination.find_all('li')[-1].find('a')
        last_page_url = last_page_link['href']
        last_page_num = int(last_page_url.split('/page/')[1].split('/')[0])
    else:
        last_page_num = 1
else:
    last_page_num = 1

print(last_page_url)
for page in range(1, last_page_num + 1):
    if page == 1:
        pass
    else:
        url = base_url.format(page)
        driver.get(url)
        time.sleep(3)
        print(url)

    if "captcha" in driver.current_url.lower():
        print(f"CAPTCHA на странице {page}, требуется ручное прохождение...")
        time.sleep(30)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    items = soup.find_all("div", class_="item")

    if not items:
        print(f"Страница {page} пуста или недоступна, завершаем")
        break
    all_items.extend(items)

for item in all_items:
    num = item.find('div', class_='num')
    name_rus = item.find('div', class_='nameRus')
    name_eng = item.find("div", class_="nameEng")
    date = item.find("div", class_="date")

    num_text = num.text.strip() if num else "Не найдено"
    name_rus_text = name_rus.text.strip() if name_rus else "Не найдено"
    name_eng_text = name_eng.text.strip() if name_eng else "Не найдено"
    date_text = date.text.strip() if date else "Не найдено"
    date_text = _convert_to_yyyy_mm_dd(date_text)

    year_match = re.search(r'\((\d{4})(?:\s*–\s*\d{4})?\)', name_rus_text)
    year = year_match.group(1) if year_match else "Не найдено"

    print(f"Номер:", {num_text})
    print(f"Название: {name_rus_text}")
    print(f"Англ. Название: {name_eng_text}")
    print(f"Год: {year}")
    print(f"Дата просмотра: {date_text}")
    print("-" * 50)

driver.quit()
