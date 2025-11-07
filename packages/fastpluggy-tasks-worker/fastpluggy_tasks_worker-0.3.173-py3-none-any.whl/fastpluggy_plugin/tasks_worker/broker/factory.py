# broker/factory.py


def get_broker():
    from ..config import TasksRunnerSettings
    setting = TasksRunnerSettings()

    if setting.BROKER_TYPE == "none":
        return None
    elif setting.BROKER_TYPE == "local":
        from .local import LocalBroker
        return LocalBroker()
    elif setting.BROKER_TYPE == "inproc":
        from .inproc import InprocBroker
        return InprocBroker()
    elif setting.BROKER_TYPE == "memory":
        from .memory import InMemoryBroker
        return InMemoryBroker()
    elif setting.BROKER_TYPE == "rabbitmq":
        from .rabbitmq import RabbitMQBroker
        rabbitmq_url = getattr(setting, "RABBITMQ_URL", None)
        return RabbitMQBroker(rabbitmq_url=rabbitmq_url)
    else:
        raise ValueError(f"Unsupported broker scheme: {setting.BROKER_TYPE}")
