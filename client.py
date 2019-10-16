import etcd
import time
import util_log
import util_python
import yaml

logger = util_log.creater_logger(name=__name__, logfile='log.txt')


class etcdClient(object):
    def __init__(self, host, master_key, current_value, ttl):
        self.host = host
        self.port = 2379
        # 获取master_key的标志
        self.current_flag = True
        self.master_key = master_key
        self.current_value = current_value
        self.ttl = ttl

    def connect(self):
        try:
            client = etcd.Client(host=self.host,
                                 port=self.port,
                                 allow_reconnect=True,
                                 protocol='http')
        except Exception as e:
            logger.error(str(e))
            return None
        return client


def get_yaml_data():
    yaml_file = 'etcd.yaml'
    try:
        yaml_data = yaml.load(open(yaml_file), Loader=yaml.FullLoader)
        host = yaml_data['etcd']['host']
        master_key = yaml_data['etcd']['master_key']
        current_value = yaml_data['etcd']['current_value']
        ttl = yaml_data['etcd']['ttl']
        result = {'host': host, 'master_key': master_key, 'current_value': current_value, 'ttl': ttl}
    except Exception as e:
        logger.error(str(e))
        return None
    return result


if __name__ == '__main__':
    initconfig = get_yaml_data()
    if not initconfig:
        raise Exception("error in getting init config")
    etcd_client_instance = etcdClient(host=initconfig['host'], master_key=initconfig['master_key'],
                                      current_value=initconfig['current_value'], ttl=initconfig['ttl'])
    etcd_client = etcd_client_instance.connect()
    if not etcd_client:
        raise Exception("error in getting etcd client")
    while True:
        # Judge if exist master_key in etcd
        try:
            result = etcd_client.read(key=etcd_client_instance.master_key).__dict__
            ttl = result['ttl']
            master_value = result['value']
        except Exception as e:
            etcd_client_instance.current_flag = False
            master_value = None
            logger.error(str(e))
            logger.error(f'error in getting key which was {etcd_client_instance.master_key} from etcd!')

        # if exist master_key in etcd and previous role is master
        if etcd_client_instance.current_flag and master_value == etcd_client_instance.current_value:
            # ttl was more then half
            if ttl > etcd_client_instance.ttl / 2:
                pass
            # ttl was less then half  and the master role need to refresh ttl
            else:
                etcd_client.write(key=etcd_client_instance.master_key, value=etcd_client_instance.current_value,
                                  ttl=etcd_client_instance.ttl)
                logger.info(f"节点开始工作,还是原来的节点{etcd_client_instance.current_value}")
        # if not exist master_key in etcd and begin to seize master role
        elif not etcd_client_instance.current_flag:
            etcd_client.write(key=etcd_client_instance.master_key, value=etcd_client_instance.current_value,
                              ttl=etcd_client_instance.ttl)
            logger.info(f"节点开始工作,我是新的节点{etcd_client_instance.current_value}")
            util_python.do_shell('sh client.sh')
        # if exist master_key and previous role is slave , then waitting for ttl was expired
        else:
            pass
        time.sleep(etcd_client_instance.ttl / 2)
        # refresh the flag
        etcd_client_instance.current_flag = True
