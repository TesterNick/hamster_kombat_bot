![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)

# Hamster Kombat Bot

Automated clicker to collect coins in the Telegram game Hamster Kombat.
Now you can sleep at night without any FOMO (fear of missing opportunities).

## Dependencies

In order to work the bot requires:
- an installed and configured Appium
- configured and connected mobile device with installed Telegram
- User should be registered in Hamster Kombat bot. If you only want to start,
 here is the referral
 [link](https://t.me/hamster_koMbat_bot/start?startapp=kentId5227105337).
 Please join. We both will get a bonus.
- Python3 with Appium module installed.

## What this does?
It:
- runs Appium server
- connects to your device
- opens your Telegram
- runs Hamster Kombat miniapp
- checks how much energy you have
- taps on hamster until there is energy
- clicks on Boost button
- checks if energy refill is available
  - if so, activates it and taps again unless energy is out
- close the application and connection
- waits while 90% energy is refilled
- go to step 2

## What it does not?
It does not:
- send your data anywhere
- upgrade your cards, or in any other way spend your balance
- earn your daily rewards, or fulfill any tasks

If you don't believe me, here is the code. Check it ;)

## Disclaimer
This was developed and tested only on Android device with Windows PC
 as a server.

For any other platforms there were no any efforts, though it may work
 with or without any additional actions.

This game is just a game though it may bring you some money.
I'm not an affiliated person, just a player like you.

## Installation
1. Install [Python](https://www.python.org/downloads/)
2. Install [Appium](https://appium.io/docs/en/2.0/quickstart/install/)
3. Install [the driver](https://appium.io/docs/en/2.0/quickstart/uiauto2-driver/)
4. Python dependencies:
```
pip install -r requirements.txt
```
Notes:

[How to connect the device to computer](https://www.seleniumeasy.com/appium-tutorials/configure-appium-on-real-devices-android-to-execute-tests#google_vignette)

[How to connect device through Wi-Fi](https://discuss.appium.io/t/tutorial-how-to-run-tests-on-real-android-device-remotely-through-wi-fi/1135)

## Conclusion

If you like this please star this repo.
If you can help me, feel free to fork the repo and make a pull request.
