# Dynamic menu bot

A small dynamic menu bot that uses a JSON file as storage

## Features

* Dynamic menu
* Custom commands
* Easy to add new commands
* Simple state management
* Uses gettext for translations
* TODO: add a language selection menu

## Installation

To install it simply clone the repository and run `pip install -r requirements.txt`

## Usage

To use it you have to first configure the config.py file. You will need to add the api_id and api_hash and the bot
token. Afterwards you can simply do

```
$ python3 main.py
```

## Included modules

The bot includes some simple modules as examples to build on. You can safely remove them all and use your own. Some
modules use an API_KEY (OCR) so you'll need to manually provide that in file.

* images
    * OCR (uses ocr.space and needs API)
* links
    * Link shortener (uses chilpit)
    * Link unshortener (uses chilpit)
* text
    * decorate
        * arabic. decorates an arabic text using random techniques
        * english. decorates an english text using random techniques
    * tashkeel, used to format arabic text
    * translate
        * arabic. translates a text to arabic
        * english. translates a text to english
* video
    * videoToAudio converts a video to audio using ffmpeg
## Debug mode
You can use the debugme file as an easy way to add more features. 

As soon as you save any file the bot will automatically restart and your changes will be applied.

## Contribution
If you want to contribute new modules or improve the existing code, please do so with a PR.

## Issues 
If you have an issue with the core code, please open an issue on the github page. 

If your issue is related to the modules, it might get ignored as they are there only as examples

## License
MIT (free to use , modify and redistribute)