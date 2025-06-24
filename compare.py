def calculate_accuracy(output_file, answer_file):
    with open(output_file, 'r', encoding='utf-8') as f_out, open(answer_file, 'r', encoding='utf-8') as f_ans:
        output_lines = f_out.readlines()
        answer_lines = f_ans.readlines()

    if len(output_lines) != len(answer_lines):
        raise ValueError("Output and answer files must have the same number of lines.")

    total_sentences = len(answer_lines)
    correct_sentences = 0
    total_chars = 0
    correct_chars = 0

    for output, answer in zip(output_lines, answer_lines):
        output = output.strip()
        answer = answer.strip()

        # Sentence accuracy
        if output == answer:
            correct_sentences += 1

        # Character accuracy
        total_chars += len(answer)
        correct_chars += sum(1 for o, a in zip(output, answer) if o == a)

    sentence_accuracy = correct_sentences / total_sentences
    char_accuracy = correct_chars / total_chars

    return sentence_accuracy, char_accuracy


if __name__ == "__main__":
    output_file = "data/output.txt"
    answer_file = "data/answer.txt"

    try:
        sentence_acc, char_acc = calculate_accuracy(output_file, answer_file)
        print(f"句准确率: {sentence_acc:.2%}")
        print(f"字准确率: {char_acc:.2%}")
    except Exception as e:
        print(f"发生错误: {e}")