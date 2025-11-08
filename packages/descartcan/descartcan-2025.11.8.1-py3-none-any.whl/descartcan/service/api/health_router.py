# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2023/12/9 13:39
# Author     ：Maxwell
# Description：
"""

from fastapi import Request, APIRouter, Security, BackgroundTasks

from app.core.response import success

health_router = APIRouter(prefix="")


@health_router.get(summary="", path="")
async def api_health(req: Request):
    return success()

