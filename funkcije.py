def punjenje_tv(tv, funkcija_baze):
    """ Za odabrani treeview učitava podatke iz baze prema zadanoj funkciji"""
    for vrs in tv.get_children():
        tv.delete(vrs)
    # punjenje treeviewa s podacima iz baze o projektima
    for red in funkcija_baze:
        tv.insert("", "end", "", values=red)


def punjenje_projekti_tv(tv, funkcija_baze):
    for vrs in tv.get_children():
        tv.delete(vrs)
    # punjenje treeviewa s podacima iz baze o projektima
    for red in funkcija_baze:
        if red[3] == 'a':
            status = 'Aktivan'
        else:
            status = 'Završen'
        tv.insert("", "0", "", values=(red[0], red[1], red[2], status), tag=status)
    # promjena boje za aktivne i zavrsene projekte
    tv.tag_configure('Aktivan', foreground="#014d80", background="#ffffff")
    tv.tag_configure('Završen', foreground="#fc0303", background="#f5dfdf")


def punjenje_radnici_tv(tv, funkcija_baze):
    for vrs in tv.get_children():
        tv.delete(vrs)
    # punjenje treeviewa s podacima iz baze o projektima
    for red in funkcija_baze:
        if red[2] == 'a':
            status = 'Zaposlen'
        else:
            status = 'Nezaposlen'
        tv.insert("", "end", "", values=(red[0], red[1], status), tag=status)
    # promjena boje za aktivne i zavrsene projekte
    tv.tag_configure('Zaposlen', foreground="#014d80", background="#ffffff")
    tv.tag_configure('Nezaposlen', foreground="#fc0303", background="#f5dfdf")
