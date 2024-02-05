import scrapy
import pandas as pd
from pathlib import Path
class MySpider(scrapy.Spider):
    name = 'twitter'
    
    custom_settings = {
        'NUMEXPR_MAX_THREADS': 32,  # Use all available cores
        'CONCURRENT_REQUESTS': 200,  # Increase concurrency as needed
        'CONCURRENT_REQUESTS_PER_DOMAIN': 5,
        'DOWNLOAD_DELAY': 1,  # Optional delay between requests to avoid being blocked
        'LOG_FILE': 'scrapy_log.txt',  # Log errors to a file
    }

    def start_requests(self):
        df = pd.read_parquet('/mnt/data/harini/twiiter_data/fortune1k-scrape/twitter/twitter/transuasion_it3_pair_sim.parquet')
        urls = df['url'].unique()  # Remove duplicates
        for index, url in enumerate(urls):
            yield scrapy.Request(url=url, callback=self.parse, meta={'index': index})

    def parse(self, response):
        
            # Extract the content from the response
        content = response.text
        self.log_statistics(response)

        # Get the index from the meta information
        index = response.meta['index']

        # Save the content to a file, using the index as part of the filename
        filename = f"../contents/content_{index}.html"
        Path(filename).write_bytes(content.encode('utf-8'))

        # Maintain a mapping of URL to filename
        url_to_filename_mapping = f"content_mapping.csv"
        with open(url_to_filename_mapping, 'a', encoding='utf-8') as mapping_file:
            mapping_file.write(f"{response.url},{filename}\n")

        self.log(f"Saved HTML content for index {index} to {filename}")

        
    def log_statistics(self, response):
        # Access Scrapy Stats Collector
        stats = self.crawler.stats

        # Log relevant statistics
        self.log(f"URL: {response.url}")
        self.log(f"Requests: {stats.get_value('downloader/request_count')}")
        self.log(f"Responses: {stats.get_value('downloader/response_count')}")
        self.log(f"Response Time: {stats.get_value('downloader/response_time_avg')} seconds (avg)")