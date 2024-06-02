import json
import microdot as dot

def json_response(data=None, code=0, msg="OK", error:Exception=None):
    """返回JSON格式的响应，包含固定的code和msg字段"""
    response_data = {
        'code': code,
        'msg': msg,
    }

    if data is not None:
        response_data['data'] = data

    if error is not None:
        response_data['error'] = str(error)

    return dot.Response(json.dumps(response_data), 200, headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'})

def error_response(error: Exception, msg='error'):
    return json_response(error=error, msg= msg)

app = dot.Microdot()

def run():
    import web.route_sys as sys
    import web.route_controller as controller
    import web.route_detect as detect
    import web.route_printer as printer

    app.mount(printer.app, '/api/printer')
    app.mount(controller.app, '/api/controller')
    app.mount(detect.app, '/api/detect')
    app.mount(sys.app, '/api/sys')
    
    app.run(port=7170, host='0.0.0.0')

def stop():
    app.shutdown()