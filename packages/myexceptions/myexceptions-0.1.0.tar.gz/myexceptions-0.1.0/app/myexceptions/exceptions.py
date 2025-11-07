class MyRuntimeError(RuntimeError):
    def __init__(self, env_var: str) -> None:
        super().__init__(f"The environment variable '{env_var}' is not set.")
