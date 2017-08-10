import requests

url = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_33340745'

print url[url.rfind('_')+1:]
