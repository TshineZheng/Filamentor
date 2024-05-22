import uuid

import microdot as dot

from controller import ChannelAction, Controller
from impl.yba_ams_controller import YBAAMSController
from app_config import config
from impl.yba_ams_py_controller import YBAAMSPYController
import web.web_configuration as web

app = dot.Microdot()

@app.route('/add')
def add(request: dot.Request):
    type = request.json["type"]
    controller: Controller = None
    try:
        if type == YBAAMSController.type_name():
            controller = YBAAMSController.from_dict(request.args)
        else:
            return web.json_response(code = 400, msg= '不支持的控制器类型：' + type)
    except Exception as e:
        return web.json_response(code = 500, msg= '创建控制器失败：' + str(e))
    
    config.add_controller(f'{type}_{uuid.uuid1()}', controller)
    config.save()
    return web.json_response()

@app.route('/remove')
def remove(request: dot.Request):
    id = request.json["id"]
    config.remove_controller(id)
    config.save()
    return web.json_response()

@app.route('/bind_printer')
def bind_printer(request: dot.Request):
    channel = request.json["channel"]
    printer_id = request.json["printer_id"]
    controller_id = request.json["controller_id"]
    config.add_channel_setting(printer_id, controller_id, channel)
    return web.json_response()

@app.route('/unbind_printer')
def unbind_printer(request: dot.Request):
    channel = request.json["channel"]
    controller_id = request.json["controller_id"]
    printer_id = request.json["printer_id"]
    config.remove_channel_setting(printer_id, controller_id, channel)
    return web.json_response()

@app.route('/control')
def controll(request: dot.Request):
    channel = request.args.get("channel")
    controller_id = request.args.get("controller_id")
    action = request.args.get("action")
    config.get_controller(controller_id).control(int(channel), ChannelAction(int(action)))
    return web.json_response()

@app.route('/get_system_status')
def get_status(request: dot.Request):
    controller_id = request.args.get("controller_id")

    c = config.get_controller(controller_id)

    if c.type_name() == YBAAMSPYController.type_name():
        return web.json_response({'status': c.get_system_info()})

    return web.json_response(msg='unsupported controller type')