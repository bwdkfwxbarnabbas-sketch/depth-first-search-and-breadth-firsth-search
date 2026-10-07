class StackFronteir():
    def __init__(self):
        self.storage=[]
        self.exploredset=[]
    def removenode(self):
        node_to_consider=self.storage[-1]
        self.exploredset.append(node_to_consider)
        self.storage.pop()
        return node_to_consider
    def addnode(self,nodes):
        for node in nodes:
            self.storage.append(node)
        