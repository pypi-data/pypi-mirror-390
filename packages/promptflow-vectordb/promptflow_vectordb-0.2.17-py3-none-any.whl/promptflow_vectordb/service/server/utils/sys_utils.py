import psutil

CGROUP_MEMORY_LIMIT_FILE = '/sys/fs/cgroup/memory/memory.limit_in_bytes'
CGROUP_MEMORY_USAGE_FILE = '/sys/fs/cgroup/memory/memory.usage_in_bytes'


class SysUtils:

    def get_available_memory_in_bytes():
        try:
            memory_info_of_host = psutil.virtual_memory()
            if not psutil.LINUX:
                return memory_info_of_host.available

            # linux only
            with open(CGROUP_MEMORY_LIMIT_FILE, 'r') as file:
                limit_for_cgroup_in_bytes = int(file.readline().strip())

                # if limit is not set for cgroup
                if limit_for_cgroup_in_bytes > memory_info_of_host.total:
                    return memory_info_of_host.available

                # if a limit is set for cgroup
                with open(CGROUP_MEMORY_USAGE_FILE, 'r') as file:
                    usage_for_cgroup_in_bytes = int(file.readline().strip())
                    available_memory = limit_for_cgroup_in_bytes - usage_for_cgroup_in_bytes
                    return available_memory
        except Exception:
            return memory_info_of_host.available
