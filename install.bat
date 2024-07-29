
winget install docker.dockerdesktop
docker pull appium/appium
for /f "delims=" %i in ('cd') do set workdir=%i
docker run --privileged -d -p 4723:4723 -v %workdir%:/home/androidusr/hamster_bot --name hamster_bot appium/appium
docker exec hamster_bot sudo apt install pip -y --fix-missing
docker exec hamster_bot pip install -r requirements.txt

ECHO OFF
ECHO Please use your device to proceed to Settings -> Developer options -> Wireless debugging
ECHO and make sure it is switched on. Then tap "Pair device with pairing code".
ECHO Don\'t click "Cancel" button!
SET /p ip=Please enter the device's "IP address & Port":
SET /p code=Please enter "Wi-Fi pairing code":
SET folder=%~dp0
ECHO ipaddress = %ip%>>%folder%\config.ini
docker exec hamster_bot adb pair %ip% %code%

ECHO *********************************
ECHO * CAUTION: Read this carefully! *
ECHO *********************************
ECHO Here are settings to unlock your device. Obviously the bot can not unlock
ECHO your device if it is locked with biometrics. So, consider what approach
ECHO will be the most suitable for you. The easiest way is no lock,
ECHO but it is not secure. In some circumstances appropriate way may be
ECHO the setting when your device is not locked when it is connected to
ECHO a particular bluetooth device or a particular WiFi network.
ECHO If these options are not suitable for you, be aware, that following options
ECHO override your device settings. E. g. You can NOT unlock a device with pin
ECHO if fingerprint is set up. Bot will unlock the device, but YOU WILL LOSE
ECHO all your fingerprints. If you still want to proceed, available options are:
ECHO - no lock or simple lock, when you just press power button to unlock
ECHO   the device, in that case answer with an empty line (just press Enter)
ECHO - pin, when you should type several numbers to unlock the device.
ECHO   If this is your case, type "pin".
ECHO - password, when you should type letters and numbers.
ECHO   To chose this, type "password"
ECHO - graphical pattern. Consider your dots as numbers in this order:
ECHO        1    2    3
ECHO        4    5    6
ECHO        7    8    9
ECHO   type "pattern" and provide numbers of dots in the next question.

SET /p unlock=Please choose how the bot should unlock your device:
ECHO unlock_type = %unlock%>>%folder%\config.ini

IF /i %unlock%=="no" (
    SET unlock=""
) ELSE IF %unlock%=="" (
    SET unlock=""
) ELSE (
    SET /p key=Please enter the key to unlock your device:
    ECHO unlock_key = %key%>>%folder%\config.ini
)

ECHO Congratulations! This is all the bot needs!
PAUSE
