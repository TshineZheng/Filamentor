from typing import List

from fastapi import APIRouter, Depends
from src.ams_core import ams_list
from src.app_config import DetectRelation, IDBrokenDetect, config

router = APIRouter()


@router.get('/config')
async def get_config():
    d = config.to_dict()

    detect_list = d['detect_list']
    detect_relation_list = d['detect_relations']

    # 将所有打印机和控制器自带的断料检测器构造出来，还有关系
    for printer in config.printer_list:
        if printer.client.filament_broken_detect() is not None:
            detect_list.append(IDBrokenDetect(printer.id, printer.client.filament_broken_detect(), printer.alias).to_dict())
            detect_relation_list.append(DetectRelation(printer.id, printer.id).to_dict())

        # FIXME： 控制器断料检测器绑定打印机的逻辑不对，断料检测器应该和通道或者控制器绑定，而不是和打印机绑定
        for c in config.controller_list:
            if c.controller.get_broken_detect() is not None:
                detect_list.append(IDBrokenDetect(c.id, c.controller.get_broken_detect(), c.alias).to_dict())
                detect_relation_list.append(DetectRelation(printer.id, c.id).to_dict())

    return d


@router.get('/sync')
async def sync():
    controller_state: List[dict] = []
    ams_info: List[dict] = []
    detect_info: List[dict] = []

    for printer in config.printer_list:
        if printer.client.filament_broken_detect() is not None:
            detect_info.append({
                'detect_id': printer.id,
                'is_broken': printer.client.filament_broken_detect().is_filament_broken()
            })

    for c in config.controller_list:
        controller_state.append(
            {
                'controller_id': c.id,
                'channel_states': c.controller.get_channel_states()
            }
        )

        if c.controller.get_broken_detect() is not None:
            detect_info.append({
                'detect_id': c.id,
                'is_broken': c.controller.get_broken_detect().is_filament_broken()
            })

    for p in ams_list:
        ams_info.append({
            'printer_id': p.use_printer,
            'fila_cur': p.fila_cur,
            'cur_task': p.task_name
        })

    for d in config.detect_list:
        detect_info.append({
            'detect_id': d.id,
            'is_broken': d.detect.is_filament_broken()
        })

    return {'ams': ams_info, 'controller': controller_state, 'detect': detect_info}
