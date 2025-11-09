
from totoapicontroller import TotoLogger
from totoapicontroller.model.TotoConfig import TotoConfig


class ExecutionContext: 
    
    logger: TotoLogger
    cid: str 
    config: TotoConfig
    
    def __init__(self, config: TotoConfig, logger: TotoLogger, cid: str) -> None:
        self.config = config
        self.logger = logger
        self.cid = cid