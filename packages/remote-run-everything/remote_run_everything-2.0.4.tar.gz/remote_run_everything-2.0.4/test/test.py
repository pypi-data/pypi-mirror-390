import time

from remote_run_everything import ByHttp
from remote_run_everything.tools.decorators import *
import requests
from multiprocessing import Process
from remote_run_everything.tools.common import Common
from remote_run_everything.db.crude_duck import CrudeDuck
from remote_run_everything import VsConf
host = "http://39.96.40.177:8888/deploy"
remote = "/data/temp"
local = "D://wq/temp"


def push_example():
    bh = ByHttp(host, local, remote, "D://wq/temp/remote_run")
    bh.up()


def test():
    wdir="D://mygit/remote_run_everything"
    vs=VsConf()
    vs.vs_rust()


def pull_local():
    host = "http://127.0.0.1:9900/deploy"
    local = "D://mypy/econ/templates"
    remote = "D://wq/temp/econ/templates"
    bh = ByHttp(host, local, remote, "D://wq/temp/testlocal.db")
    bh.up()


@cache_by_name("asdf", 1)
def test_dec():
    print("运行了函数!!!!!!!!!!!!!!!!")
    return {"a": "adaf"}


def testscheme():
    dic=Common().read_conf()['pg']
    con=CrudeDuck().install_pg_ext(**{**dic,"dbname":"projects"})
    dic = Common().read_conf()['mysql']['test']
    dic['dbname'] = Common().read_conf()['mysql']['md']['test']
    print( CrudeDuck().scheme(con, "projects", 'kv',"pg"))
    con = CrudeDuck().install_mysql_ext(**dic)
    print( CrudeDuck().scheme(con, "md-test", 'c_dictionary',"mysql"))
    con=CrudeDuck().install_sql_ext("D://wq/temp/conf.db")
    sch = CrudeDuck().scheme(con, "conf", 'down',"sqlite3")
    print(sch,len(sch))
    CrudeDuck().delete_by_id(con,"up",0)


if __name__ == '__main__':
    push_example()
