import boto3
from boto3.dynamodb.conditions import Key, Attr


def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    else:
        return 'Nada'


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "ProvideUserName":
        return set_user_name(intent, session)
    elif intent_name == "WatchMovie":
        if test_user_id(session) == 'Pass':
            return watch_movie_from_session(intent, session)
        else:
            return get_welcome_response()
    elif intent_name == "RecentReleases":
        if test_user_id(session) == 'Pass':
            return share_recent_releases_from_session(intent, session)
        else:
            return get_welcome_response()
    elif intent_name == "SearchForMovie":
        if test_user_id(session) == 'Pass':
            return search_for_movie(intent, session)
        else:
            return get_welcome_response()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    else:
        raise ValueError("Invalid intent")


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to plex select, please start by providing your user name."
    reprompt_text = "Once again, please start by providing your user name"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def test_user_id(session):
    try:
        user_id = session['attributes']['owner']
        return 'Pass'
    except:
        return 'Fail'


def set_user_name(intent, session):
    owner_name = intent['slots']['name']['value'].lower()
    dynamodb = boto3.resource('dynamodb')
    id_table = dynamodb.Table('plex-id')
    if id_table.query(KeyConditionExpression=Key('name').eq(owner_name))['Count'] > 0:
        session_attributes = {"owner": owner_name}
        card_title = "UserID"
        reprompt_text = None
        should_end_session = False
        speech_output = "Hi "+owner_name.title()+", welcome! "\
                        "Please ask to watch the movie you would like to see or ask for recent releases. " \
                        "Alternatively, search for movies by saying search and the term you want to search for. "
    else:
        session_attributes = {}
        card_title = "UserIDFail"
        reprompt_text = None
        should_end_session = False
        speech_output = "I don't recognize that name please try again."
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def search_for_movie(intent, session):
    session_attributes = session['attributes']
    reprompt_text = None
    dynamodb = boto3.resource('dynamodb')
    movie_table = dynamodb.Table('plex-select-collection')
    search_request = intent['slots']['movie']['value']
    search_clean = search_request.replace(" ", "").replace(":", "").replace("-", "").replace("'", "").replace(",", "")
    search_clean = search_clean.lower()
    search_results = movie_table.scan(Select='ALL_ATTRIBUTES', FilterExpression=Attr('Search Title').contains(search_clean))
    if search_results['Count'] <= 15:
            results_to_return = search_results['Count']
    else:
        results_to_return = 15
    results = ''
    for i in range(results_to_return):
        results += search_results['Items'][i]['Title']+', '
    if results_to_return == 0:
        speech_output = "No search results"
    else:
        speech_output = "Available movies include: "+results[:-2]
    should_end_session = False
    response = build_response(session_attributes, build_speechlet_response(intent['name'], speech_output, reprompt_text, should_end_session))
    return response


def share_recent_releases_from_session(intent, session):
    session_attributes = session['attributes']
    reprompt_text = None
    dynamodb = boto3.resource('dynamodb')
    movie_table = dynamodb.Table('plex-select-collection')
    response = movie_table.scan(Select='ALL_ATTRIBUTES', FilterExpression=Attr('Year').gt("2016"))
    response_dict = {}
    for i in response['Items']:
        response_dict[i['Release Date']] = i['Title']
    release_dates = list(response_dict.keys())
    release_dates.sort(reverse=True)
    recent = ''
    for i in release_dates[:10]:
        recent += response_dict[i]+', '
    speech_output = "Recent releases: "+recent[:-1]
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(intent['name'], speech_output, reprompt_text, should_end_session))


def watch_movie_from_session(intent, session):
    session_attributes = session['attributes']
    reprompt_text = None
    movie = intent['slots']['movie']['value'].title()
    movie_clean = movie.replace(" ", "").replace(":", "").replace("-", "").replace("'", "").replace(",", "")
    movie_clean = movie_clean.lower()
    owner = session['attributes']['owner'].lower()
    dynamodb = boto3.resource('dynamodb')
    movie_table = dynamodb.Table('plex-select-collection')
    if movie_table.query(KeyConditionExpression=Key('Search Title').eq(movie_clean))['Count'] > 0:
        file_name = movie_table.query(KeyConditionExpression=Key('Search Title').eq(movie_clean))['Items'][0]['Title']
        ec2 = boto3.client('ec2', region_name="us-east-1")
        instance = ec2.run_instances(
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': file_name

                        },
                        {
                            'Key': 'Relaunch',
                            'Value': 'F'

                        },
                        {
                            'Key': 'Owner',
                            'Value': owner

                        },
                        ]

                },
                ],
                LaunchTemplate={
                    'LaunchTemplateName': 'plex-select-ec2-launch-template',
                    'Version': '1'},
                    MaxCount = 1,
                    MinCount = 1
                    )
        speech_output = "Launching "+file_name+" server, check your Plex app in 10 to 20 minutes and look for "+file_name+" server"
        should_end_session = True
        response = build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))
    else:
        words=movie.split()
        if words[0] == 'the' or words[0] == 'a':
            search_word = words[1]
        else:
            search_word = words[0]
            search_word_clean = search_word.replace(" ", "").replace(":", "").replace("-", "").replace("'", "").replace(",", "")
            search_word_clean = search_word_clean.lower()
            search_results = movie_table.scan(Select='ALL_ATTRIBUTES', FilterExpression=Attr('Search Title').contains(search_word_clean))
        if search_results['Count']<=15:
            results_to_return = search_results['Count']
        else:
            results_to_return = 15
        alternatives = ''
        for i in range(results_to_return):
            alternatives += search_results['Items'][i]['Title']+', '
        speech_output = movie+" is not available did you mean one of the following: "+alternatives[:-2]
        should_end_session = False
        response =  build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))
    return response


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
