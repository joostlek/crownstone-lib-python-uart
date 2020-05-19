from typing import List


class MeshResult:

    def __init__(self, crownstone_uid_array : List[int]):
        self.success = False
        self.acks = {}
        for uid in crownstone_uid_array:
            self.acks[uid] = False

    def merge(self, result: 'MeshResult'):
        for uid, success in result.acks.items():
            self.acks[uid] = result.acks[uid]

    def getSuccessfulIds(self) -> List[int]:
        successList = []
        for uid, success in self.acks.items():
            if self.acks[uid]:
                successList.append(uid)
        return successList