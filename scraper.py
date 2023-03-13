import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from tqdm import tqdm
import os

MAIN_PAGE_RESULT_FILE = 'Year_link.json'
ACCIDENT_FILE = 'Date_target.json'

class PlaneCrashScraper:
    """
    A class to encapsulate the plane crash web scraper.
    
    Attributes:
        url: The url of the main page
        base_url: The URL of the base page. Since the links used are for relative pages, the base URL is used.
        year_link_mapping: A dictionary with the year as key and the corresponding link as the value.
        links_by_year: A dictionary with the full date as key and the target website (specific accident) as the value.
    """
    
    def __init__(self):
        self.url = 'http://www.planecrashinfo.com/database.htm'
        self.base_url = 'http://www.planecrashinfo.com'
        # Check if the required JSON files exist. If they do, read them directly instead of using scraping.
        if os.path.isfile(MAIN_PAGE_RESULT_FILE):
            self.main_page_results_exist = True
            with open(MAIN_PAGE_RESULT_FILE, 'r') as file:
                self.year_link_mapping = json.load(file)
        else:
            self.main_page_results_exist = False
            self.year_link_mapping = dict()
        
        if os.path.isfile(ACCIDENT_FILE):
            self.target_file_exist = True
            with open(ACCIDENT_FILE, 'r') as file:
                self.links_by_year = json.load(file)
        else:
            self.target_file_exist = False
            self.links_by_year = dict()
        
    def scrape_main_page(self):
        response = requests.get(self.url)
        content = response.content
        soup = BeautifulSoup(content, 'lxml')
        
        if self.main_page_results_exist:
            print(f'{MAIN_PAGE_RESULT_FILE} exists. Scraping was aborted.')
            return

        links = soup.find_all('a')
        for link in links:
            link_text = link.text.strip()
            # Check if the link text can be converted into an integer. If it is, then it is a valid link.
            try:
                link_text = int(link_text)
            except ValueError:
                continue
            relative_link = link.attrs['href']
            # Check if the relative_link starts with /. If not, add the slash at the beginning.
            if not relative_link.startswith('/'):
                relative_link = f'/{relative_link}'
            self.year_link_mapping[link_text] = f'{self.base_url}{relative_link}'
            
        with open('Year_link.json', 'w') as file:
            json.dump(self.year_link_mapping, file)
            
    def _get_soup(self, url):
        response = requests.get(url)
        content = response.content
        soup = BeautifulSoup(content, 'lxml')
        
        return soup
            
    def scrape_accident_list(self) -> None:
        """
        For a given year, form a dictionary containing the link text as key and the link itself as the value.
        """
        if self.target_file_exist:
            print(f'{ACCIDENT_FILE} exists. Scraping was aborted.')
            return
        
        for year, link in tqdm(self.year_link_mapping.items()):
            soup = self._get_soup(link)
            
            table = soup.find('table')
            
            for link in table.find_all('a'):
                link_text = link.text.strip()
                relative_link = link.attrs['href']
                self.links_by_year[link_text] = f'{self.base_url}/{year}/{relative_link}'
            
        with open('Date_target.json', 'w') as file:
            json.dump(self.links_by_year, file)
            
    def get_all_accident_information(self):
        df_final = pd.DataFrame()
        for _, link in tqdm(self.links_by_year.items()):
            df = pd.read_html(link, skiprows=1)[0].T
            # Convert the first row to header. 
            df.columns = df.iloc[0]
            # Ignore the first row, as it is now the header.
            df = df.iloc[1:]
            df_final = pd.concat([df, df_final], ignore_index=True)
            
        df_final.to_csv('Result_file.csv', index=False)
        df_final.to_parquet('Result_file_compressed.parquet', index=False)


if __name__ == '__main__':
    obj = PlaneCrashScraper()
    obj.scrape_main_page()
    obj.scrape_accident_list()
    obj.get_all_accident_information()