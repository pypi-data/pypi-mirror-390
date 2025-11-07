from pararun.service.singleton import Singleton


class DeferAdapterSelector(metaclass=Singleton):

    def get(self, adapter_name, queue_tenant: str):
        pass
