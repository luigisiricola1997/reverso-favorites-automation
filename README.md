
# Reverso Favorites Automation

This Python script automates the process of logging into Reverso, searching for words, and adding them to the favorites list. It uses Selenium WebDriver to interact with the Reverso website and can be run with either Brave or Chrome browser.

## Prerequisites

1. **Python 3.x**: Ensure you have Python 3 or higher installed.
2. **WebDriver**: ChromeDriver (for Chrome) or BraveDriver (for Brave) must be installed and accessible.

## Setup

1. Clone this repository or download the script.
2. Create a `.env` file in the root directory of the project, and add your Reverso login credentials:
    ```
    REVERSO_USERNAME=your_username
    REVERSO_PASSWORD=your_password
    ```
3. Install the required dependencies:
    ```bash
    pip install selenium python-dotenv
    ```

4. **Browser Options**:
    - By default, the script is configured to use **Brave** browser. If you prefer to use **Google Chrome**, update the browser path in the script:
      ```python
      options.binary_location = r"C:\Path\To\Your\Chrome\Browser\chrome.exe"
      ```
    - Make sure to have either **Brave** or **Chrome** installed.

## Usage

Once everything is set up, place the words you want to search in a text file (e.g., `words.txt`). The script will:
1. Log into Reverso using the credentials in the `.env` file.
2. Search each word in `words.txt` on Reverso's context translation page.
3. Add each found word to your favorites.

Run the script with:
```bash
python reverso_translate.py
```

## Notes
- This script automatically handles the login process and adds each word to the favorites.
- You can modify the script to customize the behavior or adapt it for other use cases.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
