import json
import boto3
import urllib3

ES_CONFIG = {
    "url": "https://search-yelp-restaurants-es-coi3ozmqyi2g5vr624aing4dja.us-east-1.es.amazonaws.com/",
    "index": "photos",
    "type": "photo",
    "master-username": "chatbot-es-root",
    "master-password": "CCBD-es-123456"
}


def search_es(search_labels):
    """
    Make an Elasticsearch query
    """
    http = urllib3.PoolManager()
    url = "%s%s/%s/_search?" % (ES_CONFIG["url"], ES_CONFIG["index"], ES_CONFIG["type"])
    headers = urllib3.make_headers(basic_auth='%s:%s' % (ES_CONFIG["master-username"], ES_CONFIG["master-password"]))
    headers.update({
        'Content-Type': 'application/json',
        "Accept": "application/json"
    })

    all_responses = []
    for i in range(len(search_labels)):
        print(search_labels[i])

        payload = {
            "query": {
                "match": {
                    "labels": "%s" % search_labels[i]
                }
            }
        }

        response = http.request('GET', url, headers=headers, body=json.dumps(payload))
        status = response.status
        data = json.loads(response.data)
        data = data['hits']['hits']
        for d in data:
            image_url = "https://" + d['_source']['bucket'] + ".s3.amazonaws.com/" + d['_source']['object_key']
            all_responses.append({
                'image-url': image_url,
                'labels': d['_source']['labels']
            })

        print("ES Response: [%s] %s" % (status, data))

    return all_responses


def prepare_error_response():
    return []


def prepare_search_response(images_data):
    unique_images = list({x['image-url']: x for x in images_data}.values())
    print(unique_images)
    return unique_images


def lambda_handler(event, context):
    # TODO implement
    print("Event: %s" % event)

    try:
        query_text = event["q"]
        # query = event["messages"][0]["text"] #parse user query
        # lex_response_labels = lex_handler(query) # send query to lex and get labels

        lex_response_labels = ['dog', 'tree']
        # lex_response_labels = query_text
        images_data = search_es(lex_response_labels)

        response = prepare_search_response(images_data)
        print("Queried data : %s" % response)


    except Exception as e:
        print("Error: %s" % str(e))
        response = prepare_error_response()

    print("Response: %s" % response)
    return response
