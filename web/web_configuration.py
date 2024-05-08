import json

import microdot as dot
import route_config as config
import route_controller as controller
import route_detect as detect
import route_printer as printer


def json_response(data=None, code=200, msg="OK", error:Exception=None):
    """返回JSON格式的响应，包含固定的code和msg字段"""
    response_data = {
        'code': code,
        'msg': msg,
    }

    if data is not None:
        response_data['data'] = data

    if error is not None:
        response_data['error'] = str(error)

    return dot.Response(json.dumps(response_data), content_type='application/json', status=code)

def error_response(error: Exception, msg='error'):
    return json_response(error=error, msg= msg)

app = dot.Microdot()

app.mount('/api/printer', printer)
app.mount('/api/controller', controller)
app.mount('/api/detect', detect)
app.mount('/api/config', config)

if __name__ == '__main__':
    app.run(port=80)