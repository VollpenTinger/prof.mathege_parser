import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
import csv

def download_images(url, download_folder='images'):
    # Create folder for downloads
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    counter = 0

    # get HTML-content
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # search main div container
    div_container = soup.find_all('div', class_='task')
    downloaded_count = 0
    
    for el in div_container:
        # get img url
        img_url = el.find('div', class_='contentTask').find('img').get('src')

        if not img_url:
            continue

        # converting a relative url an absolute
        img_url = urljoin(url, img_url)

        # get filename from mathege db
        parsed_name = filename = el.find('div', class_='titleTask').find('p').text[2:-15]
        # full path for save
        filepath = os.path.join(download_folder, filename + '.jpg')
        counter +=1
 
        record = {
            'local_num': counter, 
            'bank_num': parsed_name, 
            'answer':get_answer(parsed_name),
            'category':category
        }
        print(record)
        answers.append(record)

        try:
            #download images
            img_data = requests.get(img_url, headers=headers).content
            with open(filepath, 'wb') as f:
                f.write(img_data)
            downloaded_count += 1
            print(f'Downloaded: {filename}')
        except Exception as e:
            print(f'Error downloading {img_url}: {str(e)}')

    print(f'\nTotal images downloaded: {downloaded_count}')

def get_answer(bank_num):
    url = 'https://ege.sdamgia.ru/problem?id=' + bank_num
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    try:
        answer_container = soup.find('div', id='sol'+ bank_num)
        answer_span = answer_container.find('span', string=lambda text: text and 'Ответ:' in text)
        answer = answer_span.next_sibling.text[1:]
        if answer.endswith('.'):
            answer = answer[:-1]
        return answer
        
    except Exception as e:
        answer_container = soup.find('div', class_='answer')
        answer = answer_container.find('span').text[7:]
        if answer.endswith('.'):
            answer = answer[:-1]
        return answer

def save_csv(answers, filename='answers.csv'):
    if not answers:
        print('no answer for create csv')
        return
    fieldnames = answers[0].keys()
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(answers)
    
    print(f"Данные сохранены в {filename}")

if __name__ == '__main__':
    # add browser headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    answers = []

    url = input('Enter url mathege site: ')
    category = input('Enter variant number(1-12):')
    download_images(url)
    save_csv(answers)