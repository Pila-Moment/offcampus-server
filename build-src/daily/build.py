import sys
src=open('daily/src.html').read()
css=open('playtest/css/leaflet.css').read()
head5=open('bundle/droppin.html').read().split('\n')
inject='\n'.join(head5[2:4])  # base style + __allGames script
src=src.replace('/*LEAFLET_CSS*/',css,1)
src=src.replace('<head><meta charset="utf-8">','<head><meta charset="utf-8">'+'\n'+inject+'\n',1)
open('bundle/daily.html','w').write(src)
print(len(src))
