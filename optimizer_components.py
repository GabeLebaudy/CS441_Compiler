class SSAVariable:
    def __init__(self, base_name: str):
        self._base_name = base_name
        self._version = 0
    
    def name(self) -> str:
        return self._base_name
    
    def getVersion(self) -> int:
        return self._version
    
    def nextName(self):
        return f"{self._base_name}{self._version}"
    
    def incVersion(self) -> int:
        self._version += 1