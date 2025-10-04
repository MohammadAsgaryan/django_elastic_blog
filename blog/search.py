from rest_framework.decorators import api_view
from rest_framework.response import Response
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections
from .documents import ArticleIndex

@api_view(['GET'])
def search_articles(request):
    q = request.GET.get('q', '')
    category = request.GET.get('category')
    tag = request.GET.get('tag')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    agg = request.GET.get('agg') 

    client = connections.get_connection()
    s = Search(using=client, index=ArticleIndex.Index.name)

    if q:
        s = s.query('multi_match', query=q, fields=['title', 'content', 'tags.name'])

    if category:
        s = s.filter('term', category=category)

    if tag:
        s = s.query('nested', path='tags', query=Q('term', **{'tags.name': tag}))

    if date_from or date_to:
        range_q = {}
        if date_from:
            range_q['gte'] = date_from
        if date_to:
            range_q['lte'] = date_to
        s = s.filter('range', published_date=range_q)

    if agg == 'category':
        s.aggs.bucket('by_category', 'terms', field='category')
    elif agg == 'tags':
        s.aggs.bucket('by_tags', 'nested', path='tags')
        s.aggs['by_tags'].bucket('names', 'terms', field='tags.name')

    resp = s.execute()

    results = []
    for hit in resp.hits:
        d = hit.to_dict()
        d['id'] = hit.meta.id
        results.append(d)

    aggs = resp.aggregations.to_dict() if hasattr(resp, 'aggregations') else {}

    return Response({'results': results, 'aggregations': aggs})
