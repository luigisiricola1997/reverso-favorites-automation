from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv
import os
import time

# Load variables from the .env file
load_dotenv()

def search_words_on_reverso(file_path):
    username = os.getenv("REVERSO_USERNAME")
    password = os.getenv("REVERSO_PASSWORD")

    # Configure browser options (use Brave or Chrome)
    options = webdriver.ChromeOptions()
    options.binary_location = r"C:\Users\Siricola\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"

    # Specify the path to ChromeDriver
    driver_path = "./chromedriver-win64/chromedriver.exe"  # Replace with your chromedriver path
    service = Service(driver_path)  # Use the specified driver

    # Initialize the driver
    driver = webdriver.Chrome(service=service, options=options)

    # Go to Reverso and login
    driver.get("https://account.reverso.net/Account/Login")
    time.sleep(2)

    # Enter the Reverso username/email
    username_field = driver.find_element(By.ID, "Email")
    username_field.send_keys(username)
    username_field.send_keys(Keys.RETURN)
    time.sleep(2)

    # Enter the password
    password_field = driver.find_element(By.ID, "Password")
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)
    time.sleep(5)  # Wait for login to complete

    # Read words from the file
    with open(file_path, "r") as file:
        words = file.read().splitlines()

    # Perform the search on Reverso for each word
    for word in words:
        driver.get(f"https://context.reverso.net/translation/english-italian/{word}")
        time.sleep(3)

        # Use WebDriverWait to wait for the element before interacting with it
        try:
            # Wait for the add to favorites button to become clickable
            add_to_favorites_button = driver.find_element(By.XPATH, "//button[contains(@class, 'save-fav')]")
            add_to_favorites_button.click()
            add_to_favorites_button.click()
            print(f"'{word}' added to favorites.")
        except Exception as e:
            print(f"Error adding '{word}' to favorites: {e}")

        time.sleep(2)  # Pause between each search

    print("Search completed.")
    driver.quit()

# Use the script
search_words_on_reverso("words.txt")
