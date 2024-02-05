import re
from urllib.parse import urlparse
import pandas as pd
from collections import Counter

def get_domain(d):
    d = [_d for _d in d.split('.') if not _d in ["www", "com"]]
    if 'ly' in d or "bitly" in d:
        return ""
    else:
        return " Its domain is " + '.'.join(d) + ' '

def convert_url_to_tags(url, remove_tags=None):
    words = re.findall(r'[A-Za-z0-9]+', url)
    processed_words = []
    for word in words:
        words_split = re.findall(r'[a-z0-9]+|[A-Z][a-z0-9]*', word)
        processed_words.extend(words_split)
    
    if remove_tags:
        filtered_words = [word for word in processed_words if (word.isalpha() and len(word)>1 and (not (word in remove_tags))) or (word.isdigit() and int(word) <= 2025)]
        # Join the filtered words to create the desired string format
        result_string = "', '".join(filtered_words)
        if len(result_string)>0:
            return " The webpage can be described by keywords: '" + result_string + "' ."
        else:
            return ""
    else:
        filtered_words = [word for word in processed_words if (word.isalpha() and len(word)>1) or (word.isdigit() and int(word) <= 2025)]
        result_string = ' '.join(filtered_words)
        return result_string
    
def get_url_verb_dict(url_column, en):
    rurl = url_column.apply(lambda x: urlparse(x[x.find('next=')+5:]) if 'next=' in x else urlparse(x))
    url_df = pd.DataFrame({'url':rurl, 'rurl':url_column})
    url_df['netloc'] = url_df['url'].apply(lambda x: x.netloc)
    url_df['path'] = url_df['url'].apply(lambda x: x.path)
    url_df['query'] = url_df['url'].apply(lambda x: x.query)
    url_df['fragment'] = url_df['url'].apply(lambda x: x.fragment)
    url_df["verb"] = url_df['path'].apply(lambda x: convert_url_to_tags(x))
    x = ' '.join(url_df["verb"]).lower().split()
    remove_tags = {k for k,v in Counter(x).items() if v<3 and k} - en
    domain_verb = url_df['netloc'].apply(get_domain)
    url_df['path'] = url_df['path'].apply(lambda x: '' if len(x)==7 else x)
    url_df['verb'] = domain_verb + url_df['path'].apply(lambda x: convert_url_to_tags(x, remove_tags=remove_tags))
    url_df['verb'] = url_df['verb'].apply(lambda x: "The tweet has a webpage linked to it. " +x if len(x)>10 else x)
    url_df['url'] = url_df['url'].astype(str)
    url_verb = url_df.set_index('rurl')["verb"].to_dict()
    return url_verb, url_df