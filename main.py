import requests
import re
import time
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

def scrape_chess_openings(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the div containing the list of chess openings
        openings_div = soup.find('div', class_='elementor-element '
                                               'elementor-element-7f0d9d87 '
                                               'elementor-widget elementor-widget-shortcode')

        opening_names = []
        opening_images = []

        for opening in openings_div.find_all('a'):
            opening_names.append(opening.find('h5').text.strip())
            opening_images.append(opening.find('img')['src'])

        return opening_names, opening_images

    else:
        print('Failed to retrieve page:', response.status_code)
        return None

def create_main_page_markdown(opening_names, opening_images, filename):
    with open(filename, 'w', encoding='utf-8-sig') as f:
        f.write('# List of Chess Openings\n\n')
        f.write('---\n\n')
        for name, image_url in zip(opening_names, opening_images):
            f.write(f'## {name}\n\n')
            f.write(f'![{name}]({image_url})\n\n')
            f.write(f'### [Tutorials](tutorials/{name}.md)\n\n')


def escape_markdown(text):
    escape_dict = {
        '\\': '\\\\',
        '*': '\\*',
        '_': '\\_',
        '#': '\\#',
        '[': '\\[',
        ']': '\\]',
        '(': '\\(',
        ')': '\\)',
        '<': '\\<',
        '>': '\\>',
        '|': '\\|'
    }

    escaped_text = re.sub(r'([\\*_#\[\]<>|()])', lambda match: escape_dict[match.group()], text)
    return escaped_text

def find_videos(opening):
    results = DDGS().videos(f'{opening} chess tutorial youtube', safesearch='on', max_results=5)

    # Avoid the ratelimit exception
    time.sleep(6)

    titles = []
    links = []

    for result in results:
        escaped_title = escape_markdown(result['title'])
        titles.append(escaped_title)
        links.append(result['content'])

    return links, titles

def create_page_with_tutorials_markdown(opening):
    with open(f'tutorials/{opening}.md', 'w', encoding='utf-8-sig') as f:
        f.write(f'# {opening} Tutorials\n\n')
        f.write('---\n\n')

        links, titles = find_videos(opening)

        for link, title in zip(links, titles):
            f.write(f'[{title}]({link})\n\n')


if __name__ == '__main__':
    chess_site_url = 'https://www.thechesswebsite.com/chess-openings/'
    opening_names, opening_images = scrape_chess_openings(chess_site_url)
    if opening_names and opening_images:
        filename = 'opening_list.md'
        create_main_page_markdown(opening_names, opening_images, filename)

        for opening in opening_names:
            create_page_with_tutorials_markdown(opening)
