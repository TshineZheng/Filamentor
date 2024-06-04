from typing import List
import microdot as dot
import web.web_configuration as web

from mqtt_config import MQTTConfig
from app_config import config

import ams_core

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


@app.route('/sync')
def sync(request: dot.Request):
    controller_state: List[dict] = []
    ams_info: List[dict] = []

    for c in config.controller_list:
        controller_state.append(
            {
                'controller_id': c.id,
                'channel_states': c.controller.get_channel_states()
            }
        )

    for p in ams_core.ams_list:
        ams_info.append({
            'printer_id': p.use_printer,
            'fila_cur': p.fila_cur,
            'cur_task': p.task_name
        })

    return web.json_response(
        {
            'ams': ams_info,
            'controller': controller_state
        }
    )


@app.route('/set_fila_cur')
def set_fila_cur(request: dot.Request):
    printerid = request.args.get("printer_id")
    fila = int(request.args.get("fila_cur"))

    for p in ams_core.ams_list:
        if p.use_printer == printerid:
            if p.task_name is not None and p.task_name != '':
                return web.json_response(code=500, msg='打印中，无法设置当前通道')
            p.update_cur_fila(fila)
            return web.json_response()

    return web.error_response(msg='打印机未找到')


@app.route('/set_fila_change_temp')
def set_fila_change_temp(request: dot.Request):
    printerid = request.args.get("printer_id")
    temp = int(request.args.get("change_temp"))

    for p in ams_core.ams_list:
        if p.use_printer == printerid:
            p.change_tem = temp
            config.set_printer_change_tem(printerid, temp)
            return web.json_response()

    return web.error_response(msg='打印机未找到')


@app.route('/restart')
def restart(request: dot.Request):
    import main
    main.restart()
    return web.json_response()