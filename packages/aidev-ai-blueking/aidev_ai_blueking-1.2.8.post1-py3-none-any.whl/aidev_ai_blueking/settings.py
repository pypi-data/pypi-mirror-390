# -*- coding: utf-8 -*-
import os

# 应用模块
INSTALLED_APPS = ("aidev_ai_blueking",)

BKPAAS_APP_CODE = os.getenv("BKPAAS_APP_ID")
BKAPP_SAAS_PATH = f"/{BKPAAS_APP_CODE}"
