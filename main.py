import requests
import pyfiglet
from colorama import Fore, Style
import argparse
import concurrent.futures
import os
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

class UserProfile:
    """
    Represents a user profile on a social media site.
    """
    def __init__(self, username, site_name, url, followers=None, following=None, bio=None, pfp_url=None, additional_info=None):
        self.username = username
        self.site_name = site_name
        self.url = url
        self.followers = followers
        self.following = following
        self.bio = bio
        self.pfp_url = pfp_url
        self.additional_info = additional_info or {}

    def to_dict(self):
        """
        Returns a dictionary representation of the user profile.
        """
        return {
            "username": self.username,
            "site_name": self.site_name,
            "url": self.url,
            "followers": self.followers,
            "following": self.following,
            "bio": self.bio,
            "pfp_url": self.pfp_url,
            "additional_info": self.additional_info
        }

    def __str__(self):
        """
        Returns a string representation of the user profile.
        """
        return json.dumps(self.to_dict(), indent=4)

def extract_domain(url):
    """
    Extracts the domain name from a URL.

    Args:
        url (str): The URL to extract the domain from.

    Returns:
        str: The domain name.
    """
    try:
        parsed_uri = urlparse(url)
        domain = '{uri.netloc}'.format(uri=parsed_uri)
        return domain
    except:
        return None

def check_site(username, site, timeout=10, max_retries=3):
    """
    Checks if a username exists on a given site and retrieves profile information.

    Args:
        username (str): The username to search for.
        site (dict): A dictionary containing the site's name, URL, and existence status.
        timeout (int): Timeout for the request in seconds.
        max_retries (int): Maximum number of retries for failed requests.

    Returns:
        UserProfile: A UserProfile object if the username was found, None otherwise.
    """
    url = site["url"].format(username)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            soup = BeautifulSoup(response.content, 'html.parser')
            followers, following, bio, pfp_url = None, None, None, None
            additional_info = {}

            if site["name"] == "Instagram":
                try:
                    data = soup.find("meta",  property="og:description")
                    content = data["content"].split('-')
                    followers = content[0].replace(" Followers, ", "")
                    following = content[1].replace(" Following, ", "")
                    bio = content[2]
                    img = soup.find("meta",  property="og:image")
                    pfp_url = img["content"] if img else None
                except:
                    pass
            elif site["name"] == "Twitter":
                try:
                    followers_element = soup.find("a", {"href": f"https://twitter.com/{username}/followers"})
                    followers = followers_element.find("span", {"class": "css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0"}).text
                    following_element = soup.find("a", {"href": f"https://twitter.com/{username}/following"})
                    following = following_element.find("span", {"class": "css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0"}).text
                    bio_element = soup.find("div", {"class": "css-901oao r-1nao33i r-37j5jr r-a023e6 r-16dba41 r-rjxpzi r-bcqeeo r-bnwqim r-qvutc0"})
                    bio = bio_element.text if bio_element else None
                    img = soup.find("img", {"alt": "Profile picture"})
                    pfp_url = img["src"] if img else None
                except:
                    pass
            elif site["name"] == "YouTube":
                try:
                    # Extracting followers (subscribers)
                    subscribers_element = soup.find('yt-formatted-string', {'id': 'subscriber-count'})
                    followers = subscribers_element.text.strip() if subscribers_element else None
                    
                    # Extracting bio (description)
                    description_element = soup.find('meta', {'name': 'description'})
                    bio = description_element['content'] if description_element else None

                    # Extracting profile picture URL
                    img_element = soup.find('img', {'id': 'img', 'class': 'style-scope yt-img-shadow'})
                    pfp_url = img_element['src'] if img_element else None
                except:
                    pass
            elif site["name"] == "Facebook":
                try:
                    # Extracting followers (likes)
                    likes_element = soup.find('div', {'class': '_64-k'})
                    followers = likes_element.text.replace(' people like this', '') if likes_element else None

                    # Extracting bio (description)
                    description_element = soup.find('meta', {'name': 'description'})
                    bio = description_element['content'] if description_element else None

                    # Extracting profile picture URL
                    img_element = soup.find('img', {'class': 'profilePic img'})
                    pfp_url = img_element['src'] if img_element else None
                except:
                    pass
            elif site["name"] == "TikTok":
                try:
                    # Extracting followers, following, and likes
                    followers_element = soup.find('strong', {'data-e2e': 'followers-count'})
                    followers = followers_element.text if followers_element else None
                    following_element = soup.find('strong', {'data-e2e': 'following-count'})
                    following = following_element.text if following_element else None

                    # Extracting bio
                    bio_element = soup.find('h2', {'data-e2e': 'user-bio'})
                    bio = bio_element.text if bio_element else None

                    # Extracting profile picture URL
                    img_element = soup.find('img', {'class': 'tiktok-avatar'})
                    pfp_url = img_element['src'] if img_element else None
                except:
                    pass
            elif site["name"] == "Twitch":
                try:
                    # Extracting followers
                    followers_element = soup.find('p', {'data-a-target': 'followers-count'})
                    followers = followers_element.text if followers_element else None

                    # Extracting bio
                    bio_element = soup.find('p', {'class': 'core-section-header-description'})
                    bio = bio_element.text if bio_element else None

                    # Extracting profile picture URL
                    img_element = soup.find('img', {'class': 'channel-header__user-avatar'})
                    pfp_url = img_element['src'] if img_element else None
                except:
                    pass
            elif site["name"] == "Pinterest":
                try:
                    # Extracting followers
                    followers_element = soup.find('div', {'class': 'tBJ dyH iFc sIg zI7 iyn Hsu'})
                    followers = followers_element.text.replace(' followers', '') if followers_element else None

                    # Extracting bio
                    bio_element = soup.find('div', {'class': 'Eqh'})
                    bio = bio_element.text if bio_element else None

                    # Extracting profile picture URL
                    img_element = soup.find('img', {'class': 'hCL kVc L4E MIw'});
                    pfp_url = img_element['src'] if img_element else None
                except:
                    pass
            # Add more site-specific logic here to extract followers, following, and bio

            return UserProfile(username, site["name"], url, followers, following, bio, pfp_url, additional_info)
        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                pass
            else:
                return None
        except Exception:
            return None

    return None

