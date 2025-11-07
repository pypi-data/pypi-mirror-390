import os
import re
from functools import lru_cache


def normalize_environment_parameter(environment: str) -> str:
    environment_lower = environment.lower()

    if environment_lower == 'qa':
        return 'QA'

    if environment_lower == 'production':
        return 'Production'

    if environment_lower == 'sharedservices':
        return 'SharedServices'

    return 'Development'


@lru_cache(maxsize=1)
def get_version() -> str:
    # reading pymlconf version (same way sqlalchemy does)
    with open(
        os.path.join(os.path.dirname(__file__), '__init__.py')
    ) as v_file:
        package_version = (
            re.compile(r".*__version__ = '(.*?)'", re.S)
            .match(v_file.read())
            .group(1)
        )
        return package_version
