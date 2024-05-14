import uuid

import microdot as dot

from impl.bambu_client import BambuClient
from app_config import config
from printer_client import PrinterClient
import web.web_configuration as web

app = dot.Microdot()

@app.route('/add')
def add(request: dot.Request):
    # 解析网络请求，通过请求中的type字段，判断是什么类型的打印机，并生成相应的打印机对象
    type = request.json["type"]
    client:PrinterClient = None
    try:
      if type == BambuClient.type_name():
          client = BambuClient.from_dict(request.args)
      else:
          return web.json_response(code = 400, msg= '不支持的打印机类型：' + type)  # 不支持的打印机类型
      
      config.add_printer(f'{type}_{uuid.uuid1()}', client)
      config.save()

      return web.json_response()
    except Exception as e:
        # 返回错误信息
        return web.json_response(code = 500, msg= '创建打印机失败：' + str(e))
    

@app.route('/remove')
def remove(request: dot.Request):
    id = request.json["id"]
    config.remove_printer(id)
    config.save()

    return web.json_response()
    

        
        
  

  




