import json
from collections import defaultdict

char_to_pinyin = defaultdict(list)
char_count = defaultdict(int)
bigram_count = defaultdict(int)

with open('data/一二级汉字表.txt', 'r', encoding='GBK') as file:
    for char in file.read():
        char_count[char] = 0


with open('data/拼音汉字表.txt', 'r', encoding='GBK') as file:
    for line in file:
        parts = line.strip().split()
        if len(parts) > 1:
            pinyin = parts[0]
            chars = parts[1:]
            for char in chars:
                if pinyin not in char_to_pinyin[char]:
                    char_to_pinyin[char].append(pinyin)


for month in ['04', '05', '06', '07', '08', '09', '10', '11']:
    with open ('corpus/sina_news_gbk/2016-' + month + '.txt', 'r', encoding='GBK') as file:
        for line in file:
            data=json.loads(line.strip())
            html_content = data.get('html', '')

            # 获得一元词频
            for char in html_content:
                if char in char_count:
                    char_count[char] += 1
            
            # 获得二元词频
            for i in range(len(html_content) - 1):
                char1 = html_content[i]
                char2 = html_content[i + 1]
                if char1 in char_to_pinyin and char2 in char_to_pinyin:
                    bigram = f"{char1} {char2}"
                    bigram_count[bigram] += 1  


pinyin_to_words = defaultdict(lambda: {"words": [], "counts": []})
bigram_to_words = defaultdict(lambda: {"words": [], "counts": []})

for char, count in char_count.items():
    if count > 0:
        pinyins = char_to_pinyin.get(char, [])
        for pinyin in pinyins:
            pinyin_to_words[pinyin]["words"].append(char)
            pinyin_to_words[pinyin]["counts"].append(count)

output_path = "processed_data/1_word.txt"
with open(output_path, "w", encoding="utf-8") as file:
    json.dump(pinyin_to_words, file, ensure_ascii=False, indent=4)

for bigram, count in bigram_count.items():
    char1, char2 = bigram.split()
    pinyins1 = char_to_pinyin.get(char1, [])
    pinyins2 = char_to_pinyin.get(char2, [])
    for pinyin1 in pinyins1:
        for pinyin2 in pinyins2:
            pinyin_bigram = f"{pinyin1} {pinyin2}"
            bigram_to_words[pinyin_bigram]["words"].append(bigram)
            bigram_to_words[pinyin_bigram]["counts"].append(count)

output_path = "processed_data/2_word.txt"
with open(output_path, "w", encoding="utf-8") as file:
    json.dump(bigram_to_words, file, ensure_ascii=False, indent=4)
