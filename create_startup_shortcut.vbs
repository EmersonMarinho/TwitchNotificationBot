Set WshShell = CreateObject("WScript.Shell")
strStartup = WshShell.SpecialFolders("Startup")
Set oShellLink = WshShell.CreateShortcut(strStartup & "\TwitchBot.lnk")
oShellLink.TargetPath = WshShell.CurrentDirectory & "\start_bot.bat"
oShellLink.WorkingDirectory = WshShell.CurrentDirectory
oShellLink.Description = "Twitch Notification Bot"
oShellLink.Save 