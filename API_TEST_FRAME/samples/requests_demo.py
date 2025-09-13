
import requests

ssesion = requests.session()

hosts = 'http://127.0.0.1:3000'
#登录
get_params = {

}
headers = {
    "Content-Type": "application/json"
            }
post_params = {
    "email": "peter@klaven",
    "password": "cityslicka"
}
res01 = ssesion.get(url = hosts+'/api/login',
                     json = post_params,
                     headers = headers
                     ,params = get_params
                     )
print(res01.status_code)