def sherlock(username, sites, threads=10, timeout=10, output=None, max_retries=3):
    """
    Searches for a username on multiple social media platforms and prints the found links,
    followers, following, and bio.

    Args:
        username (str): The username to search for.
        sites (list): A list of dictionaries containing site information.
        threads (int): The number of threads to use for concurrent requests.
        timeout (int): Timeout for each request in seconds.
        output (str): The file path to save the results to (JSON format).
        max_retries (int): Maximum number of retries for failed requests.
    """
    ascii_banner = pyfiglet.figlet_format("UserScope")
    print(Fore.RED + ascii_banner + Style.RESET_ALL)

    print(Fore.BLUE + "[+] Starting Sherlock Username Search" + Style.RESET_ALL)
    print(Fore.YELLOW + "[+] Please wait while we check for the username on different social media platforms!" + Style.RESET_ALL)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(check_site, username, site, timeout, max_retries) for site in sites]
        for future in concurrent.futures.as_completed(futures):
            profile = future.result()
            if profile:
                results.append(profile.to_dict())
                print(Fore.GREEN + f"[+] Username found on {profile.site_name}: {profile.url}" + Style.RESET_ALL)
                if profile.followers:
                    print(Fore.GREEN + f"    [+] Followers: {profile.followers}" + Style.RESET_ALL)
                if profile.following:
                    print(Fore.GREEN + f"    [+] Following: {profile.following}" + Style.RESET_ALL)
                if profile.followers and profile.following:
                    print(" " + Style.RESET_ALL)
                if profile.bio:
                    print(Fore.GREEN + f"    [+] Bio: {profile.bio}" + Style.RESET_ALL)
                if profile.pfp_url:
                    print(Fore.GREEN + f"    [+] Profile Picture URL: {profile.pfp_url}" + Style.RESET_ALL)
                if profile.additional_info:
                    for key, value in profile.additional_info.items():
                         print(Fore.GREEN + f"    [+] {key}: {value}" + Style.RESET_ALL)

    if output:
        try:
            with open(output, "w") as f:
                json.dump(results, f, indent=4)
            print(Fore.GREEN + f"[+] Results saved to {output} in JSON format" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"[-] Error saving to file: {e}" + Style.RESET_ALL)

    print(Fore.BLUE + "[+] Completed, Thank you for using our tool!" + Style.RESET_ALL)

