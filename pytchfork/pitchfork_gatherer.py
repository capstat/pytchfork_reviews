#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Nicholas Capofari"
#CUNY SPS IS 602 Final Project
#December 23rd, 2015


import re
import urllib2
import pandas as pd
import datetime as dt
from bs4 import BeautifulSoup


def go_get_reviews():
    """Captures all pitchfork reviews using predefined functions
    returns data frame containing pitchfork data
    """
    #create an empty data frame that we will add our info to
    pitchfork_df = pd.DataFrame({ 'album'     : 'album',
                                  'album_id'  : -1,
                                  'album_link': 'album link',
                                  'artist'    : 'artist',
                                  'rating'    : -1,
                                  'rev_date'  : 'August 25, 1981',
                                  'reviewer'  : 'reviewer',
                                  'year'      : 1981,
                                  },
                                index=[0])
    #use urllib2 to open the urls
    open_url = urllib2.build_opener()
    open_url.addheaders = [('User-agent', 'Mozilla/5.0')]
    #keeps track of album review page, in case of crash update where to start
    current_page = 1
    review_page = "http://www.pitchfork.com/reviews/albums/"
    while(True):
        #20 most current album reviews are at pitchfork.com/reviews/albums/1
        review_page = 'http://www.pitchfork.com/reviews/albums/%s' % current_page
        #see if url is good
        try:
            #connect to the page
            r = open_url.open(review_page)
        except urllib2.HTTPError:
            print "Error scraping %s" % review_page
            break
        my_html = r.read()
        #add 20 albums to data frame
        one_page_of_albums = get_album_links(my_html)
        for album in one_page_of_albums:
            pitchfork_df.loc[pitchfork_df.index.max() + 1] = album
        #save file after each time 20 albums are added to df
        pitchfork_df.to_csv("pitchfork_albums.csv", encoding='utf-8', index=False)
        #print message to track progress
        print "\nFinished %s albums...%s\n" \
              %(current_page*20, review_page)
        #get ready to go to the next page
        current_page = current_page + 1
    #remove any duplicates
    pitchfork_df = pitchfork_df.drop_duplicates()
    #remove top row
    pitchfork_df.drop(0, inplace=True)
    #save final data frame
    pitchfork_df.to_csv("pitchfork_albums.csv", encoding='utf-8', index=False)
    return pitchfork_df


def get_album_links(html_doc):
    """Takes a review page from pitchfork and extracts the links to each albums
    Then sends these links the get_album_info function
    Returns a 20 lists of album info"""
    album_info = []
    soup = BeautifulSoup(html_doc, 'lxml')
    #find where the album links are
    extract_soup = soup.find('ul', class_='object-grid')
    #go gettem
    all_links = extract_soup.find_all('a')
    #cycle through all of our links
    for link in all_links:
        #get the album link
        album_link = link.get('href')
        album_info.append(get_album_info(album_link))
        #keep track of what album link we are scraping
    #return the album info
    return album_info


def get_album_info(a_link):
    """Extracts the album info as a list"""
    open_url = urllib2.build_opener()
    open_url.addheaders = [('User-agent', 'Mozilla/5.0')]
    #extract the album id
    album_id = "".join(re.findall(r'\d{3,5}', a_link))
    album_link = "http://www.pitchfork.com" + a_link
    try:
        r = open_url.open(album_link)
    except:
        print "Failed to open %s" % album_link
        #return dummy data
        return ['album', -1, 'album link', 'artist', -1,
                'August 25, 1981', 'reviewer', 1981]
    #print for testing purposes...see where we get stuck
    #print album_link
    my_new_html = r.read()
    more_soup = BeautifulSoup(my_new_html, 'lxml')
    album_info = more_soup.find('div', class_ = 'info')
    #get the album title
    album = album_info.h2.get_text()
    #extract the rest of the information
    artist = album_info.h1.get_text()
    reviewer = album_info.h4.address.get_text()
    rating = float(album_info.find('span', class_ = 'score').get_text().strip())
    rev_date = album_info.h4.find('span', class_ = 'pub-date').get_text()
    year = int("".join(re.findall(r'\d{4}', rev_date)))
    #return the new info
    return [album, album_id, album_link, artist, rating, rev_date, reviewer, year]


def album_update(d):
    """checks for any new reviews since last time program was ran
    returns those albums as a list of lists"""
    new_albums = []
    #use urllib2 to open the urls
    open_url = urllib2.build_opener()
    open_url.addheaders = [('User-agent', 'Mozilla/5.0')]
    #keeps track of album review page, in case of crash update where to start
    current_page = 1
    review_page = "http://www.pitchfork.com/reviews/albums/"
    while(True):
        #20 most current album reviews are at pitchfork.com/reviews/albums/1
        review_page = 'http://www.pitchfork.com/reviews/albums/%s' % current_page
        #see if url is good
        try:
            #connect to the page
            r = open_url.open(review_page)
        except:
            print "Error opening %s..." % review_page
            break
        my_html = r.read()
        #scrape last 20 albums that have been reviewed
        one_page_of_albums = get_album_links(my_html)
        #cycle through each album
        for album in one_page_of_albums:
            #change date to datetime object
            album[5] = dt.datetime.strptime(album[5],'%B %d, %Y')
            #if the dates match up delete the item and stop the for loop
            if album[5] == d:
                del one_page_of_albums[one_page_of_albums.index(album)]
                break
            #if dates don't match add album to data frame
            new_albums.append(album)
        #get ready to go to the next page
        current_page = current_page + 1
        #after each page, if an item was deleted from the list
        #stop checking for updates
        if len(one_page_of_albums) != 20:
            break
    return new_albums


if __name__ == '__main__':
    albums = go_get_reviews()
