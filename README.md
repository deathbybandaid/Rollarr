# Rollarr
This is the new and improved Automatic Pre-roll script with a GUI for Plex now called Rollarr! It should be stable but if you find a bug please let me know

## Docker Edition

## What is this?
This is a python script with web GUI that allows you to automate your Plex Server Pre-roll.
You can find out more about Plex Pre-roll here: https://support.plex.tv/articles/202920803-extras/
You can specify if you would like your pre-roll updated monthly, weekly, daily, or for specific holidays.
For example you can have this setup to apply a standard Pre-roll during regular times of the year and then during holidays update the pre-roll automatically!

## Requirements
-[Python 3.7+](https://www.python.org/)
(Probably works on a lower version haven't tested)

-[PlexAPI](https://github.com/pkkid/python-plexapi)


## Installation

Simply install like any other docker

```
docker pull thehumanrobot/rollarr:latest
```

## Usage

### Setting Plex Preroll

~~You need to schedule a job for updating the preroll each day, week, or month depending how you want your pre-rolls updated.
You will now point this at the PrerollUpdate.py script~~ This no longer required for the docker container since I have written some code to ensure the pre-roll is synced ever 60s

## Running For The First Time

The first time you run it you will see this:
![image](https://user-images.githubusercontent.com/75536101/147721323-21bbc717-bc79-424a-9a51-8e799861cca4.png)


Fill in all the fields for your plex IP and Token

How to get token: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/ 

You can then setup a default pre-roll if you want or leave it blank

To set specific pre-roll fuctions select which type you want (Monthly, Weekly, Daily, Holiday Custom), You will then see more fields on the right
### *The path to the videos must be reachable by your Plex Server!*

Monthly:
![image](https://user-images.githubusercontent.com/75536101/146992956-baa1dd72-57e0-4aa2-bbdf-8cf4e75cd4be.png)

Weekly:
![image](https://user-images.githubusercontent.com/75536101/146993034-951f7bcc-6011-40a7-994b-1564cea961d1.png)

Daily:
![image](https://user-images.githubusercontent.com/75536101/146993063-d1dc0964-233c-4e11-8099-d5e9555b1497.png)

Holiday (If you want another holiday you can add that by using the weekly function and setting a date) :
![image](https://user-images.githubusercontent.com/75536101/146993137-a99e4e79-0e4f-4348-b72a-6ffa19a370cc.png)

Custom:
![image](https://user-images.githubusercontent.com/75536101/147268244-abf0f6d2-2fe5-43bd-93ec-d69e982d7425.png)

### Once you finish setting that up whatever you select in the Schedule section will be what the script will run on

For example in this photo

![image](https://user-images.githubusercontent.com/75536101/146993632-4decbe1e-d942-4c4a-b431-2bc68568f7c0.png)

I have selected Holiday and enabled the Christmas list therefore it will run through my Christmas list. If it does not find one enabled, finds empty strings, or does not match the holiday dates set in the system it will attempt to pull from the Default files.

I hope this is useful for some people and feel free to post any ideas or bugs
