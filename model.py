import sqlite3
import hashlib
from datetime import datetime, timedelta


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
        self.conn.execute("""
            INSERT INTO kupljenaKarta (vrsta_karte_id , uporabnik_id )
                VALUES (?, ?)
            """, (karta_id, self.uporabnik_id))
        
        self.conn.commit()

    # uporabnik izbere termin (povezeva med uporabnikom in terminom)
    def izberi_termin(self, termin_id):
        '''izbira termina
        '''
        self.conn.execute("""
            INSERT INTO rezervacijaU (termin_id, uporabnik_id)
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

    def moje_rezervacije(self):
        '''prikaz rezervacij določenega uporabnika
        '''
        sql = """
                SELECT termini.datum, termini.ura_pricetka termini.ura_konca
                FROM rezervacijaU
                JOIN termini ON rezervacijaU.termin_id = termini.termin_id
                WHERE rezervacijaU.uporabnik_id = ?
            """
        return self.conn.execute(sql, (self.uporabnik_id,))
    
    def aktivne_karte(self):
        '''vse aktivne karte uporabnika
        '''
        sql = """
                SELECT karta.naziv, kk.datum, karta.trajanje FROM kupljenaKarta AS kk
                JOIN karta ON kk.vrsta_karte_id = karta.karta_id
                WHERE kk.uporabnik_id = ?
            """
        return self.conn.execute(sql, (self.uporabnik_id,))
    
    def iztek_naslednje(self):
        '''kdaj se izteče naslednja karta
        '''
        sql = """
                SELECT DATE(kk.datum, '+' || karta.trajanje || 'days')
                FROM kupljenaKarta AS kk
                JOIN karta ON kk.vrsta_karte_id = karta.karta_id
                WHERE kk.uporabnik_id = ?
                ORDER BY kk.datum DESC  
                LIMIT 1
            """
        return self.conn.execute(sql, (self.uporabnik_id,)).fetchone()
        


class Trener:
    """ razred za tremerja
    """
    def __init__(self, conn, ime, priimek, speciallizacija, trener_id = None): 
        self.conn = conn
        self.trener_id = trener_id
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

    @staticmethod
    def stevilo_rezervacij(conn):
        '''število rezervacij po trenerjih
        '''
        sql = """
                SELECT trener.ime, trener.priimek, COUNT(rezervacijaU.termin_id)
                FROM trener
                LEFT JOIN rezervacijaT ON trener.trener_id = rezervacijaT.trener_id
                LEFT JOIN rezervacijaU ON rezervacijaT.termin = rezervacijaU.termin_id
                GROUP BY trener.trener_id
            """
        return conn.execute(sql)
    

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
            """, (self.dvorana_id, self.datum, self.ura_pricetka, self.ura_konca))
        
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
    
    @staticmethod
    def vsi_s_podatki(conn):
        '''seznam vseh terminov s trenerji in dvoranami
        '''
        sql = """
            SELECT termini.termin_id,
                    termini.datum,
                    termini.ura_pricetka,
                    termini.ura_konca,
                    dvorane.naziv,
                    trener.ime,
                    trener.priimek
            FROM termini
            LEFT JOIN dvorane ON termini.dvorana_id = dvorane.dvorana_id
            LEFT JOIN rezervacijaT ON termini.termin_id = rezervacijaT.termin
            LEFT JOIN trener ON rezervacijaT.trener_id = trener.trener_id
            ORDER BY termini.datum, termini.ura_pricetka
        """
        return conn.execute(sql)
    
    @staticmethod
    def prosti_termini(conn):
        '''prosti termini (brez rezervacij)
        '''
        sql = """
                SELECT * FROM termini
                LEFT JOIN rezervacijaU ON termini.termin_id = rezervacijaU.termin_id
                WHERE rezervacijaU.termin_id IS NULL
            """
        return conn.execute(sql)
    
    def je_prostor(self):
        '''kapaciteta dvorane
        '''
        sql = """
                SELECT dvorana.kapaciteta FROM termini
                JOIN dvorane ON termini.dvorana_id = dvorane.dvorana_id
                WHERE termini.termin_id = ?
            """
        kapaciteta = self.conn.execute(sql, (self.termin_id,)).fetchone()[0]
        return self.stevilo_prijavljenih() < kapaciteta
    

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
    
    @staticmethod
    def mesecni_prihodki(conn):
        '''mesečni prihodki
        '''
        sql = """
                SELECT strftime('%Y-%m', datum) as mesec, SUM(karta.cena) 
                FROM kupljenaKarta AS kk
                JOIN karta ON kk.vrsta_karte = karta.karta_id
                GROUP BY mesec
            """
        return conn.execute(sql)

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



    