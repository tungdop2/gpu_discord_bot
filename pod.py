import uuid
from datetime import datetime, timedelta

class Pod:
    def __init__(self, owner_id: int, name: str, number_of_gpu: int, cloud: str, gpu: str, time_hours: float):
        self.id = uuid.uuid4()
        self.owner_id = owner_id
        self.name = name
        self.number_of_gpu = number_of_gpu
        self.cloud = cloud
        self.gpu = gpu
        self.time_hours = time_hours

        # init creat time and stop time = creat time + time_hours
        self.created_at = datetime.now()
        self.should_stopped_at = self.created_at + timedelta(hours=self.time_hours)

    def get_detail_info(self):
        info = f"Pod ID: `{self.id}`\n"
        info += f"Name: `{self.name}`\n"
        info += f"Cloud: `{self.cloud}`\n"
        info += f"GPU: `{self.gpu}`\n"
        info += f"Number of GPU: `{self.number_of_gpu}`\n"
        info += f"Time: `{self.time_hours} hours`\n"
        info += f"Created at: `{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}`\n"
        info += f"Should be stopped at: `{self.should_stopped_at.strftime('%Y-%m-%d %H:%M:%S')}`\n"
        return info

    def get_short_info(self):
        info = f"Pod ID: `{self.id}`. Name: `{self.name}`. Status: `{self.get_status()}`"
        return info
    
    def get_status(self):
        if self.is_over_stop_time():
            return "Need to stop"
        else:
            return "Running"
        
    def is_over_stop_time(self):
        return datetime.now() > self.should_stopped_at
    
    def extend_time(self, time_hours: float):
        self.should_stopped_at = self.should_stopped_at + timedelta(hours=time_hours)
        
    def get_id(self):
        return self.id
    
    def get_should_stopped_at(self):
        return self.should_stopped_at
