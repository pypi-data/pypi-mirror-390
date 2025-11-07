import enum

from pydantic import BaseModel, field_validator


class FargateTypes(enum.Enum):
    CPU_025 = 256
    CPU_050 = 512
    CPU_1 = 1024
    CPU_2 = 2048
    CPU_4 = 4096
    CPU_8 = 8192
    CPU_16 = 16384
    MEM_050 = 512
    MEM_1 = 1024
    MEM_2 = 2048
    MEM_4 = 4096
    MEM_8 = 8192
    MEM_16 = 16384
    MEM_30 = 30720
    MEM_32 = 32768
    MEM_60 = 61440
    MEM_120 = 122880

    valid_values = [
        {'cpu': CPU_025, 'mem': [MEM_050, MEM_1, MEM_2]},
        {
            'cpu': CPU_050,
            'mem': {'mem_min': MEM_1, 'mem_max': MEM_4, 'mem_step': MEM_1},
        },
        {
            'cpu': CPU_1,
            'mem': {'mem_min': MEM_2, 'mem_max': MEM_8, 'mem_step': MEM_1},
        },
        {
            'cpu': CPU_2,
            'mem': {'mem_min': MEM_4, 'mem_max': MEM_16, 'mem_step': MEM_1},
        },
        {
            'cpu': CPU_4,
            'mem': {'mem_min': MEM_8, 'mem_max': MEM_30, 'mem_step': MEM_1},
        },
        {
            'cpu': CPU_8,
            'mem': {'mem_min': MEM_16, 'mem_max': MEM_60, 'mem_step': MEM_4},
        },
        {
            'cpu': CPU_16,
            'mem': {'mem_min': MEM_32, 'mem_max': MEM_120, 'mem_step': MEM_8},
        },
    ]


class FargateValidator(BaseModel):
    """

    Class to validate Fargate task cpu and memory settings.

    Fargate requires specific combinations of cpu and memory settings.
    This class validates the combination of cpu and memory settings leveraging pydantic validators.

    If the combination is not valid, a ValueError exception is raised, you should handle it in your code.
    """

    cpu: int
    mem: int

    @field_validator('cpu')
    def cpu_must_be_valid(cls, v, values, **kwargs):
        allowed_cpus = [x.get('cpu') for x in FargateTypes.valid_values.value]
        if v not in allowed_cpus:
            raise ValueError(f'Fargate task cpu must be one of {allowed_cpus}')
        return v

    @field_validator('mem')
    def memory_must_be_valid_for_cpu_setting(cls, v, values, **kwargs):
        allowed_mems = next(
            x.get('mem')
            for x in FargateTypes.valid_values.value
            if x.get('cpu') == values.data.get('cpu')
        )

        if type(allowed_mems) is dict:
            allowed_mems = list(
                range(
                    allowed_mems.get('mem_min'),
                    allowed_mems.get('mem_max') + allowed_mems.get('mem_step'),
                    allowed_mems.get('mem_step'),
                )
            )

        if v not in allowed_mems:
            raise ValueError(
                f"Fargate task memory must be one of {allowed_mems} when cpu is {values.data.get('cpu')}"
            )
        return v
