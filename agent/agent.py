import os
import psutil
import json
from pynvml import *
import requests
from datetime import datetime
import time


# GLOBALS
HIGH_USAGE = 75  # Percent
HIGH_TEMP = 95  # Celcius


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
        self._cpu_temp = {}
        self._cpu_usage = {}
        self._graphics_temp = {}
        self._graphics_usage = {}
        self._memory_usage = {}
        self.issue = []

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
        raw_sensor_temps = psutil.sensors_temperatures()
        serialized_temps = {}

        for sensor_name, sensor_entries in raw_sensor_temps.items():
            serialized_temps[sensor_name] = []
            for sensor_entry in sensor_entries:
                serialized_temps[sensor_name].append(
                    {
                        "label": sensor_entry.label,
                        "current": sensor_entry.current,
                        "high": sensor_entry.high,
                        "critical": sensor_entry.critical,
                    }
                )

        self._sensor_temps = serialized_temps
        return self._sensor_temps

    def set_cpu_temp(self):
        self.set_sensor_temps()
        # Get only the core temperatures from psutil's "coretemp" sensor group.
        cores = self._sensor_temps.get("coretemp", [])
        if not cores:
            self._cpu_temp = {
                "cores": [],
                "message": "No core temperature sensors found.",
            }
            return self._cpu_temp

        core_temperatures = []
        for i, core in enumerate(cores):
            core_temperatures.append(
                {
                    "label": core.get("label") or f"Core {i}",
                    "temperature_c": core.get("current"),
                    "critical_c": core.get("critical"),
                }
            )

        self._cpu_temp = {"cores": core_temperatures}
        return self._cpu_temp

    def set_cpu_usage(self):
        usage = psutil.cpu_percent(0.1, percpu=True)
        per_cpu_usage = []

        for i, cpu_usage in enumerate(usage):
            per_cpu_usage.append({"label": f"CPU {i + 1}", "usage_percent": cpu_usage})

        average_usage = sum(usage) / len(usage) if usage else 0
        self._cpu_usage = {
            "per_cpu": per_cpu_usage,
            "average_percent": average_usage,
        }
        if average_usage > HIGH_USAGE:
            self.issue.append("High_CPU_Usage")

        return self._cpu_usage

    def set_gpu_temp(self):
        try:
            # Nvidia gpu
            nvmlInit()
            handle = nvmlDeviceGetHandleByIndex(0)
            temperature = nvmlDeviceGetTemperatureV(handle, NVML_TEMPERATURE_GPU)
            self._graphics_temp = {"temperature_c": temperature}
            if temperature > HIGH_TEMP:
                self.issue.append("High_Temps")

        except Exception as e:
            self._graphics_temp = {
                "error": f"An Error occurred getting NVIDIA GPU info: {e}"
            }
        return self._graphics_temp

    def set_gpu_usage(self):
        try:
            nvmlInit()
            handle = nvmlDeviceGetHandleByIndex(0)
            usage = nvmlDeviceGetUtilizationRates(handle).gpu
            self._graphics_usage = {"usage_percent": usage}
            if usage > HIGH_USAGE:
                self.issue.append("High_GPU_Usage")

        except Exception as e:
            self._graphics_usage = {
                "error": f"An error occurred getting NVIDIA GPU info: {e}"
            }

        return self._graphics_usage

    def set_mem_usage(self):
        try:
            usage = psutil.virtual_memory()[2]
            self._memory_usage = {"usage_percent": usage}
            if usage > HIGH_USAGE:
                self.issue.append("High_Memory_Usage")

        except Exception as e:
            self._memory_usage = {
                "error": f"An error occurred getting system memory info: {e}"
            }
        return self._memory_usage

    def _format_cpu_temp(self):
        if self._cpu_temp.get("message"):
            return self._cpu_temp["message"]

        lines = []
        for core in self._cpu_temp.get("cores", []):
            label = core.get("label", "Unknown")
            temperature = core.get("temperature_c")
            critical = core.get("critical_c")
            line = f"{label}: {temperature} C"
            if critical is not None:
                line += f" (critical: {critical} C)"
            lines.append(line)

        return "\n".join(lines) if lines else "Unavailable"

    def _format_cpu_usage(self):
        lines = []
        for cpu in self._cpu_usage.get("per_cpu", []):
            lines.append(f"{cpu.get('label', 'CPU')}: {cpu.get('usage_percent')}%")

        if "average_percent" in self._cpu_usage:
            lines.append(f"Average: {self._cpu_usage['average_percent']:.2f}%")

        return "\n".join(lines) if lines else "Unavailable"

    def _format_gpu_temp(self):
        if self._graphics_temp.get("error"):
            return self._graphics_temp["error"]

        if "temperature_c" in self._graphics_temp:
            return f"{self._graphics_temp['temperature_c']} C"

        return "Unavailable"

    def _format_gpu_usage(self):
        if self._graphics_usage.get("error"):
            return self._graphics_usage["error"]

        if "usage_percent" in self._graphics_usage:
            return f"{self._graphics_usage['usage_percent']}%"

        return "Unavailable"

    def _format_mem_usage(self):
        if self._memory_usage.get("error"):
            return self._memory_usage["error"]

        if "usage_percent" in self._memory_usage:
            return f"{self._memory_usage['usage_percent']}%"

        return "Unavailable"

    def __str__(self):
        return (
            "CPU Temp:\n"
            f"{self._format_cpu_temp()}\n"
            "CPU Usage:\n"
            f"{self._format_cpu_usage()}\n"
            "Graphics Temp:\n"
            f"{self._format_gpu_temp()}\n"
            "Graphics Usage:\n"
            f"{self._format_gpu_usage()}\n"
            "Memory Usage:\n"
            f"{self._format_mem_usage()}"
        )


def convert_to_dict(status):
    return {
        "CPU Usage": status.get_cpu_usage(),
        "CPU Temp": status.get_cpu_temp(),
        "GPU Usage": status.get_gpu_usage(),
        "Graphics Temp": status.get_gpu_temp(),
        "Memory Usage": status.get_mem_usage(),
    }


# Send metrics only if major change or critical issue arrises
# Otherwise let connection api make requests for data
previous_time = datetime.now()
while True:
    # Get health check information
    my_status = Health_Status()

    # Create payload
    json_formatted = json.dumps(
        {
            "Timestamp": datetime.now().isoformat(),
            "System Data": convert_to_dict(my_status),
        }
    )
    # save to log?
    # if issue send payload
    issues = ["High_Temps", "High_CPU_Usage", "High_GPU_Usage", "High_Memory_Usage"]
    if my_status.issue in issues:
        # Send the payload
        pass
