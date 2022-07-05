from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import sys
import datetime
import random
import time
import re
from googleapiclient.discovery import build
Const_Percentage=90
def tos_accept(browser):
    try:
        button=browser.find_elements_by_css_selector('.style-scope.ytd-consent-bump-v2-lightbox.style-primary.size-default')
        button[1].click()
    except Exception:
        pass
#getting random video from html source( that is also displayed to user)
def find_video(browser): 
    video=browser.find_elements_by_id('thumbnail')
    video_count=len(video)-1
    index=0
    url=0
    #Some videos in html arent displayed on the website(arent clickable), so we use random function
    #until we get the video that works (is clickable)
    while((video[index].is_displayed())==False or not url):
        index=random.randint(1,video_count)
        url=video[index].get_attribute('href')
    video[index].click()
    return url 
#sends api request to youtube to get informationa about the video (later used for retrieving video duration)
def get_api_response(api_key, url):
    youtube=build('youtube','v3',developerKey=api_key)
    video_id=url[32:43]
    request=youtube.videos().list(
           id=video_id,
           part='ContentDetails')
    response=request.execute()
    return response
#retrieving video duration
def parse_response(response):
    find_hour=re.compile(r'(\d+)H')
    find_minute=re.compile(r'(\d+)M')
    find_second=re.compile(r'(\d+)S')


    minute=find_minute.search(response['items'][0]['contentDetails']['duration'])
    second=find_second.search(response['items'][0]['contentDetails']['duration'])
    hour=find_hour.search(response['items'][0]['contentDetails']['duration'])

    minute=int(minute.groups(1)[0]) if minute else 0
    second=int(second.groups(1)[0]) if second else 0
    #in case video is long (>=1hour) set the max watching time to 3 minutes
    if hour:
        minute=3
    video_time=datetime.timedelta(
            minutes=minute,
            seconds=second).total_seconds()
    return video_time
def dismiss_premium_popup(browser):
    try:
        button=browser.find_element_by_css_selector(".style-scope.ytd-button-renderer.style-text.size-default")
        button.click()
    except:
        pass
def wait_through_ads(browser):   
    while( browser.find_elements_by_class_name('ytp-ad-text') ):
        print('\nReklama')
        time.sleep(10)
def main():
    if len(sys.argv)>2:
        api_key=sys.argv[1]
        gecko_path=sys.argv[2]
    else:
        print("Usage: humantrafficgenerator.py <Your_Api_Key> <Path_To_Geckodriver>\n")
        return
    binary = FirefoxBinary(sys.argv[2])
    browser=webdriver.Firefox()
    browser.get('https://www.youtube.com')

    tos_accept(browser)
    while(1):
        url=find_video(browser)
        response=get_api_response(api_key,url)
        video_time=parse_response(response)
        time.sleep(5)
        wait_through_ads(browser)
        dismiss_premium_popup(browser)
        viewing_way=random.randint(0,100)

        if viewing_way<Const_Percentage:
            sleep_count=random.randint(0,10)
        else:
            sleep_count=random.randint(10,video_time)

        print('sleep_count=%d\n'%sleep_count)
        time.sleep(sleep_count)
if __name__=="__main__":
    main()
