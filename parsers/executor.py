from collections import OrderedDict
from transformers import MPNetPreTrainedModel, MPNetModel
import torch
from transformers import AutoTokenizer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import pandas as pd
import os

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
        self.classifier = torch.nn.Sequential(OrderedDict([('norm', torch.nn.BatchNorm1d(768)),
                                                           ('linear', torch.nn.Linear(768, 512)),
                                                           ('act', torch.nn.ReLU()),
                                                           ('batch_n', torch.nn.BatchNorm1d(512)),
                                                           ('drop_class', torch.nn.Dropout(0.2)),
                                                           ('class_l', torch.nn.Linear(512, 47))]))

    def forward(self, input_ids, attention_mask):
        outputs = self.mpnet(input_ids=input_ids,
                             attention_mask=attention_mask)

        logits = self.classifier(mean_pooling(outputs['last_hidden_state'], attention_mask))

        logits = 1.0 / (1.0 + torch.exp(-logits))
        return logits

def nlp(texts):
    model = ESGify.from_pretrained('ai-lab/ESGify')
    tokenizer = AutoTokenizer.from_pretrained('ai-lab/ESGify')
    text = ''
    for i in texts:
        text += i
    texts = [text]
    to_model = tokenizer.batch_encode_plus(
        texts,
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

    if str(model.id2label[torch.topk(results, k=47).indices.tolist()[0][0]]) not in ban:
        return True
    else:
        return False


def summarization(article_text):
    words = word_tokenize(article_text)
    stop_words = set(stopwords.words("russian"))
    freqTable = dict()

    for word in words:
        word = word.lower()
        if word in stop_words:
            continue
        if word in freqTable:
            freqTable[word] += 1
        else:
            freqTable[word] = 1

    sentences = sent_tokenize(article_text)
    sentence_value = dict()

    for sentence in sentences:
        for word, freq in freqTable.items():
            if word in sentence.lower():
                if sentence in sentence_value:
                    sentence_value[sentence] += freq
                else:
                    sentence_value[sentence] = freq

    sumValues = sum(sentence_value.values())
    average = int(sumValues / len(sentence_value))

    summary = ""
    for sentence in sentences:
        if (sentence in sentence_value) and (sentence_value[sentence] > (1.2 * average)):
            summary += " " + sentence

    return summary


def all_nlp(df):
    first = []
    sec = []
    th = []
    forth = []
    for index, row in df.iterrows():
        if nlp(str(row['Описание'])):
            first.append(row['Заголовок'])
            sec.append(row['Время публикации'])
            th.append(summarization(str(row['Описание'])))
            forth.append(row['Ссылка'])

    df_final = pd.DataFrame({
            "Заголовок": first,
            "Время публикации": sec,
            "Описание": th,
            "Ссылка": forth
    })
    return df_final


def run_parsers():
    os.system("python ferra.py")
    os.system("python RBK.py")

def main():
    a = input("Update parsers? (y/n): ")
    if a == "y":
        run_parsers()

    csvs = ["RBCFrame.csv", "FerraFrame.csv"]
    for file in csvs:
        if not os.path.exists(file):
            print(f"Файл {file} не найден.")
            return

    df = pd.concat([pd.read_csv(f) for f in csvs], ignore_index=True)

    df = all_nlp(df)
    df.to_csv("svmain.csv", index=False)

if __name__ == "__main__":
    main()