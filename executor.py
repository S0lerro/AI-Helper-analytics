from collections import OrderedDict
from transformers import MPNetPreTrainedModel, MPNetModel
import torch
import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import sqlite3
import pandas as pd
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output  # First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


# Definition of ESGify class because of custom,sentence-transformers like, mean pooling function and classifier head
class ESGify(MPNetPreTrainedModel):
    def __init__(self, config):  # tuning only the head
        super().__init__(config)
        # Instantiate Parts of model
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
        # Feed input to mpnet model
        outputs = self.mpnet(input_ids=input_ids,
                             attention_mask=attention_mask)

        # mean pooling dataset and eed input to classifier to compute logits
        logits = self.classifier(mean_pooling(outputs['last_hidden_state'], attention_mask))

        # apply sigmoid
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
        #print("not in ESGFY")

def summarization(article_text):
    WHITESPACE_HANDLER = lambda k: re.sub('\s+', ' ', re.sub('\n+', ' ', k.strip()))

    model_name = "csebuetnlp/mT5_multilingual_XLSum"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    input_ids = tokenizer(
        [WHITESPACE_HANDLER(article_text)],
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=len(article_text)
    )["input_ids"]


    output_ids = model.generate(
        input_ids=input_ids,
        max_length=len(article_text) / 2,
        no_repeat_ngram_size=2,
        num_beams=4
    )[0]

    summary = tokenizer.decode(
        output_ids,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False
    )

    return summary

def all_nlp(df):
    first = []
    sec = []
    th = []
    forth = []
    for index, row in df.iterrows():
        if nlp(str(row['Описание'])):
            first.append(row['Заголовок'])
            sec.append(row['Время и автор публикации'])
            th.append(summarization(str(row['Описание'])))
            forth.append(row['Ссылка'])

    df_final = pd.DataFrame({
            "Заголовок": first,
            "Время и автор публикации": sec,
            "Описание": th,
            "Ссылка": forth
    })
    return df_final

csvs = ["RBCFrame.csv", "FerraFrame.csv", "HiTechFrame.csv"]
df = pd.concat([pd.read_csv(f) for f in csvs], ignore_index=True)
df = all_nlp(df)
df.to_csv("svmain.csv", index=False)

df = pd.read_csv("svmain.csv")
sqliteConnection = sqlite3.connect("websites.db")
cursos = conn.cursor
