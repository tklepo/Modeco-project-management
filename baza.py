import sqlite3


# =================== tablica: PROJEKTI
def ucitaj_projekte():
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute('SELECT NAZIV_PROJEKTA, KUPAC, LOKACIJA, STATUS FROM PROJEKTI ORDER BY STATUS DESC')
    rows = c.fetchall()
    conn.close()
    return rows


def ucitaj_aktivne_projekte():
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT NAZIV_PROJEKTA, KUPAC, LOKACIJA, STATUS FROM PROJEKTI WHERE STATUS = 'a'""")
    rows = c.fetchall()
    conn.close()
    return rows


def unesi_projekt(naziv, kupac, lokacija, status):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute('''INSERT INTO PROJEKTI (NAZIV_PROJEKTA, KUPAC, LOKACIJA, STATUS) VALUES(?, ?, ?, ?)''',
              (naziv, kupac, lokacija, status))
    conn.commit()
    conn.close()


def promjeni_status_projekta(ide, status):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""UPDATE PROJEKTI SET STATUS=? WHERE ID_PROJEKT = ?""", (status, ide))
    conn.commit()
    conn.close()


def id_projekt(pro):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT ID_PROJEKT FROM PROJEKTI WHERE NAZIV_PROJEKTA = ?""", (pro,))
    rows = c.fetchone()
    conn.close()
    return rows


# ======================= tablica: NAPOMENE_PROJEKTI
def unesi_napomenu(pro, nap, vri):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute('''INSERT INTO NAPOMENE_PROJEKTI (PROJEKT, NAPOMENA, VRIJEME_UNOSA)
     VALUES((SELECT ID_PROJEKT FROM PROJEKTI WHERE NAZIV_PROJEKTA = ?), ?, ?)''',
              (pro, nap, vri))
    conn.commit()
    conn.close()


def trazi_napomene(projekt):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT VRIJEME_UNOSA,
    NAPOMENA
    FROM NAPOMENE_PROJEKTI 
    WHERE 
    PROJEKT = (SELECT ID_PROJEKT FROM PROJEKTI WHERE NAZIV_PROJEKTA = ?)""", (projekt,))
    rows = c.fetchall()
    conn.close()
    return rows


# ----------- Tablica: RADNICI
def ucitaj_radnike():
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT IME_PREZIME, PLACA, STATUS FROM RADNICI ORDER BY STATUS""")
    rows = c.fetchall()
    conn.close()
    return rows


def ucitaj_zaposlene_radnike():
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT IME_PREZIME, PLACA, STATUS FROM RADNICI WHERE STATUS = 'a'""")
    rows = c.fetchall()
    conn.close()
    return rows


def promjeni_status_radnika(id_r, status):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""UPDATE RADNICI SET STATUS=? WHERE ID_RADNIK = ?""", (status, id_r))
    conn.commit()
    conn.close()


def id_radnika(ime):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT ID_RADNIK FROM RADNICI WHERE IME_PREZIME = ?""", (ime,))
    rows = c.fetchone()
    conn.close()
    return rows


def unesi_radnika(im_pr, pla, stat):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute('''INSERT INTO RADNICI (IME_PREZIME, PLACA, STATUS) VALUES(?, ?, ?)''',
              (im_pr, pla, stat))
    conn.commit()
    conn.close()


def placa_radnika(ime):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT PLACA FROM RADNICI WHERE IME_PREZIME = ?""", (ime,))
    rows = c.fetchone()
    conn.close()
    return rows


def radnik_i_placa():
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT ID_RADNIK, PLACA FROM RADNICI""")
    rows = c.fetchall()
    conn.close()
    return rows


# ----------- Tablica: SPOJNI_ELEMENTI
def ucitaj_se():
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT NAZIV_SE, SE_CIJENA_JM, JM_SE FROM SPOJNI_ELEMENTI""")
    rows = c.fetchall()
    conn.close()
    return rows


def unesi_se(naz, cij, jm):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute('''INSERT INTO SPOJNI_ELEMENTI (NAZIV_SE, SE_CIJENA_JM, JM_SE) VALUES(?, ?, ?)''',
              (naz, cij, jm))
    conn.commit()
    conn.close()


def cijena_spojnog(ime_spojnog):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT SE_CIJENA_JM FROM SPOJNI_ELEMENTI WHERE NAZIV_SE = ?""", (ime_spojnog,))
    rows = c.fetchone()
    conn.close()
    return rows


