class CTVersion:
    """
    A class for storing and managing versions for different named entities.
    """

    def __init__(self):
        """
        Initialize an empty dictionary to store versions.
        """
        self.versions = {}

    def add(self, name, version):
        """
        Add a version for a named entity.

        Args:
            name (str): The name of the entity
            version (str): The version to store for the entity
        """
        self.versions[name] = version
