import requests


def transform_ratings(ratings_list):
    if not ratings_list:
        return {}
    ratings_dict = {}
    for rating in ratings_list:
        if not isinstance(rating, dict) or 'Source' not in rating or 'Value' not in rating:
            continue
        source = rating['Source']
        value = rating['Value']
        cleaned_value = ''.join(filter(str.isdigit, value.split('/')[0].split('%')[0]))
        ratings_dict[source] = cleaned_value
    return ratings_dict


def get_movie_info(title):
    api_key = 'api_key_here'
    url = f'http://www.omdbapi.com/?apikey={api_key}&t={title}&plot=full'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data['Response'] == 'True':
            if 'Ratings' in data:
                data['Ratings'] = transform_ratings(data['Ratings'])
            return data
        else:
            print('Error from OMDb API:', data['Error'])
            return None
    except requests.exceptions.RequestException as e:
        print('Network Error:', e)
        return None
