import time
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def scrape_data():
    # 連接資料庫
    conn = sqlite3.connect("quotes.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS quotes")  # 每次執行先清空，避免重複
    # 建立資料表
    cursor.execute(
        """
        CREATE TABLE quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            author TEXT NOT NULL,
            tags TEXT
        )
    """
    )

    # 設定 Selenium (無頭模式)
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    # 開始爬取
    url = "http://quotes.toscrape.com/js/"
    driver.get(url)
    # 設定迴圈爬取第 1 頁到第 5 頁
    for page in range(1, 6):
        print(f"正在爬取第 {page} 頁...")
        time.sleep(2)  # 等待載入
        # 抓取該頁面上所有 class 為 "quote" 的區塊
        quotes = driver.find_elements(By.CLASS_NAME, "quote")
        for q in quotes:
            # 抓取名言內容，並用 .strip('“ ”') 去除前後的特殊引號符號
            text = q.find_element(By.CLASS_NAME, "text").text.strip("“ ”")
            author = q.find_element(By.CLASS_NAME, "author").text  # 抓取作者
            tags_list = [
                t.text for t in q.find_elements(By.CLASS_NAME, "tag")
            ]  # 抓標籤
            tags = ", ".join(tags_list)
            # 將資料插入資料庫
            cursor.execute(
                "INSERT INTO quotes (text, author, tags) VALUES (?, ?, ?)",
                (text, author, tags),
            )

        conn.commit()  # 資料堤交

        # 頁數小於5時，點擊「下一頁」
        if page < 5:
            try:
                # 定位「下一頁」的按鈕 (CSS 選擇器：li 標籤下的 next class 中的 a 連結)
                next_btn = driver.find_element(By.CSS_SELECTOR, "li.next > a")
                next_btn.click()
            except:
                print("找不到下一頁按鈕，停止爬取。")
                break

    driver.quit()  # 關閉瀏覽器
    conn.close()  # 關閉資料庫連線
    print("爬取完成，資料已存入 quotes.db")


if __name__ == "__main__":
    scrape_data()
