#importi...


class Uporabnik:
    """
    Razred za Uporabnik
    """
    def __init__(self, ime, priimek, email, telefon, uporabnik_id = None):
        self.uporabnik_id = uporabnik_id
        self.ime = ime
        self.priimek = priimek
        self.email = email
        self.telefon = telefon

    def __string(self):
        return f"{self.ime} {self.priimek}"

class Trener:
    """
    """
    def __init__(self, ime, priimek, speciallizacija, *, trener_id = None): #kaj naredijo te *
        self.trener_id = None
        self.ime = ime
        self.priimek = priimek
        self.special = speciallizacija

class Termin:
    """
    """
    def __init__(self, dvorana, datum, ura_pricetka, ura_konca, termin_id):
        self.termin_id = termin_id
        self.dvorana = dvorana
        self.datum = datum
        self.ura_pric = ura_pricetka
        self.ura_konca = ura_konca

class Rezervacija:
    """
    Razred za rezervaicjo
    """