# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2024/2/2 10:10
# Author     ：Maxwell
# Description：
"""
from fastapi import APIRouter
from descartcan.service.api.monitor_api import monitor_router
from descartcan.service.api.health_router import health_router
from descartcan.config import config

api_router = APIRouter(prefix=config.APP_BASE_URI)
api_router.include_router(prefix="/api/monitor", router=monitor_router, tags=["服务状态"])
api_router.include_router(prefix="/api/health", router=health_router, tags=["服务状态"])

