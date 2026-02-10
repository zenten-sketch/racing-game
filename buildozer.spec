[app]
title = Racing 2D
package.name = racing2d
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,wav
source.include_patterns = assets/*,sounds/*
version = 1.0
requirements = python3,kivy,pygame
orientation = portrait
fullscreen = 1
android.api = 31
android.minapi = 21
android.ndk = 23b
android.permissions = INTERNET
android.archs = armeabi-v7a
android.accept_sdk_license = True
p4a.branch = master

[buildozer]
log_level = 2
