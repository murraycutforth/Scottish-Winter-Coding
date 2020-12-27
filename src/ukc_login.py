import chromedriver_binary
from selenium import webdriver
import gin


@gin.configurable()
def main(profile_path: str):
    options = webdriver.ChromeOptions()
    options.add_argument("user-data-dir=" + profile_path)
    
    driver = webdriver.Chrome(chrome_options=options)
    driver.get("http://www.ukclimbing.com")

    time.sleep(30) # Log in, and click "stay logged in"


if __name__ == '__main__':
    gin.parse_config_file('ukc_config.gin', skip_unknown=True)
    main(profile_path=gin.REQUIRED)
