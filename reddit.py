import logging
from modules import hash_sha256, translate_to_english, extract_urls_from_text, find_one_document, datetime_to_string, insert_into_mongo, retrieve_key_list, read_config, update_post_counts
from datetime import datetime
import requests
import pytz
import requests
from random import randint
import praw

logging.basicConfig(filename='reddit.log', 
                    filemode='a', 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
# Get the logger instance
logger = logging.getLogger(__name__)

def reddit_main_info():
    try:
        try:
            existing_document = find_one_document('forum', 'reddit', 'forums', 'cw_scrapers')

            daily = existing_document.get('daily')
            weekly = existing_document.get('weekly')
            monthly = existing_document.get('monthly')
            total = existing_document.get('total')
            last_updated = existing_document.get('last_updated')
            forum_info = {'forum': 'reddit', 'forum_link': 'https://www.reddit.com', 'daily': daily, 'weekly':weekly, 'monthly': monthly, 'total': total, 'last_updated': last_updated}
            response = insert_into_mongo('cw_scrapers', 'forums', forum_info, 'forum')
            if 200 <= response.status_code < 300:
                logger.info(response.text)
            else:
                logger.error(f"API call failed with status code {response.status_code}: {response.text}")
        except:
            daily = 0
            weekly = 0
            monthly = 0
            total = 0
            last_updated = datetime_to_string(datetime.now(pytz.utc))
            forum_info = {'forum': 'reddit', 'forum_link': 'https://www.reddit.com', 'daily': daily, 'weekly':weekly, 'monthly': monthly, 'total': total, 'last_updated': last_updated}
            response = insert_into_mongo('cw_scrapers', 'forums', forum_info, 'forum')
            if 200 <= response.status_code < 300:
                logger.info(response.text)
            else:
                logger.error(f"API call failed with status code {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}") 

def search_subreddits(word_list, client_id, client_secret, user_agent, username, password):
    logger.info("starting search_subreddits")
       
    # Create a Reddit instance
    reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     username=username,
                     password=password,
                     user_agent=user_agent)

    
    for word in word_list:
        logger.info(f"Searching for {word}")
        subreddits_info = []
        users = []
        # Define the search query
        search_query = word  # replace with your search query

        for post in reddit.subreddit('all').search(search_query, limit=None):
            # logger.info(f"Title: {post.title}\nURL: {post.url}\n")
            post_content = post.selftext
            if not post_content:  # This will be true if post_content is None or an empty string
                post_content = post.url
            try:
                thread_link = f"https://www.reddit.com{post.permalink}"
            except:
                continue
            try:
                subreddit = str(post.subreddit)
            except:
                subreddit = None
            try:
                thread_title = post.title
            except:
                thread_title = None
            try:
                username = str(post.author)
            except:
                username = None
            try:
                joined = post.author.created_utc
            except:
                joined = None
            try:
                moderator = post.author.is_mod
            except:
                moderator = None
            try:
                gold_status = post.author.is_gold
            except:
                gold_status = None
            try: 
                profile_url = f"https://www.reddit.com/user/{username}"
            except:
                profile_url = None
            try:
                urls_in_post = extract_urls_from_text(post_content)
            except:
                urls_in_post = None
            try:
                post_content_in_english = translate_to_english(post_content)
            except:
                post_content_in_english = None
            try:
                created_utc = post.created_utc
                created_time = datetime.utcfromtimestamp(created_utc).strftime('%Y-%m-%d %H:%M:%S')
            except:
                created_utc = None
                created_time = None
            try:
                score = post.score
            except:
                score = None
            main_post = {"username": username, "profile_url": profile_url, "urls_in_post": urls_in_post, "post_content": post_content, "post_content_in_english": post_content_in_english, "date_posted": created_time, "date_posted_unix": created_utc, "score": score, "post_number": 1, "post_type": "post"}
            subreddit_info = {"forum": "reddit", "forum_link": "https://www.reddit.com", "subreddit": subreddit, "thread_title": thread_title, "thread_link": thread_link, "post": main_post}    
            user_info = {"username": username, "joined": joined, "moderator": moderator, "gold_status": gold_status, "profile_url": profile_url}
            subreddits_info.append(subreddit_info)
            users.append(user_info)
    
            
        try:
            response = insert_into_mongo('cw_scrapers', 'reddit_threads', subreddits_info, 'thread_link')
            if 200 <= response.status_code < 300:
                logger.info(response.text)
            else:
                logger.error(f"API call failed with status code {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
        try:
            response = insert_into_mongo('cw_scrapers', 'reddit_users', users, 'username')
            if 200 <= response.status_code < 300:
                logger.info(response.text)
            else:
                logger.error(f"API call failed with status code {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")


def extract_posts(client_id, client_secret, user_agent, username, password):
    logger.info("starting extract_posts")
    
    forum = "reddit"
    forum_link = "https://www.reddit.com"
    main_posts = retrieve_key_list('reddit_threads', 'post', 'cw_scrapers')
    subreddits = retrieve_key_list('reddit_threads', 'subreddit', 'cw_scrapers')
    thread_titles = retrieve_key_list('reddit_threads', 'thread_title', 'cw_scrapers')   
    thread_links = retrieve_key_list('reddit_threads', 'thread_link', 'cw_scrapers')  
    # Create a Reddit instance
    reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     username=username,
                     password=password,
                     user_agent=user_agent)
    
    for main_post, subreddit, thread_title, thread_link in zip(main_posts, subreddits, thread_titles, thread_links):
    
        submission = reddit.submission(url=thread_link)

        # Expand all comments
        submission.comments.replace_more(limit=None)
        post_and_replies = []
        post_and_replies.append(main_post)
        replies = []
        users = []
        def process_comments(comments, count=2):
            """Recursively process and log comments and their replies."""
            for comment in comments:
                post_content = comment.body
                if not post_content:  # This will be true if post_content is None or an empty string
                    post_content = comment.url
                
                try:
                    username = str(comment.author)
                except:
                    username = None
                try:
                    joined = comment.author.created_utc
                except:
                    joined = None
                try:
                    moderator = comment.author.is_mod
                except:
                    moderator = None
                try:
                    gold_status = comment.author.is_gold
                except:
                    gold_status = None
                try: 
                    profile_url = f"https://www.reddit.com/user/{username}"
                except:
                    profile_url = None
                try:
                    urls_in_post = extract_urls_from_text(post_content)
                except:
                    urls_in_post = None
                try:
                    post_content_in_english = translate_to_english(post_content)
                except:
                    post_content_in_english = None
                try:
                    created_utc = comment.created_utc
                    created_time = datetime.utcfromtimestamp(created_utc).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    created_utc = None
                    created_time = None
                try:
                    score = comment.score
                except:
                    score = None
                
                reply_info = {"username": username, "profile_url": profile_url, "urls_in_post": urls_in_post, "post_content": post_content, "post_content_in_english": post_content_in_english, "date_posted": created_time, "date_posted_unix": created_utc, "score": score, "post_number": count, "post_type": "reply"}
                replies.append(reply_info)
                post_and_replies.append(reply_info)
                user_info = {"username": username, "joined": joined, "moderator": moderator, "gold_status": gold_status, "profile_url": profile_url}
                users.append(user_info)
                count = process_comments(comment.replies, count + 1)
            return count

        # Process and log all top-level comments
        process_comments(submission.comments)

        posts_hash = hash_sha256(post_and_replies)
        existing_document_hash = None
        existing_document = find_one_document('thread_link', 'value=None', 'reddit_posts', 'cw_scrapers', thread_link)
        if existing_document:
            existing_document_hash = existing_document.get('hash')
        if existing_document_hash == posts_hash:
            logger.info(f"No changes to {thread_link}")
            continue 
        elif existing_document_hash != posts_hash and existing_document is not None:
            existing_document_date_scraped = existing_document.get('date_scraped')
            existing_document_unix_time = existing_document.get('date_scraped_unix')

            current_datetime = datetime.now()
            updated_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Truncate to 6 decimal places
            updated_unix_time = current_datetime.timestamp()
        
            post_information = {"thread_link": thread_link, "subreddit": subreddit, "date_scraped": existing_document_date_scraped, "date_scraped_unix": existing_document_unix_time, "forum": forum, "forum_link": forum_link, "hash": posts_hash, "post": main_post, "replies": replies,"thread_title": thread_title, "updated_at": updated_datetime, "updated_at_unix_time": updated_unix_time}
            try:
                response = insert_into_mongo('cw_scrapers', 'reddit_posts', post_information, 'thread_link')
                if 200 <= response.status_code < 300:
                    logger.info(response.text)
                else:
                    logger.error(f"API call failed with status code {response.status_code}: {response.text}")
                    continue
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed: {e}")
                continue
            try:
                insert_into_mongo('cw_scrapers', 'reddit_users', users, 'username')
            except Exception as e:
                logger.error(f"Failed to upload user information")
                logger.error(f"{e}")
            try:
                logger.info("trying to update post count")
                update_post_counts(1, 'forum', 'reddit', 'forums', 'cw_scrapers')
            except Exception as e:
                logger.error(f"Failed to update count on thread {thread_link}")
                logger.error(f"{e}")
        else:
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Truncate to 6 decimal places
            unix_time = current_datetime.timestamp()
            post_information = {"thread_link": thread_link,"subreddit": subreddit, "date_scraped": formatted_datetime, "date_scraped_unix": unix_time, "forum": forum, "forum_link": forum_link, "hash": posts_hash, "post": main_post, "replies": replies, "thread_title": thread_title}
            try:
                response = insert_into_mongo('cw_scrapers', 'reddit_posts', post_information, 'thread_link')
                if 200 <= response.status_code < 300:
                    logger.info(response.text)
                else:
                    logger.error(f"API call failed with status code {response.status_code}: {response.text}")
                    continue
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed: {e}")
                continue
            
            try:
                insert_into_mongo('cw_scrapers', 'reddit_users', users, 'username')
            except Exception as e:
                logger.error(f"Failed to upload user information")
                logger.error(f"{e}")
            
            try:
                logger.info("trying to update post count")
                update_post_counts(1, 'forum', 'reddit', 'forums', 'cw_scrapers')
            except Exception as e:
                logger.error(f"Failed to update count on thread {thread_link}")
        
        
        logger.info(f"Finished processing comments for {thread_link}.")
    
def main():
    config = read_config("config.json")
    client_id = config.get('client_id')
    client_secret = config.get('client_secret')
    user_agent = config.get('user_agent')
    username = config.get('username')
    password = config.get('password')
    with open('keywords.txt', 'r') as file:
        # Read the file content and split by new lines
        word_list = file.read().splitlines()
    reddit_main_info()
    search_subreddits(word_list, client_id, client_secret, user_agent, username, password)
    extract_posts(client_id, client_secret, user_agent, username, password)

if __name__ == "__main__":
    main()