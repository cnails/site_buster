from chrome_driver import return_driver


def scroll_to_element(driver, web_element):
    web_element.location
    web_element.size


def main():
    driver = return_driver()
    driver.get('')


if __name__ == '__main__':
    main()
