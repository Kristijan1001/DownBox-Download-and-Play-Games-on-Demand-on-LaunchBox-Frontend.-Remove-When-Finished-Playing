Out of space ? Want to have 50k Games setup on Launchbox but don't wanna download 1000s of games no need for 20TB HDD anymore. 

I made this for my self long ago, basically how it works is, upon boot launchbox downloads the game, once downloaded, the game boots. Once you finish it asks you if you want to remove the game or keep it so you can play it again next time. 

This process can be really streamlined and made better, if someone had the time. The idea is there, it is working for Archive.org and Myrient. I am sure it can be updated to work on other links. 

The idea is the following. 

1. First you get and run

(.Export) (A2600) Atari 2600 - (Export Titles & Links in CSV)

2. This creates a csv file with all the Roms and Links

3. Then you run

(Dummy) (A2600) Atari 2600 - (Make Dummy Roms).py

4. This makes it so it created a Fake rom in the Launchbox Directory or wherever your games are stored.

5. You need to setup launchbox to launch the script before and after the game.

6. To do this you need to add an Additional App. But since we are doing this for 1000s of entries, we need to get the plugin Additional Apps Bulk from here:

https://forums.launchbox-app.com/files/file/4375-bulk-addremove-additional-applications/

7. We also need to get start up screen delay, not sure if needed still since i made this script awhile ago set to 5 seconds, if i remember correctly it was so the game starts faster instead of waitng for those 30 Seconds after the game downloads/extracts.

https://forums.launchbox-app.com/files/file/4862-startup-screen-load-delay-greater-than-30-seconds/

8. We go to launchbox and we add the additional apps again use the Bulk Additional App to add it to tons of games:

<img width="1100" height="700" alt="LaunchBox_GMlfaSMN8b" src="https://github.com/user-attachments/assets/74079fb5-3085-446d-9575-fd1a902af083" />

<img width="640" height="475" alt="LaunchBox_KJ0gZYLsWp" src="https://github.com/user-attachments/assets/e4069515-eedd-439d-811f-af75376dcb9a" />

9. Start a game, alt tab a CMD should be open asking if you are sure you want to download this game, this can be disabled by editing the script.

10. Do yes and the game will download then boot. Make sure your emulators are setup properly, as in some platforms you need extraction before running otherwise you will just get error.

11. Play your game.

12. Upon exit it will ask you if u want to keep the game to play it next time or remove it. Removing it removes the actual game and keeps the dummy file.

