Facebook Event -> Google Calendar Syncroniser
==========

I saw a need for a service which reflects Facebook events into a more accessible
calendar service. This repo is designed to do exactly that.

Tech stack is just Python 3 and pipenv.

Installation
-----------

To install, ensure you already have pipenv installed.
1. Clone
2. `pipenv sync`
3. Fetch your FB user token (detailed below)
4. Fetch your Google client id and secret.
5. `./run.sh`

I've set up a simple AWS ec2 instance to run the bash script every 1/2 hour. You
can choose to do the same if you wish :)


Fetching the Facebook User Token
----------

Facebook uniquely identifies the app or person trying to access their Graph API
using an *access token*. An access token fits into two categories and this
app needs a particular permission type to get access to FB events called `user_events`.
This requires a *user access token* which can be assigned (and extended to last
  a few months) [here](https://developers.facebook.com/tools/debug/accesstoken/).
  The reason this is not done programmatically is because this tool sits in the
  backend and Facebook provide no means of using backend tools (unlike Google) to
  get user permissions. It all has to be done in their JS, iOS or Android SDK.


Fetching your Google Details
----------

Go [here](developers.google.com) and start a new app, copy the client id and
secret into the files called g_client_id and g_client_secret (maybe someday I'll
let them be entered on startup, but not today!)
