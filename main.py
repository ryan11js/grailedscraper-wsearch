from selenium import webdriver
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import msvcrt
import os
from termcolor import colored
import pyfiglet

## global options for webscraping:
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})


class Grailed():
    def __init__(self, options, category=None):
        self.options = options
        self.category_init()
        self.category = category

    def category_init(self):
        try:
            self.ItemDF = pd.read_excel('categories.xlsx')
        except:
            self.category_scrape()

    def category_scrape(self):
        category_url = "https://www.grailed.com/designers/"

        # options.add_experimental_option("detach", True)

        driver = webdriver.Chrome("C:\\Users\\ripco\\chromedriver\\chromedriver.exe", options=self.options)
        driver.get(category_url)

        timeout = 30

        # this code below was from
        # https://medium.com/analytics-vidhya/web-scraping-sold-clothing-on-grailed-with-selenium-2514cbe6855e
        # to help organize data and get past timeout errors

        try:
            WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((
                By.XPATH,
                "//body"
            )))
        except TimeoutException:
            print("Timed out")
            driver.quit()


        # get all links on designer page
        categories = driver.find_elements(By.XPATH, "//div[@class='designers']")
        Name = []
        Link = []
        Count = []
        for i, category in enumerate(categories):
            results = category.find_elements(By.XPATH, "./div/a[@class='designer']")
            for result in results:
                try:
                    childs = result.find_elements(By.XPATH, "./child::*")
                    count = int(childs[1].get_attribute("innerHTML").strip("()"))
                    Count.append(count)
                    link = result.get_attribute("href")  # grabbing the link href
                    Link.append(link)
                    name = childs[0].get_attribute("innerHTML")
                    Name.append(name)

                except:
                    pass
            print(str(round((i+1)/len(categories)*100)) + "% done")
        print('Finished!')

        # Turn the Links into a DataFrame
        self.ItemDF = pd.DataFrame(list(zip(Name, Link, Count)), columns=['Name', 'Link', 'Count'])

        #store as xlsx to use for optimization
        self.ItemDF.to_excel('categories.xlsx', index=False)

    def grailed_scrape(self):
        driver = webdriver.Chrome("C:\\Users\\ripco\\chromedriver\\chromedriver.exe", options=self.options)
        if self.category is not None:
            category_link = self.ItemDF.loc[self.ItemDF['Name'] == self.category, 'Link'].iloc[0]
            driver.get(category_link)

            timeout = 30

            # this code below was from to get past timeouts
            # https://medium.com/analytics-vidhya/web-scraping-sold-clothing-on-grailed-with-selenium-2514cbe6855e

            try:
                WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='feed']")))
            except TimeoutException:
                print("Timed out")
                driver.quit()

            listings = driver.find_elements(By.XPATH, "//div[@class='feed-item']")
            for listing in listings:
                texts = listing.find_elements(By.XPATH, "./p")
                [print(p.text, p.get_attribute('class')) for p in texts]

class StockX():
    def __init__(self, options, keywords):
        self.options = options
        self.keywords = keywords
        self.toStockXlink()
        self.getPrice()

    def toStockXlink(self):
        self.links = []
        for keyword in self.keywords:
            term = 'https://stockx.com/search?s='
            for char in keyword:
                if char != ' ':
                    term += char.lower()
                else:
                    term += "%20"
            self.links.append(term)

    def getPrice(self):
        driver = webdriver.Chrome("C:\\Users\\ripco\\chromedriver\\chromedriver.exe", options=self.options)
        self.prices = []
        # for link in self.links:
        driver.get(self.links[0])



def search(df):
    junk = msvcrt.getch()
    search_term = []
    searching = True
    downkey = 0
    var = ''
    print('Search Here:')
    while searching:
        if msvcrt.kbhit():
            keypress = msvcrt.getch()
            if keypress == b'\x00':
                keypress = msvcrt.getch()
                if keypress == b'P' and len(search_term) > 1 and downkey < 4:
                    downkey += 1
            if keypress == b'\x08':
                if downkey == 0:
                    try:
                        search_term.pop()
                    except:
                        print("\nNoGO")
                        pass

            elif keypress == b'\r':
                searching = False
                if downkey != 0:
                    search_term = var
                continue

            elif ord(keypress.decode('utf-8').lower()) in range(97, 123):
                search_term.append(keypress.decode("utf-8"))

            os.system('cls')
            print('Search Here:')

            if downkey == 0:
                tempterm = ''.join(search_term)
                print(tempterm)
            else:
                var = autofill(tempterm, df, downkey=downkey-1)
                print(var)

            if len(tempterm) > 1:
                af = autofill(tempterm, df)
                for i in range(4):
                    try:
                        print(af[i])
                    except:
                        pass

    return search_term


def autofill(search_term, df, count=3000, downkey=-1):
    result = df.loc[(df['Name'].str.contains(search_term, case=False, na=False)) & (df['Count'] > count), ['Name']]
    if downkey >= 0:
        return result['Name'].values.tolist()[downkey]
    else:
        return result['Name'].values.tolist()


def titleScreen():
    os.system('cls')
    title = [line for line in pyfiglet.figlet_format("Welcome", font="basic").splitlines() if len(line.strip()) > 1]
    [print(line) for line in title]
    time.sleep(5)
    os.system('cls')
    for l in range(len(title)):
        for i, line in enumerate(title):
            if i - l >= 0:
                print(line)
        time.sleep(0.2)
        os.system('cls')
    time.sleep(1)


def main():
    titleScreen()
    decision = input("Press r to refresh listings. Press any other key to continue: ")
    grailed = Grailed(options)
    if decision == 'r':
        grailed.category_scrape()
    df = grailed.ItemDF
    grailed.category = search(df)
    print(df.loc[df['Name'].str.contains(grailed.category, case=False, na=False), :])

if __name__ == '__main__':
    main()
