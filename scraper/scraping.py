from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import time
import re


### Setting Up Chrome ###
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
chrome_options = webdriver.ChromeOptions()
# chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')  # for heroku
chrome_options.binary_location = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--window-size=1920,1080")

chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--proxy-server='direct://'")
chrome_options.add_argument("--proxy-bypass-list=*")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-gpu")

chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
# driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)  # for heroku
driver = webdriver.Chrome("C:/Users/benedict/Desktop/BEN-LEARNING/scraping/selenium-chrome91-driver/chromedriver.exe",
                          options=chrome_options)

# Nike
def nike_func(link='https://www.nike.com/id/w/mens-shoes-nik1zy7ok'):
    # Nike Normal Page
    driver.get(link)
    last_height = driver.execute_script('return document.body.scrollHeight')
    # Infinite Scrolling
    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        time.sleep(2)
        new_height = driver.execute_script('return document.body.scrollHeight')
        if new_height == last_height:
            break
        else:
            last_height = new_height

    soup = BeautifulSoup(driver.page_source, 'lxml')
    product_card = soup.find_all('div', class_='product-card__body')

    df_nike = pd.DataFrame({'Link': [], 'Name': [], 'Subtitle': [], 'Price': []})
    counter = 1

    for product in product_card:
        try:

            link = product.find('a', class_='product-card__link-overlay').get('href')
            name = product.find('div', class_='product-card__title').text.strip()
            subtitle = product.find('div', class_='product-card__subtitle').text.strip()
            full_price = product.find('div', class_='product-price css-11s12ax is--current-price').text.strip()[
                         3:].replace(',', '')
            df_nike = df_nike.append({'Link': link, 'Name': name, 'Subtitle': subtitle, 'Price': int(full_price)},
                                     ignore_index=True)
            print(counter)
            counter += 1

        except:
            pass

    return df_nike


# Nike Sales
def nike_sale_func(link='https://www.nike.com/id/w/sale-3yaep'):
    # Nike Sale Page
    driver.get(link)
    last_height = driver.execute_script('return document.body.scrollHeight')
    # Infinite Scrolling
    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        time.sleep(2)
        new_height = driver.execute_script('return document.body.scrollHeight')
        if new_height == last_height:
            break
        else:
            last_height = new_height

    soup = BeautifulSoup(driver.page_source, 'lxml')
    product_card = soup.find_all('div', class_='product-card__body')

    df_nikeSales = pd.DataFrame({'Link': [], 'Name': [], 'Subtitle': [], 'Price': [], 'Sale_Price': []})
    counter = 1

    for product in product_card:
        try:
            link = product.find('a', class_='product-card__img-link-overlay').get('href')
            name = product.find('div', class_='product-card__title').text.strip()
            subtitle = product.find('div', class_='product-card__subtitle').text.strip()
            full_price = product.find('div', class_='product-price is--striked-out').text.strip().replace(' ', '')[
                         3:].replace(',', '')
            sale_price = product.find('div', class_='product-price is--current-price css-s56yt7').text.strip().replace(
                ' ', '')[3:].replace(',', '')
            df_nikeSales = df_nikeSales.append(
                {'Link': link, 'Name': name, 'Subtitle': subtitle, 'Price': int(full_price),
                 'Sale_Price': int(sale_price)}, ignore_index=True)

            print(counter)
            counter += 1
        except:
            pass

    # adding discount and reformatting
    df_nikeSales['Discount'] = round((df_nikeSales['Price'] - df_nikeSales['Sale_Price']) / df_nikeSales['Price'] * 100, 1)
    df_nikeSales.sort_values(['Discount'], ascending=False, inplace=True)
    df_nikeSales['Discount'] = df_nikeSales['Discount'].apply(lambda x: f"{x} %")
    df_nikeSales.reset_index(drop=True, inplace=True)
    return df_nikeSales


# Tokopedia
def tokopedia_func(link_web='https://www.tokopedia.com/search?st=product&q=gateron%20switch&navsource=home'):
    driver.get(link_web)
    df_tokopedia = pd.DataFrame(
        {'Link': [], 'Title': [], 'Price': [], 'Rating': [], 'Number_of_sold_items': [], 'Location': [], 'Seller': []})
    next_page = 2
    product_searched = link_web[46:-15]

    while True:
        # Auto scroll
        last_height = driver.execute_script("return document.body.scrollHeight")
        print("THIS IS LAST HEIGHT: ", last_height)
        while True:

            driver.execute_script('window.scrollTo(0, document.body.scrollHeight/2)')
            time.sleep(2)

            driver.execute_script('window.scrollTo(document.body.scrollHeight/2, document.body.scrollHeight)')
            time.sleep(2)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("THIS IS NEW HEIGHT: ", new_height)
                break
            else:
                last_height = new_height

        soup = BeautifulSoup(driver.page_source, 'lxml')
        contents = soup.find_all('div', class_='css-12sieg3')

        # next page validators
        next_button = soup.find('button', class_='css-1m1b4qs-unf-pagination-item e19tp72t3')
        div_product_not_found = soup.find('div', class_='css-849sqi')
        if (next_button == None) or (div_product_not_found != None):
            break

        for con in contents:
            try:
                link = con.find('a', class_='pcv3__info-content css-1qnnuob').get('href')
                title = con.find('div', class_='css-1f4mp12').text.strip()
                price = con.find('div', class_='css-rhd610').text.strip().replace('.', '')[2:]

                try:
                    rating = con.find('span', class_='css-etd83i').text.strip()
                except:
                    rating = '-'

                try:
                    items_sold = con.find('span', class_='css-1kgbcz0').text.strip()[8:]
                except:
                    items_sold = '-'

                location = con.find('div', class_='css-1rn0irl').find_all('span', class_='css-qjiozs flip')[0].text
                seller = con.find('div', class_='css-1rn0irl').find_all('span', class_='css-qjiozs flip')[1].text

                df_tokopedia = df_tokopedia.append({'Link': link, 'Title': title, 'Price': int(price), 'Rating': rating,
                                                    'Number_of_sold_items': items_sold, 'Location': location,
                                                    'Seller': seller},
                                                   ignore_index=True)
            except:
                pass

        try:
            driver.get(
                f"https://www.tokopedia.com/search?navsource=home&page={next_page}&q={product_searched}&st=product")
            next_page += 1
        except:
            break

        print(df_tokopedia)
    return df_tokopedia
