# How to downgrade Fallout 4 manually

Pre-requisites for downgrading:
Fallout 4, Wasteland Workshop DLC, Automatron DLC

First you need to download SteamCMD [via this link]([steam://open/console](https://developer.valvesoftware.com/wiki/SteamCMD#Downloading_SteamCMD)) and extract the archive to a known place.

Then run the following command depending on your operating system. These will download the depots in the folder where you extracted SteamCMD.

**Note**: You must replace `<username>` and `<password>`, but it's suggested to keep the quotes around your password in case you have any special characters.

**Windows**
```
steamcmd.exe +login <username> "<password>" +download_depot 377160 377161 7497069378349273908 +download_depot 377160 377162 5847529232406005096 +download_depot 377160 377163 5819088023757897745 +download_depot 377160 377164 2178106366609958945 +download_depot 377160 435880 1255562923187931216 +download_depot 377160 435870 1691678129192680960 +download_depot 377160 435871 5106118861901111234 +quit
```

**Unix**
```
./steamcmd +login <username> "<password>" +download_depot 377160 377161 7497069378349273908 +download_depot 377160 377162 5847529232406005096 +download_depot 377160 377163 5819088023757897745 +download_depot 377160 377164 2178106366609958945 +download_depot 377160 435880 1255562923187931216 +download_depot 377160 435870 1691678129192680960 +download_depot 377160 435871 5106118861901111234 +quit
```

After download each depot manually you can move the contents of each subfolder, from within the SteamCMD folder, into your Fallout 4 installation folder, ensuring you overwrite all files in the destination folder

_Note 1: The location of your ‘steamapps/content’ folder may vary if your Steam install isn’t in the default location or you’re using an Operating System other than Windows  
Note 2: You can open up your Fallout 4 installation folder easily in Steam by right-clicking on Fallout 4 in your Steam Library and then selecting Manage > Browse Local Files:_

<details open>
<summary>Image examples</summary>

![](./img/Manually/image5.png)
![](./img/Manually/image6.png)
</details>

<br>

```
C:/Program Files (x86)/Steam/steamapps/content/app_377160
```

If you want to block updates you additionally have set the following file to read only

_Note 1: The location of your ‘steamapps/appmanifest_377160.acf’ file may vary if the Steam Library Fallout 4 is installed to isn’t in the default location or you’re using an Operating System other than Windows:_
 
<details open>
<summary>Image examples</summary>

![](./img/Manually/image7.jpg)
![](./img/Manually/image8.jpg)
</details>

<br>

```
C:\Program Files (x86)\Steam\steamapps\appmanifest_377160.acf
```

After doing all of this you should remove Creation Club content by removing every file inside 'steamapps/common/Fallout 4/Data' with cc in the start

<details open>
<summary>Image examples</summary>

![](./img/Manually/image9.png)
</details>

<br>
