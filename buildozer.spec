[app]

title = Tetris
package.name = tetris
package.domain = org.tetris
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 0.5

requirements = python3,kivy==2.2.1

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 34
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# Signing
android.keystore = tetris.keystore
android.keystore.alias = tetris
android.keystore.password = tetris123
android.keystore.keypassword = tetris123

[buildozer]

log_level = 2
warn_on_root = 1
