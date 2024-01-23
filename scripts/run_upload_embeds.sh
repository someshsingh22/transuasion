aws s3 sync s3://<BUCKET>/<PREFIX>/parallel_shards ./parallel_shards
NUM_SHARDS=$(ls ./parallel_shards | wc -l)

for i in $(seq 0 $((NUM_SHARDS-1))); do
    python get_bert_embeds.py --idx $i &
done

aws s3 sync ./parallel_shards_embeddings s3://<BUCKET>/<PREFIX>/parallel_shards_embeddings/