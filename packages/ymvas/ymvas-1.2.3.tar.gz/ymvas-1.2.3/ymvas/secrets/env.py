from ymvas.compiler.references import Ref
from ymvas.settings import Settings
from os.path import exists, dirname, isdir, join, basename
import inspect, os, json, yaml, io
from dotenv.main import DotEnv
from ymvas.utils import YException

class Environ:
    ref      : Ref
    file     : str
    settings : Settings

    def __init__(
        self, 
        src:str = '.env', 
        settings:Settings | None = None
    ):

        caller = inspect.stack()[1]
        source = dirname(caller.filename)

        self.src      = join(source, dirname(src))
        self.settings = settings if settings is not None else self.__get_settings()
        self.__is_env = False

        self.file     = self.__find__file()

        if not (self.file is None):
            self.ref = Ref(
                self.file,
                self.settings
            )

        self.__data = {}
    
    @property
    def is_complex(self):
        if self.ref is None:
            return False
        return self.ref.is_complex

    def __get_settings(self):
        return Settings(self.src)

    def __find__file(self) -> str:

        if exists(self.src) and not isdir(self.src):
            dna = basename(self.src)
            self.__is_env = (dna == '.env')
            return self.src

        posible = [
            ['.env'     , True],
            [".env.json", False],
            [".env.yaml", False],
            [".env.yml" , False],
        ]

        for f,is_env in posible:
            ff = join(self.src,f)
            if not exists(ff) or isdir(ff):
                continue
            self.__is_env = is_env
            return ff

        for f,is_env in posible:
            ff = join(self.settings.root,f)
            if not exists(ff) or isdir(ff):
                continue
            self.__is_env = is_env
            return ff

    def __load_env(self):
        e = DotEnv( None, stream = io.StringIO(self.ref.content) )
        return e.dict()

    def __parse(self):
        if self.ref is None:
            return {}

        cnt = self.ref.content
        if self.__is_env:
            return self.__load_env()
        elif self.ref.lang == 'json':
            return json.loads(cnt)
        elif self.ref.lang == 'yaml':
            return yaml.safe_load(cnt)
        elif self.ref.lang == 'yml':
            return yaml.safe_load(cnt)
        return {}

    def load(self):
        self.__data = self.__parse()
        if not isinstance(self.__data,dict):
            return {}
        for k, v in self.__data.items():
            if isinstance(v,(dict,list)):
                os.environ[k] = json.dumps(v)
            else:
                os.environ[k] = str(v)
        return self.__data

    def __get__(self,key):
        return os.environ.get(key)

    def get(self,key,default=None):
        return os.environ.get(key,default)

    def set(self,key:str,value:str):
        os.environ[key] = value
        self.__data[key] = value

    def save(self):
        if self.is_complex:
            raise YException('complex-secret', {
                'src' : self.src
            })

        lang = self.ref.lang
        if lang == 'json':
            open(self.file,'w').write(json.dumps(self.__data,indent=2))
        elif lang == 'yaml':
            open(self.file,'w').write(yaml.dump(self.__data))
