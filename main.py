import os
import time
import logger
from utils import Popen, pretty_time

NAME = 'plugin-updater'
API = 665

SETTINGS = 'plugin_updater_config'


class Main:
    def __init__(self, cfg, log, owner):
        self.cfg = cfg
        self.log = log
        self.own = owner
        self.disable = False

        self._settings = self._get_settings()

    def _get_settings(self) -> dict:
        def_cfg = {'deprecated': True, 'broken': False, 'all': False, 'restart': True}
        cfg = self.cfg.load_dict(SETTINGS)
        if isinstance(cfg, dict):
            is_ok = True
            for key, val in def_cfg.items():
                if key not in cfg or not isinstance(cfg[key], type(val)):
                    is_ok = False
                    break
            if is_ok:
                return cfg
        self.cfg.save_dict(SETTINGS, def_cfg, True)
        return def_cfg

    def start(self):
        upgraded = []
        checked = 0
        states = ('all',) if self._settings['all'] else ('deprecated', 'broken')
        work_time = time.time()
        for state in states:
            if self._settings[state]:
                result = self._upgrade(self.own.plugins_status(state))
                upgraded.extend(result[0])
                checked += result[1]
        work_time = time.time() - work_time
        if checked:
            self.log('Checked {} plugins in {}'.format(checked, pretty_time(work_time)))
        if not upgraded:
            return
        if self._settings['restart']:
            msg = 'Restarting...'
        else:
            msg = 'Terminal must be restarted.'
        self.log('Updated plugins: {}. {}'.format(', '.join(upgraded), msg), logger.INFO)
        if self._settings['restart']:
            self.own.die_in(wait=8, reload=True)

    def _upgrade(self, targets: dict) -> tuple:
        result = []
        checked = 0
        for name, path in targets.items():
            if not os.path.isdir(os.path.join(path, '.git')):
                continue
            checked += 1
            try:
                if _upgrade_from_git(path):
                    result.append(name)
            except RuntimeError as e:
                self.log('Error plugin upgrading {} in {}: {}'.format(name, path, e), logger.ERROR)
        return result, checked


def _upgrade_from_git(path: str) -> bool:
    old_hash = _get_hash(path)
    _git(['pull'], path)
    new_hash = _get_hash(path)
    return old_hash != new_hash


def _is_commit_hash(commit_hash):
    if not isinstance(commit_hash, str):
        return False
    return len(commit_hash) == 40


def _get_hash(path: str):
    data = _git(['log', '-n', '1'], path)
    hash_ = data.split('\n')[0].split(' ')[-1]
    if not _is_commit_hash(hash_):
        raise RuntimeError('Error getting hash from git: {}'.format(repr(data)))
    return hash_


def _git(cmd: list, path: str):
    return Popen(['git', '-C', path] + cmd).run()
