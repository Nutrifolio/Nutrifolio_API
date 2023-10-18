class ProductNotFound(Exception):
    pass


class DuplicateProductNameForTheSameStore(Exception):
    pass


class ProductBelongsToAnotherStore(Exception):
    pass
