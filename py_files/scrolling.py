import time

SCROLL_PAUSE_TIME = 0.5


def get_scroll_height(driver):
    return driver.execute_script(
        "return document.documentElement.scrollHeight")

def scroll(driver, x):
    current_y = driver.execute_script('return window.pageYOffset')
    driver.execute_script(f"window.scrollTo({current_y}, {x + current_y})")
    return driver.execute_script('return window.pageYOffset')

def scroll_to_the_end(driver):
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

        time.sleep(SCROLL_PAUSE_TIME)

        new_height = driver.execute_script("document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


# def main():
#     driver = return_driver()
#     url = 'https://im-a-good-boye.itch.io/blawk'
#     driver.get(url)
#     while True:
#         elem = find_by_css_selector(driver, '[href="https://itch.io/profile/tomger"]')
#         if is_visible(driver, elem):
#             scroll(driver, 100)
#             if not is_visible(driver, elem):
#                 scroll(driver, -200)
#             break
#         scroll(driver, 15)
#         # time.sleep(uniform(0., 0.007))
#         print('all good')
#     mouse_move(ActionChains(driver), elem=elem)
#     print('mouse was moved')
#     time.sleep(0.5)
#     mouse_click(ActionChains(driver))
#     time.sleep(4)


# if __name__ == '__main__':
#     main()
