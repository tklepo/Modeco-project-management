from tkinter import *
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from tkinter import ttk
from tkinter import messagebox
from ttkwidgets.autocomplete import AutocompleteCombobox
from tkinter.scrolledtext import ScrolledText
import baza
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Image
from reportlab.lib import colors
import os
import sys
from tkinter import filedialog
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from PIL import ImageTk, Image
from funkcije import *
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from babel.numbers import *


class Page(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

    def show(self):
        self.lift()


class PageProjekti(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        """ Stranica za unos novih projekata u bazu"""

        # prozor sadrzi 2 taba: projekti,  napomene
        pro_lbl = Label(self, text='Projekti', font=('Arial', 24), bg='#FFFF00')

        tab_parent1 = ttk.Notebook(self)
        projekti_tab = ttk.Frame(tab_parent1)
        napomene_tab = ttk.Frame(tab_parent1)

        tab_parent1.add(projekti_tab, text="Projekti")
        tab_parent1.add(napomene_tab, text="Napomene")

        # -------------- Projekti - tab
        # ----------tablica sa svim projektima, omogućen unos napomene vezane za projekt i promjenu statusa projekta

        projekti_tv = ttk.Treeview(projekti_tab, column=("column1", "column2", "column3", "column4"),
                                   show='headings', height=18)
        projekti_tv.column("#1", width=350, minwidth=40)
        projekti_tv.column("#2", width=320, minwidth=40)
        projekti_tv.column("#3", width=320, minwidth=40)
        projekti_tv.column("#4", width=100, minwidth=100)

        projekti_tv.heading("#1", text="Naziv")
        projekti_tv.heading("#2", text="Kupac")
        projekti_tv.heading("#3", text="Lokacija")
        projekti_tv.heading("#4", text="Status")

        scrollbar_pro = Scrollbar(projekti_tab)
        projekti_tv.configure(yscrollcommand=scrollbar_pro.set)
        scrollbar_pro.configure(command=projekti_tv.yview)

        punjenje_projekti_tv(projekti_tv, baza.ucitaj_projekte())

        promijeni_status_btn = Button(projekti_tab, text='Promijeni status')

        def promijeni_status():
            """Funkcija za promjenu statusa projekta iz a u z i obrnuto"""
            odabrani_item = projekti_tv.selection()[0]  # rad s oznacenim redom u Treeviewu
            vrijednosti_itema = tuple(
                projekti_tv.item(odabrani_item)['values'])  # tuple sa vrijednostima odabranog reda
            # print(vrijednosti_itema)
            id_projekta = baza.id_projekt(vrijednosti_itema[0])[0]
            status_projekta = vrijednosti_itema[3]

            if status_projekta == 'Aktivan':
                baza.promjeni_status_projekta(id_projekta, 'z')
            else:
                baza.promjeni_status_projekta(id_projekta, 'a')

            punjenje_projekti_tv(projekti_tv, baza.ucitaj_projekte())

        promijeni_status_btn.configure(command=promijeni_status)

        novi_pr_frame = Frame(projekti_tab)

        # projekt_id_lbl = Label(projekti_tab, text='Šifra projekta:')
        # projekt_id_ent = Entry(projekti_tab, width=22)
        projekt_naziv_lbl = Label(novi_pr_frame, text='Naziv projekta:')
        projekt_naziv_ent = Entry(novi_pr_frame, width=30)
        kupac_lbl = Label(novi_pr_frame, text='Kupac:')
        kupac_ent = Entry(novi_pr_frame, width=30)
        lokacija_lbl = Label(novi_pr_frame, text='Lokacija:')
        lokacija_ent = Entry(novi_pr_frame, width=30)

        dodaj_projekt_btn = Button(novi_pr_frame, text='Dodaj')

        def novi_projekt_unos():
            """ INSERT novi projekt"""
            projekt_naziv = projekt_naziv_ent.get()
            kupac = kupac_ent.get()
            lokacija = lokacija_ent.get()

            # sprjecavanje nepotpunog unosa
            if projekt_naziv == '' or kupac == '':
                messagebox.showerror('Nepotpun unos', 'Popunite polja koja su prazna!', parent=self)
                return

            # unos novog zapisa u bazu
            baza.unesi_projekt(projekt_naziv, kupac, lokacija, 'a')

            # prikaz novog zapisa u treeviewu
            punjenje_projekti_tv(projekti_tv, baza.ucitaj_projekte())

            # ciscenje widgeta entryja
            projekt_naziv_ent.delete(0, END)
            kupac_ent.delete(0, END)
            lokacija_ent.delete(0, END)

            # dodavanje novog projekta u izborniku taba napomene
            projekti.clear()
            for red in baza.ucitaj_projekte():
                projekti.append(red[1])
            nap_projekt_ent.configure(values=projekti)
            tra_projekt_ent.configure(values=projekti)

        dodaj_projekt_btn.configure(command=novi_projekt_unos)

        # ----- raspored - Projekti - tab

        projekti_tv.grid(row=1, column=0, padx=3, pady=2, columnspan=7)
        promijeni_status_btn.grid(row=2, column=6, padx=3, pady=2)
        scrollbar_pro.grid(row=1, column=7, sticky='ns')

        # projekt_id_lbl.grid(row=2, column=0, padx=5, pady=2, sticky='w')
        # projekt_id_ent.grid(row=2, column=1, padx=3, pady=2)
        novi_pr_frame.grid(row=0, column=0, padx=3, pady=2)
        projekt_naziv_lbl.grid(row=0, column=0, padx=5, pady=2, sticky='w')
        projekt_naziv_ent.grid(row=0, column=1, padx=10, pady=2)
        kupac_lbl.grid(row=0, column=2, padx=5, pady=2, sticky='w')
        kupac_ent.grid(row=0, column=3, padx=10, pady=2)
        lokacija_lbl.grid(row=0, column=4, padx=5, pady=2, sticky='w')
        lokacija_ent.grid(row=0, column=5, padx=10, pady=2)
        dodaj_projekt_btn.grid(row=0, column=6, padx=3, pady=2)

        # ---------------- Napomene - tab
        def nap():
            """Ovisno o odabranom radio buttonu disable-a buttone koji nisu odabrani"""
            odabrano = vari.get()
            if odabrano == 4:
                nap_projekt_ent.configure(state='disabled')
                napomena_ent.configure(state='disabled')
                unesi_nap_btn.configure(state='disabled')

                tra_projekt_ent.configure(state='normal')
                trazi_nap_btn.configure(state='normal')
                izvjestaj_nap_btn.configure(state='normal')
            else:
                nap_projekt_ent.configure(state='normal')
                napomena_ent.configure(state='normal')
                unesi_nap_btn.configure(state='normal')

                tra_projekt_ent.configure(state='disabled')
                trazi_nap_btn.configure(state='disabled')
                izvjestaj_nap_btn.configure(state='disabled')

        vari = IntVar()
        nova_nap_rb = Radiobutton(napomene_tab, text="Nova napomena", variable=vari, value=3, command=nap)
        trazi_nap_rb = Radiobutton(napomene_tab, text="Pretraži", variable=vari, value=4, command=nap)
        nova_nap_rb.select()
        projekti = []

        for red in baza.ucitaj_projekte():
            projekti.append(red[0])

        unos_napomene_frame = Frame(napomene_tab)
        nap_projekti_lbl = Label(unos_napomene_frame, text='Projekt:')
        nap_projekt_ent_value = StringVar()
        nap_projekt_ent = AutocompleteCombobox(unos_napomene_frame, textvariable=nap_projekt_ent_value,
                                                               width=40)
        nap_projekt_ent.set_completion_list(projekti)
        napomena_lbl = Label(unos_napomene_frame, text='Napomena:')
        napomena_ent = ScrolledText(unos_napomene_frame, width=40, height=10, font=('Calibri', 10))
        unesi_nap_btn = Button(unos_napomene_frame, text='Unesi', width=10)

        def unos_napomene():
            projekt = nap_projekt_ent.get()
            napomena = napomena_ent.get("1.0", END)
            # sprjecavanje nepotpunog unosa
            if projekt == '' or napomena == '':
                messagebox.showerror('Nepotpun unos', 'Popunite polja koja su prazna!', parent=napomene_tab)
                return

            # unos napomene u bazu
            vrij = datetime.now()
            baza.unesi_napomenu(projekt, napomena, vrij)

            nap_projekt_ent.delete(0, END)
            napomena_ent.delete("1.0", END)

        unesi_nap_btn.configure(command=unos_napomene)

        pretraga_napomene_frame = Frame(napomene_tab)
        tra_projekti_lbl = Label(pretraga_napomene_frame, text='Projekt:')
        tra_projekt_ent_value = StringVar()
        tra_projekt_ent = AutocompleteCombobox(pretraga_napomene_frame, width=40,
                                                               textvariable=tra_projekt_ent_value, state='disabled')
        tra_projekt_ent.set_completion_list(projekti)
        trazi_nap_btn = Button(pretraga_napomene_frame, text='Traži', state='disabled', width=11)
        izvjestaj_nap_btn = Button(pretraga_napomene_frame, text='Izvještaj', state='disabled', width=11)

        napomene_tv = ttk.Treeview(pretraga_napomene_frame, column=("Vrijeme unosa", "Napomena"),
                                   show='headings', height=14)
        napomene_tv.column("#1", width=150, minwidth=40, stretch=YES)
        napomene_tv.column("#2", width=500, minwidth=40, stretch=YES)

        napomene_tv.heading("#1", text="Vrijeme unosa")
        napomene_tv.heading("#2", text="Napomena")

        scrollbar_nap = Scrollbar(pretraga_napomene_frame)
        napomene_tv.configure(yscrollcommand=scrollbar_nap.set)
        scrollbar_nap.configure(command=napomene_tv.yview)

        def trazi_napomene():
            """Funkcija za trazenje napomena prema projektima"""
            # stil_tv = ttk.Style() --> za promjenu visine reda treeviewa
            # stil_tv.configure("Treeview", rowheight=12*3)
            pro = tra_projekt_ent.get()
            print(pro)
            if pro == '':
                messagebox.showerror('Nepotpun unos', 'Odaberite projekt za pretraživanje!', parent=napomene_tab)
                return
            for vrs in napomene_tv.get_children():
                napomene_tv.delete(vrs)
            # punjenje treeviewa s podacima iz baze o projektima
            for red in baza.trazi_napomene(pro):
                print(red)
                napomene_tv.insert("", "end", "", values=(red[0][0:19], red[1]))

        def izvjestaj_napomene(tv):

            """Za uneseni treeview generira pdf izvjestaj s podacima iz treeviewa"""
            width, height = A4
            podaci = []
            stupci = tv.cget('column')
            nazivi_stupaca = []
            for stup in stupci:
                nazivi_stupaca.append(stup)
            podaci.append(nazivi_stupaca)
            for vrs in tv.get_children():
                red = tv.item(vrs)['values']
                podaci.append(red)

            f = filedialog.asksaveasfile(mode='w', defaultextension=".pdf", filetypes=[("PDF datoteka", ".pdf")],
                                         title='Spremi', initialfile='Izvještaj', parent=self)
            if f is None:  # asksaveasfile return `None` if dialog closed with "cancel".
                return
            mjesto_i_ime = f.name

            pdf = SimpleDocTemplate(mjesto_i_ime, pagesize=A4,
                                    rightMargin=72, leftMargin=72,
                                    topMargin=72, bottomMargin=18)
            tablica = Table(podaci, colWidths=[140, 350])
            stil = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.yellow), ('FONT', (0, 0), (-1, -1), 'Verdana')])

            tablica.setStyle(stil)
            pdfmetrics.registerFont(TTFont('Verdana', 'Verdana.ttf'))
            broj_redova = len(podaci)

            for i in range(1, broj_redova):
                if i % 2 == 0:
                    pozadina_reda = colors.beige
                    ts = TableStyle([('BACKGROUND', (0, i), (-1, i), pozadina_reda)])
                    tablica.setStyle(ts)

            stil = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.yellow)
            ])

            tablica.setStyle(stil)
            elementi_pdfa = []
            elementi_pdfa.append(Spacer(1, 12))

            elementi_pdfa.append(tablica)
            elementi_pdfa.append(Spacer(1, 12))

            def zaglavlje(canvas, doc):
                canvas.saveState()
                # logo i datum se prikazuju u zaglavlju
                datum = datetime.today()
                logo_naziv = 'modeco_logo1x.png'
                canvas.drawImage(logo_naziv, 0.7*width, 0.95*height, 85, 20)
                canvas.setFont('Times-Bold', 11)
                canvas.drawString(0.1*width, 0.95*height, str('Datum izvještaja:' + datetime.strftime(datum, "%m-%d-%Y")))
                canvas.setFont('Times-Roman', 11)
                # broj stranice u desnom dnu svake stranice
                page_num = str(canvas._pageNumber)
                canvas.drawString(0.9 * width, 0.5 * inch, page_num)
                canvas.restoreState()

            pdf.build(elementi_pdfa,  onFirstPage=zaglavlje, onLaterPages=zaglavlje)
            os.startfile(mjesto_i_ime)

        trazi_nap_btn.configure(command=trazi_napomene)
        izvjestaj_nap_btn.configure(command=lambda: izvjestaj_napomene(napomene_tv))

        # raspored - Napomene - tab
        nova_nap_rb.grid(row=0, column=0, padx=3, pady=2, sticky='w')
        unos_napomene_frame.grid(row=1, column=0, sticky='n', padx=10)
        nap_projekti_lbl.grid(row=0, column=0, padx=3, pady=2, sticky='w')
        nap_projekt_ent.grid(row=0, column=1, padx=3, pady=2, sticky='w')
        napomena_lbl.grid(row=1, column=0, padx=3, pady=2, sticky='w')
        napomena_ent.grid(row=1, column=1, padx=3, pady=2)
        unesi_nap_btn.grid(row=2, column=1, padx=3, pady=2, sticky='e')

        trazi_nap_rb.grid(row=0, column=1, padx=3, pady=2, sticky='w')
        pretraga_napomene_frame.grid(row=1, column=1)
        tra_projekti_lbl.grid(row=0, column=0, padx=3, pady=2)
        tra_projekt_ent.grid(row=0, column=1, padx=3, pady=2)
        trazi_nap_btn.grid(row=0, column=2, padx=3, pady=2)
        izvjestaj_nap_btn.grid(row=0, column=3, padx=3, pady=2)
        napomene_tv.grid(row=3, column=0, padx=3, pady=2, columnspan=4)
        scrollbar_nap.grid(row=3, column=4, sticky='nse')

        # raspored
        pro_lbl.grid(row=0, column=0, sticky='ew')
        tab_parent1.grid(row=1, column=0, padx=10, pady=10)