def id_spojni(id_se):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT ID_SE FROM SPOJNI_ELEMENTI WHERE NAZIV_SE = ?""", (id_se,))
    rows = c.fetchone()
    conn.close()
    return rows


# ----------- Tablica: STAVKE MONTAZE
def ucitaj_stavke():
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT NAZIV, CIJENA_JM, JM FROM STAVKE_MONTAZE""")
    rows = c.fetchall()
    conn.close()
    return rows


def unesi_stavku(naz, cij, jm):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute('''INSERT INTO STAVKE_MONTAZE (NAZIV, CIJENA_JM, JM) VALUES(?, ?, ?)''',
              (naz, cij, jm))
    conn.commit()
    conn.close()


def cijena_stavke(stavka_naz):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT CIJENA_JM FROM STAVKE_MONTAZE WHERE NAZIV = ?""", (stavka_naz,))
    rows = c.fetchone()
    conn.close()
    return rows


def jm_spoj(sm):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT JM_SE FROM SPOJNI_ELEMENTI WHERE NAZIV_se = ?""", (sm,))
    rows = c.fetchone()
    conn.close()
    return rows


def jm_stavka(sm):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT JM FROM STAVKE_MONTAZE WHERE NAZIV = ?""", (sm,))
    rows = c.fetchone()
    conn.close()
    return rows


# ----------- Tablica: STROJEVI
def ucitaj_strojeve():
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT NAZIV, CIJENA, JM FROM STROJEVI""")
    rows = c.fetchall()
    conn.close()
    return rows


def unesi_stroj(naz, jm, cij):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute('''INSERT INTO STROJEVI (NAZIV, JM, CIJENA) VALUES(?, ?, ?)''',
              (naz, jm, cij))
    conn.commit()
    conn.close()


def cijena_stroja(ime_stroja):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT CIJENA FROM STROJEVI WHERE NAZIV = ?""", (ime_stroja,))
    rows = c.fetchone()
    conn.close()
    return rows


def jm_stroja(stro):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT JM FROM STROJEVI WHERE NAZIV = ?""", (stro,))
    rows = c.fetchone()
    conn.close()
    return rows


# ----------------- Tablica: TROSAK_RADNICI
def unos_troska_radnika(pro, rad, kol, dat):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute('''INSERT INTO TROSAK_RADNICI(PROJEKT, RADNIK, BROJ_SATI, DATUM) 
    VALUES(?, (SELECT ID_RADNIK FROM RADNICI WHERE IME_PREZIME = ?), ?, ?)''',
              (pro, rad, kol, dat))
    conn.commit()
    conn.close()


def trosak_radnika_po_projektu(pro):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT TROSAK_RADNICI.DATUM, RADNICI.IME_PREZIME, TROSAK_RADNICI.BROJ_SATI FROM TROSAK_RADNICI
    JOIN RADNICI ON TROSAK_RADNICI.RADNIK = RADNICI.ID_RADNIK
    WHERE TROSAK_RADNICI.PROJEKT = ?""", (pro,))
    rows = c.fetchall()
    conn.close()
    return rows


def obracun_sati_radnika(od, do, radnik):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT RADNICI.IME_PREZIME, SUM(TROSAK_RADNICI.BROJ_SATI) FROM TROSAK_RADNICI
    JOIN RADNICI ON TROSAK_RADNICI.RADNIK = RADNICI.ID_RADNIK
    WHERE TROSAK_RADNICI.DATUM BETWEEN ? AND ? 
    AND TROSAK_RADNICI.RADNIK = ?""", (od, do, radnik))
    rows = c.fetchall()
    conn.close()
    return rows


def obracun_sati_radnika_po_pro(od, do, radnik, pro):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT PROJEKTI.NAZIV_PROJEKTA, RADNICI.IME_PREZIME, SUM(TROSAK_RADNICI.BROJ_SATI) FROM TROSAK_RADNICI
    JOIN RADNICI ON TROSAK_RADNICI.RADNIK = RADNICI.ID_RADNIK
    JOIN PROJEKTI ON TROSAK_RADNICI.PROJEKT = PROJEKTI.ID_PROJEKT
    WHERE TROSAK_RADNICI.DATUM BETWEEN ? AND ? 
    AND TROSAK_RADNICI.RADNIK = ?
    AND TROSAK_RADNICI.PROJEKT = ?""", (od, do, radnik, pro))
    rows = c.fetchall()
    conn.close()
    return rows


def projekti_u_periodu(od, do):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT DISTINCT PROJEKT FROM TROSAK_RADNICI WHERE DATUM BETWEEN ? AND ?""", (od, do))
    rows = c.fetchall()
    conn.close()
    return rows


