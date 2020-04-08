def is_visible(driver, elem):
    elem_left_bound = elem.location.get('x')
    elem_top_bound = elem.location.get('y')
    elem_width = elem.size.get('width')
    elem_height = elem.size.get('height')
    elem_right_bound = elem_left_bound + elem_width
    elem_lower_bound = elem_top_bound + elem_height

    win_upper_bound = driver.execute_script('return window.pageYOffset')
    win_left_bound = driver.execute_script('return window.pageXOffset')
    win_width = driver.execute_script(
        'return document.documentElement.clientWidth')
    win_height = driver.execute_script(
        'return document.documentElement.clientHeight')
    win_right_bound = win_left_bound + win_width
    win_lower_bound = win_upper_bound + win_height

    return all((
        win_left_bound <= elem_left_bound,
        win_right_bound >= elem_right_bound,
        win_upper_bound <= elem_top_bound,
        win_lower_bound >= elem_lower_bound))
