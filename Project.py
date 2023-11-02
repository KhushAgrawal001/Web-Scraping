import pandas as pd
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

df = pd.read_excel("C:/Users/OMEN/Desktop/Black Coffer/Project 2/Input.xlsx")
text_list = []
results = []


def clean_text(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    cleaned_words = [word for word in words if word not in stop_words]
    return cleaned_words


def create_word_dictionary():
    positive_words = set()
    negative_words = set()
    with open("C:/Users/OMEN/Desktop/Black Coffer/MasterDictionary/positive-words.txt", 'r') as file:
        for line in file:
            positive_words.add(line.strip())

    with open('C:/Users/OMEN/Desktop/Black Coffer/MasterDictionary/negative-words.txt', 'r') as file:
        for line in file:
            negative_words.add(line.strip())

    return positive_words, negative_words


def calculate_sentiment_scores(text):
    positive_words, negative_words = create_word_dictionary()
    tokens = clean_text(text)
    positive_score = sum(1 for token in tokens if token in positive_words)
    negative_score = sum(1 for token in tokens if token in negative_words)
    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) or 0.000001)
    subjectivity_score = (positive_score + negative_score) / (len(tokens) or 0.000001)
    return positive_score, negative_score, polarity_score, subjectivity_score


def calculate_average_sentence_length(text):
    sentences = sent_tokenize(text)
    total_words = sum(len(word_tokenize(sentence)) for sentence in sentences)
    average_sentence_length = total_words / len(sentences) or 1
    return average_sentence_length


def calculate_complex_word_percentage(text):
    tokens = clean_text(text)
    complex_word_count = sum(1 for token in tokens if len(token) > 2 and token.isalpha())
    percentage_complex_words = complex_word_count / (len(tokens) or 1) * 100
    return percentage_complex_words


def calculate_fog_index(text):
    average_sentence_length = calculate_average_sentence_length(text)
    percentage_complex_words = calculate_complex_word_percentage(text)
    fog_index = 0.4 * (average_sentence_length + percentage_complex_words)
    return fog_index


def calculate_average_words_per_sentence(text):
    sentences = sent_tokenize(text)
    total_word = sum(len(word_tokenize(sentence)) for sentence in sentences)
    average_words_per_sentence = total_word / len(sentences) or 1
    return average_words_per_sentence


def count_complex_words(text):
    tokens = clean_text(text)
    complex_word_count = sum(1 for token in tokens if len(token) > 2 and token.isalpha())
    return complex_word_count


def count_words(text):
    tokens = clean_text(text)
    word_count = len(tokens)
    return word_count


def count_syllables(word):
    syllable_count = 0
    vowels = 'aeiou'
    word = word.lower()
    if word[0] in vowels:
        syllable_count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            syllable_count += 1
    if word.endswith(('es', 'ed')):
        syllable_count -= 1
    return syllable_count


def calculate_average_syllables_per_word(text):
    tokens = clean_text(text)
    syllable_count = sum(count_syllables(token) for token in tokens)
    average_syllables_per_word = syllable_count / (len(tokens) or 1)
    return average_syllables_per_word


def count_personal_pronouns(text):
    personal_pronouns = ['i', 'we', 'my', 'ours', 'us']
    counts = {pronoun: 0 for pronoun in personal_pronouns}
    word_tokens = word_tokenize(text.lower())
    for token in word_tokens:
        if token in counts:
            counts[token] += 1
    return counts


def calculate_average_word_length(text):
    tokens = clean_text(text)
    total_characters = sum(len(token) for token in tokens)
    average_word_length = total_characters / (len(tokens) or 1)
    return average_word_length


for index, row in df.iterrows():
    url_id = row["URL_ID"]
    url = row["URL"]
    # Send a GET request to the URL
    response = requests.get(url)

    # Create a BeautifulSoup object to parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the elements containing the article title and text
    title_element = soup.find_all("h1", class_=["tdb-title-text", "entry-title"])
    text_elements = soup.find_all('div', class_=['td-post-content tagdiv-type', 'tdb-block-inner td-fix-index'])

    if len(title_element) > 0:
        title = title_element[0].text.strip()
    else:
        print(f"No title element found for URL_ID: {url_id}")
        continue

    if len(text_elements) > 0:
        text_list.clear()
        for element in text_elements:
            text = element.text.strip()

            # Append each text to the text_list
            text_list.append(text)
        full_text = '\n'.join(text_list)
    else:
        print(f"No text elements found for URL_ID: {url_id}")
        continue

    positive_score, negative_score, polarity_score, subjectivity_score = calculate_sentiment_scores(full_text)

    print("Positive Score:", positive_score)
    print("Negative Score:", negative_score)
    print("Polarity Score:", polarity_score)
    print("Subjectivity Score:", subjectivity_score)

    average_sentence_length = calculate_average_words_per_sentence(full_text)
    print("Average Number of Words Per Sentence:", average_sentence_length)

    percentage_of_complex_words = calculate_complex_word_percentage(full_text)
    print("Percentage Complex Words:", percentage_of_complex_words)

    fog_index = calculate_fog_index(full_text)
    print("Fog Index:", fog_index)

    complex_word_count = count_complex_words(full_text)
    print("Complex Word Count:", complex_word_count)

    word_count = count_words(full_text)
    print("Word Count:", word_count)

    average_syllables_per_word = calculate_average_syllables_per_word(full_text)
    print("Average Syllables Per Word:", average_syllables_per_word)

    personal_pronoun_counts = count_personal_pronouns(full_text)
    print("Personal Pronoun Counts:", personal_pronoun_counts)

    average_word_length = calculate_average_word_length(full_text)
    print("Average Word Length:", average_word_length)

    # Save the extracted article text in a text file
    with open(f"{url_id}.txt", "w", encoding="utf-8") as file:
        file.write(f"{title}\n{full_text}")

    result = {
        "URL_ID": url_id,
        "URL": url,
        "Positive Score": positive_score,
        "Negative Score": negative_score,
        "Polarity Score": polarity_score,
        "Subjectivity Score": subjectivity_score,
        "Average Sentence length": average_sentence_length,
        "Percentage Of Complex Words": percentage_of_complex_words,
        "Fog Index": fog_index,
        "Average Number of Words Per Sentence": average_sentence_length,  # corrected variable name
        "Complex Word Count": complex_word_count,
        "Word Count": word_count,
        "Average Syllables Per Word": average_syllables_per_word,
        "Personal Pronoun Counts": personal_pronoun_counts,
        "Average Word Length": average_word_length,
         
    }
    results.append(result)

output_df = pd.DataFrame(results)
output_df.to_excel("C:/Users/OMEN/Desktop/Black Coffer/Project 2/Output.xlsx", index=False)