class PageRadnici(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        """ Stranica za rad s podacima o radnicima"""

        # prozor sadrzi 2 taba: unos novih radnika i obracun sati
        rad_lbl = Label(self, text='Radnici', font=('Arial', 24), bg='#FFFF00')
        glavni_frame = Frame(self)

        radnici_tab = LabelFrame(glavni_frame, text='Radnici')

        radnici_tv = ttk.Treeview(radnici_tab, column=("column1", "column2", "column3"),
                                  show='headings', height=16)
        radnici_tv.column("#1", width=200, minwidth=40)
        radnici_tv.column("#2", width=80, minwidth=40)
        radnici_tv.column("#3", width=80, minwidth=40)

        radnici_tv.heading("#1", text="Ime i prezime")
        radnici_tv.heading("#2", text="Plaća, kn/h")
        radnici_tv.heading("#3", text="Status")

        scrollbar_pro = Scrollbar(radnici_tab)
        radnici_tv.configure(yscrollcommand=scrollbar_pro.set)
        scrollbar_pro.configure(command=radnici_tv.yview)

        punjenje_radnici_tv(radnici_tv, baza.ucitaj_radnike())

        promijeni_status_btn = Button(radnici_tab, text='Promijeni status')

        def promijeni_status():
            """Funkcija za promjenu statusa radnika iz a u z i obrnuto"""
            odabrani_item = radnici_tv.selection()[0]  # rad s oznacenim redom u Treeviewu
            vrijednosti_itema = tuple(
                radnici_tv.item(odabrani_item)['values'])  # tuple sa vrijednostima odabranog reda
            # print(vrijednosti_itema)
            id_radnika = baza.id_radnika(vrijednosti_itema[0])[0]
            status_radnika = vrijednosti_itema[2]

            if status_radnika == 'Zaposlen':
                baza.promjeni_status_radnika(id_radnika, 'z')
            else:
                baza.promjeni_status_radnika(id_radnika, 'a')

            punjenje_radnici_tv(radnici_tv, baza.ucitaj_radnike())

        promijeni_status_btn.configure(command=promijeni_status)

        novi_radnik_frame = Frame(radnici_tab)
        radnik_im_pr_lbl = Label(novi_radnik_frame, text='Ime i prezime:')
        radnik_im_pr_ent = Entry(novi_radnik_frame, width=22)
        placa_lbl = Label(novi_radnik_frame, text='Plaća kn/h:')
        placa_ent = Entry(novi_radnik_frame, width=22)

        dodaj_radnika_btn = Button(novi_radnik_frame, text='Dodaj', width=15)

        def novi_radnik_unos():
            """ INSERT novi radnik"""
            radnik_im_pr = radnik_im_pr_ent.get()
            placa = placa_ent.get()

            # sprjecavanje nepotpunog unosa
            if radnik_im_pr == '' or placa == '':
                messagebox.showerror('Nepotpun unos', 'Popunite polja koja su prazna!', parent=self)
                return

            # unos novog zapisa u bazu
            baza.unesi_radnika(radnik_im_pr, float(placa), 'a')

            # prikaz novog zapisa u treeviewu
            punjenje_radnici_tv(radnici_tv, baza.ucitaj_radnike())

            # ciscenje widgeta entryja
            radnik_im_pr_ent.delete(0, END)
            placa_ent.delete(0, END)

        dodaj_radnika_btn.configure(command=novi_radnik_unos)

        # ----- raspored - radnici_tab
        novi_radnik_frame.grid(row=0, column=0, padx=3, pady=2, columnspan=3, sticky='w')
        radnik_im_pr_lbl.grid(row=0, column=0, padx=5, pady=2, sticky='w')
        radnik_im_pr_ent.grid(row=0, column=1, padx=3, pady=2)
        placa_lbl.grid(row=1, column=0, padx=5, pady=2, sticky='w')
        placa_ent.grid(row=1, column=1, padx=3, pady=2)
        dodaj_radnika_btn.grid(row=2, column=1, padx=3, pady=2)

        radnici_tv.grid(row=1, column=0, padx=3, pady=2, columnspan=3)
        promijeni_status_btn.grid(row=2, column=2, padx=3, pady=3, sticky='e')
        scrollbar_pro.grid(row=1, column=3, sticky='nse')

        # ------------------- sati_tab
        sati_tab = LabelFrame(glavni_frame, text='Odrađeni sati')
        datum_lbl = Label(sati_tab, text='Datum:')
        crtica_lbl = Label(sati_tab, text='-')
        od_ent = DateEntry(sati_tab, width=15, background='darkblue', foreground='white',
                           borderwidth=2, date_pattern='dd-MM-yyyy', showweeknumbers=True)
        do_ent = DateEntry(sati_tab, width=15, background='darkblue', foreground='white',
                           borderwidth=2, date_pattern='dd-MM-yyyy', showweeknumbers=True)
        trazi_btn = Button(sati_tab, text='Pretraži', width=12)
        izvjestaj_btn = Button(sati_tab, text='Izvještaj', width=12)

        po_projektima_lbl = Label(sati_tab, text='Ukupno')
        pro_tv = ttk.Treeview(sati_tab, column=("column1", "column2", "column3", "column4"),
                              show='headings', height=19)
        pro_tv.column("#1", width=150, minwidth=40)
        pro_tv.column("#2", width=180, minwidth=40)
        pro_tv.column("#3", width=150, minwidth=40)
        pro_tv.column("#4", width=150, minwidth=40)

        pro_tv.heading("#1", text="Radnik")
        pro_tv.heading("#2", text="Projekt")
        pro_tv.heading("#3", text="Broj sati")
        pro_tv.heading("#4", text="Iznos")

        scrollbar_pr = Scrollbar(sati_tab)
        pro_tv.configure(yscrollcommand=scrollbar_pr.set)
        scrollbar_pr.configure(command=pro_tv.yview)

        lista_radnik_sati = []

        def broj_sati_radnika():
            """Funkcija koja iz baze obračunava broj odrađenih sati za odabrani period"""
            for vrs in pro_tv.get_children():
                pro_tv.delete(vrs)
            od = od_ent.get_date()
            do = do_ent.get_date()
            # print(baza.projekti_u_periodu(od, do))

            brojac_radnika = 1

            for red in baza.radnik_i_placa():

                radnik_id = red[0]
                placa = float(red[1])
                br_sati_uk = 0
                trosak_uk = 0
                radnikk = ''
                boja = ''

                for projekt in baza.projekti_u_periodu(od, do):
                    radnik_sati_pro = baza.obracun_sati_radnika_po_pro(od, do, radnik_id, projekt[0])[0]
                    if radnik_sati_pro[0] != None:
                        projektt = radnik_sati_pro[0]
                        radnik = radnik_sati_pro[1]
                        br_sati = radnik_sati_pro[2]
                        trosak = float(br_sati) * placa
                        br_sati_uk += br_sati
                        trosak_uk += trosak
                        radnikk = radnik
                        if radnikk != '':
                            # boja pozadine reda
                            if brojac_radnika % 2 == 0:
                                boja = 'p'
                            else:
                                boja = 'i'
                        pro_tv.insert("", "0", "", values=('', projektt, br_sati, str("%.2f" % round(trosak, 2))),
                                      tag=boja)

                if radnikk != '':
                    brojac_radnika += 1
                    pro_tv.insert("", "0", "", values=(radnikk, '', str("%.2f" % round(br_sati_uk, 2)),
                                                       str("%.2f" % round(trosak_uk, 2))), tag=boja)
                    lista_radnik_sati.append([radnikk, str("%.2f" % round(br_sati_uk, 2)),
                                                           str("%.2f" % round(trosak_uk, 2))])
                    pro_tv.tag_configure('p', foreground="#33270d", background="#faf766")  # , background="#3FE872"
                    pro_tv.tag_configure('i', foreground="#33270d", background="#FFFFFF")

        def izvjestaj_br_sati():
            """ pdf izvjestaj u kojem je izlistan broj sati svih radnika za odabrani period"""
            f = filedialog.asksaveasfile(mode='w', defaultextension=".pdf", filetypes=[("PDF datoteka", ".pdf")],
                                         title='Spremi', initialfile='Izvještaj', parent=self)
            mjesto_i_ime = f.name

            pdf = SimpleDocTemplate(mjesto_i_ime, pagesize=A4,
                                    rightMargin=72, leftMargin=72,
                                    topMargin=72, bottomMargin=60)
            if f is None:  # asksaveasfile return `None` if dialog closed with "cancel".
                return
            elementi_pdfa = []

            """Za uneseni treeview generira pdf izvjestaj s podacima iz treeviewa"""
            width, height = A4

            podaci = lista_radnik_sati
            podaci_naslovi = ['Radnik', 'Broj sati', 'Iznos']
            podaci.insert(0, podaci_naslovi)
            print(podaci)
            tablica = Table(podaci, colWidths=[290, 100, 100])  # za svaki stupac upisati njegovu širinu
            pdfmetrics.registerFont(TTFont('Verdana', 'Verdana.ttf'))

            stil = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.yellow),
                ('FONT', (0, 0), (-1, -1), 'Verdana')])

            tablica.setStyle(stil)
            elementi_pdfa.append(Spacer(1, 12))
            elementi_pdfa.append(tablica)
            elementi_pdfa.append(Spacer(1, 12))

            def zaglavlje(canvas, doc):
                canvas.saveState()
                # logo i datum se prikazuju u zaglavlju
                datum = datetime.today()
                logo_naziv = 'modeco_logo1x.png'
                canvas.drawImage(logo_naziv, 0.7 * width, 0.95 * height, 85, 20)
                canvas.setFont('Verdana', 11)
                canvas.drawString(0.1 * width, 0.95 * height,
                                  str('Datum izvještaja:' + datetime.strftime(datum, "%m-%d-%Y")))
                canvas.drawString(0.1 * width, 0.93 * height,
                                  str('Obračun sati za period: ' + od_ent.get() + ' - ' + do_ent.get()))
                canvas.setFont('Times-Roman', 11)
                # broj stranice u desnom dnu svake stranice
                page_num = str(canvas._pageNumber)
                canvas.drawString(0.9 * width, 0.5 * inch, page_num)
                canvas.restoreState()

            pdf.build(elementi_pdfa, onFirstPage=zaglavlje, onLaterPages=zaglavlje)
            os.startfile(mjesto_i_ime)

        trazi_btn.configure(command=broj_sati_radnika)
        izvjestaj_btn.configure(command=izvjestaj_br_sati)

        radnici_tab.grid(row=0, column=0, padx=15, pady=5)
        sati_tab.grid(row=0, column=1, padx=15, pady=5)
        # ---------------- raspored sati_tab
        datum_lbl.grid(row=0, column=0)
        od_ent.grid(row=0, column=1)
        crtica_lbl.grid(row=0, column=2)
        do_ent.grid(row=0, column=3)
        trazi_btn.grid(row=0, column=4, padx=5)
        izvjestaj_btn.grid(row=0, column=5, padx=5)
        po_projektima_lbl.grid(row=1, column=0, columnspan=4)
        pro_tv.grid(row=2, column=0, columnspan=5, pady=5, padx=5)
        scrollbar_pr.grid(row=2, column=5, sticky='nsw')

        # raspored
        rad_lbl.grid(row=0, column=0, sticky='ew')
        glavni_frame.grid(row=1, column=0, sticky='ew')


