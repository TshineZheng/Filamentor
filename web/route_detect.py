import uuid

import microdot as dot

from broken_detect import BrokenDetect
from impl.mqtt_broken_detect import MQTTBrokenDetect
from main import app_config
from web.web_configuration import json_response

app = dot.Microdot()

@app.route('/add')
def add(request: dot.Request):
    type = request.json["type"]
    bd:BrokenDetect = None
    try:
        if type == MQTTBrokenDetect.type_name():
            bd = MQTTBrokenDetect.from_dict(request.args)
        else:
            return json_response(code = 400, msg= '不支持的检测类型：' + type)
    except Exception as e:
        return json_response(code = 500, msg= '创建断料检测器失败：' + str(e))
    
    app_config.add_detect(f'{type}_{uuid.uuid1()}', bd)
    app_config.save()

    return json_response()

@app.route('/remove')
def remove(request: dot.Request):
    id = request.json["id"]
    app_config.remove_detect(id)
    app_config.save()
    return json_response()

@app.route('/bind_printer')
def bind_printer(request: dot.Request):
    printer_id = request.json["printer_id"]
    id = request.json["id"]
    app_config.add_detect_setting(printer_id, id)
    app_config.save()
    return json_response()

@app.route('/unbind_printer')
def unbind_printer(request: dot.Request):
    printer_id = request.json["printer_id"]
    id = request.json["id"]
    app_config.remove_detect_setting(printer_id, id)
    app_config.save()
    return json_response()

