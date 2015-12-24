#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Nicholas Capofari"
#CUNY SPS IS 602 Final Project
#December 23rd, 2015

import os
import cPickle
import webbrowser
import pandas as pd
import datetime as dt
from fuzzywuzzy import process
from welcome import welcome
from pitchfork_gatherer import album_update

#to help with utf-8 ascii trouble
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def main():
    """A command line program to quickly access ratings from pitchfork.com"""
    #if the program has been run, previous data has been stored
    #check to see if data is there
    my_csv =  os.getcwd() + '/pytchfork/all_pitchfork_albums.csv'
    my_pickle = os.getcwd() + '/pytchfork/all_pitchfork_albums'
    print my_csv
    try:
        data = open(my_pickle, 'rb')
        pitchfork_df = cPickle.load(data)
        data.close()
    #if it is not, read the album review csv file
    except IOError:
        try:
            pitchfork_df = pd.read_csv(my_csv)
        except IOError:
            print "YIKES! We are missing the data..."
            
    #convert date types for sorting
    try:
        pitchfork_df['rev_date'] = pitchfork_df['rev_date'].apply(
            lambda x: dt.datetime.strptime(x,'%B %d, %Y'))
    except TypeError:
        #already stored as datetime
        pass
    #sort by date
    pitchfork_df.sort_values(by='rev_date', inplace=True, ascending=False)
    #check for updates since last time program was run
    #date of last album review
    last_date = pitchfork_df['rev_date'].iloc[0]
    print "Checking for updates..."
    #get new album reviews
    new_albums = album_update(last_date)
    #add these albums to data frame
    for album in new_albums:
        pitchfork_df.loc[pitchfork_df.index.max() + 1] = album
    #remove characters that cause issues so fuzzy wuzzy works
    pitchfork_df['artist'] = pitchfork_df.artist.apply(scrub)
    #pickle data for next time
    output = open(my_pickle, 'wb')
    cPickle.dump(pitchfork_df, output)
    output.close()
    #set output options for pandas
    pd.set_option('max_colwidth',30)
    pd.set_option('max_rows',500)
    pd.set_option('expand_frame_repr',True)

    #start program
    menu(pitchfork_df)


def menu(p_df):
    """user interface to access the functions"""
    #welcome graphic
    welcome()
    #menu as dictionary
    menu = {    '1' : "Latest Reviews",
                '2' : "Year's Best",
                '3' : "Review by Band",
                '4' : "Custom Search"   }
    #functions that match the dictionary menu
    action = {  '1' : get_latest_reviews,
                '2' : get_years_best,
                '3' : get_band_reviews,
                '4' : custom_search     }
    #run the menu
    while True:
        #set the options
        options = menu.keys()
        options.sort()
        #print the options
        for entry in options:
            print entry, menu[entry]
        selection = raw_input("\nPlease Select an Option\nEnter 0 to exit.\n")
        if selection == '0':
            print "\n\nThank You!  Good Bye..."
            break
        #if option is selected run corresponding function
        elif selection in action:
            action[selection](p_df)
        else:
            print "Unknown Option Selected!"


def get_latest_reviews(p_df):
    """prints last n reviews"""
    #sort by date
    p_df.sort_values(by='rev_date', inplace=True, ascending=False)
    #get number of albums to list
    n = 0
    while(n < 1 or n > 99):
        n = raw_input("How many reviews should we list? (max is 99)\n")
        try:
            n = int(n)
        except ValueError:
            print "%s is not a valid choice." % n
            continue
        if n < 1 or n > 99:
            print "Number of albums must be 1 to 99."
            continue
    print p_df.head(n)[['artist', 'album', 'rating']]
    #access the the album review
    go_to_review(p_df)


def get_years_best(p_df):
    """prints top 10 albums of a given year"""
    #get year to search
    year = raw_input("Enter a year, or press enter for the current year.\n")
    try:
        year = int(year)
    #if its a bad year just use current year
    except ValueError:
        year = dt.datetime.now().year
    #check to see if there are any reviews for the year given
    if year in p_df.year.values:
        print "Top 10 albums from %s" % year
        info = p_df[p_df.year == year].copy()
        info.sort_values(by='rating', inplace=True, ascending=False)
        print info.head(10)[['artist', 'album', 'rating']]
        #access the album review
        go_to_review(info)
    #if no reviews for that year ex 1990
    else:
        print "No data from that year.\n"


def get_band_reviews(p_df):
    """prints all reviews for a particular band"""
    #used the fuzzy wuzzy package --- it is awesome
    #set possible choices
    choices = p_df['artist']
    #get artist to search for
    artist = raw_input("Please enter an artist...\n")
    #find the artist that is closest to the input
    artist =  process.extractOne(artist, choices)[0]
    #mini df for the given artist
    info =  p_df.loc[p_df['artist'] == artist]
    print info[['artist', 'album', 'year', 'rating']]
    #access the album review
    go_to_review(info)


def custom_search(p_df):
    """custom search by year and minimum rating"""
    #get year from user
    year = raw_input("Enter a year, or press enter for the current year.\n")
    #make sure its an integer
    try:
        year = int(year)
    except ValueError:
        #bad year use current year
        year = dt.datetime.now().year
    if year in p_df.year.values:
        info = p_df[p_df.year == year].copy()
        info.sort_values(by='rating', inplace=True, ascending=False)
    #if no data from that year
    else:
        print "No data from that year.\n\n"
        return 0
    #get minimum rating from user
    rating = -1
    while(rating > 10 or rating < 0):
        rating = raw_input("Enter a rating 0-10.\n")
        try:
            rating = int(rating)
        except ValueError:
            print "%s is not a valid score." % rating
            continue
        if rating > 10 or rating < 0:
            print "Rating must be from 0 to 10."
            continue
    output = info[['artist', 'album', 'rating']][info.rating >= rating]
    print "In %s, there were %s albums with a rating of at least %s." \
          % (year, output.shape[0], rating)
    print output
    #access the album review
    go_to_review(output)


def go_to_review(df):
    """lets user quickly go a pitchfork review that is printed on screen"""
    #get index number of album review
    go_to = raw_input("\nEnter the index number to read the review. "
                      "\nPress enter to continue.\n")
    try:
        #make sure the index is there
        go_to = int(go_to)
        if go_to in df.index:
            try:
                #if it is open web browser and get goin
                webbrowser.open(df['album_link'].loc[go_to])
            except:
                #any problems
                print "Error opening %s" % df['link'].loc[go_to]
    except ValueError:
        print "Index not found..."


def scrub(a_string):
    """helper function for utf-8 trouble"""
    return a_string.decode('utf-8', 'ignore')


if __name__ == '__main__':
    main()
