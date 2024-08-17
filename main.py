import urllib3
import json
from bs4 import BeautifulSoup

def chooseCategory():

    # TODO: Dynamic choices
    choices = [
        {'title':'[1] Movies In Theaters', 'value': 'movies_in_theaters'},
        {'title':'[2] Movies At Home', 'value': 'movies_at_home'},
        {'title':'[3] Movies Coming Soon', 'value': 'movies_coming_soon'},
        {'title':'[4] TV Series Browse', 'value': 'tv_series_browse'},
    ]

    for index, choice in enumerate(choices):
        print(choice['title']);

    choice = input("Choose: ")
    category = choices[int(choice) - 1]['value']

    return category

def getFilters():
    url = f"https://www.rottentomatoes.com/browse/"
    ourUrl = urllib3.PoolManager().request('GET', url).data
    soup = BeautifulSoup(ourUrl, "lxml")

    filterContainers = soup.find_all('bottom-sheet-menu', attrs={
        'data-discoveryfiltersmanager': 'bottomSheetMenu:cta1,cta2,hidden',
        'data-watchlistfiltersmanager': 'bottomSheetMenu:cta1,cta2,hidden',
        'data-filter': True,
        'data-qa': True,
    })

    filters = []
    for item in filterContainers:
        filterTitleContainer = item.find(
            'span',
            attrs={
                'class': 'label',
                'data-qa': 'title',
                'slot': 'title',
            }
        )

        filterTitle = filterTitleContainer.text.strip()
        multiple = True if item.find('select-checkbox-group') else False
        dataFilter = item.get('data-filter')
        subFilters = {}


        if filterTitle:
            selectLabelElements = item.find_all('select-label')

            for selectLabel in selectLabelElements:
                title = selectLabel.find('span', attrs={'slot': 'label'}).text.strip()
                value = selectLabel.find('select-radio').get('value') if selectLabel.find('select-radio') else selectLabel.find('select-checkbox').get('value')

                subFilters[title] = value
            filters.append({'title': filterTitle, 'value': subFilters, 'multiple': multiple, 'dataFilter': dataFilter})
    return filters

def chooseFilter(filters):
    queryParts = []

    while True:
        print('Available Filters:')
        for index, value in enumerate(filters):
            print(f"[{index + 1}] {value['title']}")

        chosen = input("Choose a filter or press Enter to finish: ")
        if chosen == "":
            break

        chosenFilter = filters[int(chosen) - 1]
        isMultiple = " (Select multiple, comma separated): " if chosenFilter['multiple'] else " (Select one): "
        print('\n')
        print(f'{chosenFilter["title"]}{isMultiple}')

        for index, (key, value) in enumerate(chosenFilter['value'].items()):
            print(f"[{index + 1}] {key}")

        subFilters = input("Choose: ").split(',')

        filterValues = []
        queryPart = f"{chosenFilter['dataFilter']}:"
        for item in subFilters:
            key = list(chosenFilter['value'])[int(item) - 1]
            filterValues.append(chosenFilter['value'][key])

        queryPart += ",".join(filterValues)
        queryParts.append(queryPart)
    return "~".join(queryParts)

category = chooseCategory()
filters = getFilters()
query = chooseFilter(filters)
page = input("How many pages: ")

url = f"https://www.rottentomatoes.com/browse/{category}/{query}?page={page}"
print(url)
ourUrl = urllib3.PoolManager().request('GET', url).data
soup = BeautifulSoup(ourUrl, "lxml")

container = soup.find(
    'div',
    attrs={
        'class': 'discovery-tiles__wrap',
        'data-qa': 'discovery-media-list',
        'data-adsdiscoverysponsoredmediamanager': 'tilesWrap',
        'data-gridpageadsmanager': 'tilesWrap'
    })

if container:
    movieInfos = container.find_all('tile-dynamic')
    for info in movieInfos:
        movieTitleElement = info.find('span', attrs={'class': 'p--small', 'data-qa': 'discovery-media-list-item-title'})
        criticsScoreElement = info.find('rt-text', attrs={'slot': 'criticsScore', 'context': 'label', 'size': '1'})
        audienceScoreElement = info.find('rt-text', attrs={'slot': 'audienceScore', 'context': 'label', 'size': '1'})
        dateElement = info.find('span', attrs={'class': 'smaller', 'data-qa': 'discovery-media-list-item-start-date'})

        title = movieTitleElement.text.strip() if movieTitleElement.text.strip() else 'No Title.'
        criticsScore = criticsScoreElement.text.strip() if criticsScoreElement.text.strip() else 'No Score.'
        audienceScore = audienceScoreElement.text.strip() if audienceScoreElement.text.strip() else 'No Score.'
        date = dateElement.text.strip() if dateElement.text.strip() else 'No Date.'

        print(f"Movie: {title} | Critic Score: {criticsScore} | Audience Score: {audienceScore} | Date: {date}")
