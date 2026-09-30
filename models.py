"""models.py — one class for the storefront product model."""


class Product:
    def __init__(self, name, price, tag="SAINT SINNER", image=""):
        self.name = name
        self.price = price
        self.tag = tag
        self.image = image

    def describe(self):
        return f"{self.name} is a {self.tag.lower()} statement piece priced at ฿{self.price}."
