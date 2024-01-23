import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModel
from torch.multiprocessing import Pool
import os, glob
import argparse

num_gpus = 8

def process_chunk(gpu_no, index_list, text_list):
    batch_size = 16384
    gpu_no = gpu_no % num_gpus
    device = f"cuda:{gpu_no}"
    tokenizer = AutoTokenizer.from_pretrained('bert-large-uncased')
    model = AutoModel.from_pretrained('bert-large-uncased').to(device)
    batches = [text_list[i:i + batch_size] for i in range(0, len(text_list), batch_size)]
    batch_indices = [index_list[i:i + batch_size] for i in range(0, len(index_list), batch_size)]
    for batch_no, (batch_index, batch_text) in enumerate(zip(batch_indices, batches)):
        inputs = tokenizer(batch_text, return_tensors="pt", padding=True, truncation=True).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1).detach().cpu()
        result_dict = {"index": batch_index, "embeddings": embeddings}
        file_name = f"embeds/batch_gpu{gpu_no}_{batch_no}.pt"
        torch.save(result_dict, file_name)

parser = argparse.ArgumentParser()
parser.add_argument("--idx", type=int, default=0)
args = parser.parse_args()

if __name__ == '__main__':
    dff = 'parallel_shards/' + sorted(os.listdir('parallel_shards/'))[args.idx]
    
    if os.path.exists(dff.replace('shards', 'shards_embeddings').replace('parquet', 'pt')):
        print(f"Skipping {dff} as it already exists")
        exit()
    
    df = pd.read_parquet(dff).drop_duplicates('id')[['clean_tweet', 'id']]
    chunks = [
        (i, df_chunk['id'].tolist(), df_chunk['clean_tweet'].tolist()) for i, df_chunk in enumerate([df.iloc[i:i + len(df) // num_gpus] for i in range(0, len(df), len(df) // num_gpus)])
    ]
    
    with Pool(processes=num_gpus) as pool:
        pool.starmap(process_chunk, chunks)
        embeds = [torch.load(f) for f in glob.glob('embeds/*.pt')]
        embed = {'index':[], 'embeddings':[]}
    
    for emb in embeds:
        embed['index'].extend(emb['index'])
        embed['embeddings'].append(emb['embeddings'])
    
    embed['embeddings'] = torch.cat(embed['embeddings'])
    torch.save(embed, dff.replace('shards', 'shards_embeddings').replace('parquet', 'pt'))
    
    rm = [os.remove(f) for f in glob.glob('embeds/*.pt')]