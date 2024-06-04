import uuid

import microdot as dot

from controller import ChannelAction, Controller
from impl.yba_ams_controller import YBAAMSController
from app_config import config
from impl.yba_ams_py_controller import YBAAMSPYController
from impl.yba_ams_servo_controller import YBAAMSServoController
import web.web_configuration as web
import main
from urllib.parse import unquote

app = dot.Microdot()

@app.route('/add')
def add(request: dot.Request):
    type = request.json["type"]
    alias = unquote(request.json["alias"])
    controller: Controller = None
    try:
        if type == YBAAMSController.type_name():
            controller = YBAAMSController.from_dict(request.json['info'])
        elif type == YBAAMSPYController.type_name():
            controller = YBAAMSPYController.from_dict(request.json['info'])
        elif type == YBAAMSServoController.type_name():
            controller = YBAAMSServoController.from_dict(request.json['info'])
        else:
            return web.json_response(code = 400, msg= '不支持的控制器类型：' + type)
    except Exception as e:
        return web.json_response(code = 500, msg= '创建控制器失败：' + str(e))
    
    r,msg = config.add_controller(f'{type}_{uuid.uuid1()}', controller, alias)

    if r == False:
        return web.json_response(code = 500, msg= msg)

    config.save()
    main.restart()
    return web.json_response()

@app.route('/remove')
def remove(request: dot.Request):
    id = request.args["controller_id"]
    config.remove_controller(id)
    config.save()
    main.restart()
    return web.json_response()

@app.route('/bind_printer')
def bind_printer(request: dot.Request):
    printer_id = request.args["printer_id"]
    controller_id = request.args["controller_id"]
    channel = int(request.args["channel"])
    config.add_channel_setting(printer_id, controller_id, channel)
    config.save()
    return web.json_response()

@app.route('/unbind_printer')
def unbind_printer(request: dot.Request):
    controller_id = request.args["controller_id"]
    printer_id = request.args["printer_id"]
    channel = int(request.args["channel"])
    config.remove_channel_setting(printer_id, controller_id, channel)
    config.save()
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
        return web.json_response({'status': c.get_system_status()})

    return web.json_response(msg='unsupported controller type')

@app.route('/edit_channel_filament_setting')
def edit_channel_filament_setting(request: dot.Request):
    controller_id = request.args.get("controller_id")
    channel = int(request.args.get("channel"))
    filament_type = unquote(request.args.get("filament_type"))
    filament_color = request.args.get("filament_color")
    for cr in config.channel_relations:
        if cr.controller_id == controller_id and cr.channel == channel:
            cr.filament_type = filament_type
            cr.filament_color = filament_color
            break
    config.save()
    return web.json_response()