import os

import pandas as pd
from torch.utils.data import Dataset
from transformers import (AutoModelWithLMHead, Trainer, AutoTokenizer, TextDataset,
                          DataCollatorForLanguageModeling, TrainingArguments, GPT2LMHeadModel, pipeline)

from util.utils import ROOT_DIR


def combine_data():
    df = pd.read_csv(ROOT_DIR + 'data/training/training_data.csv', delimiter='\t')
    df['combined'] = '<s>' + df.get('original') + '</s>>>>><p>' + df.get('paraphrased') + '</p>'
    df['combined'] = df.combined.to_csv(ROOT_DIR + 'data/training/combined', sep='\n', index=False)


def train_model(text_path, epochs, model='gpt2', batch_size=2, cache_dir='cache'):
    model = GPT2LMHeadModel.from_pretrained(model)
    tokenizer = AutoTokenizer.from_pretrained('gpt2', bos_token='<s>', eos_token='</p>', pad_token='<pad>',
                                              max_length=512, sep='\n', delimiter='\n')
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False, )
    model.resize_token_embeddings(len(tokenizer))

    train_dataset = TextDataset(
        tokenizer=tokenizer,
        file_path=text_path,
        block_size=256
    )

    print(len(train_dataset))

    training_args = TrainingArguments(
        output_dir=ROOT_DIR + "data/training/gpt2_fine_tune/{}".format(os.path.basename(text_path)),
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        warmup_steps=500,
        save_steps=2000,
        logging_steps=10
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=train_dataset
    )

    trainer.train()
    trainer.save_model()


def generate(original):
    model = GPT2LMHeadModel.from_pretrained(ROOT_DIR + 'data/training/gpt2_fine_tune/combined.txt', max_length=512)
    tokenizer = AutoTokenizer.from_pretrained('gpt2', bos_token='<s>', eos_token='</p>', pad_token='<pad>')
    generator = pipeline('text-generation', model=model, tokenizer=tokenizer)
    model.resize_token_embeddings(len(tokenizer))
    return generator('<s>' + original + '</s>>>>><p>')


if __name__ == "__main__":
    # combine_data()
    train_model(ROOT_DIR + 'data/training/combined.txt', 1)
    print(generate(
        'Stockfish answers with the Scandinavian Defense. Stockfish moves the pawn up to d5. You may want to try b2b3, b2b4 or g1f3. Playing b2b3 leads to the Scandinavian Defense. Playing b2b4 leads to the Zilbermints Gambit. Playing g1f3 leads to the Zukertort Opening: Tennison Gambit.'))
    print(generate('Hello'))
