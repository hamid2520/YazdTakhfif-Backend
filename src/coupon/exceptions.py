class MaximumNumberOfDeletableObjectsError(Exception):
    def __init__(self):
        self.message = "The number of deleted objects is lower than available objects!"
        super().__init__(self.message)