# ----------------- Tablica: TROSAK_STROJEVI
def unos_troska_strojeva(stro, pro, dat, kol):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute('''INSERT INTO TROSAK_STROJEVI(STROJ, PROJEKT, DATUM, KOLICINA) 
    VALUES((SELECT ID_STROJ FROM STROJEVI WHERE NAZIV = ?), ?, ?, ?)''',
              (stro, pro, dat, kol))
    conn.commit()
    conn.close()


def trosak_stroja_po_projektu(pro):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT TROSAK_STROJEVI.DATUM, STROJEVI.NAZIV, STROJEVI.JM, TROSAK_STROJEVI.KOLICINA FROM TROSAK_STROJEVI
        JOIN STROJEVI ON TROSAK_STROJEVI.STROJ = STROJEVI.ID_STROJ
        WHERE TROSAK_STROJEVI.PROJEKT = ?""", (pro,))
    rows = c.fetchall()
    conn.close()
    return rows


# ----------------- Tablica: TROSAK_SPOJNI
def unos_troska_spojeva(pro, se, kol, dat):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute('''INSERT INTO TROSAK_SPOJNI(PROJEKT, SPOJNI_ELEMENT, KOLICINA, DATUM) 
    VALUES(?, (SELECT ID_SE FROM SPOJNI_ELEMENTI WHERE NAZIV_SE = ?), ?, ?)''',
              (pro, se, kol, dat))
    conn.commit()
    conn.close()


def trosak_spojnih_po_projektu(pro):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT TROSAK_SPOJNI.DATUM, SPOJNI_ELEMENTI.NAZIV_SE, TROSAK_SPOJNI.KOLICINA, SPOJNI_ELEMENTI.JM_SE
    FROM TROSAK_SPOJNI
        JOIN SPOJNI_ELEMENTI ON TROSAK_SPOJNI.SPOJNI_ELEMENT = SPOJNI_ELEMENTI.ID_SE
        WHERE TROSAK_SPOJNI.PROJEKT = ?""", (pro,))
    rows = c.fetchall()
    conn.close()
    return rows


# ----------------- Tablica: IZVRSENE_STAVKE
def unos_izvrsenih_stavki(pro, dat, sta, kol):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute('''INSERT INTO IZVRSENE_STAVKE(PROJEKT, DATUM, STAVKA, KOLICINA) 
    VALUES(?, ?, (SELECT ID_SM FROM STAVKE_MONTAZE WHERE NAZIV = ?), ?)''',
              (pro, dat, sta, kol))
    conn.commit()
    conn.close()


def izvrseno_po_projektu(pro):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT IZVRSENE_STAVKE.DATUM, STAVKE_MONTAZE.NAZIV, IZVRSENE_STAVKE.KOLICINA, STAVKE_MONTAZE.JM
    FROM IZVRSENE_STAVKE
            JOIN STAVKE_MONTAZE ON IZVRSENE_STAVKE.STAVKA = STAVKE_MONTAZE.ID_SM
            WHERE IZVRSENE_STAVKE.PROJEKT = ?""", (pro,))
    rows = c.fetchall()
    conn.close()
    return rows


# ----------------- Tablica: TERENSKI_TROSAK
def unesi_terenske_troskove(ruc, spa, ter, ces, gor, dat, pro):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute('''INSERT INTO TERENSKI_TROSAK(RUCAK, SPAVANJE, TERENSKI_DODATAK, CESTARINA, GORIVO, DATUM, PROJEKT) 
    VALUES(?, ?, ?, ?, ?, ?, ?)''',
              (ruc, spa, ter, ces, gor, dat, pro))
    conn.commit()
    conn.close()


def terenski_trosat_po_projektu(pro):
    conn = sqlite3.connect('baza_pm.db')
    c = conn.cursor()
    c.execute("""SELECT DATUM, RUCAK, SPAVANJE, TERENSKI_DODATAK, CESTARINA, GORIVO FROM TERENSKI_TROSAK
        WHERE PROJEKT = ?""", (pro,))
    rows = c.fetchall()
    conn.close()
    return rows