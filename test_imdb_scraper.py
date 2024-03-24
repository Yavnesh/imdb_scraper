import unittest
from unittest.mock import MagicMock, patch
from .imdb_scraper import scrape_items, click_load_more
from selenium.common.exceptions import TimeoutException

class TestIMDBScraper(unittest.TestCase):
    
    def setUp(self):
        # Mocking WebDriver and WebDriverWait
        self.driver = MagicMock()
        self.wait = MagicMock()
        
    def test_scrape_items(self):
        # Mocking page source content
        self.driver.page_source = '<html><body><p>Hello, world!</p></body></html>'
        
        # Mocking BeautifulSoup to return sample movies
        movies_html = '<li class="ipc-metadata-list-summary-item"><h3 class="ipc-title__text">Movie Title</h3></li>'
        self.wait.until.return_value.text = movies_html
        self.wait.until.return_value.find_element.return_value.text = "2022"
        
        # Mocking click on modal button
        self.wait.until.return_value.find_element.side_effect = [MagicMock(), TimeoutException()]
        
        # Test the function
        scraped_data = scrape_items(self.wait)
        
        # Assertions
        self.assertEqual(len(scraped_data), 1)  # Ensure only one movie is scraped
        
    def test_click_load_more(self):
        # Mocking load more button
        self.wait.until.return_value = MagicMock()
        
        # Test the function
        result = click_load_more(self.wait)
        
        # Assertions
        self.assertTrue(result)  # Ensure click_load_more returns True if successful
        

if __name__ == '__main__':
    unittest.main()