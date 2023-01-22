from datetime import date
from sqlalchemy.orm import validates
from .base import db
import re

# Let's only start with german IBANS
IBAN_RE = re.compile("^DE\d{20}$")


class SepaMandate(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    person_id = db.Column(db.Integer, db.ForeignKey("person.id"))
    person = db.relationship("Person", backref="sepamandates", lazy="subquery")

    adress = db.Column(db.UnicodeText(), nullable=False)
    iban = db.Column(db.String, nullable=False)
    bank = db.Column(db.String, nullable=False)
    # can also be un-given
    given = db.Column(db.Boolean, nullable=False)

    # wether to use standard value
    default = db.Column(db.Boolean, nullable=False)
    # value = null means use right membership fee
    value = db.Column(db.Integer, nullable=True)

    creation_date = db.Column(db.DateTime(timezone=True), nullable=False)

    @validates("iban")
    def validate_iban(self, key, iban):
        if IBAN_RE.match(iban) is None:
            raise ValueError("Incorrect IBAN")

        iban_rearranged = iban[4:] + iban[0:4]
        # replace letters
        iban_replaced = ""
        for c in iban_rearranged:
            if c.isdigit():
                iban_replaced += c
            else:
                iban_replaced += str(10 + ord(c) - ord("A"))
        if int(iban_replaced) % 97 != 1:
            raise ValueError("Not a valid IBAN.")
        return iban

    def __repr__(self):
        return f"Sepa mandat for {'NULL' if self.person is None else self.person.name}"
