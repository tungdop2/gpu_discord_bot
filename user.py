from pod import Pod

class User:
    def __init__(self, id: int):
        self.id = id
        self.pods = []

    def add_pod(self, pod: Pod):
        self.pods.append(pod)

    def remove_pod(self, pod: Pod):
        self.pods.remove(pod)
    
    def get_pod(self, pod_id: str):
        for pod in self.pods:
            if pod.id == pod_id:
                return pod
        return None
    
    def get_pods(self):
        return self.pods
