#importi...


class Uporabnik:
    """
    Razred za Uporabnik
    """
    def __init__(self, conn, ime, priimek, email, telefon, uporabnik_id = None):
        self.conn = conn
        self.uporabnik_id = uporabnik_id
        self.ime = ime
        self.priimek = priimek
        self.email = email
        self.telefon = telefon

    def __str__(self):
        return f"{self.ime} {self.priimek}"
    
    # metode:
    # ustvari račun
    def ustvari_racun(self):
        ''' ustvarjanje računa
        '''
        cur = self.conn.execute("""
            INSERT INTO uporabniki (ime, priimek, email, telefon)
            VALUES (?, ?, ?, ?)
            """, (self.ime, self.priimek, self.email, self.telefon))
        
        self.uporabnik_id = cur.lastrowid # ID zadnje dodane vrstice
        self.conn.commit() # trajno shranimo spremembe v bazo
    
    # prijava
    @staticmethod
    def prijava(conn, email):
        ''' prijava po emailu
        '''
        cur = conn.execute("""
            SELECT uporabnik_id, ime, priimek, email, telefon
            FROM uporabniki
                WHERE email = ?
        """, (email,))

        vrstica = cur.fetchone()
        if vrstica:
            return Uporabnik(conn, vrstica[1], vrstica[2], vrstica[3], vrstica[4], vrstica[0])
        return None
    
    # nakup karte(povezava med uporabnik in karta - karta_id)
    def kupi_karto(self, karta_id):
        '''nakup karte
        '''
        self.conn.execute(""""
            INSERT INTO kupljenaKarta (vrsta_karte, uporabnik)
                VALUES (?, ?)
            """, (karta_id, self.uporabnik_id))
        
        self.conn.commit()

    # uporabnik izbere termin (povezeva med uporabnikom in terminom)
    def izberi_termin(self, termin_id):
        '''izbira termina
        '''
        self.conn.execute("""
            INSERT INTO rezervacijaU (tremin_id, uporabnik_id)
                VALUES (?, ?)
            """, (termin_id, self.uporabnik_id))
        
        self.conn.commit()

class Trener:
    """
    """
    def __init__(self, conn, ime, priimek, speciallizacija, trener_id = None): 
        self.conn = conn
        self.trener_id = None
        self.ime = ime
        self.priimek = priimek
        self.special = speciallizacija

    # metode:
    # prijava
    # rezervacija termina
    # je na wordu

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
    