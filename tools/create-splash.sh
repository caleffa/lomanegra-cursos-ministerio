#!/bin/bash

## Script para generar las splash screens
## requiere mogrify (de ImageMagick) instalado en el sistema y un LaunchImage.png (de 1024x768) que será el splash default
## extiende la imagen manteniendo la relación vertical/horizontal del centro de la imagen y agrega color de fondo blanco en los bordes
## para cambiarlo sólo hace falta cambiar el color 'white' por 'black' por ejemplo

cp LaunchImage.png launch-640x1136.png
cp LaunchImage.png launch-750x1334.png
cp LaunchImage.png launch-1125x2436.png
cp LaunchImage.png launch-1242x2208.png
cp LaunchImage.png launch-1536x2048.png
cp LaunchImage.png launch-1668x2224.png
cp LaunchImage.png launch-2048x2732.png
cp LaunchImage.png LaunchImage-750@2x~iphone6-landscape_1334x750.png
cp LaunchImage.png LaunchImage-828@2x~iphoneXr-portrait_828x1792.png
cp LaunchImage.png LaunchImage-1242@3x~iphone6s-landscape_2208x1242.png
cp LaunchImage.png LaunchImage-1242@3x~iphoneXsMax-portrait_1242x2688.png
cp LaunchImage.png LaunchImage-1792@2x~iphoneXr-landscape_1792x828.png
cp LaunchImage.png LaunchImage-2436@3x~iphoneX-landscape_2436x1125.png
cp LaunchImage.png LaunchImage-2688@3x~iphoneXsMax-landscape_2688x1242.png
cp LaunchImage.png LaunchImage-Landscape@2x~ipad_2048x1496.png
cp LaunchImage.png LaunchImage-Landscape@2x~ipad_2048x1536.png
cp LaunchImage.png LaunchImage-Landscape@2x~ipad_2224x1668.png
cp LaunchImage.png LaunchImage-Landscape@2x~ipad_2732x2048.png
cp LaunchImage.png LaunchImage-Landscape~ipad_1024x748.png
cp LaunchImage.png LaunchImage-Landscape~ipad_1024x768.png
cp LaunchImage.png LaunchImage-Portrait@2x~ipad_1536x2008.png
cp LaunchImage.png LaunchImage-Portrait~ipad_768x1024.png
cp LaunchImage.png LaunchImage~ipad.png
cp LaunchImage.png LaunchImage~iphone_640x960.png
cp LaunchImage.png LaunchImage~iphone-320x480.png
mogrify -resize 640x1136 -extent 640x1136 -gravity center -background white launch-640x1136.png
mogrify -resize 750x1334 -extent 750x1334 -gravity center -background white launch-750x1334.png
mogrify -resize 1125x2436 -extent 1125x2436 -gravity center -background white launch-1125x2436.png
mogrify -resize 1242x2208 -extent 1242x2208 -gravity center -background white launch-1242x2208.png
mogrify -resize 1536x2048 -extent 1536x2048 -gravity center -background white launch-1536x2048.png
mogrify -resize 1668x2224 -extent 1668x2224 -gravity center -background white launch-1668x2224.png
mogrify -resize 2048x2732 -extent 2048x2732 -gravity center -background white launch-2048x2732.png
mogrify -resize 1334x750 -extent 1334x750 -gravity center -background white LaunchImage-750@2x~iphone6-landscape_1334x750.png
mogrify -resize 828x1792 -extent 828x1792 -gravity center -background white LaunchImage-828@2x~iphoneXr-portrait_828x1792.png
mogrify -resize 2208x1242 -extent 2208x1242 -gravity center -background white LaunchImage-1242@3x~iphone6s-landscape_2208x1242.png
mogrify -resize 1242x2688 -extent 1242x2688 -gravity center -background white LaunchImage-1242@3x~iphoneXsMax-portrait_1242x2688.png
mogrify -resize 1792x828 -extent 1792x828 -gravity center -background white LaunchImage-1792@2x~iphoneXr-landscape_1792x828.png
mogrify -resize 2436x1125 -extent 2436x1125 -gravity center -background white LaunchImage-2436@3x~iphoneX-landscape_2436x1125.png
mogrify -resize 2688x1242 -extent 2688x1242 -gravity center -background white LaunchImage-2688@3x~iphoneXsMax-landscape_2688x1242.png
mogrify -resize 2048x1496 -extent 2048x1496 -gravity center -background white LaunchImage-Landscape@2x~ipad_2048x1496.png
mogrify -resize 2048x1536 -extent 2048x1536 -gravity center -background white LaunchImage-Landscape@2x~ipad_2048x1536.png
mogrify -resize 2224x1668 -extent 2224x1668 -gravity center -background white LaunchImage-Landscape@2x~ipad_2224x1668.png
mogrify -resize 2732x2048 -extent 2732x2048 -gravity center -background white LaunchImage-Landscape@2x~ipad_2732x2048.png
mogrify -resize 1024x748 -extent 1024x748 -gravity center -background white LaunchImage-Landscape~ipad_1024x748.png
mogrify -resize 1024x768 -extent 1024x768 -gravity center -background white LaunchImage-Landscape~ipad_1024x768.png
mogrify -resize 1536x2008 -extent 1536x2008 -gravity center -background white LaunchImage-Portrait@2x~ipad_1536x2008.png
mogrify -resize 768x1024 -extent 768x1024 -gravity center -background white LaunchImage-Portrait~ipad_768x1024.png
mogrify -resize 640x960 -extent 640x960 -gravity center -background white LaunchImage~iphone_640x960.png
mogrify -resize 320x480 -extent 320x480 -gravity center -background white LaunchImage~iphone-320x480.png
mogrify -resize 1536x2008 -extent 1536x2008 -gravity center -background white LaunchImage~ipad.png
