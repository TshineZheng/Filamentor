import uuid

import microdot as dot

from controller import Controller
from impl.yba_ams_controller import YBAAMSController
from main import app_config
from web.web_configuration import json_response

app = dot.Microdot()

@app.route('/add')
def add(request: dot.Request):
    type = request.json["type"]
    controller: Controller = None
    try:
        if type == YBAAMSController.type_name():
            controller = YBAAMSController.from_dict(request.args)
        else:
            return json_response(code = 400, msg= '不支持的控制器类型：' + type)
    except Exception as e:
        return json_response(code = 500, msg= '创建控制器失败：' + str(e))
    
    app_config.add_controller(f'{type}_{uuid.uuid1()}', controller)
    app_config.save()
    return json_response()

@app.route('/remove')
def remove(request: dot.Request):
    id = request.json["id"]
    app_config.remove_controller(id)
    app_config.save()
    return json_response()

@app.route('/bind_printer')
def bind_printer(request: dot.Request):
    channel = request.json["channel"]
    printer_id = request.json["printer_id"]
    controller_id = request.json["controller_id"]
    app_config.add_channel_setting(printer_id, controller_id, channel)
    return json_response()

@app.route('/unbind_printer')
def unbind_printer(request: dot.Request):
    channel = request.json["channel"]
    controller_id = request.json["controller_id"]
    printer_id = request.json["printer_id"]
    app_config.remove_channel_setting(printer_id, controller_id, channel)
    return json_response()
