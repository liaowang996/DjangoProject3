

import jsonpath


d1 ={"errcode":40164,"errmsg":"invalid ip 175.8.24.229 ipv6 ::ffff:175.8.24.229, not in whitelist rid: 68c57311-7b08856b-6a087b67"}

print(jsonpath.jsonpath(d1,'$.errmsg'))

d2 = {"tags":[{'id':1,"name":"tag1"},
              {'id':2,"name":"tag2"},
              {'id':3,"name":"tag3"},
              {'id':4,"name":"tag4"},
              {'id':5,"name":"tag5"},
              {'id':6,"name":"tag6"}]}