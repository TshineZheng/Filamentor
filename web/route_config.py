import microdot as dot
import web.web_configuration as web

from mqtt_config import MQTTConfig
from app_config import config

app = dot.Microdot()

@app.route('/get_config')
def save(request: dot.Request):
    return web.json_response(config.to_dict())

@app.route('/mqtt_config')
def mqtt_config(request: dot.Request):
    mqtt = MQTTConfig.from_dict(request.json)
    config.mqtt_config = mqtt
    config.save()
    return web.json_response()
