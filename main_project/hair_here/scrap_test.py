import requests
from bs4 import BeautifulSoup

# 타겟 URL을 읽어서 HTML를 받아오고,
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query=%EC%84%9C%EC%9A%B8+%EB%AF%B8%EC%9A%A9%EC%8B%A4+&oquery=%EC%84%9C%EC%9A%B8+%EB%AF%B8%EC%9A%A9%EC%8B%A4+%EB%A6%AC%EC%8A%A4%ED%8A%B8&tqi=UHqh9dp0Jy0ss5JN4MNssssst8l-050573',headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

#_business_1700494654 > div > div > div.tit > span > a > span

hair_shops = soup.select('li > div > div')

for hair_shop in hair_shops:
    # movie 안에 a 가 있으면,
    a_tag = hair_shop.select_one('div.tit > span > a > span')


    if a_tag is not None:
        print(a_tag.text)



