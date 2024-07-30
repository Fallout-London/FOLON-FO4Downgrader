# FOLON's Fallout 4 Downgrader

If you do not trust it there's a [document Here](./Manually.md) which guides you through downgrading manually.

On linux This requires qt and curl to be installed, how it is installed depends on your distro, but it should work on windows out of the box.

To run this [get a binary from Releases](https://github.com/Fallout-London/FOLON-FO4Downgrader/releases/latest) for windows or run the following on Linux.

```
git clone https://github.com/Fallout-London/FOLON-FO4Downgrader.git && cd FOLON-FO4Downgrader && chmod +x Run.sh && ./Run.sh
```

## Issues with Steam Authenticator?
If you tried to sign in with your Steam username and password, but are stuck at being asked for your Steam Guard code in the console window, try:
1. Open `FOLON-Downgrader-Files\SteamFiles` in the same folder as the downgrader.exe
2. Click the folder path at the top of your File Explorer, type `cmd` and hit Enter.
3. In this new window, copy and paste the following (Replacing `<username>` and `<password>`, then hit Enter: `DepotDownloader.exe -username <username> -password <password> -remember-password -app 377160 -depot 377162`
4. You should now be able to type your Steam Guard code when requested. After it starts to download, close the window, and resume using FOLON's Fallout 4 Downgrader.
5. FOLON's Fallout 4 Downgrader should now not need a Steam Guard code, as Steam DepotDownloader should remember your token.

## To build
Read the [build document](./build.md)

## Thanks to
[Cornelius Rosenaa for making this](https://coffandro.github.io/)\
[Michel for testing on windows](https://www.linkedin.com/in/michellichand/)\
[SteamRE for DepotDownloader](https://github.com/SteamRE/DepotDownloader)\
[Zerratar for reference FO4-Downgrader](https://www.twitch.tv/zerratar)\
[feathericons for icons](https://feathericons.com/)\
[yjg30737 for his PyQtLoadingscreen script](https://github.com/yjg30737/pyqt-translucent-full-loading-screen-thread)
