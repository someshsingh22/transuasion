import re

def clean_tweet(tweet):
    masked_tweet = re.sub(r'@(\w+)', '<USERNAME>', tweet)
    usernames = re.findall(r'(@\w+)', tweet)
    links = re.findall(r'https?://\S+|www\.\S+', tweet)
    masked_tweet = re.sub(r'https?://\S+|www\.\S+', '<HYPERLINK>', masked_tweet)

    return {
        'cleaned_tweet': masked_tweet,
        'usernames': ' '.join(usernames),
    }