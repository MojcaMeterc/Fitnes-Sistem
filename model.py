import sqlite3
import hashlib
from datetime import datetime, timedelta

def hash_geslo(geslo):
    '''hash gesla
    '''
    return hashlib.sha256(geslo.encode()).hexdigest()

# ==================
# UPORABNIK
# ==================

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

    # REGISTRACIJA
    def ustvari_racun(self, geslo):
        ''' ustvarjanje računa
        '''
        geslo_hash = hash_geslo(geslo)

        cur = self.conn.execute("""
            INSERT INTO uporabniki (ime, priimek, email, telefon, geslo_hash)
            VALUES (?, ?, ?, ?, ?)
            """, (self.ime, self.priimek, self.email, self.telefon, geslo_hash))
        
        self.uporabnik_id = cur.lastrowid # ID zadnje dodane vrstice
        self.conn.commit() # trajno shranimo spremembe v bazo
    
    # prijava
    @staticmethod
    def prijava(conn, email, geslo):
        ''' prijava po emailu
        '''
        geslo_hash = hash_geslo(geslo)

        cur = conn.execute("""
            SELECT uporabnik_id, ime, priimek, email, telefon
            FROM uporabniki
            WHERE email = ? AND geslo_hash = ?
        """, (email, geslo_hash))


        vrstica = cur.fetchone()
        if vrstica:
            return Uporabnik(conn, vrstica[1], vrstica[2], vrstica[3], vrstica[4], vrstica[0])
        return None
    
    # nakup karte(povezava med uporabnik in karta - karta_id)
    def kupi_karto(self, karta_id):
        '''nakup karte
        '''
        self.conn.execute("""
            INSERT INTO kupljenaKarta (vrsta_karte, uporabnik_id)
                VALUES (?, ?)
            """, (karta_id, self.uporabnik_id))
        
        self.conn.commit()

    # uporabnik izbere termin (povezeva med uporabnikom in terminom)
    def izberi_termin(self, termin_id):
        '''izbira termina
        '''
        termin = Termin(self.conn, None, None, None, None, termin_id)

        # preveri veljavnost karte
        if not self.ima_veljavno_karto():
            raise Exception('Nimate veljavne karte')
        
        # preveri kapaciteto dvorane
        if not termin.je_prostor():
            raise Exception("Žal, dvorana je polna. Izberite drug termin.")

        # doda rezervacijo        
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
                SELECT termini.datum, termini.ura_pricetka, termini.ura_konca, dvorane.naziv AS dvorana
                FROM rezervacijaU
                JOIN termini ON rezervacijaU.termin_id = termini.termin_id
                LEFT JOIN dvorane ON termini.dvorana_id = dvorane.dvorana_id
                WHERE rezervacijaU.uporabnik_id = ?
            """
        return self.conn.execute(sql, (self.uporabnik_id,))

    def aktivne_karte(self):
        '''vse aktivne karte uporabnika
        '''
        sql = """
                SELECT karta.naziv,
                    kk.datum,
                    DATE(kk.datum, '+' || karta.trajanje || ' days') AS datum_izteka,
                    CAST(julianday(DATE(kk.datum, '+' || karta.trajanje || ' days')) - julianday('now') AS INTEGER) AS dni_do_izteka
                FROM kupljenaKarta AS kk
                JOIN karta ON kk.vrsta_karte = karta.karta_id
                WHERE kk.uporabnik_id = ?
                AND DATE(kk.datum, '+' || karta.trajanje || ' days') >= DATE('now')
            """
        return self.conn.execute(sql, (self.uporabnik_id,))
    
    def iztek_naslednje(self):
        '''kdaj se izteče naslednja karta
        '''
        sql = """
                SELECT DATE(kk.datum, '+' || karta.trajanje || ' days')
                FROM kupljenaKarta AS kk
                JOIN karta ON kk.vrsta_karte = karta.karta_id
                WHERE kk.uporabnik_id = ?
                ORDER BY kk.datum DESC  
                LIMIT 1
            """
        return self.conn.execute(sql, (self.uporabnik_id,)).fetchone()
    
    def ima_veljavno_karto(self):
        '''metoda preveri ali ima uporabnik veljavno karto ali ne
        '''
        vrst = self.iztek_naslednje()

        if not vrst or vrst[0] is None:
            return False
        
        iztek = datetime.strptime(vrst[0], "%Y-%m-%d").date()
        return iztek >= datetime.now().date()
        
    @staticmethod
    def pridobi_po_id(conn, uporabnik_id):
        '''Vrne objekt uporabnik po ID-ju'''
        sql = "SELECT * FROM uporabniki WHERE uporabnik_id = ?"
        cur = conn.execute(sql, (uporabnik_id,))
        vrstica = cur.fetchone()
        if vrstica:
            return Uporabnik(
                conn,
                vrstica['ime'],
                vrstica['priimek'],
                vrstica['email'],
                vrstica['telefon'],
                uporabnik_id = vrstica['uporabnik_id']   
            )
        return None

# ==================
# TRENER
# ==================   

class Trener:
    """ razred za trenerja
    """
    def __init__(self, conn, ime, priimek, email, specializacija, trener_id = None): 
        self.conn = conn
        self.trener_id = trener_id
        self.ime = ime
        self.priimek = priimek
        self.email = email
        self.special = specializacija

    @staticmethod
    def prijava(conn, email, geslo):
        ''' Prijava trennerja
        '''
        geslo_hash = hash_geslo(geslo)

        cur = conn.execute("""
            SELECT trener_id, ime, priimek, email, specializacija
            FROM trener
            WHERE email = ? AND geslo_hash = ?
        """, (email, geslo_hash))

        vrstica = cur.fetchone()
        if vrstica:
            return Trener(conn, vrstica[1], vrstica[2], vrstica[3], vrstica[4], vrstica[0])
        return None
    
    @staticmethod
    def pridobi_po_id(conn, trener_id):
        sql = "SELECT * FROM trener WHERE trener_id = ?"
        vrstica = conn.execute(sql, (trener_id,)).fetchone()

        if vrstica:
            return Trener(
                conn,
                vrstica['ime'],
                vrstica['priimek'],
                vrstica['email'],
                vrstica['specializacija'],
                trener_id = vrstica['trener_id']
            )
        return None

    def izberi_termin(self, termin_id):
        '''rezervacija termina
        '''
        self.conn.execute("""
            INSERT INTO rezervacijaT (trener_id, termin_id)
                VALUES (?, ?)
            """, (self.trener_id, termin_id))
        
        self.conn.commit()

    def moji_termini(self):
        '''Termini trenerja
        '''
        sql = """
                SELECT termini.termin_id,
                    termini.datum,
                    termini.ura_pricetka,
                    termini.ura_konca,
                    dvorane.naziv AS dvorana,
                    COUNT(rezervacijaU.termin_id) AS stevilo_prijavljenih
                FROM rezervacijaT
                JOIN termini ON rezervacijaT.termin_id = termini.termin_id
                LEFT JOIN dvorane ON termini.dvorana_id = dvorane.dvorana_id
                LEFT JOIN rezervacijaU ON termini.termin_id = rezervacijaU.termin_id
                WHERE rezervacijaT.trener_id = ?
                GROUP BY termini.termin_id
                ORDER BY termini.datum, termini.ura_pricetka
                """
        return self.conn.execute(sql, (self.trener_id,)).fetchall()


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
                LEFT JOIN rezervacijaU ON rezervacijaT.termin_id = rezervacijaU.termin_id
                GROUP BY trener.trener_id
            """
        return conn.execute(sql)
    
