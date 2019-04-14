import boto3
import datetime
from imdb import IMDb


def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('plex-collection')
    m = event["Records"][0]["s3"]["object"]["key"][7:-4].replace("+", " ")
    print(m)
    ia = IMDb()
    today = datetime.datetime.today().strftime('%Y %m %d')
    s_result = ia.search_movie(m)
    entry = s_result[0]
    ia.update(entry)
    m_search = m.replace(" ", "").replace(":", "").replace("-", "").replace("'", "").replace(".", "").replace(",","")
    m_search = m_search.lower()
    data_input = {}
    data_input['Search Title'] = m_search
    data_input['Title'] = m
    data_input['Plot'] = entry['plot'][0]
    data_input['Genres'] = entry['genres']
    release_date = entry['original air date'][:11]
    datetime_object = datetime.datetime.strptime(release_date, '%d %b %Y')
    data_input['Release Date'] = datetime_object.strftime('%Y %m %d')
    data_input['Add Date'] = today
    data_input['Year'] = datetime_object.strftime('%Y')
    table.put_item(Item=data_input)
    return data_input
