import os

__version__: str = ""

def get_version():
    global __version__

    __version__ = os.environ.get("APP_VERSION")

    if __version__ is None:
        with open(".env", "r") as env_file:
            env_variables: str = ""

            for line in env_file:
                env_variables += line

        each_env_variable: list[str] = env_variables.split("\n")

        for env in each_env_variable:

            if "APP_VERSION" in env:
                __version__ = env.split("=")[1]        
                break

get_version()

