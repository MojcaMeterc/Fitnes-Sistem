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
    
    # metoda za izpis uporabnikovih rezervacij
    def rezervacije(self):
        '''uporabnikove rezervacije
        '''
        cur = self.conn.execute("""
            SELECT termin_id FROM rezervacijaU
                WHERE uporabnik_id = ?
            """, (self.uporabnik_id,))
        
        return cur.fetchall()
    
    # metoda za brisanje rezervacije
    def preklici_rezervacijo(self, termin_id):
        self.conn.execute("""
            DELETE FROM rezervacijaU 
                WHERE uporabnik_id = ? AND termin_id = ?
            """, (self.uporabnik_id, termin_id))
        
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
    
    @staticmethod
    def vsi_tren(conn):
        '''metoda za branje podatkov
        '''
        cur = conn.execute("""
            SELECT termin_id, dvorana_id, datum, ura_pricetka, ura_konca
            FROM termini
                ORDER BY datum, ura_pricetka
            """)
        for vrstica in cur:
            yield Termin(conn, vrstica[1], vrstica[2], vrstica[3], vrstica[4], vrstica[0])


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

    def shrani_termin(self):
        '''ustvarjanje termina
        '''
        cur = self.conn.execute("""
            INSERT INTO termini (dvorana_id, datum, ura_pricetka, ura_konca)
                VALUES (?, ?, ?, ?)
            """, (self.dvorana_id, self.datumm, self.ura_pricetka, self.ura_konca))
        
        self.termin_id = cur.lastrowid
        self.conn.commit()

    # metoda za preverjanje kapacitete termina
    def stevilo_prijavljenih(self):
        '''kapaciteta termina
        '''
        cur = self.conn.execute("""
            SELECT COUNT(*) FROM rezervacijaU
                WHERE termin_id = ?
            """, (self.termin_id,))
        
        return cur.fetchone()[0]
    

class Rezervacija:
    """
    Razred za rezervacijo
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
    
class Karta:
    """
    Razred za karto
    """
    def __init__(self, conn, naziv, trajanje_dni, cena, karta_id=None):
        self.conn= conn
        self.karta_id = karta_id
        self.naziv = naziv
        self.trajanje_dni = trajanje_dni
        self.cena = cena
    
    def shrani_karto(self):
        '''
        '''
        cur = self.conn.execute("""
            INSERT INTO karta (naziv, trajanje_dni, cena)
                VALUES (?, ?, ?)
            """, (self.naziv, self.trajanje_dni, self.cena))
        
        self.karta_id = cur.lastrowid
        self.conn.commit()

class Dvorana:
    """
    Razred za dvorano
    """
    def __init__(self, conn, naziv, kapaciteta, dvorana_id=None):
        self.conn = conn
        self.dvorana_id = dvorana_id
        self.naziv = naziv
        self.kapaciteta = kapaciteta

    def shrani_dvorano(self):
        cur = self.conn.execute("""
            INSERT INTO dvorane (naziv, kapaciteta)
                VALUES (?, ?)
            """, (self.naziv, self.kapaciteta))
        
        self.dvorana_id = cur.lastrowid
        self.conn.commit()



    