def main():
    parser = argparse.ArgumentParser(description="Sherlock: Hunt down social media accounts by username")
    parser.add_argument("username", help="The username to search for")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads to use (default: 10)")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for requests in seconds (default: 10)")
    parser.add_argument("-o", "--output", help="Output file to save results (JSON format)")
    parser.add_argument("-r", "--retry", type=int, default=3, help="Maximum number of retries for failed requests (default: 3)")
    parser.add_argument("-f", "--file", type=str, help="File containing a list of sites to check (JSON format)")
    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, "r") as f:
                sites = json.load(f)
        except FileNotFoundError:
            print(Fore.RED + f"[-] Error: Site list file '{args.file}' not found." + Style.RESET_ALL)
            return
        except json.JSONDecodeError:
            print(Fore.RED + f"[-] Error: Invalid JSON format in site list file '{args.file}'." + Style.RESET_ALL)
            return
    else:
        # Default list of sites (as defined previously)
        sites = [
            {"name": "Facebook", "url": "https://www.facebook.com/{}", "exists": True},
            {"name": "Twitter", "url": "https://twitter.com/{}", "exists": True},
            {"name": "Instagram", "url": "https://www.instagram.com/{}", "exists": True},
            {"name": "YouTube", "url": "https://www.youtube.com/{}", "exists": True},
            {"name": "TikTok", "url": "https://www.tiktok.com/@{}", "exists": True},
            {"name": "Pinterest", "url": "https://www.pinterest.com/{}", "exists": True},
            {"name": "LinkedIn", "url": "https://www.linkedin.com/in/{}", "exists": True},
            {"name": "Reddit", "url": "https://www.reddit.com/user/{}", "exists": True},
            {"name": "Tumblr", "url": "https://{}.tumblr.com", "exists": True},
            {"name": "Flickr", "url": "https://www.flickr.com/people/{}", "exists": True},
            {"name": "Vimeo", "url": "https://vimeo.com/{}", "exists": True},
            {"name": "Twitch", "url": "https://www.twitch.tv/{}", "exists": True},
            {"name": "Dribbble", "url": "https://dribbble.com/{}", "exists": True},
            {"name": "Behance", "url": "https://www.behance.net/{}", "exists": True},
            {"name": "Medium", "url": "https://medium.com/@{}", "exists": True},
            {"name": "Quora", "url": "https://www.quora.com/profile/{}", "exists": True},
            {"name": "Snapchat", "url": "https://www.snapchat.com/add/{}", "exists": True},
            {"name": "SoundCloud", "url": "https://soundcloud.com/{}", "exists": True},
            {"name": "GitLab", "url": "https://gitlab.com/{}", "exists": True},
            {"name": "Bitbucket", "url": "https://bitbucket.org/{}/", "exists": True},
            {"name": "DeviantArt", "url": "https://www.deviantart.com/{}", "exists": True},
            {"name": "LiveJournal", "url": "https://{}.livejournal.com/", "exists": True},
            {"name": "VK", "url": "https://vk.com/{}", "exists": True},
            {"name": "About.me", "url": "https://about.me/{}", "exists": True},
            {"name": "AngelList", "url": "https://angel.co/{}", "exists": True},
            {"name": "Ameba", "url": "https://profile.ameba.jp/ameba/{}", "exists": True},
            {"name": "Badoo", "url": "https://badoo.com/en/profile/{}", "exists": True},
            {"name": "Bandcamp", "url": "https://bandcamp.com/{}", "exists": True},
            {"name": "Basecamp", "url": "https://basecamp.com/{}", "exists": True},
            {"name": "Blogger", "url": "https://{}.blogspot.com/", "exists": True},
            {"name": "BuzzFeed", "url": "https://www.buzzfeed.com/{}", "exists": True},
            {"name": "Couchsurfing", "url": "https://www.couchsurfing.com/people/{}", "exists": True},
            {"name": "CreativeMarket", "url": "https://creativemarket.com/{}", "exists": True},
            {"name": "Crunchbase", "url": "https://www.crunchbase.com/person/{}", "exists": True},
            {"name": "Disqus", "url": "https://disqus.com/by/{}", "exists": True},
            {"name": "eBay", "url": "https://www.ebay.com/usr/{}", "exists": True},
            {"name": "Etsy", "url": "https://www.etsy.com/shop/{}", "exists": True},
            {"name": "Foursquare", "url": "https://foursquare.com/user/{}", "exists": True},
            {"name": "Gravatar", "url": "https://en.gravatar.com/{}", "exists": True},
            {"name": "Gumroad", "url": "https://gumroad.com/{}", "exists": True},
            {"name": "HackerNews", "url": "https://news.ycombinator.com/user?id={}", "exists": True},
            {"name": "Instructables", "url": "https://www.instructables.com/member/{}", "exists": True},
            {"name": "Keybase", "url": "https://keybase.io/{}", "exists": True},
            {"name": "Kickstarter", "url": "https://www.kickstarter.com/profile/{}", "exists": True},
            {"name": "Last.fm", "url": "https://www.last.fm/user/{}", "exists": True},
            {"name": "Meetup", "url": "https://www.meetup.com/members/{}", "exists": True},
            {"name": "MySpace", "url": "https://myspace.com/{}", "exists": True},
            {"name": "Patreon", "url": "https://www.patreon.com/{}", "exists": True},
            {"name": "ProductHunt", "url": "https://www.producthunt.com/@{}", "exists": True},
            {"name": "500px", "url": "https://500px.com/p/{}?view=photos", "exists": True},
            {"name": "Academia.edu", "url": "https://independent.academia.edu/{}", "exists": True},
            {"name": "AllTrails", "url": "https://www.alltrails.com/members/{}", "exists": True},
            {"name": "Anilist", "url": "https://anilist.co/user/{}", "exists": True},
            {"name": "Archive.org", "url": "https://archive.org/details/{}", "exists": True},
            {"name": "AskFM", "url": "https://ask.fm/{}", "exists": True},
            {"name": "BLIP.fm", "url": "https://blip.fm/{}", "exists": True},
            {"name": "Bitwarden", "url": "https://bitwarden.com/help/article/username-availability/#{}", "exists": False},
            {"name": "Bookcrossing", "url": "https://www.bookcrossing.com/mybookshelf/{}", "exists": True},
            {"name": "Buy Me a Coffee", "url": "https://www.buymeacoffee.com/{}", "exists": True},
            {"name": "Carbonmade", "url": "https://carbonmade.com/{}", "exists": True},
            {"name": "CareerBuilder", "url": "https://www.careerbuilder.com/share/en/site/candidate_profile.aspx?uid={}", "exists": False},
            {"name": "Chess.com", "url": "https://www.chess.com/member/{}", "exists": True},
            {"name": "Codecademy", "url": "https://www.codecademy.com/profiles/{}", "exists": True},
            {"name": "Codepen", "url": "https://codepen.io/{}", "exists": True},
            {"name": "ColourLovers", "url": "https://www.colourlovers.com/lover/{}", "exists": True},
            {"name": "Contently", "url": "https://contently.com/portfolios/{}", "exists": True},
            {"name": "Coroflot", "url": "https://www.coroflot.com/{}", "exists": True},
            {"name": "Creative Market", "url": "https://creativemarket.com/{}", "exists": True},
            {"name": "Crevado", "url": "https://crevado.com/{}", "exists": True},
            {"name": "культиватор", "url": "https://cultivator.ee/users/{}", "exists": True},
            {"name": "Dcard", "url": "https://www.dcard.tw/@{}", "exists": True},
            {"name": "Delicious", "url": "https://delicious.com/{}", "exists": True},
            {"name": "Discogs", "url": "https://www.discogs.com/user/{}", "exists": True},
            {"name": " এলা", "url": "https://ella.network/{}", "exists": True},
            {"name": "EyeEm", "url": "https://www.eyeem.com/u/{}", "exists": True},
            {"name": "Fandom", "url": "https://www.fandom.com/u/{}", "exists": True},
            {"name": "Filmogs", "url": "https://filmogs.com/@{}", "exists": True},
            {"name": "FlightAware", "url": "https://flightaware.com/user/{}", "exists": True},
            {"name": "FontStruct", "url": "https://fontstruct.com/fontstructors/{}", "exists": True},
            {"name": "FreeCodeCamp", "url": "https://www.freecodecamp.org/{}", "exists": True},
            {"name": "Freesound", "url": "https://freesound.org/people/{}", "exists": True},
            {"name": "GameSpot", "url": "https://www.gamespot.com/profile/{}", "exists": True},
            {"name": "GitHub", "url": "https://github.com/{}", "exists": True},
            {"name": "Gitee", "url": "https://gitee.com/{}", "exists": True},
            {"name": "Goodreads", "url": "https://www.goodreads.com/user/show/{}", "exists": True},
            {"name": "Hackaday", "url": "https://hackaday.io/{}", "exists": True},
            {"name": "HackerOne", "url": "https://hackerone.com/{}", "exists": True},
            {"name": "HackerRank", "url": "https://www.hackerrank.com/{}", "exists": True},
            {"name": "Housecreep", "url": "https://www.housecreep.com/user/{}", "exists": True},
            {"name": "Houzz", "url": "https://www.houzz.com/user/{}", "exists": True},
            {"name": "ICQ", "url": "https://icq.com/people/{}", "exists": True},
            {"name": "IFTTT", "url": "https://ifttt.com/p/{}", "exists": True},
            {"name": "ImageShack", "url": "https://imageshack.com/user/{}", "exists": True},
            {"name": "Imgur", "url": "https://imgur.com/user/{}", "exists": True},
            {"name": "Issuu", "url": "https://issuu.com/{}", "exists": True},
            {"name": "itch.io", "url": "https://{}.itch.io/", "exists": True},
            {"name": "Joomla", "url": "https://community.joomla.org/user/profile/{}", "exists": True},
            {"name": "Kaggle", "url": "https://www.kaggle.com/{}", "exists": True},
            {"name": "Kongregate", "url": "https://www.kongregate.com/accounts/{}", "exists": True},
            {"name": "LORI.ru", "url": "https://lori.ru/portfolio/{}", "exists": True},
            {"name": "Launchpad", "url": "https://launchpad.net/~{}", "exists": True},
            {"name": "LeetCode", "url": "https://leetcode.com/{}", "exists": True},
            {"name": "Letterboxd", "url": "https://letterboxd.com/{}", "exists": True},
            {"name": "Mastodon", "url": "https://mastodon.social/@{}", "exists": True},
            {"name": "Mixcloud", "url": "https://www.mixcloud.com/{}", "exists": True},
            {"name": "MyAnimeList", "url": "https://myanimelist.net/profile/{}", "exists": True},
            {"name": "Myspace", "url": "https://myspace.com/{}", "exists": True},
            {"name": "NameMC", "url": "https://namemc.com/profile/{}", "exists": True},
            {"name": "Napster", "url": "https://napster.com/artist/{}", "exists": True},
            {"name": "npmjs", "url": "https://www.npmjs.com/~{}", "exists": True},
            {"name": "OK.ru", "url": "https://ok.ru/profile/{}", "exists": True},
            {"name": "OnlyFans", "url": "https://onlyfans.com/{}", "exists": True},
            {"name": "OpenStreetMap", "url": "https://www.openstreetmap.org/user/{}", "exists": True},
            {"name": "Photobucket", "url": "https://photobucket.com/user/{}", "exists": True},
            {"name": "Pixabay", "url": "https://pixabay.com/users/{}", "exists": True},
            {"name": "Plug.dj", "url": "https://plug.dj/@/{}", "exists": True},
            {"name": "Product Hunt", "url": "https://www.producthunt.com/@{}", "exists": True},
            {"name": "Ravelry", "url": "https://www.ravelry.com/people/{}", "exists": True},
            {"name": "ResearchGate", "url": "https://www.researchgate.net/profile/{}", "exists": True},
            {"name": "Roblox", "url": "https://www.roblox.com/user.aspx?ID={}", "exists": False},
            {"name": "Scribd", "url": "https://www.scribd.com/user/{}", "exists": True},
            {"name": "Shutterstock", "url": "https://www.shutterstock.com/g/{}", "exists": True},
            {"name": "Slack", "url": "https://slack.com/{}", "exists": True},
            {"name": "Slideshare", "url": "https://www.slideshare.net/{}", "exists": True},
            {"name": "Smashcast", "url": "https://smashcast.tv/{}", "exists": True},
            {"name": "SourceForge", "url": "https://sourceforge.net/u/{}", "exists": True},
            {"name": "Spotify", "url": "https://open.spotify.com/user/{}", "exists": True},
            {"name": "Steam", "url": "https://steamcommunity.com/id/{}", "exists": True},
            {"name": "Strava", "url": "https://www.strava.com/athletes/{}", "exists": True},
            {"name": "Telegram", "url": "https://t.me/{}", "exists": True},
            {"name": "TradingView", "url": "https://www.tradingview.com/~{}", "exists": True},
            {"name": "Trakt", "url": "https://trakt.tv/users/{}", "exists": True},
            {"name": "TripAdvisor", "url": "https://www.tripadvisor.com/members/{}", "exists": True},
            {"name": "Typeracer", "url": "https://data.typeracer.com/pit/profile?user={}", "exists": True},
            {"name": " ultimate-guitar", "url": "https://www.ultimate-guitar.com/u/{}", "exists": True},
            {"name": "Unsplash", "url": "https://unsplash.com/@{}", "exists": True},
            {"name": "Virustotal", "url": "https://www.virustotal.com/gui/user/{}", "exists": True},
            {"name": "Wattpad", "url": "https://www.wattpad.com/user/{}", "exists": True},
            {"name": "Wix", "url": "https://{}.wix.com", "exists": True},
            {"name": "WordPress", "url": "https://{}.wordpress.com/", "exists": True},
            {"name": "Xbox Gamertag", "url": "https://account.xbox.com/en-us/profile?gamertag={}", "exists": False},
            {"name": "Xing", "url": "https://www.xing.com/profile/{}", "exists": True},
            {"name": "YouPic", "url": "https://youpic.com/photographer/{}", "exists": True},
            {"name": "Zhihu", "url": "https://www.zhihu.com/people/{}", "exists": True},
            {"name": "Pornhub", "url": "https://www.pornhub.com/users/{}", "exists": True},
            {"name": "XVideos", "url": "https://www.xvideos.com/profiles/{}", "exists": True},
            {"name": "RedTube", "url": "https://www.redtube.com/users/{}", "exists": True},
            {"name": "TNAFlix", "url": "https://www.tnaflix.com/user/profile/{}", "exists": True},
            {"name": "Brazzers", "url": "https://www.brazzers.com/search/performers?q={}", "exists": True},
            {"name": "Academia", "url": "https://www.academia.edu/{}", "exists": True},
            {"name": "Bandzoogle", "url": "https://bandzoogle.com/{}", "exists": True},
            {"name": "Bsky Social", "url": "https://bsky.app/profile/{}", "exists": True},

        ]

    sherlock(args.username, sites, args.threads, args.timeout, args.output, args.retry)

if __name__ == "__main__":
    main()
