import glob
import numpy as np
import scipy.sparse as sp
from gensim.models import Doc2Vec
from lightfm import LightFM
from lightfm.evaluation import precision_at_k
from lightfm.evaluation import auc_score

def predict(user_id, item_ids, item_features, document_list):
    output = model.predict(
        user_id,
        item_ids,
        item_features = item_features,
        num_threads = 2
    )
    combined_output = zip(output, document_list)
    combined_output = sorted(combined_output, key = lambda x: -x[0])
    top = combined_output[0:20]
    for item in top:
        print('score: {}'.format(item[0]))
        print('file: {}'.format(item[1]['file']))


# getting input
print('getting input')
print('...............')
list_of_files = glob.glob('/home/rakvat/mydev/nlp_experiments/scrape_anarchist_library/en/*.txt')
documents = {}
for filename in list_of_files:
    content = []
    f = open(filename, 'r')
    for line in f:
        content.append(line)
    f.close()
    documents[filename.split('/')[-1]] = content


# preprocessing
print('preprocessing')
print('...............')
for key, value in documents.items():
    document = {}
    first_line_without_meta = 0
    for i, line in enumerate(value[:15]):
        if line.startswith('#author'):
            document['author'] = line[8:-1]
        if line.startswith('#title'):
            document['title'] = line[7:-1]
        if first_line_without_meta == 0 and line[0] != '#':
            first_line_without_meta = i
    document['text'] = ''.join(value[first_line_without_meta:])
    document['length'] = len(document['text'])
    document['file'] = key
    document['author'] = document.get('author', '-')
    documents[key] = document

document_list = [d for d in documents.values()]

# building the model
print('building model')
print('...............')

good_texts = [
    'economics-of-freedom.muse.txt',
    'paul-buckermann-on-socialist-cybernetics.muse.txt',
    'gaston-leval-libertarian-socialism-a-practical-outline.muse.txt',
    'diego-abad-de-santillan-after-the-revolution.muse.txt',
    'james-guillaume-ideas-on-social-organization.muse.txt',
    'ilan-shalif-glimpses-into-the-year-2100-50-years-after-the-revoution.muse.txt',
]
#good_texts = [
#    'emma-goldman-marriage-and-love.muse.txt',
#    'aviv-etrebilal-butterflies-polyamory-and-ideology.muse.txt',
#    'susan-song-polyamory-and-queer-anarchism-infinite-possibilities-for-resistance.muse.txt',
#    'emile-armand-on-sexual-liberty.muse.txt',
#]
good_ids = []
for idx, document in enumerate(document_list):
    if document['file'] in good_texts:
        good_ids.append(idx)
print(good_ids)
num_good = len(good_ids)

fname = 'data/doc2vec_model'
doc_2_vec_model = Doc2Vec.load(fname)
l = list(map(lambda x: doc_2_vec_model.docvecs[x], range(0,len(document_list))))
X = np.concatenate(l).reshape((len(l), 300))
doc2vec_data = sp.csr_matrix(X)

model = LightFM(no_components=1, loss='warp')
num_items = len(document_list)
item_ids = np.arange(num_items)
user_id = 0

length_rows = np.arange(0, num_items)
length_columns = [0] * num_items
item_features = doc2vec_data
interaction_matrix = sp.coo_matrix(([1]*num_good, ([0]*num_good, good_ids)), shape = (1, num_items))
test_matrix = interaction_matrix # yes, I know, I should not take that as test data

# training
print('training')
print('...............')
for i in range(0, 1000):
    print('iteration {}'.format(i))
    model.fit_partial(
        interaction_matrix,
        item_features = item_features,
        epochs = 1,
        num_threads = 2,
    )
    print('in progress prediction')
    predict(user_id, item_ids, item_features, document_list)

    score = auc_score(model, test_matrix, item_features=item_features, num_threads = 2)
    print('auc score: {}'.format(score))


# output prediction
print('final prediction')
print('...............')
predict(user_id, item_ids, item_features, document_list)

