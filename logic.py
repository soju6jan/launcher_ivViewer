# -*- coding: utf-8 -*-
#########################################################
# python
import os
import sys
import traceback
import logging
import threading
import subprocess
import platform
import time
# third-party

# sjva 공용
from framework import app, path_app_root, db
from framework.logger import get_logger
from framework.util import Util

# 패키지
from .plugin import package_name, logger
from .model import ModelSetting

#########################################################
import requests
import urllib
import time
import threading
from datetime import datetime

class Logic(object):
    db_default = {
        'auto_start' : 'False',
        'url' : 'http://localhost:48000/ivViewer',
        'path' : ''
    }
    current_process = None

    @staticmethod
    def db_init():
        try:
            for key, value in Logic.db_default.items():
                if db.session.query(ModelSetting).filter_by(key=key).count() == 0:
                    db.session.add(ModelSetting(key, value))
            db.session.commit()
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())


    @staticmethod
    def plugin_load():
        try:
            logger.debug('%s plugin_load', package_name)
            Logic.git_pull()

            if platform.system() != 'Windows':
                custom = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'file')    
                os.system("chmod 777 -R %s" % custom)

            # DB 초기화 
            Logic.db_init()

            # 편의를 위해 json 파일 생성
            from plugin import plugin_info
            Util.save_from_dict_to_json(plugin_info, os.path.join(os.path.dirname(__file__), 'info.json'))

            # 자동시작 옵션이 있으면 보통 여기서 
            if ModelSetting.query.filter_by(key='auto_start').first().value == 'True':
                Logic.scheduler_start()
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())


    @staticmethod
    def plugin_unload():
        try:
            Logic.kill()
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())


    @staticmethod
    def scheduler_start():
        try:
            Logic.run()
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())


    @staticmethod
    def scheduler_stop():
        try:
            Logic.kill()
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    # 기본 구조 End
    ##################################################################

    @staticmethod
    def run():
        try:
            Logic.kill()
            command = ['/app/data/custom/launcher_ivViewer/files/run.sh']
            #Util.execute_command(command)
            Logic.current_process = subprocess.Popen(command)
            logger.debug('RUN............................')
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            
    @staticmethod
    def kill():
        try:
            command = ['/app/data/custom/launcher_ivViewer/files/kill.sh']
            Util.execute_command(command)
            if Logic.current_process is not None and Logic.current_process.poll() is None:
                import psutil
                process = psutil.Process(Logic.current_process.pid)
                for proc in process.children(recursive=True):
                    proc.kill()
                process.kill()
            Logic.current_process = None

        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def install():
        try:
            def func():
                import system
                Logic.kill()
                commands = [
                    ['msg', u'잠시만 기다려주세요.'],
                    ['/app/data/custom/launcher_ivViewer/files/install.sh'],
                    ['msg', u'설치가 완료되었습니다.']
                ]
                system.SystemLogicCommand.start('설치', commands)
            t = threading.Thread(target=func, args=())
            t.setDaemon(True)
            t.start()
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def is_installed():
        try:
            target = '/www/ivViewer'
            if os.path.exists(target):
                return True
            else:
                return False
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def git_pull():
        try:
            php_path = '/www/ivViewer'
            if os.path.exists(php_path):
                command = ['git', '-C', php_path, 'reset', '--hard', 'HEAD']
                ret = Util.execute_command(command)
                command = ['git', '-C', php_path, 'pull']
                ret = Util.execute_command(command)
            os.system("chmod 777 -R %s" % php_path)
            return True
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
        return False