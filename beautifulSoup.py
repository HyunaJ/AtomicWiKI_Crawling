import requests
from bs4 import BeautifulSoup
import csv
import time

def get_page_content(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, 'html.parser')

def crawl_document(doc_url):
    doc_soup = get_page_content(doc_url)
    
    title = doc_soup.select_one('h1#firstHeading').text.strip()
    content = doc_soup.select_one('div#mw-content-text').text.strip()
    
    images = []
    for img in doc_soup.select('div#mw-content-text img'):
        if img.get('src'):
            img_url = f"https://atomic.snu.ac.kr{img['src']}"
            images.append(img_url)
    
    return {
        'title': title,
        'content': content,
        'url': doc_url,
        'images': images
    }

def crawl_atomic_wiki(start_url):
    documents = []
    current_url = start_url
    
    while current_url:
        print(f"Crawling page: {current_url}")
        soup = get_page_content(current_url)
        
        # 문서 링크 추출
        links = soup.select('ul.mw-allpages-chunk li a')
        
        for link in links:
            doc_url = f"https://atomic.snu.ac.kr{link['href']}"
            doc_info = crawl_document(doc_url)
            documents.append(doc_info)
            print(f"Crawled: {doc_info['title']}")
            time.sleep(1)  # 서버 부하를 줄이기 위한 딜레이
        
        # 다음 페이지 링크 찾기
        next_link = soup.select_one('a:contains("다음 문서")')
        if next_link:
            current_url = f"https://atomic.snu.ac.kr{next_link['href']}"
        else:
            current_url = None
        
        time.sleep(2)  # 페이지 간 딜레이
    
    return documents

# 크롤링 실행
start_url = "https://atomic.snu.ac.kr/index.php?title=%ED%8A%B9%EC%88%98:%EB%AA%A8%EB%93%A0%EB%AC%B8%EC%84%9C&from=%EA%B8%B0%EC%A4%80%EC%9D%B8"
crawled_data = crawl_atomic_wiki(start_url)
# CSV 파일로 저장
with open('atomic_wiki_data02.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['title', 'content', 'url', 'images'])
    writer.writeheader()
    for doc in crawled_data:
        writer.writerow({
            'title': doc['title'],
            'content': doc['content'],
            'url': doc['url'],
            'images': ','.join(doc['images'])
        })

print(f"크롤링 완료. 총 {len(crawled_data)}개의 문서가 'atomic_wiki_data.csv' 파일로 저장되었습니다.")
