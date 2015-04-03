# reddit-paper
Automated wallpaper downloader which lets you download and set the top posts' pictures from any subreddit. ex. r/earthporn, r/spaceporn

I have not tested this on any other systems/setups other than Python 3.4 and Ubuntu 14.04.
This program is still buggy. Mostly with finding width/height from the title, and downloading from a few sites like flickr. The width and height fix is in process, should be done soon. Let me know of any other errors that you may come across, and I'd be happy to add it to the tofix/todo list.

If anyone has comments, critiques, or contributions to this program, let me know and I'd be happy to improve, change, and/or add to what is here. I will continue to develop this program until I see it as 'complete'. In the end I aim to have a GUI as well, just for the learning experience and all.

NOTE: At the end of the program, it will always terminate with something of the sort "sys:1: ResourceWarning: unclosed <ssl.SSLSocket fd=5 ..." this is does not indicate an error in the program, it is, from my understanding, the way that PRAW handles the connection that it terminates in this way.

TODO LIST:
* fix regex on parsing of title to find width and height
* add flickr support
* add different subreddit's support, such as ones that don't list width && height in title of post, to avoid
* incorrect parsing of title everytime
* tidy up output
* create debugging output to log file
* save photos into folders by date, then access these folders to set the correct images
* Add Windows support, then Mac
* create gui
