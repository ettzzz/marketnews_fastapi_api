# -*- coding: utf-8 -*-
"""
Created on Sun Aug 29 16:56:48 2021

@author: ert
"""

import os
import random

import torch

from config.static_vars import ROOT

train_texts = []
train_labels = []
test_texts = []
test_labels = []

# ROOT = "/content/drive/My Drive/colab/marketnews_fastapi_api"
for file_name in ['negative', 'positive']:
    with open(os.path.join(ROOT, 'engine', '{}.txt'.format(file_name)), 'r') as f:
        file_str = f.read()
    datasets = file_str.split('\n')
    for data in datasets:
        try:
            data_piece = data.split('<|>')
            content = data_piece[0]
            label = int(data_piece[1])
        except: 
            continue
        if random.random() >= 0.1:
            train_texts.append(content)
            train_labels.append(label)
        else:
            test_texts.append(content)
            test_labels.append(label)
print(len(train_texts), len(test_texts))

from sklearn.model_selection import train_test_split
train_texts, val_texts, train_labels, val_labels = train_test_split(train_texts, train_labels, test_size=.2)


from transformers import AutoTokenizer, AutoModel, AutoConfig
from transformers import AutoModelForSequenceClassification

pretrain_model_path = "voidful/albert_chinese_tiny"
tokenizer = AutoTokenizer.from_pretrained(pretrain_model_path)

train_encodings = tokenizer(train_texts, truncation=True, padding=True)
val_encodings = tokenizer(val_texts, truncation=True, padding=True)
test_encodings = tokenizer(test_texts, truncation=True, padding=True)


class MarketNewsDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = MarketNewsDataset(train_encodings, train_labels)
val_dataset = MarketNewsDataset(val_encodings, val_labels)
test_dataset = MarketNewsDataset(test_encodings, test_labels)


from transformers import AlbertForSequenceClassification, Trainer, TrainingArguments

os.makedirs(os.path.join(ROOT, 'models', 'results'), exist_ok=True)
os.makedirs(os.path.join(ROOT, 'models', 'logs'), exist_ok=True)

training_args = TrainingArguments(
    output_dir=os.path.join(ROOT, 'models', 'results'),          # output directory
    num_train_epochs=3,              # total number of training epochs
    per_device_train_batch_size=16,  # batch size per device during training
    per_device_eval_batch_size=64,   # batch size for evaluation
    warmup_steps=500,                # number of warmup steps for learning rate scheduler
    weight_decay=0.01,               # strength of weight decay
    logging_dir=os.path.join(ROOT, 'models', 'logs'),            # directory for storing logs
    logging_steps=10,
)

model = AlbertForSequenceClassification.from_pretrained(pretrain_model_path)

trainer = Trainer(
    model=model,                         # the instantiated 🤗 Transformers model to be trained
    args=training_args,                  # training arguments, defined above
    train_dataset=train_dataset,         # training dataset
    eval_dataset=val_dataset             # evaluation dataset
)

trainer.train()

tokenizer.save_pretrained(os.path.join(ROOT, 'models', 'trained'))
model.save_pretrained(os.path.join(ROOT, 'models', 'trained'))
