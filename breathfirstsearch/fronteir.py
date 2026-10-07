class QeueFronteir():
    def __init__(self):
        self.storage=[]
        self.exploredset=[]
    def removenode(self):
        node_to_consider=self.storage[0]
        self.exploredset.append(node_to_consider)
        del self.storage[0]
        return node_to_consider
    def addnode(self,nodes):
        for node in nodes:
            self.storage.append(node)
        