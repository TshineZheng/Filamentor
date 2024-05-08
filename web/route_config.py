import microdot as dot
from web_configuration import json_response

from ..main import app_config
from ..mqtt_config import MQTTConfig

app = dot.Microdot()

@app.route('/get_config')
def save(request: dot.Request):
    return json_response(app_config.to_dict())

@app.route('/mqtt_config')
def mqtt_config(request: dot.Request):
    mqtt = MQTTConfig.from_dict(request.json)
    app_config.mqtt_config = mqtt
    app_config.save()
    return json_response()
