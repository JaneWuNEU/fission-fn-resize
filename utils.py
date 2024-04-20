import sys
import subprocess
def _exec_cmd(cmd, print_cmd=True):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    if print_cmd:
        print(cmd)
    try:
        result.check_returncode()
    except:
        # print('check env details errors' )
        return False, result.stderr
    return True, result.stdout


def resize_cpu_memory(cmd, cpu, memory):
    if cpu is not None:
        cmd.extend(['--maxcpu', str(cpu)])
    if memory is not None:
        cmd.extend(['--maxmemory', str(memory)])  # ,' --minmemory', str(memory)



    # if maxscale is not None:
    #     if 'env' in cmd:
    #         cmd.extend(['--poolsize', str(maxscale),"--version",'1'])
    #     else:
    #         cmd.extend(['--maxscale', str(maxscale)])
    # print(cmd)

def resource_exist(res_type,res_name,info):
    if ('not found' in info) and (res_type in info) and (res_name in info):
        return True
    else:
        return False

def delete_func(func_name):
    cmd = ['fission', 'fn', 'delete', '--name', func_name]
    tmp = _exec_cmd(cmd)
    if not tmp[0]:
        info = tmp[1]
        if info is None:
            pass
        else:
            print("!!!!!!error happens when checking function info", info)
            sys.exit(1)
def delete_env(env_name):
    # 1. check the env details
    env_exist = is_env_exist(env_name)

    ## 2. delete the function, fission env delete --name env_name
    if env_exist:
        cmd = ['fission', 'env', 'delete', '--name', env_name, '--force']
        tmp = _exec_cmd(cmd)
        if not tmp[0]:
            print("!!!!!!error happens when deleting env", env_name, tmp[1])
            sys.exit(1)
        print("delete env")
        # terminate invalid pods
        delete_all_terminate_env_pod()

def is_func_exist(func_name):
    cmd = ['fission', 'fn', 'get', '--name', func_name]
    tmp = _exec_cmd(cmd)
    info = tmp[1]
    env_exist = True
    if not tmp[0]:
        if info is None: #('not found' in info) and ('environment' in info) and (env_name in info):
            env_exist = False
        else:
            print("!!!!!!error happens when checking func info", info)
            sys.exit(1)
    return env_exist

def is_env_exist(env_name):
    cmd = ['fission', 'env', 'get', '--name', env_name]
    tmp = _exec_cmd(cmd)
    info = tmp[1]
    env_exist = True
    if not tmp[0]:
        if info is None: #('not found' in info) and ('environment' in info) and (env_name in info):
            env_exist = False
        else:
            print("!!!!!!error happens when checking env info", info)
            sys.exit(1)
    return env_exist

def create_func(func_name,env_name,env_image,env_builder,executor_type,code_path):
    if env_builder is not None:
        prefix_name = func_name+"-intensive"
        cmd = ['fission', 'fn', 'create', '--name', func_name, '--pkg', prefix_name+"-pkg", '--executortype', executor_type, '--env',
               env_name,'--entrypoint', prefix_name+".main"]
    else:
        cmd = ['fission', 'fn', 'create', '--name', func_name, '--code', code_path, '--executortype', executor_type, '--env',
               env_name]

    tmp = _exec_cmd(cmd)
    if not tmp[0]:
        print("error happens when create function", func_name, env_name, env_image, tmp[1])
        return False
    else:
        return True

def create_env(env_name,env_image,env_builder,cpu,memory,poolsize):
    cmd = ['fission', 'env', 'create', '--name', env_name, '--image', env_image, '--maxcpu', str(cpu), '--maxmemory',
           str(memory), '--poolsize',
           str(poolsize), '--version', '3']

    if env_builder is not None:
        cmd.extend(["--builder", env_builder])

    tmp = _exec_cmd(cmd)
    if not tmp[0]:
        print("error happens when create env", env_name, env_image, tmp[1])
        return False
    else:
        return True

def update_func(func_name,cpu,memory):
    cmd = ["fission", "fn", "update", "--name", func_name]
    resize_cpu_memory(cmd, cpu, memory)
    cmd.append('--force')
    tmp = _exec_cmd(cmd)
    if not tmp[0]:
        print("resize function/env fails", tmp[1])
        sys.exit(1)

def delete_all_terminate_env_pod():
    counts = 0
    for record in _get_env_pod_record_list():
        try:

            if ("Terminating"  in record) or ('Pending' in record):
                pod_name = record[:record.index('/') - 1].strip()
                cmd = ['kubectl', 'delete', 'pod', pod_name, "-n", "fission-function", "--force"]
                subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
                counts += 1
        except Exception as e:
            print(e)
    print("# of removed pkg is", counts)

def _get_env_pod_record_list():
    result = subprocess.run(['kubectl', 'get', 'pods', '-n', 'fission-function'], stdout=subprocess.PIPE,
                            universal_newlines=True)
    data = result.stdout
    # print(data)
    counts = 0
    if data.split("\n") == 1:
        print("no available pkg")
        return []
    else:
        return data.split("\n")[1:]