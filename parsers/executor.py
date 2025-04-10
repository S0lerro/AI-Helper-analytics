from collections import OrderedDict
from transformers import MPNetPreTrainedModel, MPNetModel
import torch
from transformers import AutoTokenizer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import pandas as pd
import os
import sqlite3
from deep_translator import GoogleTranslator

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

class ESGify(MPNetPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.mpnet = MPNetModel(config, add_pooling_layer=False)
        self.id2label = config.id2label
        self.label2id = config.label2id
        self.classifier = torch.nn.Sequential(OrderedDict([
            ('norm', torch.nn.BatchNorm1d(768)),
            ('linear', torch.nn.Linear(768, 512)),
            ('act', torch.nn.ReLU()),
            ('batch_n', torch.nn.BatchNorm1d(512)),
            ('drop_class', torch.nn.Dropout(0.2)),
            ('class_l', torch.nn.Linear(512, 47))
        ]))

    def forward(self, input_ids, attention_mask):
        outputs = self.mpnet(input_ids=input_ids, attention_mask=attention_mask)
        logits = self.classifier(mean_pooling(outputs['last_hidden_state'], attention_mask))
        logits = 1.0 / (1.0 + torch.exp(-logits))
        return logits

def translate_text(text, chunk_size=3000):
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    translated_chunks = []
    for chunk in chunks:
        try:
            translated = GoogleTranslator(source='auto', target='en').translate(chunk)
            translated_chunks.append(translated)
        except Exception as e:
            print(f"Ошибка при переводе: {e}")
            return ""
    return ' '.join(translated_chunks)

def nlp(text, model, tokenizer, debug=False, title=None, index=None):
    translated_text = translate_text(text)
    if not translated_text:
        return False

    if debug:
        print(f"\n[DEBUG] Article #{index}")
        print(f"[DEBUG] Title: {title}")
        print(f"[DEBUG] Translated Text: {translated_text[:200]}...")

    to_model = tokenizer.batch_encode_plus(
        [translated_text],
        add_special_tokens=True,
        max_length=140,
        return_token_type_ids=False,
        padding="max_length",
        truncation=True,
        return_attention_mask=True,
        return_tensors='pt',
    )
    results = model(**to_model)

    ban = ['Economic Crime', 'Legal Proceedings & Law Violations', 'Corporate Governance', 'Values and Ethics',
           'Risk Management and Internal Control', 'Strategy Implementation', 'Disclosure',
           'Responsible Investment & Greenwashing', 'Supply Chain (Economic / Governance)', 'Indigenous People',
           'Human Rights', 'Emergencies (Social)', 'Land Acquisition and Resettlement (S)', 'Data Safety',
           'Freedom of Association and Right to Organise', 'Minimum Age and Child Labour', 'Forced Labour',
           'Discrimination', 'Retrenchment', 'Labor Relations Management', 'Supply Chain (Social)']

    top_label = str(model.id2label[torch.topk(results, k=47).indices.tolist()[0][0]])

    if debug:
        print(f"[DEBUG] Predicted Category: {top_label}")
        if top_label in ban:
            print(f"[DEBUG] Category is in banned list. Skipped.")

    if top_label not in ban:
        return top_label
    else:
        return False

def summarization(article_text):
    words = word_tokenize(article_text)
    stop_words = set(stopwords.words("russian"))
    freqTable = {}

    for word in words:
        word = word.lower()
        if word in stop_words:
            continue
        freqTable[word] = freqTable.get(word, 0) + 1

    sentences = sent_tokenize(article_text)
    sentence_value = {}

    for sentence in sentences:
        for word, freq in freqTable.items():
            if word in sentence.lower():
                sentence_value[sentence] = sentence_value.get(sentence, 0) + freq

    sumValues = sum(sentence_value.values())
    average = int(sumValues / len(sentence_value)) if sentence_value else 0

    summary = ""
    for sentence in sentences:
        if sentence_value.get(sentence, 0) > (1.2 * average):
            summary += " " + sentence

    return summary.strip()

def all_nlp(df, fast_mode=False, debug=False):
    if fast_mode:
        df = df.head(30)

    model = ESGify.from_pretrained('ai-lab/ESGify')
    tokenizer = AutoTokenizer.from_pretrained('ai-lab/ESGify')

    first, sec, th, forth, fifth = [], [], [], [], []

    for index, row in df.iterrows():
        category = nlp(
            text=str(row['Описание']),
            model=model,
            tokenizer=tokenizer,
            debug=debug,
            title=row['Заголовок'],
            index=index
        )
        if category:
            first.append(row['Заголовок'])
            sec.append(row['Время публикации'])
            summary = summarization(str(row['Описание']))
            if debug:
                print(f"[DEBUG] Summary: {summary[:200]}...\n")
            th.append(summary)
            forth.append(row['Ссылка'])
            fifth.append(category)

    df_final = pd.DataFrame({
        "Категория": fifth,
        "Заголовок": first,
        "Время публикации": sec,
        "Описание": th,
        "Ссылка": forth
    })
    return df_final

def run_parsers():
    os.system("python ferra.py")
    os.system("python RBK.py")

def database():
    df = pd.read_csv('svmain.csv')

    conn = sqlite3.connect('websites.db')
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS AllArticles')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS AllArticles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        headline TEXT,
        time_author TEXT,
        description TEXT,
        link TEXT,
        category TEXT
    )
    ''')

    for index, row in df.iterrows():
        cursor.execute('''
        INSERT INTO AllArticles (headline, time_author, description, link, category) 
        VALUES (?, ?, ?, ?, ?)
        ''', (row['Заголовок'], row['Время публикации'], row['Описание'], row['Ссылка'], row['Категория']))

    conn.commit()
    conn.close()
    print("Данные успешно добавлены в таблицу AllArticles.")

def main():
    a = input("Update parsers? (y/n): ").lower()
    fast_mode = input("Enable fast mode? (y/n): ").lower() == "y"
    debug_mode = input("Enable debug mode? (y/n): ").lower() == "y"

    if a == "y":
        run_parsers()

    csvs = ["RBCFrame.csv", "FerraFrame.csv"]
    for file in csvs:
        if not os.path.exists(file):
            print(f"Файл {file} не найден.")
            return

    df = pd.concat([pd.read_csv(f) for f in csvs], ignore_index=True)
    df = all_nlp(df, fast_mode=fast_mode, debug=debug_mode)
    df.to_csv("svmain.csv", index=False)
    database()

if __name__ == "__main__":
    main()
