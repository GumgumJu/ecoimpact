import scrapy
from scrapy import Request
from scrapy_selenium import SeleniumRequest
from ..items import ScrapmeublesItem
from bs4 import BeautifulSoup
import json

class Spider(scrapy.Spider):
    name = 'ecode'
    start_urls = [
            "https://tres-ecodesign.com/collections/hubsch",
            "https://tres-ecodesign.com/collections/hubsch?page=2",
        ]
    
    
    def parse(self, response):
        ## scrapy all links of products
        all_urls = response.xpath('//a[@class="grid-item__link"]/@href').extract()
        for urls in all_urls:
            product_url = 'https://tres-ecodesign.com'+ urls
            yield scrapy.Request(url=product_url, callback= self.parse_category)
            # yield SeleniumRequest(url=urls, 
            #                       callback=self.parse_category,
            #                       wait_time= 5,
            #                       script="document.querySelector('span:contains(\"dimension\").click()'"
            #                       )

    def parse_category(self, response):
        catagory = ['Matériaux','Dimensions','Poids','Doit être assemblé',
                'Poids maximum sur l\'étagère','Distance entre les étagères',
                'Origine','Garantie','Conseils et entretien']
        
        product_name = response.css('h1').css('::text').extract()[0]

        ## extract the aim data from "Dimensions & Caractéristiques"
        all_text = response.css('div[class*="station-tabs"]').css('p').extract()[-9:-1]
        aim_text = [] 
        ## Extraire des données sur la base d'attributs
        for text in all_text:
            for feature in catagory:
                if feature in text:
                    aim_text.append(text)
                    break
        
        data_list = []
        unique_list = []

        ## Prétraitement des données <html to text>
        for html_text in aim_text:
            for feature in catagory:
                soup = BeautifulSoup(html_text, 'html.parser')
                strong_text = soup.find('strong').text.strip().replace('\xa0',"").replace(":","")
                content_text = soup.find('p').text.strip().replace('\xa0',"").replace(":","")
                item_dict = {strong_text: content_text.replace(strong_text,"")}
                data_list.append(item_dict)
                for item in data_list:
                    if item not in unique_list:
                        unique_list.append(item)

        json_data = json.dumps(unique_list, ensure_ascii=False)
        yield ScrapmeublesItem(name = product_name, text = json_data)

        
        