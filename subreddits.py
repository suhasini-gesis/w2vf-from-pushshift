import zreader
import json
import pickle

filename = "reddit_subreddits.ndjson.zst"
reader = zreader.Zreader(filename, chunk_size=8192)

top_sub_reds = []

# Read each line from the reader and find all the subreddits with subscribers more than 1000
for line in reader.readlines():
    sub_red = json.loads(line)
    if sub_red['subscribers'] != None and sub_red['subscribers'] >= 1000:
        top_sub_reds.append(sub_red)

with open('subreddits.pickle', 'wb') as f:
    pickle.dump(top_sub_reds, f)