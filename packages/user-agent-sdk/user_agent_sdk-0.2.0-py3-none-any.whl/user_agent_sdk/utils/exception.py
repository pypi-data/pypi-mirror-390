class NonRetryableException(Exception):
    """
    Exception indicating that the operation should not be retried.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
