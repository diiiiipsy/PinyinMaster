import json
import math
import sys
import time
from collections import defaultdict

big_num = 100
_lambda = 1-2e-4
search_width = 20

pinyin_dict = defaultdict(list)
with open('data/拼音汉字表.txt', 'r', encoding='GBK') as file:
    for line in file:
        parts = line.strip().split()
        if len(parts) > 1:
            pinyin = parts[0]
            chars = parts[1:]
            for char in chars:
                if pinyin not in pinyin_dict[char]:
                    pinyin_dict[char].append(pinyin)

with open('processed_data/1_word.txt', 'r', encoding='utf-8') as file:
    single_frequency_data = json.load(file)

with open('processed_data/2_word.txt', 'r', encoding='utf-8') as file:
    double_frequency_data = json.load(file)

def getPinyin(word):
    return pinyin_dict.get(word, [])

def getWord(pinyin):
    chars = [char for char, pinyins in pinyin_dict.items() if pinyin in pinyins]
    return chars


appr_single_cache = {}

def getAppearanceSingle(word):
    if word in appr_single_cache:
        return appr_single_cache[word]

    pinyins = getPinyin(word)
    if not pinyins:
        result = 0

    total_count = 0
    for pinyin in pinyins:
        if pinyin in single_frequency_data:
            words = single_frequency_data[pinyin]['words']
            counts = single_frequency_data[pinyin]['counts']
            if word in words:
                word_index = words.index(word)
                total_count += counts[word_index]

    if total_count > 0:
        result = total_count
    else:
        result = 0
    
    appr_single_cache[word] = result
    return result


appr_single_total_cache = {}

def getAppearanceSingleTotal(word):
    if word in appr_single_total_cache:
        return appr_single_total_cache[word]
    
    pinyins = getPinyin(word)
    if not pinyins:
        result = 0

    total_count = 0
    for pinyin in pinyins:
        if pinyin in single_frequency_data:
            counts = single_frequency_data[pinyin]['counts']
            total_count += sum(counts)
    if total_count > 0:
        result = total_count
    else:
        result = 0

    appr_single_total_cache[word] = result
    return result


appr_double_cache = {}

def getAppearanceDouble(word_1, word_2):
    key = (word_1,word_2)
    if key in appr_double_cache:
        return appr_double_cache[key]
    
    pinyins_1 = getPinyin(word_1)
    pinyins_2 = getPinyin(word_2)
    if not pinyins_1 or not pinyins_2:
        result = 0

    total_count = 0
    for pinyin_1 in pinyins_1:
        for pinyin_2 in pinyins_2:
            key = f"{pinyin_1} {pinyin_2}"
            if key in double_frequency_data:
                words = double_frequency_data[key]['words']
                counts = double_frequency_data[key]['counts']
                bigram = f"{word_1} {word_2}"
                if bigram in words:
                    word_index = words.index(bigram)
                    total_count += counts[word_index]
    if total_count > 0:
        result = total_count
    else:
        result = 0
    
    appr_double_cache[key] = result
    return result


appr_double_total_cache = {}

def getAppearanceDoubleTotal(word_1, word_2):
    key = (word_1, word_2)
    if key in appr_double_total_cache:
        return appr_double_total_cache[key]
    
    pinyins_1 = getPinyin(word_1)
    pinyins_2 = getPinyin(word_2)
    
    if not pinyins_1 or not pinyins_2:
        return 0

    total_count = 0
    for pinyin_1 in pinyins_1:
        for pinyin_2 in pinyins_2:
            key = f"{pinyin_1} {pinyin_2}"
            if key in double_frequency_data:
                words = double_frequency_data[key]['words']
                counts = double_frequency_data[key]['counts']
                for i, bigram in enumerate(words):
                    first_word, second_word = bigram.split()
                    if first_word == word_1:
                        total_count += counts[i]

    appr_double_total_cache[key] = total_count
    return total_count

val_single_cache = {}

def getValSingle(word):
    if word in val_single_cache:
        return val_single_cache[word]

    single_count = getAppearanceSingle(word)
    total_count = getAppearanceSingleTotal(word)
    if single_count == 0 or total_count == 0:
        result =  big_num
    else:
        result = -math.log(single_count / total_count)

    val_single_cache[word] = result
    return result


val_double_cache = {}

def getValDouble(word_1, word_2):
    key = (word_1, word_2)
    if key in val_double_cache:
        return val_double_cache[key]
    
    double_count = getAppearanceDouble(word_1, word_2)
    single_count = getAppearanceSingle(word_1)
    # total_count = getAppearanceDoubleTotal(word_1,word_2)

    if double_count == 0 or single_count == 0:
        result = big_num
    else:
        result = -math.log(double_count / single_count)

    val_double_cache[key] = result
    return result


def getValDoubleSmoothed(word_1, word_2):
    key = (word_1, word_2)
    if key in val_double_cache:
        return val_double_cache[key]
    
    double_count = getAppearanceDouble(word_1, word_2)
    single_count = getAppearanceSingle(word_1)
    single_count_total = getAppearanceSingleTotal(word_1)
    
    if  single_count == 0 or single_count_total == 0:
        result = big_num
    else:
        result = -math.log(_lambda*(double_count / single_count)+(1-_lambda)*(single_count / single_count_total))

    val_double_cache[key] = result
    return result


def viterbi(pinyin_sequence):
    n = len(pinyin_sequence)
    dp = [{} for _ in range(n)]
    path = [{} for _ in range(n)]

    first_pinyin = pinyin_sequence[0]
    first_chars = getWord(first_pinyin)
    for char in first_chars:
        dp[0][char] = getValSingle(char)
        path[0][char] = [char]

    for i in range(1, n):
        current_pinyin = pinyin_sequence[i]
        current_chars = getWord(current_pinyin)
        previous_chars = dp[i - 1].keys()

        current_dp = {}
        current_path = {}

        for current_char in current_chars:
            min_val = float('inf')
            best_prev_char = None
            for prev_char in previous_chars:
                val = dp[i - 1][prev_char] + getValDouble(prev_char, current_char)
                if val < min_val:
                    min_val = val
                    best_prev_char = prev_char

            current_dp[current_char] = min_val
            if best_prev_char is None:
                current_path[current_char] = []
            else:
                current_path[current_char] = path[i - 1][best_prev_char] + [current_char]

        # 只保留最小的 20 个值
        sorted_chars = sorted(current_dp.items(), key=lambda x: x[1])[:
                                                                      #max(1, len(current_chars))
                                                                      search_width
                                                                      ]
        dp[i] = {char: val for char, val in sorted_chars}
        path[i] = {char: current_path[char] for char, val in sorted_chars}

    min_val = float('inf')
    best_last_char = None
    for char, val in dp[-1].items():
        if val < min_val:
            min_val = val
            best_last_char = char
    if best_last_char is None:
        return []
    return path[-1][best_last_char]


if __name__ == "__main__":
    
    input_lines = sys.stdin.read().strip().splitlines()
    for line in input_lines:
        pinyin_sequence = line.split()
        result = viterbi(pinyin_sequence)
        print("".join(result))