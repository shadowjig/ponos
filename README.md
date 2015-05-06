This is an app for sending podcast URI's to a Sonos zone.
It's written in python and uses Flask, Bootstrap CSS, and jQuery.

This app will allow the user manage RSS/ATOM feeds for podcast.
After selecting a feed, the episodes will be presented and the
user can send the episode to the selected Sonos zone.

Requires python 3.3 or higher for Flask.

After cloning the code run the following to install python 
requirements and initalize the sqlite database file.

```
pip3 install -r requirements.txt
python3 ./initalize_db.py
```