class PageSpojni(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        """ Stranica za rad s podacima o spojnim elementima"""

        se_lbl = Label(self, text='Spojni elementi', font=('Arial', 24), bg='#FFFF00')
        glavni_frame = Frame(self)

        se_tv = ttk.Treeview(glavni_frame, column=("column1", "column2", "column3"),
                             show='headings', height=17)
        se_tv.column("#1", width=450, minwidth=40)
        se_tv.column("#2", width=200, minwidth=40)
        se_tv.column("#3", width=150, minwidth=40)

        se_tv.heading("#1", text="Naziv")
        se_tv.heading("#2", text="Cijena kn/JM")
        se_tv.heading("#3", text="JM")

        scrollbar_pro = Scrollbar(glavni_frame)
        se_tv.configure(yscrollcommand=scrollbar_pro.set)
        scrollbar_pro.configure(command=se_tv.yview)

        punjenje_tv(se_tv, baza.ucitaj_se())

        se_naziv_lbl = Label(glavni_frame, text='Naziv:')
        se_naziv_ent = Entry(glavni_frame, width=38)
        se_cijena_lbl = Label(glavni_frame, text='Cijena kn/JM:')
        se_cijena_ent = Entry(glavni_frame, width=38)
        se_jm_lbl = Label(glavni_frame, text='JM:')
        se_jm_ent = Entry(glavni_frame, width=38)

        pro_gumbovi_frame = Frame(glavni_frame)
        dodaj_se_btn = Button(pro_gumbovi_frame, text='Dodaj', width=15)

        def novi_se_unos():
            """ INSERT novi spojni element"""
            se_naziv = se_naziv_ent.get()
            se_cijena = se_cijena_ent.get()
            se_jm = se_jm_ent.get()

            # sprjecavanje nepotpunog unosa
            if se_naziv == '' or se_cijena == '' or se_jm == '':
                messagebox.showerror('Nepotpun unos', 'Popunite polja koja su prazna!', parent=self)
                return

            # unos novog zapisa u bazu
            baza.unesi_se(se_naziv, float(se_cijena), se_jm)

            # prikaz novog zapisa u treeviewu
            punjenje_tv(se_tv, baza.ucitaj_se())

            # ciscenje widgeta entryja
            se_naziv_ent.delete(0, END)
            se_cijena_ent.delete(0, END)
            se_jm_ent.delete(0, END)

        dodaj_se_btn.configure(command=novi_se_unos)

        # ----- raspored - glavni_frame
        se_naziv_lbl.grid(row=1, column=0, padx=5, pady=2, sticky='w')
        se_naziv_ent.grid(row=1, column=1, pady=2, sticky='w')
        se_cijena_lbl.grid(row=2, column=0, padx=5, pady=2, sticky='w')
        se_cijena_ent.grid(row=2, column=1, pady=2, sticky='w')
        se_jm_lbl.grid(row=3, column=0, padx=3, pady=2, sticky='w')
        se_jm_ent.grid(row=3, column=1, pady=2, sticky='w')

        pro_gumbovi_frame.grid(row=4, column=1, padx=3, pady=2)
        dodaj_se_btn.grid(row=0, column=0, padx=3, pady=2)

        se_tv.grid(row=5, column=0, padx=3, pady=2, columnspan=4)
        scrollbar_pro.grid(row=5, column=4, sticky='ns')

        # raspored
        se_lbl.grid(row=0, column=0, sticky='ew')
        glavni_frame.grid(row=1, column=0, sticky='ew', padx=20, pady=5)


class PageStavke(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        """ Stranica za rad s podacima o stavkama montaze"""

        stavke_lbl = Label(self, text='Stavke montaže', font=('Arial', 24), bg='#FFFF00')
        glavni_frame = Frame(self)

        stavke_tv = ttk.Treeview(glavni_frame, column=("column1", "column2", "column3"),
                                 show='headings', height=15)
        stavke_tv.column("#1", width=450, minwidth=40)
        stavke_tv.column("#2", width=200, minwidth=40)
        stavke_tv.column("#3", width=150, minwidth=40)

        stavke_tv.heading("#1", text="Naziv stavke")
        stavke_tv.heading("#2", text="Cijena kn/JM")
        stavke_tv.heading("#3", text="JM")

        scrollbar_pro = Scrollbar(glavni_frame)
        stavke_tv.configure(yscrollcommand=scrollbar_pro.set)
        scrollbar_pro.configure(command=stavke_tv.yview)

        punjenje_tv(stavke_tv, baza.ucitaj_stavke())

        stavka_naziv_lbl = Label(glavni_frame, text='Naziv:')
        stavka_naziv_ent = Entry(glavni_frame, width=110)  # , height=4, font=('Calibri', 10))
        stavka_cijena_lbl = Label(glavni_frame, text='Cijena kn/JM:')
        stavka_cijena_ent = Entry(glavni_frame, width=38)
        stavka_jm_lbl = Label(glavni_frame, text='JM:')
        stavka_jm_ent = Entry(glavni_frame, width=38)

        pro_gumbovi_frame = Frame(glavni_frame)
        dodaj_stavku_btn = Button(pro_gumbovi_frame, text='Dodaj', width=15)

        def novi_se_unos():
            """ INSERT novi radnik"""
            stavka_naziv = stavka_naziv_ent.get()
            stavka_cijena = stavka_cijena_ent.get()
            stavka_jm = stavka_jm_ent.get()

            # sprjecavanje nepotpunog unosa
            if stavka_naziv == '' or stavka_cijena == '' or stavka_jm == '':
                messagebox.showerror('Nepotpun unos', 'Popunite polja koja su prazna!', parent=self)
                return

            # unos novog zapisa u bazu
            baza.unesi_stavku(stavka_naziv, float(stavka_cijena), stavka_jm)

            # prikaz novog zapisa u treeviewu
            punjenje_tv(stavke_tv, baza.ucitaj_stavke())

            # ciscenje widgeta entryja
            stavka_naziv_ent.delete(0, END)
            stavka_cijena_ent.delete(0, END)
            stavka_jm_ent.delete(0, END)

        dodaj_stavku_btn.configure(command=novi_se_unos)

        # ----- raspored - glavni_frame
        stavka_naziv_lbl.grid(row=1, column=0, padx=5, pady=2, sticky='nw')
        stavka_naziv_ent.grid(row=1, column=1, pady=2, sticky='w', columnspan=4)
        stavka_cijena_lbl.grid(row=2, column=0, padx=5, pady=2, sticky='w')
        stavka_cijena_ent.grid(row=2, column=1, pady=2, sticky='w')
        stavka_jm_lbl.grid(row=2, column=2, padx=3, pady=2)
        stavka_jm_ent.grid(row=2, column=3, pady=2, sticky='e')

        pro_gumbovi_frame.grid(row=4, column=3, padx=3, pady=2)
        dodaj_stavku_btn.grid(row=0, column=0, padx=3, pady=2)

        stavke_tv.grid(row=5, column=0, padx=3, pady=2, columnspan=4)
        scrollbar_pro.grid(row=5, column=4, sticky='ns')

        # raspored
        stavke_lbl.grid(row=0, column=0, sticky='ew')
        glavni_frame.grid(row=1, column=0, sticky='ew', padx=20, pady=5)


class PageStrojevi(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        """ Stranica za rad s podacima o strojevima"""

        strojevi_lbl = Label(self, text='Strojevi', font=('Arial', 24), bg='#FFFF00')
        glavni_frame = Frame(self)

        strojevi_tv = ttk.Treeview(glavni_frame, column=("column1", "column2", "column3"),
                                   show='headings', height=17)
        strojevi_tv.column("#1", width=450, minwidth=40)
        strojevi_tv.column("#2", width=200, minwidth=40)
        strojevi_tv.column("#3", width=150, minwidth=40)

        strojevi_tv.heading("#1", text="Naziv stroja")
        strojevi_tv.heading("#2", text="Cijena kn/JM")
        strojevi_tv.heading("#3", text="JM")

        scrollbar_pro = Scrollbar(glavni_frame)
        strojevi_tv.configure(yscrollcommand=scrollbar_pro.set)
        scrollbar_pro.configure(command=strojevi_tv.yview)

        punjenje_tv(strojevi_tv, baza.ucitaj_strojeve())

        stroj_naziv_lbl = Label(glavni_frame, text='Naziv:')
        stroj_naziv_ent = Entry(glavni_frame, width=38)
        stroj_cijena_lbl = Label(glavni_frame, text='Cijena kn/JM:')
        stroj_cijena_ent = Entry(glavni_frame, width=38)
        stroj_jm_lbl = Label(glavni_frame, text='JM:')
        stroj_jm_ent = Entry(glavni_frame, width=38)

        pro_gumbovi_frame = Frame(glavni_frame)
        dodaj_stroj_btn = Button(pro_gumbovi_frame, text='Dodaj', width=15)

        def novi_stroj_unos():
            """ INSERT novi stroj"""
            stroj_naziv = stroj_naziv_ent.get()
            stroj_cijena = stroj_cijena_ent.get()
            stroj_jm = stroj_jm_ent.get()

            # sprjecavanje nepotpunog unosa
            if stroj_naziv == '' or stroj_cijena == '' or stroj_jm == '':
                messagebox.showerror('Nepotpun unos', 'Popunite polja koja su prazna!', parent=self)
                return

            # unos novog zapisa u bazu
            baza.unesi_stroj(stroj_naziv, stroj_jm, float(stroj_cijena))

            # prikaz novog zapisa u treeviewu
            punjenje_tv(strojevi_tv, baza.ucitaj_strojeve())

            # ciscenje widgeta entryja
            stroj_naziv_ent.delete(0, END)
            stroj_cijena_ent.delete(0, END)
            stroj_jm_ent.delete(0, END)

        dodaj_stroj_btn.configure(command=novi_stroj_unos)

        # ----- raspored - glavni_frame
        stroj_naziv_lbl.grid(row=1, column=0, padx=5, pady=2, sticky='w')
        stroj_naziv_ent.grid(row=1, column=1, pady=2, sticky='w')
        stroj_cijena_lbl.grid(row=2, column=0, padx=5, pady=2, sticky='w')
        stroj_cijena_ent.grid(row=2, column=1, pady=2, sticky='w')
        stroj_jm_lbl.grid(row=3, column=0, padx=3, pady=2, sticky='w')
        stroj_jm_ent.grid(row=3, column=1, pady=2, sticky='w')

        pro_gumbovi_frame.grid(row=4, column=1, padx=3, pady=2)
        dodaj_stroj_btn.grid(row=0, column=0, padx=3, pady=2)

        strojevi_tv.grid(row=5, column=0, padx=3, pady=2, columnspan=4)
        scrollbar_pro.grid(row=5, column=4, sticky='ns')

        # raspored
        strojevi_lbl.grid(row=0, column=0, sticky='ew')
        glavni_frame.grid(row=1, column=0, sticky='ew', padx=20, pady=5)


class PageUnosTroskova(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        """ Stranica za unos troskova u bazu - PROBA"""
        container = ttk.Frame(self)
        canvas = Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        glavni_frame = ttk.Frame(canvas)
        glavni_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"), width=1100, height=500))
        canvas.create_window((0, 0), window=glavni_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        container.grid(row=2, column=0, columnspan=4)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        unos_troskova_lbl = Label(self, text='Unos troškova', font=('Arial', 24), bg='#FFFF00')
        pro_frame = Frame(self)
        projekt_lbl = Label(pro_frame, text='Projekt:')
        projekti_lista = []

        def aktivni_projekti():
            # upit na bazu da se povuku svi projekti koji su uneseni kako bi se mogli prikazati u comboboxu
            for red in baza.ucitaj_aktivne_projekte():
                projekti_lista.append(red[0])

        def combo_post_command_projekti():
            projekti_lista.clear()
            aktivni_projekti()
            projekt_ent.configure(values=projekti_lista)

        projekti_ent_value = StringVar()
        projekt_ent = AutocompleteCombobox(pro_frame, textvariable=projekti_ent_value,
                                                           postcommand=combo_post_command_projekti, width=40)
        projekt_ent.set_completion_list(projekti_lista)
        datum_lbl = Label(pro_frame, text='Datum:')
        datum_ent = DateEntry(pro_frame, width=15, background='darkblue', foreground='white',
                              borderwidth=2, date_pattern='dd-MM-yyyy', showweeknumbers=True)

        unos_troskova_lbl.grid(row=0, column=0, sticky='ew', columnspan=4)
        pro_frame.grid(row=1, column=0, sticky='ew', columnspan=4, padx=5, pady=3)
        projekt_lbl.grid(row=0, column=0, padx=5, pady=3)
        projekt_ent.grid(row=0, column=1, padx=5, pady=3)
        datum_lbl.grid(row=0, column=2, padx=5, pady=3)
        datum_ent.grid(row=0, column=3, padx=5, pady=3)

        # ---------- unos troskova radnika - radnici _lbl_fr
        radnici_lbl_fr = LabelFrame(glavni_frame, text='Radnici')
        radnici_lbl = Label(radnici_lbl_fr, text='Radnik:')
        radnici_lista = []

        def zaposleni_radnici():
            # upit na bazu da se povuku svi projekti koji su uneseni kako bi se mogli prikazati u comboboxu
            for red in baza.ucitaj_zaposlene_radnike():
                radnici_lista.append(red[0])

        def combo_post_command_radnici():
            radnici_lista.clear()
            zaposleni_radnici()
            radnici_ent.configure(values=radnici_lista)

        radnici_ent_value = StringVar()
        radnici_ent = AutocompleteCombobox(radnici_lbl_fr, textvariable=radnici_ent_value,
                                                           postcommand=combo_post_command_radnici, width=30)
        radnici_ent.set_completion_list(radnici_lista)

        br_sati_lbl = Label(radnici_lbl_fr, text='Broj sati:')
        br_sati_ent = Entry(radnici_lbl_fr, width=33)
        unesi_radnika_btn = Button(radnici_lbl_fr, text='Unesi', width=12)
        obrisi_radnika_btn = Button(radnici_lbl_fr, text='Obriši', width=12)

        radnici_tv = ttk.Treeview(radnici_lbl_fr, column=("column1", "column2"),
                                  show='headings', height=8)
        radnici_tv.column("#1", width=450, minwidth=40)
        radnici_tv.column("#2", width=120, minwidth=40)

        radnici_tv.heading("#1", text="Radnik")
        radnici_tv.heading("#2", text="Broj sati")

        def unesi_radnika():
            radnik = radnici_ent.get()
            br_sati = br_sati_ent.get()

            radnici_tv.insert("", "end", "", values=(radnik, br_sati))

            radnici_ent.delete(0, END)
            br_sati_ent.delete(0, END)

        def obrisi_radnika():
            odabrani_item = radnici_tv.selection()[0]  # rad s oznacenim redom u Treeviewu
            if odabrani_item != None:
                radnici_tv.delete(odabrani_item)
            else:
                messagebox.showerror('Nepotpun odabir', 'Odaberi radnika!', parent=self)
                return

        unesi_radnika_btn.configure(command=unesi_radnika)
        obrisi_radnika_btn.configure(command=obrisi_radnika)

        scrollbar_rad = Scrollbar(radnici_lbl_fr)
        radnici_tv.configure(yscrollcommand=scrollbar_rad.set)
        scrollbar_rad.configure(command=radnici_tv.yview)

        radnici_lbl_fr.grid(row=1, column=0, padx=10, pady=5)
        #                                                           radnici_lbl_fr - RASPORED
        radnici_lbl.grid(row=0, column=0, padx=5, pady=1)
        radnici_ent.grid(row=0, column=1, padx=5, pady=1, sticky='w')
        br_sati_lbl.grid(row=1, column=0, padx=5, pady=1)
        br_sati_ent.grid(row=1, column=1, padx=5, pady=1, sticky='w')
        radnici_tv.grid(row=0, column=2, rowspan=60, padx=5, pady=3)
        scrollbar_rad.grid(row=0, column=4, sticky='nse', rowspan=60, padx=2)
        unesi_radnika_btn.grid(row=2, column=1, sticky='e', pady=1, padx=5)
        obrisi_radnika_btn.grid(row=3, column=1, sticky='e', pady=1, padx=5)

        # ---------- unos terenskih troskova - terenski_lbl_fr
        terenski_lbl_fr = LabelFrame(glavni_frame, text='Terenski troškovi')
        ruc_lbl = Label(terenski_lbl_fr, text='Ručak')
        rucak_ent = Entry(terenski_lbl_fr, width=22)
        spa_lbl = Label(terenski_lbl_fr, text='Spavanje')
        spa_ent = Entry(terenski_lbl_fr, width=22)
        ter_dod_lbl = Label(terenski_lbl_fr, text='Terenski dodatak')
        ter_dod_ent = Entry(terenski_lbl_fr, width=22)
        cest_lbl = Label(terenski_lbl_fr, text='Cestarina')
        cest_ent = Entry(terenski_lbl_fr, width=22)
        gor_lbl = Label(terenski_lbl_fr, text='Gorivo')
        gor_ent = Entry(terenski_lbl_fr, width=22)

        unesi_ter_btn = Button(terenski_lbl_fr, text='Unesi', width=12)
        promijeni_ter_btn = Button(terenski_lbl_fr, text='Promjeni', width=12)

        def unesi_ter():
            rucak_ent.configure(state='disabled')
            spa_ent.configure(state='disabled')
            ter_dod_ent.configure(state='disabled')
            cest_ent.configure(state='disabled')
            gor_ent.configure(state='disabled')

        def promijeni_ter():
            rucak_ent.configure(state='normal')
            spa_ent.configure(state='normal')
            ter_dod_ent.configure(state='normal')
            cest_ent.configure(state='normal')
            gor_ent.configure(state='normal')

        unesi_ter_btn.configure(command=unesi_ter)
        promijeni_ter_btn.configure(command=promijeni_ter)

        terenski_lbl_fr.grid(row=2, column=0, columnspan=4, padx=10, pady=5)
        #                                                           terenski_lbl_fr - RASPORED
        ruc_lbl.grid(row=0, column=0, sticky='w', padx=20)
        rucak_ent.grid(row=0, column=1, sticky='e')
        spa_lbl.grid(row=0, column=2, sticky='w', padx=20)
        spa_ent.grid(row=0, column=3, sticky='e')
        gor_lbl.grid(row=0, column=4, sticky='w', padx=20)
        gor_ent.grid(row=0, column=5, sticky='e')
        ter_dod_lbl.grid(row=1, column=0, sticky='w', padx=20)
        ter_dod_ent.grid(row=1, column=1, sticky='e')
        cest_lbl.grid(row=1, column=2, sticky='w', padx=20)
        cest_ent.grid(row=1, column=3, sticky='w')

        unesi_ter_btn.grid(row=2, column=2, pady=5)
        promijeni_ter_btn.grid(row=2, column=3, pady=5)

        # ---------- unos troskova strojeva - strojevi_lbl_fr
        strojevi_lbl_fr = LabelFrame(glavni_frame, text='Strojevi')
        strojevi_lbl = Label(strojevi_lbl_fr, text='Stroj:')
        strojevi_lista = []

        def strojevi():
            # upit na bazu da se povuku svi projekti koji su uneseni kako bi se mogli prikazati u comboboxu
            for red in baza.ucitaj_strojeve():
                strojevi_lista.append(red[0])

        def combo_post_command_strojevi():
            strojevi_lista.clear()
            strojevi()
            strojevi_ent.configure(values=strojevi_lista)

        strojevi_ent_value = StringVar()
        strojevi_ent = AutocompleteCombobox(strojevi_lbl_fr, textvariable=strojevi_ent_value,
                                                            postcommand=combo_post_command_strojevi, width=30)
        strojevi_ent.set_completion_list(strojevi_lista)

        def callback(obj):
            jm_str_ent.configure(state='normal')
            jm_str_ent.delete(0, END)
            jm = baza.jm_stroja(strojevi_ent.get())
            jm_str_ent.insert(0, jm)
            jm_str_ent.configure(state='disabled')

        strojevi_ent.bind("<<ComboboxSelected>>", callback)

        jm_str_lbl = Label(strojevi_lbl_fr, text='JM:')
        jm_str_ent = Entry(strojevi_lbl_fr, width=33)
        iznos_str_lbl = Label(strojevi_lbl_fr, text='Iznos:')
        iznos_str_ent = Entry(strojevi_lbl_fr, width=33)
        unesi_stroj_btn = Button(strojevi_lbl_fr, text='Unesi', width=12)
        obrisi_stroj_btn = Button(strojevi_lbl_fr, text='Obriši', width=12)

        strojevi_tv = ttk.Treeview(strojevi_lbl_fr, column=("column1", "column2", "column3"),
                                   show='headings', height=8)
        strojevi_tv.column("#1", width=270, minwidth=40)
        strojevi_tv.column("#2", width=150, minwidth=40)
        strojevi_tv.column("#3", width=150, minwidth=40)

        strojevi_tv.heading("#1", text="Stroj")
        strojevi_tv.heading("#2", text="JM")
        strojevi_tv.heading("#3", text="Iznos")

        def unesi_str():
            stroj = strojevi_ent.get()
            jm_str = jm_str_ent.get()
            iznos_str = iznos_str_ent.get()

            strojevi_tv.insert("", "end", "", values=(stroj, jm_str, iznos_str))

            strojevi_ent.delete(0, END)
            jm_str_ent.delete(0, END)
            iznos_str_ent.delete(0, END)

        def obrisi_str():
            odabrani_item = strojevi_tv.selection()[0]  # rad s oznacenim redom u Treeviewu
            if odabrani_item != None:
                strojevi_tv.delete(odabrani_item)
            else:
                messagebox.showerror('Nepotpun odabir', 'Odaberi stroj!', parent=self)
                return

        unesi_stroj_btn.configure(command=unesi_str)
        obrisi_stroj_btn.configure(command=obrisi_str)

        scrollbar_str = Scrollbar(strojevi_lbl_fr)
        strojevi_tv.configure(yscrollcommand=scrollbar_str.set)
        scrollbar_str.configure(command=strojevi_tv.yview)

        strojevi_lbl_fr.grid(row=3, column=0, columnspan=4, padx=10, pady=5)
        #                                                           strojevi_lbl_fr - RASPORED
        strojevi_lbl.grid(row=0, column=0, padx=5, pady=1)
        strojevi_ent.grid(row=0, column=1, padx=5, pady=1, sticky='w')
        jm_str_lbl.grid(row=1, column=0, padx=5, pady=1)
        jm_str_ent.grid(row=1, column=1, padx=5, pady=1, sticky='w')
        iznos_str_lbl.grid(row=2, column=0, padx=5, pady=1)
        iznos_str_ent.grid(row=2, column=1, padx=5, pady=1, sticky='w')
        strojevi_tv.grid(row=0, column=2, rowspan=10, padx=5, pady=3)
        scrollbar_str.grid(row=0, column=4, sticky='nse', rowspan=10, padx=2)
        unesi_stroj_btn.grid(row=3, column=1, sticky='e', pady=1, padx=5)
        obrisi_stroj_btn.grid(row=4, column=1, sticky='e', pady=1, padx=5)

        # ---------- unos troskova sponih elemenata - se_lbl_fr
        se_lbl_fr = LabelFrame(glavni_frame, text='Spojni elementi')
        se_lbl = Label(se_lbl_fr, text='Spojni element:')
        se_lista = []

        def se():
            # upit na bazu da se povuku svi projekti koji su uneseni kako bi se mogli prikazati u comboboxu
            for red in baza.ucitaj_se():
                se_lista.append(red[0])

        def combo_post_command_se():
            se_lista.clear()
            se()
            se_ent.configure(values=se_lista)

        se_ent_value = StringVar()
        se_ent = AutocompleteCombobox(se_lbl_fr, textvariable=se_ent_value,
                                                      postcommand=combo_post_command_se, width=30)
        se_ent.set_completion_list(se_lista)

        def callback_se(obj):
            jm_se_ent.configure(state='normal')
            jm_se_ent.delete(0, END)
            jm_se = baza.jm_spoj(se_ent.get())
            jm_se_ent.insert(0, jm_se)
            jm_se_ent.configure(state='disabled')

        se_ent.bind("<<ComboboxSelected>>", callback_se)
        jm_se_lbl = Label(se_lbl_fr, text='JM:')
        jm_se_ent = Entry(se_lbl_fr, width=33)
        iznos_se_lbl = Label(se_lbl_fr, text='Iznos:')
        iznos_se_ent = Entry(se_lbl_fr, width=33)
        unesi_se_btn = Button(se_lbl_fr, text='Unesi', width=12)
        obrisi_se_btn = Button(se_lbl_fr, text='Obriši', width=12)

        se_tv = ttk.Treeview(se_lbl_fr, column=("column1", "column2", "column3"),
                             show='headings', height=8)
        se_tv.column("#1", width=270, minwidth=40)
        se_tv.column("#2", width=150, minwidth=40)
        se_tv.column("#3", width=150, minwidth=40)

        se_tv.heading("#1", text="Spojni element")
        se_tv.heading("#2", text="JM")
        se_tv.heading("#3", text="Iznos")

        def unesi_se():
            se = se_ent.get()
            jm_se = jm_se_ent.get()
            iznos_se = iznos_se_ent.get()

            se_tv.insert("", "end", "", values=(se, jm_se, iznos_se))

            se_ent.delete(0, END)
            jm_se_ent.delete(0, END)
            iznos_se_ent.delete(0, END)

        def obrisi_se():
            odabrani_item = se_tv.selection()[0]  # rad s oznacenim redom u Treeviewu
            if odabrani_item != None:
                se_tv.delete(odabrani_item)
            else:
                messagebox.showerror('Nepotpun odabir', 'Odaberi spojni element!', parent=self)
                return

        unesi_se_btn.configure(command=unesi_se)
        obrisi_se_btn.configure(command=obrisi_se)

        scrollbar_se = Scrollbar(se_lbl_fr)
        se_tv.configure(yscrollcommand=scrollbar_se.set)
        scrollbar_se.configure(command=se_tv.yview)

        se_lbl_fr.grid(row=4, column=0, columnspan=4, padx=10, pady=5)
        #                                                           se_lbl_fr - RASPORED
        se_lbl.grid(row=0, column=0, padx=5, pady=1)
        se_ent.grid(row=0, column=1, padx=5, pady=1, sticky='w')
        jm_se_lbl.grid(row=1, column=0, padx=5, pady=1)
        jm_se_ent.grid(row=1, column=1, padx=5, pady=1, sticky='w')
        iznos_se_lbl.grid(row=2, column=0, padx=5, pady=1)
        iznos_se_ent.grid(row=2, column=1, padx=5, pady=1, sticky='w')
        se_tv.grid(row=0, column=2, rowspan=10, padx=5, pady=3)
        scrollbar_se.grid(row=0, column=4, sticky='nse', rowspan=10, padx=2)
        unesi_se_btn.grid(row=3, column=1, sticky='e', pady=1, padx=5)
        obrisi_se_btn.grid(row=4, column=1, sticky='e', pady=1, padx=5)

        # ---------- unos ostvarenih stavki montaze - sm_lbl_fr
        sm_lbl_fr = LabelFrame(glavni_frame, text='Stavke montaže')
        sm_lbl = Label(sm_lbl_fr, text='Stavka montaže:')
        sm_lista = []

        def sm():
            # upit na bazu da se povuku svi projekti koji su uneseni kako bi se mogli prikazati u comboboxu
            for red in baza.ucitaj_stavke():
                sm_lista.append(red[0])

        def combo_post_command_sm():
            sm_lista.clear()
            sm()
            sm_ent.configure(values=sm_lista)

        sm_ent_value = StringVar()
        sm_ent = AutocompleteCombobox(sm_lbl_fr, textvariable=sm_ent_value,
                                                      postcommand=combo_post_command_sm, width=130)
        sm_ent.set_completion_list(sm_lista)

        def callback_sm(obj):
            jm_sm_ent.configure(state='normal')
            jm_sm_ent.delete(0, END)
            jm_se = baza.jm_stavka(sm_ent.get())
            jm_sm_ent.insert(0, jm_se)
            jm_sm_ent.configure(state='disabled')

        sm_ent.bind("<<ComboboxSelected>>", callback_sm)
        jm_sm_lbl = Label(sm_lbl_fr, text='JM:')
        jm_sm_ent = Entry(sm_lbl_fr, width=30)
        iznos_sm_lbl = Label(sm_lbl_fr, text='Iznos:')
        iznos_sm_ent = Entry(sm_lbl_fr, width=30)
        unesi_sm_btn = Button(sm_lbl_fr, text='Unesi', width=12)
        obrisi_sm_btn = Button(sm_lbl_fr, text='Obriši', width=12)

        sm_tv = ttk.Treeview(sm_lbl_fr, column=("column1", "column2", "column3"),
                             show='headings', height=8)
        sm_tv.column("#1", width=270, minwidth=40)
        sm_tv.column("#2", width=150, minwidth=40)
        sm_tv.column("#3", width=150, minwidth=40)

        sm_tv.heading("#1", text="Stavka montaže")
        sm_tv.heading("#2", text="JM")
        sm_tv.heading("#3", text="Iznos")

        def unesi_sm():
            sm = sm_ent.get()
            jm_sm = jm_sm_ent.get()
            iznos_sm = iznos_sm_ent.get()

            sm_tv.insert("", "end", "", values=(sm, jm_sm, iznos_sm))

            sm_ent.delete(0, END)
            jm_sm_ent.delete(0, END)
            iznos_sm_ent.delete(0, END)

        def obrisi_sm():
            odabrani_item = sm_tv.selection()[0]  # rad s oznacenim redom u Treeviewu
            if odabrani_item != None:
                sm_tv.delete(odabrani_item)
            else:
                messagebox.showerror('Nepotpun odabir', 'Odaberi spojni element!', parent=self)
                return

        unesi_sm_btn.configure(command=unesi_sm)
        obrisi_sm_btn.configure(command=obrisi_sm)

        scrollbar_sm = Scrollbar(sm_lbl_fr)
        sm_tv.configure(yscrollcommand=scrollbar_sm.set)
        scrollbar_sm.configure(command=sm_tv.yview)

        sm_lbl_fr.grid(row=5, column=0, columnspan=4, padx=10, pady=5)
        #                                                           sm_lbl_fr - RASPORED
        sm_lbl.grid(row=0, column=0, padx=5, pady=1)
        sm_ent.grid(row=0, column=1, padx=5, pady=1, sticky='w', columnspan=2)
        jm_sm_lbl.grid(row=1, column=0, padx=5, pady=1)
        jm_sm_ent.grid(row=1, column=1, padx=5, pady=1, sticky='w')
        iznos_sm_lbl.grid(row=2, column=0, padx=5, pady=1)
        iznos_sm_ent.grid(row=2, column=1, padx=5, pady=1, sticky='w')
        sm_tv.grid(row=1, column=2, rowspan=10, padx=5, pady=3)
        scrollbar_sm.grid(row=0, column=4, sticky='nse', rowspan=10, padx=2)
        unesi_sm_btn.grid(row=3, column=1, sticky='e', pady=1, padx=5)
        obrisi_sm_btn.grid(row=4, column=1, sticky='e', pady=1, padx=5)

        upisi_u_bazu_btn = Button(glavni_frame, text='Upiši u bazu', width=15)
        upisi_u_bazu_btn.grid(row=6, column=0)

        def upisi_u_bazu():
            """ Ako korisnik potvrdi, svi podaci iz treeviewa i entryja se unose u bazu"""
            datum = datum_ent.get_date()
            projekt = projekt_ent.get()
            if projekt == '':
                messagebox.showerror('Nepotpun unos', 'Odaberi projekt!', parent=self)
                return

            projekt_id = int(baza.id_projekt(projekt)[0])
            print(radnici_tv.get_children())
            if radnici_tv.get_children() != ():
                for zapis in radnici_tv.get_children():
                    # print(sm_tv.item(zapis)['values'])
                    red = radnici_tv.item(zapis)['values']
                    radnik = red[0]
                    br_sati = float(red[1])
                    baza.unos_troska_radnika(projekt_id, radnik, br_sati, datum)
                for vrs in radnici_tv.get_children():
                    radnici_tv.delete(vrs)
            else:
                pass

            if strojevi_tv.get_children() != ():
                for zapis in strojevi_tv.get_children():
                    red = strojevi_tv.item(zapis)['values']
                    stroj = red[0]
                    iznos = float(red[2])
                    baza.unos_troska_strojeva(stroj, projekt_id, datum, iznos)
                for vrs in strojevi_tv.get_children():
                    strojevi_tv.delete(vrs)
            else:
                pass

            if se_tv.get_children() != ():
                for zapis in se_tv.get_children():
                    red = se_tv.item(zapis)['values']
                    sp_e = red[0]
                    iznos = float(red[2])
                    baza.unos_troska_spojeva(projekt_id, sp_e, iznos, datum)
                for vrs in se_tv.get_children():
                    se_tv.delete(vrs)
            else:
                pass

            if sm_tv.get_children() != ():
                for zapis in sm_tv.get_children():
                    red = sm_tv.item(zapis)['values']
                    smo = red[0]
                    iznos = float(red[2])
                    baza.unos_izvrsenih_stavki(projekt_id, datum, smo, iznos)
                for vrs in sm_tv.get_children():
                    sm_tv.delete(vrs)
            else:
                pass

            rucak_ent.configure(state='normal')
            spa_ent.configure(state='normal')
            ter_dod_ent.configure(state='normal')
            cest_ent.configure(state='normal')
            gor_ent.configure(state='normal')

            terenski_troskovi = []
            ruc = rucak_ent.get()
            if ruc != '':
                rucak = float(ruc)
            else:
                rucak = 0
            terenski_troskovi.append(rucak)

            spa = spa_ent.get()
            if spa != '':
                spavanje = float(spa)
            else:
                spavanje = 0
            terenski_troskovi.append(spavanje)

            ter_dod = ter_dod_ent.get()
            if ter_dod != '':
                terenski = float(ter_dod)
            else:
                terenski = 0
            terenski_troskovi.append(terenski)

            cest = cest_ent.get()
            if cest != '':
                cestarina = float(cest)
            else:
                cestarina = 0
            terenski_troskovi.append(cestarina)

            gor = gor_ent.get()
            if gor != '':
                gorivo = float(gor)
            else:
                gorivo = 0
            terenski_troskovi.append(gorivo)

            rucak_ent.delete(0, END)
            spa_ent.delete(0, END)
            ter_dod_ent.delete(0, END)
            cest_ent.delete(0, END)
            gor_ent.delete(0, END)

            if terenski_troskovi != [0, 0, 0, 0, 0]:
                baza.unesi_terenske_troskove(terenski_troskovi[0], terenski_troskovi[1], terenski_troskovi[2],
                                             terenski_troskovi[3], terenski_troskovi[4], datum, projekt_id)
            else:
                pass

        upisi_u_bazu_btn.configure(command=upisi_u_bazu)


class PageObracun(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        """ Stranica za pregled troskova i ostvarenih stavki prema podacima u bazi, izrada pdf izvjestaja"""
        container = ttk.Frame(self)
        canvas = Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        glavni_frame = ttk.Frame(canvas)
        glavni_frame.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all"), width=1100, height=400))
        canvas.create_window((0, 0), window=glavni_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        container.grid(row=3, column=0, columnspan=4)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        obracun_lbl = Label(self, text='Obračun', font=('Arial', 24), bg='#FFFF00')
        projekt_lbl = Label(self, text='Projekt:')
        projekti_lista = []

        def svi_projekti():
            # upit na bazu da se povuku svi projekti koji su uneseni kako bi se mogli prikazati u comboboxu
            for red in baza.ucitaj_projekte():
                projekti_lista.insert(0, red[0])

        def combo_post_command_projekti():
            projekti_lista.clear()
            svi_projekti()
            projekt_ent.configure(values=projekti_lista)

        svi_projekti()

        projekti_ent_value = StringVar()
        projekt_ent = AutocompleteCombobox(self, textvariable=projekti_ent_value,
                                                           postcommand=combo_post_command_projekti, width=50)
        projekt_ent.set_completion_list(projekti_lista)

        izvjestaj_btn = Button(self, text='Izvještaj')

        obracun_lbl.grid(row=0, column=0, sticky='ew', columnspan=4)
        projekt_lbl.grid(row=1, column=0)
        projekt_ent.grid(row=1, column=1)
        izvjestaj_btn.grid(row=1, column=3)

        # ---------- glavni_frame
        obracun_frame = Frame(self)
        ukupno_lbl = Label(obracun_frame, text='Ukupni trošak:', font=('Calibri', 12))
        iznos_ukupno_lbl = Label(obracun_frame, text='', font=('Calibri', 12))
        ukupno_izvrseno_lbl = Label(obracun_frame, text='Izvršene stavke:', font=('Calibri', 12))
        iznos_izvrseno_lbl = Label(obracun_frame, text='', font=('Calibri', 12))
        ukupno_razlika_lbl = Label(obracun_frame, text='Zarada:', font=('Calibri', 16))
        iznos_razlika_lbl = Label(obracun_frame, text='', font=('Calibri', 16))

        obracun_frame.grid(row=2, column=0, padx=5, columnspan=5)
        ukupno_lbl.grid(row=4, column=0, sticky='w', padx=5)
        iznos_ukupno_lbl.grid(row=4, column=1, sticky='e', padx=5)
        ukupno_izvrseno_lbl.grid(row=5, column=0, sticky='w', padx=5)
        iznos_izvrseno_lbl.grid(row=5, column=1, sticky='e', padx=5)
        ukupno_razlika_lbl.grid(row=6, column=0, sticky='w', padx=5)
        iznos_razlika_lbl.grid(row=6, column=1, sticky='e', padx=5)
        # ------------------------------- radnici

        radnici_tv = ttk.Treeview(glavni_frame, column=("Datum", "Radnik", "Broj sati", "Iznos/kn"),
                                  show='headings', height=8)
        radnici_tv.column("#1", width=130, minwidth=40)
        radnici_tv.column("#2", width=250, minwidth=40)
        radnici_tv.column("#3", width=100, minwidth=40)
        radnici_tv.column("#4", width=150, minwidth=40)

        radnici_tv.heading("#1", text="Datum")
        radnici_tv.heading("#2", text="Radnik")
        radnici_tv.heading("#3", text="Broj sati")
        radnici_tv.heading("#4", text="Iznos/kn")

        scrollbar_rad = Scrollbar(glavni_frame)
        radnici_tv.configure(yscrollcommand=scrollbar_rad.set)
        scrollbar_rad.configure(command=radnici_tv.yview)
        ukupno_radnici_lbl = Label(glavni_frame, text='Trošak radnika:', font=('Calibri', 11))
        iznos_radnici_lbl = Label(glavni_frame, text='', font=('Calibri', 11))

        radnici_tv.grid(row=1, column=0, columnspan=6, pady=5, sticky='ew')
        scrollbar_rad.grid(row=1, column=6, sticky='nse')
        ukupno_radnici_lbl.grid(row=2, column=4, sticky='wn', padx=5)
        iznos_radnici_lbl.grid(row=2, column=5, sticky='en', padx=5)
        prazan1_lbl = Label(glavni_frame, text='', width=30).grid(row=2, column=0, columnspan=3, pady=10)

        # --------------------------------- terenski
        terenski_tv = ttk.Treeview(glavni_frame, column=("Datum", "Rucak", "Spavanje", "Terenski", "Cestarina",
                                                         "Gorivo"),
                                   show='headings', height=8)
        terenski_tv.column("#1", width=130, minwidth=40)
        terenski_tv.column("#2", width=100, minwidth=40)
        terenski_tv.column("#3", width=100, minwidth=40)
        terenski_tv.column("#4", width=100, minwidth=40)
        terenski_tv.column("#5", width=100, minwidth=40)
        terenski_tv.column("#6", width=100, minwidth=40)

        terenski_tv.heading("#1", text="Datum")
        terenski_tv.heading("#2", text="Ručak")
        terenski_tv.heading("#3", text="Spavanje")
        terenski_tv.heading("#4", text="Terenski")
        terenski_tv.heading("#5", text="Cestarina")
        terenski_tv.heading("#6", text="Gorivo")

        scrollbar_ter = Scrollbar(glavni_frame)
        terenski_tv.configure(yscrollcommand=scrollbar_ter.set)
        scrollbar_ter.configure(command=terenski_tv.yview)
        ukupno_terenski_lbl = Label(glavni_frame, text='Terenski trošak:', font=('Calibri', 11))
        iznos_terenski_lbl = Label(glavni_frame, text='', font=('Calibri', 11))

        terenski_tv.grid(row=3, column=0, columnspan=6, sticky='ew')
        scrollbar_ter.grid(row=3, column=6, sticky='nse')
        ukupno_terenski_lbl.grid(row=4, column=4, sticky='wn', padx=5)
        iznos_terenski_lbl.grid(row=4, column=5, sticky='ne', padx=5)
        prazan2_lbl = Label(glavni_frame, text='', width=30).grid(row=4, column=0, columnspan=3, pady=10)

        # ------------------------------- strojevi

        strojevi_tv = ttk.Treeview(glavni_frame, column=("Datum", "Stroj", "Kolicina", "JM", "Iznos"),
                                   show='headings', height=8)
        strojevi_tv.column("#1", width=130, minwidth=40)
        strojevi_tv.column("#2", width=150, minwidth=40)
        strojevi_tv.column("#3", width=70, minwidth=40)
        strojevi_tv.column("#4", width=70, minwidth=40)
        strojevi_tv.column("#5", width=130, minwidth=40)

        strojevi_tv.heading("#1", text="Datum")
        strojevi_tv.heading("#2", text="Stroj")
        strojevi_tv.heading("#3", text="Količina")
        strojevi_tv.heading("#4", text="JM")
        strojevi_tv.heading("#5", text="Iznos")

        scrollbar_str = Scrollbar(glavni_frame)
        strojevi_tv.configure(yscrollcommand=scrollbar_str.set)
        scrollbar_str.configure(command=strojevi_tv.yview)
        ukupno_strojevi_lbl = Label(glavni_frame, text='Trošak strojeva:', font=('Calibri', 11))
        iznos_strojevi_lbl = Label(glavni_frame, text='', font=('Calibri', 11))

        strojevi_tv.grid(row=5, column=0, columnspan=6, sticky='ew')
        scrollbar_str.grid(row=5, column=6, sticky='nse')
        ukupno_strojevi_lbl.grid(row=6, column=4, sticky='wn', padx=5)
        iznos_strojevi_lbl.grid(row=6, column=5, sticky='en', padx=5)
        prazan3_lbl = Label(glavni_frame, text='', width=30).grid(row=6, column=0, columnspan=3, pady=10)

        # ------------------------------- spojni elementi

        spojni_tv = ttk.Treeview(glavni_frame, column=("Datum", "Spojni el.", "Kolicina", "JM", "Iznos"),
                                 show='headings', height=8)
        spojni_tv.column("#1", width=130, minwidth=40)
        spojni_tv.column("#2", width=150, minwidth=40)
        spojni_tv.column("#3", width=70, minwidth=40)
        spojni_tv.column("#4", width=70, minwidth=40)
        spojni_tv.column("#5", width=100, minwidth=40)

        spojni_tv.heading("#1", text="Datum")
        spojni_tv.heading("#2", text="Spojni el.")
        spojni_tv.heading("#3", text="Količina")
        spojni_tv.heading("#4", text="JM")
        spojni_tv.heading("#5", text="Iznos")

        scrollbar_sp = Scrollbar(glavni_frame)
        spojni_tv.configure(yscrollcommand=scrollbar_sp.set)
        scrollbar_sp.configure(command=spojni_tv.yview)
        ukupno_spojni_lbl = Label(glavni_frame, text='Trošak spojnih el.:', font=('Calibri', 11))
        iznos_spojni_lbl = Label(glavni_frame, text='', font=('Calibri', 11))

        spojni_tv.grid(row=7, column=0, columnspan=6, sticky='ew')
        scrollbar_sp.grid(row=7, column=6, sticky='nse')
        ukupno_spojni_lbl.grid(row=8, column=4, sticky='wn', padx=5)
        iznos_spojni_lbl.grid(row=8, column=5, sticky='en', padx=5)
        prazan4_lbl = Label(glavni_frame, text='', width=30).grid(row=8, column=0, columnspan=3, pady=10)

        # ------------------------------- izvrsene stavke

        izvrseno_tv = ttk.Treeview(glavni_frame, column=("Datum", "Stavka montaze", "Količina", "JM", "Iznos"),
                                   show='headings', height=8)
        izvrseno_tv.column("#1", width=130, minwidth=40)
        izvrseno_tv.column("#2", width=300, minwidth=40)
        izvrseno_tv.column("#3", width=70, minwidth=40)
        izvrseno_tv.column("#4", width=70, minwidth=40)
        izvrseno_tv.column("#5", width=100, minwidth=40)

        izvrseno_tv.heading("#1", text="Datum")
        izvrseno_tv.heading("#2", text="Stavka montaže")
        izvrseno_tv.heading("#3", text="Količina")
        izvrseno_tv.heading("#4", text="JM")
        izvrseno_tv.heading("#5", text="Iznos")

        scrollbar_iz = Scrollbar(glavni_frame)
        izvrseno_tv.configure(yscrollcommand=scrollbar_iz.set)
        scrollbar_iz.configure(command=izvrseno_tv.yview)

        izvrseno_tv.grid(row=9, column=0, columnspan=6, rowspan=10, sticky='ew')
        scrollbar_iz.grid(row=9, column=6, sticky='nse', rowspan=10)
        # prazan5_lbl = Label(glavni_frame, text='', width=30).grid(row=9, column=0, columnspan=3, pady=10)

        def trazi_po_projektu(obj):
            """ Za odabrani projekt ispisuje sve podatke iz baze"""
            projekt = projekt_ent.get()

            # brisanje svih treeviewa
            for vrs in radnici_tv.get_children():
                radnici_tv.delete(vrs)
            for vrs in terenski_tv.get_children():
                terenski_tv.delete(vrs)
            for vrs in strojevi_tv.get_children():
                strojevi_tv.delete(vrs)
            for vrs in spojni_tv.get_children():
                spojni_tv.delete(vrs)
            for vrs in izvrseno_tv.get_children():
                izvrseno_tv.delete(vrs)

            if projekt != '':
                projekt_id = int(baza.id_projekt(projekt)[0])
            else:
                messagebox.showerror('Nepotpun unos', 'Odaberi projekt!', parent=self)
                return

            ukupno_radnici = 0
            ukupno_terenski = 0
            ukupno_strojevi = 0
            ukupno_spojni = 0
            ukupno_izvrseno = 0

            for red in baza.trosak_radnika_po_projektu(projekt_id):
                placa = float(baza.placa_radnika(red[1])[0]) * float(red[2])
                placa_str = str("%.2f" % round(placa, 2))
                radnici_tv.insert("", "end", "", values=(red[0], red[1], red[2], placa_str))
                ukupno_radnici = ukupno_radnici + placa

            for red in baza.terenski_trosat_po_projektu(projekt_id):
                teren_po_danu = red[5] + red[1] + red[2] + red[3] + red[4]
                terenski_tv.insert("", "end", "", values=red)
                ukupno_terenski = ukupno_terenski + teren_po_danu

            for red in baza.trosak_stroja_po_projektu(projekt_id):
                strojevi_cijena = float(baza.cijena_stroja(red[1])[0]) * float(red[3])
                strojevi_cijena_str = str("%.2f" % round(strojevi_cijena, 2))
                strojevi_tv.insert("", "end", "", values=(red[0], red[1], red[2], red[3], strojevi_cijena_str))
                ukupno_strojevi = ukupno_strojevi + strojevi_cijena

            for red in baza.trosak_spojnih_po_projektu(projekt_id):
                spojni_cijena = float(baza.cijena_spojnog(red[1])[0]) * float(red[2])
                spojni_cijena_str = str("%.2f" % round(spojni_cijena, 2))
                spojni_tv.insert("", "end", "", values=(red[0], red[1], red[2], red[3], spojni_cijena_str))
                ukupno_spojni = ukupno_spojni + spojni_cijena

            for red in baza.izvrseno_po_projektu(projekt_id):
                izvrseno = float(baza.cijena_stavke(red[1])[0]) * float(red[2])
                izvrseno_str = str("%.2f" % round(izvrseno, 2))
                izvrseno_tv.insert("", "end", "", values=(red[0], red[1], red[2], red[3], izvrseno_str))
                ukupno_izvrseno = ukupno_izvrseno + izvrseno

            ukupni_trosak = ukupno_radnici + ukupno_terenski + ukupno_strojevi + ukupno_spojni

            razlika = ukupno_izvrseno - ukupni_trosak

            iznos_radnici_lbl.configure(text=str("%.2f" % round(ukupno_radnici, 2) + ' kn'), fg='red')
            iznos_terenski_lbl.configure(text=str("%.2f" % round(ukupno_terenski, 2) + ' kn'), fg='red')
            iznos_strojevi_lbl.configure(text=str("%.2f" % round(ukupno_strojevi, 2) + ' kn'), fg='red')
            iznos_spojni_lbl.configure(text=str("%.2f" % round(ukupno_spojni, 2) + ' kn'), fg='red')
            iznos_izvrseno_lbl.configure(text=str("%.2f" % round(ukupno_izvrseno, 2) + ' kn'), fg='blue')
            iznos_ukupno_lbl.configure(text=str("%.2f" % round(ukupni_trosak, 2) + ' kn'), fg='red')
            if razlika >= 0:
                boja_razlike = 'green'
            else:
                boja_razlike = 'red'
            iznos_razlika_lbl.configure(text=str("%.2f" % round(razlika, 2) + ' kn'), fg=boja_razlike)

        projekt_ent.bind("<<ComboboxSelected>>", trazi_po_projektu)

        def izvjestaj_obracun():
            f = filedialog.asksaveasfile(mode='w', defaultextension=".pdf", filetypes=[("PDF datoteka", ".pdf")],
                                         title='Spremi', initialfile='Izvještaj', parent=self)
            mjesto_i_ime = f.name

            pdf = SimpleDocTemplate(mjesto_i_ime, pagesize=A4,
                                    rightMargin=72, leftMargin=72,
                                    topMargin=72, bottomMargin=60)
            if f is None:  # asksaveasfile return `None` if dialog closed with "cancel".
                return
            elementi_pdfa = []

            """Za uneseni treeview generira pdf izvjestaj s podacima iz treeviewa"""
            width, height = A4

            podaci = []
            ukupni_podaci_naslovi = ['Ukupni trošak', 'Izvršeno', 'Razlika']
            ukupni_podaci = [iznos_ukupno_lbl.cget('text'),
                             iznos_izvrseno_lbl.cget('text'),
                             iznos_razlika_lbl.cget('text')]
            podaci.append(ukupni_podaci_naslovi)
            podaci.append(ukupni_podaci)
            tablica = Table(podaci, colWidths=[160, 170, 160])  # za svaki stupac upisati njegovu širinu

            stil = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.yellow),
                ('FONT', (0, 0), (-1, -1), 'Verdana')])

            tablica.setStyle(stil)
            elementi_pdfa.append(Spacer(1, 12))
            elementi_pdfa.append(tablica)
            elementi_pdfa.append(Spacer(1, 12))

            podaci = []
            nazivi_stupaca = ['Datum', 'Radnik', 'Broj sati', 'Iznos']
            podaci.append(nazivi_stupaca)
            for vrs in radnici_tv.get_children():
                red = radnici_tv.item(vrs)['values']
                podaci.append(red)
            podaci.append(['', 'Ukupni trošak radnika', '', iznos_radnici_lbl.cget('text')])

            tablica = Table(podaci, colWidths=[100, 150, 100, 140])
            pdfmetrics.registerFont(TTFont('Verdana', 'Verdana.ttf'))
            broj_redova = len(podaci)

            for i in range(1, broj_redova):
                if i % 2 == 0:
                    pozadina_reda = colors.beige
                    ts = TableStyle([('BACKGROUND', (0, i), (-1, i), pozadina_reda)])
                    tablica.setStyle(ts)

            stil = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.yellow),
                ('FONT', (0, 0), (-1, -1), 'Verdana'),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black)
                ])

            tablica.setStyle(stil)
            elementi_pdfa.append(Spacer(1, 12))
            elementi_pdfa.append(tablica)
            elementi_pdfa.append(Spacer(1, 12))

            podaci = []
            nazivi_stupaca = ['Datum', 'Ručak', 'Spavanje', 'Terenski', 'Cestarina', 'Gorivo']
            podaci.append(nazivi_stupaca)
            for vrs in terenski_tv.get_children():
                red = terenski_tv.item(vrs)['values']
                podaci.append(red)
            podaci.append(['', 'Ukupni terenski trošak', '', iznos_terenski_lbl.cget('text')])

            tablica = Table(podaci, colWidths=[90, 80, 80, 80, 80, 80])
            broj_redova = len(podaci)

            for i in range(1, broj_redova):
                if i % 2 == 0:
                    pozadina_reda = colors.beige
                    ts = TableStyle([('BACKGROUND', (0, i), (-1, i), pozadina_reda)])
                    tablica.setStyle(ts)

            stil = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.yellow),
                ('FONT', (0, 0), (-1, -1), 'Verdana'),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black)
            ])

            tablica.setStyle(stil)
            elementi_pdfa.append(Spacer(1, 12))
            elementi_pdfa.append(tablica)
            elementi_pdfa.append(Spacer(1, 12))

            podaci = []
            nazivi_stupaca = ['Datum', 'Stroj', 'Količina', 'JM', 'Iznos']
            podaci.append(nazivi_stupaca)
            for vrs in strojevi_tv.get_children():
                red = strojevi_tv.item(vrs)['values']
                podaci.append(red)
            podaci.append(['', 'Ukupni trošak strojeva', '', iznos_strojevi_lbl.cget('text')])

            tablica = Table(podaci, colWidths=[100, 150, 80, 70, 90])
            broj_redova = len(podaci)

            for i in range(1, broj_redova):
                if i % 2 == 0:
                    pozadina_reda = colors.beige
                    ts = TableStyle([('BACKGROUND', (0, i), (-1, i), pozadina_reda)])
                    tablica.setStyle(ts)

            stil = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.yellow),
                ('FONT', (0, 0), (-1, -1), 'Verdana'),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black)])

            tablica.setStyle(stil)
            elementi_pdfa.append(Spacer(1, 12))
            elementi_pdfa.append(tablica)
            elementi_pdfa.append(Spacer(1, 12))

            podaci = []
            nazivi_stupaca = ['Datum', 'Spojni element', 'Količina', 'JM', 'Iznos']
            podaci.append(nazivi_stupaca)
            for vrs in spojni_tv.get_children():
                red = spojni_tv.item(vrs)['values']
                podaci.append(red)
            podaci.append(['', 'Ukupni trošak spojnih el.', '', iznos_spojni_lbl.cget('text')])

            tablica = Table(podaci, colWidths=[100, 150, 80, 70, 90])
            broj_redova = len(podaci)

            for i in range(1, broj_redova):
                if i % 2 == 0:
                    pozadina_reda = colors.beige
                    ts = TableStyle([('BACKGROUND', (0, i), (-1, i), pozadina_reda)])
                    tablica.setStyle(ts)

            stil = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.yellow),
                ('FONT', (0, 0), (-1, -1), 'Verdana'),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black)])

            tablica.setStyle(stil)
            elementi_pdfa.append(Spacer(1, 12))
            elementi_pdfa.append(tablica)
            elementi_pdfa.append(Spacer(1, 12))

            podaci = []
            nazivi_stupaca = ['Datum', 'Stavka', 'Količina', 'JM', 'Iznos']
            podaci.append(nazivi_stupaca)
            for vrs in izvrseno_tv.get_children():
                red = izvrseno_tv.item(vrs)['values']
                podaci.append(red)
            podaci.append(['', 'Ukupno izvršeno', '', iznos_izvrseno_lbl.cget('text')])

            tablica = Table(podaci, colWidths=[70, 220, 60, 50, 90])
            broj_redova = len(podaci)

            for i in range(1, broj_redova):
                if i % 2 == 0:
                    pozadina_reda = colors.beige
                    ts = TableStyle([('BACKGROUND', (0, i), (-1, i), pozadina_reda)])
                    tablica.setStyle(ts)

            stil = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.yellow),
                ('FONT', (0, 0), (-1, -1), 'Verdana'),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black)])

            tablica.setStyle(stil)

            elementi_pdfa.append(Spacer(1, 12))
            elementi_pdfa.append(tablica)
            elementi_pdfa.append(Spacer(1, 12))

            def zaglavlje(canvas, doc):
                canvas.saveState()
                # logo i datum se prikazuju u zaglavlju
                datum = datetime.today()
                logo_naziv = 'modeco_logo1x.png'
                canvas.drawImage(logo_naziv, 0.7 * width, 0.95 * height, 85, 20)
                canvas.setFont('Times-Bold', 11)
                canvas.drawString(0.1 * width, 0.95 * height,
                                  str('Datum izvještaja:' + datetime.strftime(datum, "%m-%d-%Y")))
                canvas.setFont('Times-Roman', 11)
                # broj stranice u desnom dnu svake stranice
                page_num = str(canvas._pageNumber)
                canvas.drawString(0.9 * width, 0.5 * inch, page_num)
                canvas.restoreState()

            pdf.build(elementi_pdfa, onFirstPage=zaglavlje, onLaterPages=zaglavlje)
            os.startfile(mjesto_i_ime)

        izvjestaj_btn.configure(command=izvjestaj_obracun)


