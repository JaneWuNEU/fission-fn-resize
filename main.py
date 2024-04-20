import sys
from utils import is_env_exist,is_func_exist,create_env,create_func,update_func,delete_env,delete_func
sys.path.append(".")


def update_size_for_newdeploy(executor_type, env_name, func_name, code_path, env_image, env_builder, cpu, memory=0, poolsize=1):
    """
    The unit for CPU and memory are millicore and MB respectively.
    """
    if executor_type not in ['newdeploy', 'poolmgr']:
        print("invalid executor type")
        sys.exit(1)
    # 1. check whether the required env is ready; otherwise, create it
    if not is_env_exist(env_name):
        status = create_env(env_name,env_image,env_builder,cpu,memory,poolsize)
        if not status:
            sys.exit(1)
    if not is_func_exist(func_name):
        status = create_func(func_name,env_name,env_image,env_builder,executor_type,code_path)
        if not status:
            sys.exit(1)
    else:
        update_func(func_name,cpu,memory)

def update_size_for_poolmgr(executor_type, env_name, func_name, code_path, env_image, env_builder, cpu, memory=0, poolsize=1):
    """
    Unlike newdeploy, poolmgr does not support updating.
    As long as we update any fields, it will terminate the outdated ones while creating new pods with specified sizes as well as the function
    :return:
    """
    if executor_type not in ['poolmgr','newdeploy']:
        print("invalid executor type", executor_type)
        return None

    # 1. delete func
    delete_func(func_name)
    # 2. delete env
    delete_env(env_name)
    # 3. create the env with the specified name and image, fission env create --name env_name --image
    status = create_env(env_name, env_image, env_builder, cpu, memory, poolsize)
    if not status:
        sys.exit(1)
    status = create_func(func_name,env_name,env_image,env_builder,executor_type,code_path)
    if not status:
        sys.exit(1)

def adjust_func_size(executor_type, env_name,func_name,cpu, memory,code_path=None,env_image=None,builder_image=None):
    """

    :param executor_type: ['newdeploy, poolmgr']
    :param env_name:
    :param func_name:
    :param cpu: integer, the basic unit is million core
    :param memory: integer, the basic unit is MB
    :param code_path:
    :param env_image:
    :param builder_image: optional. It is only required by newdeploy-based functions.
    :return:
    """
    if executor_type == 'newdeploy':
        # this requires to build the env first
        update_size_for_newdeploy(executor_type, env_name, func_name,code_path,env_image,builder_image,cpu, memory)
    elif executor_type == 'poolmgr':
        if code_path is None:
            print('please provide code path when resizing poolmgr-based functions',env_name,func_name)
            sys.exit(1)
        update_size_for_poolmgr(executor_type, env_name, func_name,code_path,env_image,builder_image,cpu, memory)

if __name__ == '__main__':
    adjust_func_size()








