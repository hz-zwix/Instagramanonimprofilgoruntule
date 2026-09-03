# --- buildozer.spec ---
[app]
title = IG Profil Analiz
package.name = igprofilanaliz
package.domain = org.wenzy
source.dir = .
source.include_exts = py,kv,png,jpg,ttf
version = 1.0.0
requirements = python3==3.11,kivy==2.3.0,instaloader==4.10,certifi,urllib3,requests
orientation = portrait
fullscreen = 0
android.minapi = 21
android.targetapi = 33
android.archs = arm64-v8a, armeabi-v7a
android.permissions = INTERNET
android.allow_backup = False

[buildozer]
log_level = 2
warn_on_root = 1