class MainView(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        p1 = PageProjekti(self)
        p2 = PageRadnici(self)
        p3 = PageSpojni(self)
        p4 = PageStavke(self)
        p5 = PageStrojevi(self)
        p6 = PageUnosTroskova(self)
        p7 = PageObracun(self)
        # =================================== Frameovi na pocetnom prozoru ===========================================
        # photoimage = photo.subsample(15, 15)
        # create a canvas to show image on
        canvas_for_image = Canvas(self, height=100, width=500, borderwidth=0, highlightthickness=0)

        # create image from image location resize it to 200X200 and put in on canvas
        image = Image.open('modeco_logo1x.png')
        canvas_for_image.image = ImageTk.PhotoImage(image.resize((191 * 2, 43 * 2), Image.ANTIALIAS))
        canvas_for_image.create_image(0, 0, image=canvas_for_image.image, anchor='nw')
        gumbovi = Frame(self, background='#FFFF00', relief=FLAT)
        container = Frame(self, background='#A0A0A0', height=600, relief=FLAT, width=1200)
        prazan_okvir = Frame(self, relief=FLAT, height=150, width=230)

        p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p3.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p4.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p5.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p6.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p7.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        # raspored
        prazan_okvir.grid(row=0, column=0)
        canvas_for_image.grid(row=0, column=1, pady=15)
        gumbovi.grid(row=1, column=0, sticky='n')
        container.grid(row=1, column=1)

        """stil = ttk.Style()
        # stil.theme_use('classic')
        stil.configure("Treeview", rowheight=22, fieldbackground='D3D3D3')
        stil.configure("Treeview.Heading", background="#faf766", foreground="#33270d")
        stil.map("Treeview")
        """

        # ==================================== gumbovi u frameu pocetnog prozora imena gumbovi =====================
        sirina_gumba = 25
        visina_gumba = 2

        self.projekti_btn = Button(gumbovi, text='       Projekti', anchor='w',
                                   width=25, height=2,
                                   # width=sirina_gumba, height=visina_gumba,
                                   command=p1.lift, activebackground='#000000', bg='#FFFF00',
                                   compound='left', font=24, relief=FLAT)
        self.radnici_btn = Button(gumbovi, text='       Radnici', anchor='w',
                                  width=25, height=2,
                                  # width=sirina_gumba, height=visina_gumba,
                                  command=p2.lift, activebackground='#000000', bg='#FFFF00',
                                  compound='left', font=24, relief=FLAT)
        self.spojni_btn = Button(gumbovi, text='       Spojni elementi', anchor='w',
                                 width=25, height=2,
                                 # width=sirina_gumba, height=visina_gumba,
                                 command=p3.lift, activebackground='#000000', bg='#FFFF00',
                                 compound='left', font=24, relief=FLAT)
        self.stavke_btn = Button(gumbovi, text='       Stavke montaže', anchor='w',
                                 width=25, height=2,
                                 # width=sirina_gumba, height=visina_gumba,
                                 command=p4.lift, activebackground='#000000', bg='#FFFF00',
                                 compound='left', font=24, relief=FLAT)
        self.strojevi_btn = Button(gumbovi, text='       Strojevi', anchor='w',
                                   width=25, height=2,
                                   # width=sirina_gumba, height=visina_gumba,
                                   command=p5.lift, activebackground='#000000', bg='#FFFF00',
                                   compound='left', font=24, relief=FLAT)
        self.unos_troskova_btn = Button(gumbovi, text='       Unos troškova', anchor='w',
                                        width=25, height=2,
                                        # width=sirina_gumba, height=visina_gumba,
                                        command=p6.lift, activebackground='#000000', bg='#FFFF00',
                                        compound='left', font=24, relief=FLAT)
        self.obracun_btn = Button(gumbovi, text='       Obračun', anchor='w',
                                  width=25, height=2,
                                  # width=sirina_gumba, height=visina_gumba,
                                  command=p7.lift, activebackground='#000000', bg='#FFFF00',
                                  compound='left', font=24, relief=FLAT)

        # promjena boje kod prelaska misa preko gumbova
        def on_enter(e):
            e.widget['background'] = 'SystemButtonFace'

        def on_leave(e):
            e.widget['background'] = '#FFFF00'
        self.projekti_btn.bind("<Enter>", on_enter)
        self.projekti_btn.bind("<Leave>", on_leave)
        self.radnici_btn.bind("<Enter>", on_enter)
        self.radnici_btn.bind("<Leave>", on_leave)
        self.spojni_btn.bind("<Enter>", on_enter)
        self.spojni_btn.bind("<Leave>", on_leave)
        self.stavke_btn.bind("<Enter>", on_enter)
        self.stavke_btn.bind("<Leave>", on_leave)
        self.strojevi_btn.bind("<Enter>", on_enter)
        self.strojevi_btn.bind("<Leave>", on_leave)
        self.unos_troskova_btn.bind("<Enter>", on_enter)
        self.unos_troskova_btn.bind("<Leave>", on_leave)
        self.obracun_btn.bind("<Enter>", on_enter)
        self.obracun_btn.bind("<Leave>", on_leave)

        # raspored
        self.projekti_btn.grid(row=0, column=0)
        self.radnici_btn.grid(row=1, column=0)
        self.spojni_btn.grid(row=2, column=0)
        self.strojevi_btn.grid(row=3, column=0)
        self.stavke_btn.grid(row=4, column=0)
        self.unos_troskova_btn.grid(row=5, column=0)
        self.obracun_btn.grid(row=6, column=0)


def prozor():    #
    # wmic bios get serialnumber#Windows
    # hal-get-property --udi /org/freedesktop/Hal/devices/computer --key system.hardware.uuid#Linux
    # ioreg -l | grep IOPlatformSerialNumber#Mac OS X

    def get_machine_addr():
        os_type = sys.platform.lower()
        if "win" in os_type:
            command = "wmic bios get serialnumber"
        return os.popen(command).read().replace("\n", "").replace("	", "").replace(" ", "")

    # output machine serial code: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXX
    mbo_id = get_machine_addr()  # serijski broj maticne ploce preko kojeg se ogranicava program na jedno racunalo

    datum = datetime.now()  # .date()
    rok = datetime.strptime('2022-1-1 00:00:00.0', '%Y-%m-%d %H:%M:%S.%f')
    rok_y = datetime.strptime('2021', '%Y')
    # print(rok_y)
    # print(type(rok_y))

    # prvo se provjerava koristi li se program na ispravnom racunalu
    # Domagoj Susak serijski broj: PF1L3GLP
    # Moj serijski broj 5CD1440FPD
    if __name__ == "__main__":  # and mbo_id == 'SerialNumber5CD1440FPD' and datum < rok:
        root = Tk()

        main = MainView(root)
        root.title("Modeco - Project Management")
        root.configure(background='#A0A0A0')
        main.pack(side="top", fill="both", expand=True)
        root.wm_geometry("1550x800+0+0")
        root.mainloop()
    else:
        messagebox.showerror('Greška', 'Licenca je istekla!')
        return


prozor()
