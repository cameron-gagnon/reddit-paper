# reddit-paper
Automated wallpaper downloader which lets you download and set the top posts' pictures from any subreddit. ex. r/earthporn, r/spaceporn

I have not tested this on any other systems/setups other than Python 3.4 and Ubuntu 14.04.
This program is still buggy. The biggest issue is downloading from flikcr. Let me know of any other errors that you may come across, and I'd be happy to add it to the todo list.

If anyone has comments, critiques, or contributions to this program, let me know and I'd love to improve, change, and/or add to what is here. I will continue to develop this program until I see it as 'complete'. In the end I aim to have a GUI as well, mostly for the learning experience but also useabilty to others.

**NOTE:** At the end of the program, it will always terminate with something of the sort "sys:1: ResourceWarning: unclosed <ssl.SSLSocket fd=5 ..." this is does not indicate an error in the program, it is, from my understanding, the way that PRAW handles the connection that it terminates in this way.

**TODO LIST:**
* add flickr support
* add different subreddit's support, such as ones that don't list width && height in title of post, to avoid
* incorrect parsing of title everytime
* save photos into folders by date, then access these folders to set the correct images
* Add Windows support, then Mac
* create gui
