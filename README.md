Two Factor Auth 
==========

The lib adds support of two factor authentication to ensure security on the high level
for Django REST applications. 


Installation
------------

In settings.py do the following:

* Add django_rest_tfa to the installed apps with base libs and middlewares.
```
INSTALLED_APPS = [
    ...

    'django_otp',
    'django_otp.plugins.otp_email',
    'django_user_agents',
    'django_rest_tfa',
]

MIDDLEWARE = [
    ...

    'django_user_agents.middleware.UserAgentMiddleware',
    'django_rest_tfa.middleware.TwoFactorAuthMiddleware',
]
```

* Then define supported types
```
DRF_TFA_ENABLED_AUTH_TYPES = [
    'email',
]
```

* Configure URLs in urls.py
```python
urlpatterns = [
    path('auth/tfa/', include('django_rest_tfa.urls')),
]
```

* Configure ages of client or token
```
DRF_TFA_CLIENT_AGE = 1209600  # 2 weeks
DRF_TFA_TOKEN_AGE = 3600  # 60 min
```

* And name the base identifiers
```
TFA_CLIENT_IDENTIFIERS = [
    'django_rest_tfa.client_identifiers.browser_version',
    'django_rest_tfa.client_identifiers.os_version',
    'django_rest_tfa.client_identifiers.ip_address'
]
```


User flow
------------
A User is not able to see UI without confirmed and active Device even if it has been 
successfully logged-in.
Device is a second factor that the User has and must be associated with User through the Client -
literally a parsed string from the User Agent HTTP header and represented as name of defined Device.
Every Device should be confirmed and activated by the User with accepting challenges. 

TFA lib watches user's Client and tries to create a Challenge for the User 
if the User does not have active Challenge.
The Challenge is an event when TFA defines a new Device, sends an email (for example)
with OTP code and waits for a User's attempts to accept the challenge.

The User has only 3 attempts to take it up. 
The Device will be confirmed if the User has the Device and enters the correct code.   

After that the User will enjoy the UI while the Device is alive.
The Device lifetime is declared in settings.DRF_TFA_CLIENT_AGE.

Here is a simple diagram: 
```
 \O <{ Hallo! }
  |\
 / \                 APP                  BE                2 Factor
 +-------------------+-------------------+--------------------+
 |load the app       |                   |                    |
 |------------------>|/api/              |                    |
 |                   |------------------>|check a device      |
 |                   |                   |---|                |
 |                   |                   |<--|                |
 |                   |                   |                    |
 |                   |          if user doesn't have          |
 |                   |          an active challege:           |
 |                   |                   |send the challenge  |
 |                   |                   |------------------->|
 |                   |                 else:                  |
 |                   |redirect 303       |                    |
 |                   |with LOCATION      |                    |
 |                   |/accept_challenge/ |                    |
 |                   |<------------------|                    |
 |show the form      |                   |                    |
 |ACCEPT CHALLENGE   |                   |                    |
 |<------------------|                   |                    |
 |                   |                   |                    |
 |get an OTP code    |                   |                    |read an email
 |----------------------------------------------------------->|---|
 |                   |                   |                    |<--|
 |enter the code     |                   |                    |
 |------------------>|                   |                    |
 |                   |POST auth/tfa/email|                    |
 |                   |/accept_challenge/ |                    |
 |                   |------------------>|process the OTP code|
 |                   |                   |---|                |
 |                   |                   |<--|                |
 |                   |                   |                    |
 |                   |             if the code is not valid:  |
 |                   |raise 400          |                    |
 |                   |"Invalid code"     |                    |
 |                   |<------------------|                    |
 |show an error      |                   |                    |
 |"Invalid code"     |                   |                    |
 |"pls repeat"       |                   |                    |
 |<------------------|                   |                    |
 |                   |                 else:                  |
 |                   |                   |save the device     |
 |                   |                   |in DB and session   |
 |                   |                   |---|                |
 |                   |                   |<--|                |
 |                   |redirect 303       |                    |
 |                   |with LOCATION      |                    |
 |                   |/                  |                    |
 |                   |<------------------|                    |
 |open UI            |                   |                    |
 |<------------------|                   |                    |
 +-------------------+-------------------+--------------------+
```

The User has only 3 attempts for accept the challenge with one token. After that
it has to create a new challenge:
```
 \O/<{ Oh no! It's said my token is outdated. I will ask it about new one }
  |
 / \                 APP                  BE                2 Factor
 +-------------------+-------------------+--------------------+
 |create a new       |                   |                    |
 |challenge          |                   |                    |
 |------------------>|                   |                    |
 |                   |POST auth/tfa/email|                    |
 |                   |/create_challenge/ |                    |
 |                   |------------------>|process new code    |
 |                   |                   |---|                |
 |                   |                   |<--|                |
 |                   |                   |                    |
 |                   |                   | send the challenge |
 |                   |                   |------------------->|
 |                   |redirect 303       |                    |
 |                   |with LOCATION      |                    |
 |                   |/accept_challenge/ |                    |
 |                   |<------------------|                    |
 |show the form      |                   |                    |
 |ACCEPT CHALLENGE   |                   |                    |
 |<------------------|                   |                    |
 +-------------------+-------------------+--------------------+
```
