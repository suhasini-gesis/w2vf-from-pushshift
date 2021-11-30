from selenium import webdriver
from selenium.webdriver.common.by import By
from dateutil import parser
from pathlib import Path
from datetime import datetime
import bz2
import os
import time
import json
import csv
import re

def set_driver_options():

    '''
    Function to set the options for the chrome web driver
    '''
    
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--incognito")
    # Downloading the files didnt seem to happen in the headless browser
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    return options

def download_files(url):

    '''
    Function to download all the files created/modified between the year 2015 to 2020 
    
    Args : 
        url: url of the website from where the files are downloaded
    '''
    
    options = set_driver_options()
    driver = webdriver.Chrome(options=options, executable_path=r'chromedriver.exe')
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.get(url)
    rows = driver.find_elements_by_class_name("file")
    for row in rows[:31]:
        column = row.find_elements(By.TAG_NAME, "td")[3]
        year = parser.parse(column.text).year
        if year >= 2015 or year <= 2020:
            column.click()
    driver.close()
    
def decompress_files():
    
    '''
    Function to decompress all the downloaded files. 
    The function converts the files in 3 types of formats: bz2, xz, zst, to txt format
    '''
    
    folder_path = str(Path.home() / "Downloads")
    fileList = os.listdir(folder_path)  

    for file_name in fileList:
        if(file_name.endswith('.bz2')):
            newfilepath = os.path.join(folder_path, (file_name[:len(file_name) - 4]+"_decompressed"+".txt"))
            filepath = os.path.join(folder_path, file_name)
            with open(newfilepath, 'wb') as new_file, open(filepath, 'rb') as file:
                decompressor = bz2.BZ2Decompressor()
                for data in iter(lambda : file.read(100 * 1024), b''):
                    new_file.write(decompressor.decompress(data))
                    new_file.write('\n'.encode())
                    
def decompressed_data_to_csv():
    
    '''
    Function reads all the decompressed files in txt format to extract particular information to a csv format.
    '''
    
    folder_path = str(Path.home() / "Downloads")
    fileList = os.listdir(folder_path)
    csv_file_name = os.path.join(folder_path, "subreddit_author_created.csv")
    with open(csv_file_name, 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        header = ['Author', 'Subreddit', 'Created_utc']
        writer.writerow(header)
        for file_name in fileList:
            if(file_name.endswith('decompressed.txt')): 
                text_file_name = os.path.join(folder_path, file_name)
                text_file = open(text_file_name, "r")
                lines = text_file.readlines()
                del lines[0]
                for line in lines:
                    try:
                        d = json.loads(line)
                        data = [d['author'], d['subreddit'], d['created_utc']]
                        writer.writerow(data)
                    except:
                        pass
    
def delete_files():
    
    '''
    Function deletes all the downloaded and decompressed files.
    '''
    
    folder_path = str(Path.home() / "Downloads")
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.bz2') or file_name.endswith('.xz') or file_name.endswith('.zst') or file_name.endswith('.crdownload') or file_name.endswith('decompressed.txt'):
            file_path = os.path.join(folder_path, file_name)
            file_creation_date = time.strftime('%d/%m/%Y', time.localtime(os.path.getmtime(file_path)))
            current_date = datetime.today().strftime('%d/%m/%Y')
            if file_creation_date == current_date:
                os.remove(file_path)

if __name__ == '__main__':

    url = 'https://files.pushshift.io/reddit/comments/'
    download_files(url) 
    decompress_files()
    decompressed_data_to_csv()
    delete_files()
