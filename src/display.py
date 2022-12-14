from termcolor import colored





def get_correct_size_string(string: str, spacing: int) -> int: 
    string = str(string)
    s = string + ' ' * (spacing - len(string))

    return s

def color_int(text_to_print, threshold=0, spacing=0, prefix='', suffix=''):
    if text_to_print < threshold:
        float_colored = colored(get_correct_size_string(prefix + str(text_to_print) + suffix, spacing), 'red')
    else:
        float_colored = colored(get_correct_size_string(prefix + str(text_to_print) + suffix, spacing), 'green')
    
    return float_colored


def info_to_print(display_infos, sentence_to_display, char, key_pressed, best_wpm, words_left_to_type):
    '''For every key pressed when playing the game, what is printed refreshed. 
    This function is made for what's get printed and in which case'''
    print('\n'*20)

    if len(key_pressed) > 1 and display_infos == True: 
        count_correct_keys = len(list(filter(lambda x: x[1] == True, key_pressed)))
        duration = key_pressed[-1][2] - key_pressed[0][2]
        wpm = count_correct_keys / duration * 60 / 5

        wpm_colored = color_int(round(wpm, 1), best_wpm)
        print('\n'*20)
        print(f'Words left to type: {words_left_to_type}\nWPM: {wpm_colored}\n')#|{wpm_var_best}|{wpm_diff_best}\t{wpm_var_avg}|{wpm_diff_avg}\n')

    else: 
        print(f'Words left to type: {words_left_to_type}\n')

    words_to_display_count = 5
    words_to_display = ' '.join(sentence_to_display.split(' ')[:words_to_display_count])
    print(' ', words_to_display, '\t'*5, end='\r')
    return words_to_display



