# Importing necessary libraries
from bs4 import BeautifulSoup
import requests
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global variable for WebDriver
driver = None

# Global variable to keep track of the last scraped item
last_scraped_index = 0

# Function to scrape items
def scrape_items(wait):
    global last_scraped_index  # Accessing the global variable
    scraped_data = []
    try:
        # Extracting page content
        page_content = driver.page_source
        soup = BeautifulSoup(page_content, 'html.parser')

        # Finding all movies
        movies = soup.find_all('li', class_ ='ipc-metadata-list-summary-item')

        # Iterating through each movie, starting from the last scraped index
        for i in range(last_scraped_index, len(movies)):
            movie = movies[i]
            # Extracting movie title
            h3_tag = movie.find('h3', class_ ='ipc-title__text').text.split('. ', 1)
            movie_title = h3_tag[1]

            # Extracting movie release year
            movie_release_year = movie.find('span', class_ ='sc-b0691f29-8 ilsLEX dli-title-metadata-item').text

            # Extracting movie rating
            movie_rating_tag = movie.find('span', class_ ='ipc-rating-star ipc-rating-star--base ipc-rating-star--imdb ratingGroup--imdb-rating')
            movie_rating = movie_rating_tag.text.split(' ')[0] if movie_rating_tag else 'N/A'

            # Finding and clicking on the button to open the modal
            info_title = "See more information about " + movie_title 
            print("<<<<<----info_title------>",i + 1, info_title )
            more_info_button = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, f"//*[@title=\"{info_title}\"]")))
            driver.execute_script("arguments[0].click();", more_info_button)
            
            # Waiting for the button to be invisible
            wait.until(EC.invisibility_of_element_located(
                        (By.XPATH, f"//*[@title=\"{info_title}\"]")))
            
            # Scrolling the webpage to the bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Waiting for the modal to appear
            modal = wait.until(
                EC.visibility_of_element_located((By.CLASS_NAME, "ipc-promptable-base__panel"))
            )

            # Extracting information from the modal
            movie_plot_summary = modal.find_element(By.CSS_SELECTOR, ".sc-d3701649-2.cPgMft").text

            # Extracting director and cast data
            movie_director_and_cast_elements = modal.find_elements(By.CSS_SELECTOR, '.sc-9bca7e5d-2.itmyuK')
            if len(movie_director_and_cast_elements) == 2:
                director_list = movie_director_and_cast_elements[0].find_element(By.CSS_SELECTOR, '.ipc-inline-list--inline').find_elements(By.CSS_SELECTOR, '.ipc-link--baseAlt')
                movie_directors = [director.text for director in director_list]

                # Extract cast data
                cast_list = movie_director_and_cast_elements[1].find_element(By.CSS_SELECTOR, '.ipc-inline-list--inline').find_elements(By.CSS_SELECTOR, '.ipc-link--baseAlt')
                movie_cast = [actor.text for actor in cast_list]
            else:
                cast_list = movie_director_and_cast_elements[0].find_element(By.CSS_SELECTOR, '.ipc-inline-list--inline').find_elements(By.CSS_SELECTOR, '.ipc-link--baseAlt')
                movie_cast = [actor.text for actor in cast_list]

            # Creating dict of the requied values
            scraped_info = {
                "id": i + 1,
                "movie_title": movie_title,
                "movie_release_year": movie_release_year,
                "movie_rating": movie_rating,
                "movie_directors": movie_directors,
                "movie_cast": movie_cast,
                "movie_plot_summary": movie_plot_summary,
            }

            # Append the dict to list
            scraped_data.append(scraped_info)
            
            # Closing the modal
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='ipc-icon-button ipc-icon-button--baseAlt ipc-icon-button--onBase']"))).click()

        # Update the last scraped index for the next iteration
        last_scraped_index = len(movies)
        print(scraped_data)
        return scraped_data
    except TimeoutException:
        logger.error("Timeout occurred while waiting for an element.")
    except NoSuchElementException as e:
        logger.error(f"Element not found: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        # Log the full traceback if an unexpected error occurs
    

# Calling the scrape_items function                           
# scrape_items()


# Function to click on load more button
def click_load_more(wait):
    global driver  # Accessing the global driver object
    try:
        # Finding and clicking on the button to load next 50 items
        load_more_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, f"//button[contains(@class, 'ipc-see-more__button')]")
                ))
        driver.execute_script("arguments[0].click();", load_more_button)

        # Waiting for the button to be invisible
        wait.until(EC.invisibility_of_element_located(
                    (By.XPATH, f"//button[contains(@class, 'ipc-see-more__button') and @disabled]")
                ))
        
        # # Scrolling the webpage to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        return True
    except requests.RequestException as e:
        return False
    except TimeoutException:
        logger.error("Timeout occurred while waiting for the load more button.")
        return False
    except NoSuchElementException as e:
        logger.error(f"Load more button not found: {e}")
        return False
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        # Log the full traceback if an unexpected error occurs
        return False
    
# Main scraping process
def main():
    global driver  # Accessing the global driver object
    # Code for initializing WebDriver, navigating to the URL, etc.
    
    # Getting the genre from user
    input_genre = input("Enter any genre - ")

    # Setting up the base_url
    base_url = "https://www.imdb.com/search/title/?genres={}"

    # Inserting the input_genre in base_url
    genre_url = base_url.format(input_genre)

    # Initializing WebDriver
    driver = webdriver.Chrome()

    try:
        all_scraped_data = []
        # Requesting the URL
        driver.get(genre_url)

        # Implicit wait for 5 seconds
        driver.implicitly_wait(5)

        # Explicit wait setup
        wait = WebDriverWait(driver, 5)

        scraped_data  = scrape_items(wait)
        # Loop to click load more button and scrape items
        while click_load_more(wait):
            all_scraped_data.append(scraped_data)    
            scraped_data = scrape_items(wait)
        print(all_scraped_data)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        # Log the full traceback if an unexpected error occurs

    finally:
        # Close the WebDriver
        driver.quit()

if __name__ == "__main__":
    main()