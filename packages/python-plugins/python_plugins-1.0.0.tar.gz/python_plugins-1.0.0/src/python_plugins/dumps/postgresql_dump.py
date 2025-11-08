import subprocess
import sys


def pg_dump(dump_dir, username, dbname, tbname):
    """pg_dump

    :param dir: dump dir
    :param username: db user
    :param dbname: db name
    :param tbname: table name
    """
    pgdump_cmd = (
        f"dump_user={username};dump_db={dbname};dump_tb={tbname};dump_dir={dump_dir};"
        "pg_dump -U ${dump_user} --no-password -d ${dump_db} -t ${dump_tb} | gzip > ${dump_dir}/${dump_db}.${dump_tb}-`date +'%Y%m%d'`.gz;"
        "cp ${dump_dir}/${dump_db}.${dump_tb}-`date +'%Y%m%d'`.gz  ${dump_dir}/${dump_db}.${dump_tb}.gz;"
    )
    if sys.platform == "linux":
        r = subprocess.run(pgdump_cmd, shell=True)
    else:
        r = f"not pg_dump because sys.platform is {sys.platform}"
    return r


def remove_ndays_ago(dir, days=30):
    remove_cmd = f"rm -f {dir}/*`date +'%Y%m%d' -d'-{days} days'`.gz"
    if sys.platform == "linux":
        r = subprocess.run(remove_cmd, shell=True)
    else:
        r = f"not remove files because sys.platform is {sys.platform}"
    return r