# ==================
# ADMIN
# ==================

class Admin:
    '''Admin sistem
    '''
    def __init__(self, conn, ime, email, admin_id=None):
        self.conn = conn
        self.admin_id = admin_id
        self.ime = ime
        self.email = email

    @staticmethod
    def prijava(conn, email, geslo):
        '''Prijava admina
        '''
        geslo_hash = hash_geslo(geslo)
        vrstica = conn.execute(
            "SELECT admin_id, ime, email FROM admin WHERE email = ? AND geslo_hash = ?",
            (email, geslo_hash)).fetchone()
        if vrstica:
            return Admin(conn, vrstica['ime'], vrstica['email'], vrstica['admin_id'])
        return None

    @staticmethod
    def pridobi_po_id(conn, admin_id):
        vrstica = conn.execute(
            "SELECT * FROM admin WHERE admin_id = ?",
            (admin_id,)).fetchone()
        if vrstica:
            return Admin(conn, vrstica['ime'], vrstica['email'], vrstica['admin_id'])
        return None

    def vsi_trenerji(self):
        return self.conn.execute(
            "SELECT * FROM trener ORDER BY priimek"
        ).fetchall()

    def dodaj_trenerja(self, ime, priimek, email, specializacija, geslo):
        geslo_hash = hash_geslo(geslo)
        self.conn.execute(
            "INSERT INTO trener (ime, priimek, email, specializacija, geslo_hash) VALUES (?, ?, ?, ?, ?)",
            (ime, priimek, email, specializacija, geslo_hash))
        self.conn.commit()

    def izbrisi_trenerja(self, trener_id):
        self.conn.execute(
            "DELETE FROM trener WHERE trener_id = ?",
            (trener_id,))
        self.conn.commit()
    

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
            LEFT JOIN rezervacijaT ON termini.termin_id = rezervacijaT.termin_id
            LEFT JOIN trener ON rezervacijaT.trener_id = trener.trener_id
            ORDER BY termini.datum, termini.ura_pricetka
        """
        return conn.execute(sql)
    
    @staticmethod
    def prosti_term_trener(conn, uporabnik_id):
        sql = """
            SELECT termini.termin_id,
                termini.datum,
                termini.ura_pricetka,
                termini.ura_konca,
                dvorane.naziv AS dvorana,
                trener.ime AS trener_ime,
                trener.priimek AS trene_priimek
            FROM termini
            JOIN rezervacijaT ON termini.termin_id = rezervacijaT.termin_id
            JOIN trener ON rezervacijaT.trener_id = trener.trener_id
            LEFT JOIN dvorane ON termini.dvorana_id = dvorane.dvorana_id
            WHERE termini.termin_id NOT IN (
                SELECT termin_id FROM rezervacijaU WHERE uporabnik_id = ?
                )
            AND termini.datum >= DATE('now')
            ORDER BY termini.datum, termini.ura_pricetka
            """
        return conn.execute(sql, (uporabnik_id,)).fetchall()
    
    @staticmethod
    def termini_brez_trenerja(conn, dvorana_id=None):
        filter_sql = f"AND termini.dvorana_id = {int(dvorana_id)}" if dvorana_id else ""
        sql = f"""
            SELECT termini.termin_id, termini.datum, termini.ura_pricetka,
                termini.ura_konca, dvorane.naziv AS dvorana
            FROM termini
            LEFT JOIN rezervacijaT ON termini.termin_id = rezervacijaT.termin_id
            LEFT JOIN dvorane ON termini.dvorana_id = dvorane.dvorana_id
            WHERE rezervacijaT.termin_id IS NULL
            AND termini.datum >= DATE('now')
            {filter_sql}
            ORDER BY termini.datum, termini.ura_pricetka"""
        return conn.execute(sql).fetchall()
    
    def je_prostor(self):
        '''kapaciteta dvorane
        '''
        sql = """
                SELECT dvorane.kapaciteta FROM termini
                JOIN dvorane ON termini.dvorana_id = dvorane.dvorana_id
                WHERE termini.termin_id = ?
            """
        kapaciteta = self.conn.execute(sql, (int(self.termin_id),)).fetchone()[0]
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
    def __init__(self, conn, naziv, trajanje, cena, karta_id=None):
        self.conn= conn
        self.karta_id = karta_id
        self.naziv = naziv
        self.trajanje = trajanje
        self.cena = cena
    
    def shrani_karto(self):
        '''
        '''
        cur = self.conn.execute("""
            INSERT INTO karta (naziv, trajanje, cena)
                VALUES (?, ?, ?)
            """, (self.naziv, self.trajanje, self.cena))
        
        self.karta_id = cur.lastrowid
        self.conn.commit()
    
    @staticmethod
    def mesecni_prihodki(conn):
        '''mesečni prihodki
        '''
        sql = """
                SELECT strftime('%Y-%m', kk.datum) as mesec, SUM(karta.cena) 
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

    @staticmethod
    def vse_dvorane(conn):
        """Vrne vse dvorane"""
        return conn.execute("SELECT dvorana_id, naziv FROM dvorane").fetchall()

    