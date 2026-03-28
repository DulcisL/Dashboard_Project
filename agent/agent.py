import os
import psutil
import json
from pynvml import *

"""Health_Status
desc: Gets health status information and returns it in a json string
params: None
return: status (json) - a json string of the health status
"""


class Health_Status:
    _cpu_temp = float
    _cpu_usage = float
    _graphics_temp = float
    _graphics_usage = float
    _memory_usage = float
    _sensor_temps = dict

    def __init__(self):
        self._sensor_temps = {}
        self._cpu_temp = ""
        self._cpu_usage = ""
        self._graphics_temp = ""
        self._graphics_usage = ""
        self._memory_usage = ""

        self.set_sensor_temps()
        self.set_cpu_temp()
        self.set_cpu_usage()
        self.set_gpu_temp()
        self.set_gpu_usage()
        self.set_mem_usage()

    def get_sensor_temps(self):
        return self._sensor_temps

    def get_cpu_temp(self):
        return self._cpu_temp

    def get_cpu_usage(self):
        return self._cpu_usage

    def get_gpu_temp(self):
        return self._graphics_temp

    def get_gpu_usage(self):
        return self._graphics_usage

    def get_mem_usage(self):
        return self._memory_usage

    def set_sensor_temps(self):
        # Gets all temp sensor information in a dict : list format
        self._sensor_temps = psutil.sensors_temperatures()
        return self._sensor_temps

    def set_cpu_temp(self):
        temps_string = "\n"
        self.set_sensor_temps()
        # Get only the core temperatures from psutil's "coretemp" sensor group.
        cores = self._sensor_temps.get("coretemp", [])
        if not cores:
            self._cpu_temp = temps_string + "No core temperature sensors found.\n"
            return self._cpu_temp

        for i, core in enumerate(cores):
            label = f"Core {i}"
            temp = core.current
            critical = core.critical
            if temp is None:
                temps_string += f"{label}: unavailable\n"
            else:
                temps_string += f"{label}: {temp}, {critical}\n"
        self._cpu_temp = temps_string
        return self._cpu_temp

    def set_cpu_usage(self):
        usage_string = " \n"
        usage = psutil.cpu_percent(0.1, percpu=True)
        average = 0
        end_count = 0
        for i in range(len(usage)):
            usage_string += f"CPU {i + 1}: {usage[i]}% \n"
            average += usage[i]
            end_count = i + 1
        usage_string += f"CPU Average: {average / end_count}% \n"
        self._cpu_usage = usage_string
        return self._cpu_usage

    def set_gpu_temp(self):
        temp_string = ""
        try:
            # Nvidia gpu
            nvmlInit()
            handle = nvmlDeviceGetHandleByIndex(0)
            temp_string = (
                f"{nvmlDeviceGetTemperatureV(handle, NVML_TEMPERATURE_GPU)} C\n"
            )
        except Exception as e:
            temp_string = f"An Error occurred getting NVIDIA GPU info: {e}"
        self._graphics_temp = temp_string
        return self._graphics_temp

    def set_gpu_usage(self):
        usage_string = ""
        try:
            nvmlInit()
            handle = nvmlDeviceGetHandleByIndex(0)
            usage_string = f"{nvmlDeviceGetUtilizationRates(handle).gpu}"
        except Exception as e:
            usage_string = f"An error occurred getting NVIDIA GPU info: {e}"

        self._graphics_usage = usage_string
        return self._graphics_usage

    def set_mem_usage(self):
        usage_string = ""
        try:
            usage_string = f" {psutil.virtual_memory()[2]}"
        except Exception as e:
            usage_string = f"An error occurred getting system memory info: {e}"
        self._memory_usage = usage_string
        return self._memory_usage

    def __str__(self):
        return f"""
CPU Temp: {self._cpu_temp}
CPU Usage: {self._cpu_usage}
Graphics Temp: {self._graphics_temp}
Graphics Usage: {self._graphics_usage}
Memory Usage: {self._memory_usage}
        """


def convert_to_dict(status):
    return {
        "CPU Usage": status.get_cpu_usage(),
        "CPU Temp": status.get_cpu_temp(),
        "GPU Usage": status.get_gpu_usage(),
        "Graphics Temp": status.get_gpu_temp(),
        "Memory Usage": status.get_mem_usage(),
    }


# Get health check information
my_status = Health_Status()

# Convert status to a json string
json_formatted = json.dumps(convert_to_dict(my_status))


print(json_formatted)

# send system information
