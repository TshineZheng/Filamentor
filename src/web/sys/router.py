from typing import List

from fastapi import APIRouter, Depends
from src.ams_core import ams_list
from src.app_config import config

router = APIRouter()


@router.get('/config')
async def get_config():
    return config.to_dict()


@router.get('/sync')
async def sync():
    controller_state: List[dict] = []
    ams_info: List[dict] = []

    for c in config.controller_list:
        controller_state.append(
            {
                'controller_id': c.id,
                'channel_states': c.controller.get_channel_states()
            }
        )

    for p in ams_list:
        ams_info.append({
            'printer_id': p.use_printer,
            'fila_cur': p.fila_cur,
            'cur_task': p.task_name
        })

    return {'ams': ams_info, 'controller': controller_state}
