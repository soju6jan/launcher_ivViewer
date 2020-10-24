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
from framework import app, path_app_root, db, path_data
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
        'db_version' : '1',  #추후 2로 변경
        'auto_start' : 'False',
        'url' : 'http://localhost:48000/ivViewer',
        'toon_path' : ''
    }
    current_process = None

    @staticmethod
    def db_init():
        try:
            for key, value in Logic.db_default.items():
                if db.session.query(ModelSetting).filter_by(key=key).count() == 0:
                    db.session.add(ModelSetting(key, value))
            db.session.commit()
            Logic.migration()
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())


    @staticmethod
    def plugin_load():
        try:
            logger.debug('%s plugin_load', package_name)
            tmp = os.path.join(path_data, 'ivViewer_metadata')
            if not os.path.exists(tmp):
                os.makedirs(tmp)
                os.system('chmod 777 -R %s' % tmp)

            Logic.git_pull()
            if platform.system() != 'Windows':
                custom = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')    
                os.system("chmod 777 -R %s" % custom)

            # DB 초기화 
            Logic.db_init()

            # 편의를 위해 json 파일 생성
            from .plugin import plugin_info
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

    @staticmethod
    def migration():
        try:
            db_version = ModelSetting.get('db_version')
            if ModelSetting.get('db_version') == '1':
                tmp = os.path.join(path_data, 'ivViewer_metadata', 'titles')
                if os.path.exists(tmp):
                    import shutil
                    shutil.rmtree(tmp)
                ModelSetting.set('db_version', '2')
                db.session.flush()
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
            if not os.path.exists(command[0]):
                return
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
    def uninstall():
        try:
            def func():
                import system
                Logic.kill()
                commands = [
                    ['msg', u'잠시만 기다려주세요.'],
                    ['/app/data/custom/launcher_ivViewer/files/uninstall.sh'],
                    ['msg', u'삭제가 완료되었습니다.']
                ]
                system.SystemLogicCommand.start('삭제', commands)
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
            else:
                return
            os.system("chmod 777 -R %s" % php_path)
            return True
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
        return False

    
    @staticmethod
    def git_pull_foreground():
        try:
            def func():
                import system
                php_path = '/www/ivViewer'
                if os.path.exists(php_path):
                    commands = [
                        ['msg', u'잠시만 기다려주세요.'],
                        ['git', '-C', php_path, 'reset', '--hard', 'HEAD'],
                        ['git', '-C', php_path, 'pull'],
                        ['chmod', '777', '-R', php_path],
                        ['msg', u'업데이트 완료되었습니다.']
                    ]
                else:
                    commands = [['msg', u'먼저 설치하세요.']]
                system.SystemLogicCommand.start('업데이트', commands)
            t = threading.Thread(target=func, args=())
            t.setDaemon(True)
            t.start()
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
    
    @staticmethod
    def do_soft_link(old):
        try:
            for t in old:
                try:
                    name = os.path.basename(t).strip()
                    logger.debug(name)
                    if name != '':
                        os.system('rm -rf /www/ivViewer/data/%s' % name)
                except Exception as e: 
                    logger.error('Exception:%s', e)
                    logger.error(traceback.format_exc())

            tmp = ModelSetting.get_list('toon_path')
            for t in tmp:
                try:
                    name = os.path.basename(t)
                    os.system('ln -s "%s" /www/ivViewer/data/%s' % (t, name))
                    os.system('chmod 777 -R /www/ivViewer/data/%s' % name)
                except Exception as e: 
                    logger.error('Exception:%s', e)
                    logger.error(traceback.format_exc())
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
    
    
    @staticmethod
    def get_version():
        ret = {}
        try:
            import requests
            ret['ret'] = True
            ret['data'] = requests.get('%s/version.php' % ModelSetting.get('url')).text
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            ret['ret'] = False
            ret['data'] = str(e)
        return ret