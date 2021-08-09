#!/bin/bash

## Script para generar los íconos (excepto favicon.ico, que se puede generar desde https://favicon.io/, por ejemplo)
## requiere convert (de ImageMagick) instalado en el sistema y un Logo.png (de tamaño cuadrado) que será la imagen del ícono

convert Logo.png -resize 144x144 android-chrome-144x144.png
convert Logo.png -resize 192x192 android-chrome-192x192.png
convert Logo.png -resize 256x256 android-chrome-256x256.png
convert Logo.png -resize 36x36 android-chrome-36x36.png
convert Logo.png -resize 384x384 android-chrome-384x384.png
convert Logo.png -resize 48x48 android-chrome-48x48.png
convert Logo.png -resize 512x512 android-chrome-512x512.png
convert Logo.png -resize 72x72 android-chrome-72x72.png
convert Logo.png -resize 96x96 android-chrome-96x96.png
convert Logo.png -resize 144x144 android-icon-144x144.png
convert Logo.png -resize 192x192 android-icon-192x192.png
convert Logo.png -resize 36x36 android-icon-36x36.png
convert Logo.png -resize 48x48 android-icon-48x48.png
convert Logo.png -resize 72x72 android-icon-72x72.png
convert Logo.png -resize 96x96 android-icon-96x96.png
convert Logo.png -resize 114x114 apple-icon-114x114.png
convert Logo.png -resize 120x120 apple-icon-120x120.png
convert Logo.png -resize 144x144 apple-icon-144x144.png
convert Logo.png -resize 152x152 apple-icon-152x152.png
convert Logo.png -resize 180x180 apple-icon-180x180.png
convert Logo.png -resize 57x57 apple-icon-57x57.png
convert Logo.png -resize 60x60 apple-icon-60x60.png
convert Logo.png -resize 72x72 apple-icon-72x72.png
convert Logo.png -resize 76x76 apple-icon-76x76.png
convert Logo.png -resize 72x72 apple-icon-precomposed.png
convert Logo.png -resize 192x192 apple-icon.png
convert Logo.png -resize 114x114 apple-touch-icon-114x114.png
convert Logo.png -resize 120x120 apple-touch-icon-120x120.png
convert Logo.png -resize 144x144 apple-touch-icon-144x144.png
convert Logo.png -resize 152x152 apple-touch-icon-152x152.png
convert Logo.png -resize 180x180 apple-touch-icon-180x180.png
convert Logo.png -resize 57x57 apple-touch-icon-57x57.png
convert Logo.png -resize 60x60 apple-touch-icon-60x60.png
convert Logo.png -resize 72x72 apple-touch-icon-72x72.png
convert Logo.png -resize 76x76 apple-touch-icon-76x76.png
convert Logo.png -resize 180x180 apple-touch-icon.png
convert Logo.png -resize 16x16 favicon-16x16.png
convert Logo.png -resize 32x32 favicon-32x32.png
convert Logo.png -resize 96x96 favicon-96x96.png
convert Logo.png -resize 144x144 ms-icon-144x144.png
convert Logo.png -resize 150x150 ms-icon-150x150.png
convert Logo.png -resize 310x310 ms-icon-310x310.png
convert Logo.png -resize 70x70 ms-icon-70x70.png
convert Logo.png -resize 144x144 mstile-144x144.png
convert Logo.png -resize 150x150 mstile-150x150.png
convert Logo.png -resize 310x150 mstile-310x150.png
convert Logo.png -resize 310x310 mstile-310x310.png
convert Logo.png -resize 70x70 mstile-70x70.png
