#importi...


class Uporabnik:
    """
    Razred za Uporabnika
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
    """ razred za tremerja
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
    def rezerviraj_termin(self, termin_id):
        '''rezervacija termina
        '''
        self.conn.execute("""
            INSERT INTO rezervacijaT (trener_id, termin)
                VALUES (?, ?)
            """, (self.trener_id, termin_id))
        
        self.conn.commit()
    # je na wordu

class Termin:
    """
    Razred za termin
    """
    def __init__(self, conn, dvorana_id, datum, ura_pricetka, ura_konca, termin_id):
        self.conn = conn
        self.termin_id = termin_id
        self.dvorana_id = dvorana_id
        self.datum = datum
        self.ura_pricetka = ura_pricetka
        self.ura_konca = ura_konca

    def shrani(self):
        '''ustvarjanje termina
        '''
        cur = self.conn.execute("""
            INSERT INTO termini (dvorana_id, datum, ura_pricetka, ura_konca)
                VALUES (?, ?, ?, ?)
            """, (self.dvorana_id, self.datumm, self.ura_pricetka, self.ura_konca))
        
        self.termin_id = cur.lastrowid
        self.conn.commit()

class Rezervacija:
    """
    Razred za rezervaicjo
    """
    def __init__(self, conn):
        self.conn = conn
    
    def rezervacije_uporabnika(self, uporabnik_id):
        '''
        '''
        cur = self.conn.execute("""
            SELECT * FROM rezervacijaU
            WHERE uporabnik_id = ?
            """, (uporabnik_id,))
        return cur.fetchall()
    
    