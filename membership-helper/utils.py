import html
from datetime import datetime
import requests
from urllib.parse import urlparse, unquote, parse_qs
from db import get_all_newsletter_names, fetch_all_newsletters

def extract_slug_from_url(post_url):
    """
    Extract the slug from the given URL, handling nested tracking URLs
    and direct slugs in the path.

    Args:
        post_url (str): The full URL containing the slug.

    Returns:
        str: The extracted slug, or None if the slug cannot be found.
    """
    if post_url:
        print(f"postURL : {post_url}")

        # Parse the outer URL
        parsed_url = urlparse(post_url)
        query_params = parse_qs(parsed_url.query)
        print(f"Query params: {query_params}")

        # Case 1: Slug is in the 'url' query parameter
        if 'url' in query_params:
            decoded_url = unquote(query_params['url'][0])
            print(f"decoded_url: {decoded_url}")

            # Parse the decoded URL to get the slug
            parsed_decoded_url = urlparse(decoded_url)
            slug = parsed_decoded_url.path.strip('/').split('/')[-1]
            print(f"Got this slug: {slug}")
            return slug

        # Case 2: Slug is in the main URL path
        path_parts = parsed_url.path.strip('/').split('/')
        if path_parts:
            slug = path_parts[-1]  # Last part of the path
            print(f"Got this slug from main path: {slug}")
            return slug

    # Return None if no slug is found
    print("No valid slug found.")
    return None


def get_post_details(slug, list_id):
    # Extract the slug from the post URL

    #slug = extract_slug_from_url(post_url)
    #print("Slug:", slug)

    # WordPress REST API URL to get the post details by slug
 

    wp_api_url = ""

    if list_id == '7867c6e5a8':
        wp_api_url = f"https://richmondside.org/wp-json/wp/v2/posts?slug={slug}"
    elif list_id == '8612bcc0f3':
        wp_api_url =  f"https://berkeleyside.org/wp-json/wp/v2/posts?slug={slug}"
    elif list_id == 'aad4b5ee64':
        wp_api_url =  f"https://berkeleyside.org/wp-json/wp/v2/posts?slug={slug}"


    try:
        response = requests.get(wp_api_url)

        if response.status_code == 200:
            json_data = response.json()
            if json_data:
                post_data = json_data[0]  # Assuming the slug is unique and returns one post
                return post_data.get('title', {}).get('rendered')
            else:
                print(f"No post data found for slug {slug} at {wp_api_url}")
                return None
        else:
            print(f"Error fetching post details: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Error fetching post details for slug {slug}: {e}")
        return None
    

def clean_headline(headline):
   
    return html.unescape(headline)