from chrome_driver import driver


def fill_form(driver):
    forms = driver.find_elements_by_tag_name('form')

    if not forms:
        return
    form = forms[0]
    textareas = form.find_elements_by_tag_name('textarea')
    text_inputs = form.find_elements_by_xpath('//input[@type="text"]')
    email_inputs = form.find_elements_by_xpath('//input[@type="email"]')
    url_inputs = form.find_elements_by_xpath('//input[@type="url"]')
    checkbox_inputs = form.find_elements_by_xpath('//input[@type="checkbox"]')
    # submit_buttons = form.find_elements_by_xpath('//input[@type="submit"]')
    for textarea in textareas:
        textarea.send_keys('some text here')
    for text_input in text_inputs:
        text_input.send_keys('another text here')
    for email_input in email_inputs:
        email_input.send_keys('tmp@gmail.com')
    for url_input in url_inputs:
        url_input.send_keys('www.google.com')
    for checkbox_input in checkbox_inputs:
        checkbox_input.click()
    # for submit_button in submit_buttons:
    #     submit_button.click()


def main():
    url = 'https://zonaofgames.ru/%d1%81%d0%b0%d0%b9%d1%82-%d0%b4%d0%bb%d1%8f-%d0%be%d0%b3%d1%80%d0%be%d0%bc%d0%bd%d0%be%d0%b3%d0%be-%d0%ba%d0%be%d0%bb%d0%b8%d1%87%d0%b5%d1%81%d1%82%d0%b2%d0%b0-%d0%b3%d0%b5%d0%b9%d0%bc%d0%b5%d1%80/%d0%be%d0%bd%d0%bb%d0%b0%d0%b9%d0%bd-%d0%b8%d0%b3%d1%80%d1%8b/'
    driver.get(url)
    fill_form(driver)


if __name__ == '__main__':
    main()
