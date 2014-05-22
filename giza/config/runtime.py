import logging
import os.path
import yaml

logger = logging.getLogger(os.path.basename(__file__))

from utils.shell import CommandError

from config.base import ConfigurationBase

class RuntimeStateConfig(ConfigurationBase):
    _option_registry = [ 'length', 'conf_path', 'days_to_save', 'builder_to_delete' ]

    def __init__(self, obj=None):
        super(RuntimeStateConfig, self).__init__(obj)
        self._conf = None
        self._branch_conf = None

    def __setattr__(self, key, value):
        if key in self._option_registry:
            self.state[key] = value
        else:
            ConfigurationBase.__setattr__(self, key, value)

    def __getattr__(self, key):
        try:
            return object.__getattr__(self, key)
        except AttributeError as e:
            if key in self._option_registry:
                return self.state[key]
            else:
                raise e

    @property
    def function(self):
        return self.state['_entry_point']

    @function.setter
    def function(self, value):
        self.state['_entry_point'] = value

    @property
    def conf(self):
        return self._conf

    @conf.setter
    def conf(self, value):
        if isinstance(value, ConfigurationBase):
            self._conf = value
        else:
            m = 'invalid configuration object: {0}'.format(value)
            m.error(m)
            raise TypeError(m)

    @property
    def level(self):
        return self.state['level']

    @level.setter
    def level(self, value):
        levels = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.critical
        }
        if value in levels:
            level = levels[value]
            logging.basicConfig(level=level)
            self.state['level'] = value

    @property
    def runner(self):
        if 'runner' not in self.state:
            self.runner = None

        return self.state['runner']

    @runner.setter
    def runner(self, value):
        supported_runners = ['process', 'thread', 'serial']

        if value is None:
            self.state['runner'] = 'process'
        elif value in supported_runners:
            self.state['runner'] = value
        else:
            m = '{0} is not a supported runner type, choose from: {1}'.format(vale, supported_runners)
            logger.error(m)
            raise TypeError(m)

    @property
    def force(self):
        if 'force' in self.state:
            return self.state['force']
        else:
            return False

    @force.setter
    def force(self, value):
        if isinstance(value, bool):
            self.state['force'] = value
        else:
            raise TypeError

    @property
    def language(self):
        if 'language' not in self.state:
            return 'en'
        else:
            return self.state['language']

    @language.setter
    def language(self, value):
        self.state['language'] = value

    @property
    def edition(self):
        if 'edition' not in self.state:
            return False
        else:
            return self.state['edition']

    @edition.setter
    def edition(self, value):
        self.state['edition'] = value

    @property
    def branch_conf(self):
        if self._branch_conf is None:
            self.branch_conf = None

        return self._branch_conf

    @branch_conf.setter
    def branch_conf(self, value):
        fn = os.path.join(self.conf.paths.builddata, 'published_branches.yaml')

        if self.conf.git.branches.current == 'master'and not os.path.exists(fn):
            self._branch_conf = {}
        else:
            try:
                data = self.conf.git.repo.branch_file(path=fn, branch='master')
            except CommandError:
                logger.critical('giza not configured to work with buildbot repos')
                self._branch_conf = {}
                return

            self._branch_conf = yaml.load(data)

    @property
    def builder(self):
        if 'builder' not in self.state:
            self.state['builder'] = 'html'

        return self.state['builder']

    @builder.setter
    def builder(self, value):
        #todo: make following validation list more dynamically assembled.
        #todo ensure this value is always a list.

        if value in [None, 'dirhtml', 'html', 'json', 'epub', 'latex', 'singlehtml']:
            self.state['builder'] = value
        elif value == 'pdf':
            self.state['builder'] = 'latex'
