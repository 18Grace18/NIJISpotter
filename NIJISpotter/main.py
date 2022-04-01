from flask import Flask, render_template, jsonify, request
from elasticsearch import Elasticsearch
import math

es = Elasticsearch()
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():

    keyword = request.args.get('keyword')

    page_size = 10
    if request.args.get('page'):
        page_no = int(request.args.get('page'))
    else:
        page_no = 1

    body = {
        'size': page_size,
        'from': page_size * (page_no-1),
        'query': {
            'multi_match': {
                'query': keyword,
                'type': 'most_fields', #calculated from the combination of all the matching fields
                'fields': ['firstname', 'lastname', 'profile'],
                'fuzziness': "AUTO", #handle typos
                'analyzer': "my_analyzer", #using the analyzer configured from elasticsearch/kibana
                'operator': "or" #either match one of the fields
            }
        }
    }

    res = es.search(index='livers', body=body)

    hits = [{'firstname': doc['_source']['firstname'], 
    'lastname': doc['_source']['lastname'], 'profile': doc['_source']['profile'], 
    'image_url': doc['_source']['image_url'], 'youtube': doc['_source']['youtube'], 
    'twitter': doc['_source']['twitter'], 'character_designer': doc['_source']['character_designer'], 
    'debut_date': doc['_source']['debut_date'], '_score': doc['_score']} for doc in res['hits']['hits']]

    page_total = math.ceil(res['hits']['total']['value']/page_size)
    return render_template('search.html', keyword=keyword, hits=hits, page_no=page_no, page_total=page_total)