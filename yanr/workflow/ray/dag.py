import time

import ray


# from ray import workflow

# https://docs.ray.io/en/latest/ray-core/package-ref.html#ray.init
# r = ray.init(address="127.0.0.1:6379")
# r = ray.init(address="10.254.55.75:6379")
# r = ray.init(
#     num_cpus=2,
#     include_dashboard=True,
#     dashboard_host="10.254.55.75",
#     dashboard_port=8625,
# runtime_env={"container": {"image": "yanr",
#                           "worker_path": "/opt/yanr/workglow/ray/dag.py",
#                         "run_options": ["--privileged", "--cap-drop SYS_ADMIN",
#                         "--log-level=debug", "--entrypoint /bin/bash"]}}
# #   runtime_env={"working_dir": ".",
# "py_modules": ["yanr"], "pip": "./requirements/common.txt"}
# )

# r = ray.init(
#    # address="127.0.0.1:6379",
#    _temp_dir='./tmp/ray',
#    num_cpus=2,
#    _plasma_directory='./tmp',
#    # ignore_reinit_error=False,
#    # _enable_object_reconstruction=False,
#    object_store_memory=100e6,
#    _memory=None,
#    _redis_max_memory=100e6,
#    include_dashboard=False,
#    # log_to_driver=False,
#    # local_mode=True,
#    # logging_level='debug'
# )
# print(r)
# print(ray.is_initialized())
# print(ray.nodes())
# print(r.address_info['address'])


@ray.remote
def cwd():
    from yanr.getter import Url

    Url(source='https://www.example.com', destination='example.html')()
    with open('example.html') as f:
        data = f.read()
    return data


@ray.remote
def slow_function():
    #    time.sleep(20)
    time.sleep(30)
    return 1


refs = [cwd.remote() for _ in range(2)]
print(refs)
print(ray.get(refs))

# @ray.remote
# class Counter:
#     def __init__(self):
#         self.value = 0
#
#     def increment(self):
#         self.value += 1
#         return self.value
#
#
# c = Counter.remote()
# ref = c.increment.remote()
# print(ref)
# print(ray.get(ref))
#
# ray.shutdown()

# print(ray.get_runtime_context())
#
# @ray.remote
# def slow_function():
#     time.sleep(60)
#     return 1
#
#
# @ray.remote
# class Counter(object):
#     def __init__(self):
#         self.value = 0
#
#     def increment(self):
#         self.value += 1
#         return self.value
#
#
# # Create an actor from this class.
# counter = Counter.remote()
# obj_ref = counter.increment.remote()
# assert ray.get(obj_ref) == 1
# assert ray.get(slow_function.remote()) == 1


# # https://docs.ray.io/en/latest/workflows/package-ref.html
# @workflow.step
# def one() -> int:
#    return 1


# @workflow.step
# def add(a: int, b: int) -> int:
#   return a + b

# dag = add.step(100, one.step())
# print(dag)

# dag = one.step()
# workflow.init(storage="./tmp/data")
# print([workflow.delete(workflow_id=x[0]) for x in workflow.list_all()])
# print(dag.run(workflow_id="run_1"))
# print(workflow.get_status("run_1"))
# print(workflow.get_output("run_1"))

# # assert workflow.get_status("run_1") == workflow.WorkflowStatus.SUCCESSFUL
# # assert workflow.get_output("run_1") == 101
