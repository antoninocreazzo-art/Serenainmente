#!/usr/bin/env python3
"""Genera scarica/gestionale-di-famiglia.xlsx: il gestionale di famiglia di Serena.
Uso: python3 gen/gestionale.py  (viene chiamato anche da build.py)"""
import os, datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'scarica', 'gestionale-di-famiglia.xlsx')

MALVA, INK, MUTED, ROSA, CREMA, LINE, BLU = '97606F', '3A2C30', '7A6569', 'F4E9EC', 'FBF6F4', 'EADCDF', '0000FF'
F = 'Arial'
thin = Side(style='thin', color=LINE)
H = Font(name=F, bold=True, color='FFFFFF', size=10)
IN = Font(name=F, color=BLU, size=10)          # celle da compilare
FX = Font(name=F, color=INK, size=10)          # formule
TITLE = Font(name='Georgia', bold=True, size=16, color=INK)
SUB = Font(name=F, italic=True, size=10, color=MUTED)
FILL_H = PatternFill('solid', fgColor=MALVA)
FILL_IN = PatternFill('solid', fgColor='FFFBE6')   # giallo chiaro: compila qui
FILL_ALT = PatternFill('solid', fgColor=CREMA)
N_ROWS = 40  # righe pronte da compilare per ogni tabella

wb = Workbook()

def sheet(title, headline, sub, headers, widths, first_row=5):
    ws = wb.create_sheet(title)
    ws.sheet_view.showGridLines = False
    ws['A1'] = headline; ws['A1'].font = TITLE
    ws['A2'] = sub; ws['A2'].font = SUB
    ws.row_dimensions[1].height = 26
    for i, (h, w) in enumerate(zip(headers, widths)):
        col = chr(65 + i)
        ws.column_dimensions[col].width = w
        c = ws[f'{col}{first_row - 1}']; c.value = h; c.font = H; c.fill = FILL_H
        c.alignment = Alignment(vertical='center', wrap_text=True)
    ws.row_dimensions[first_row - 1].height = 30
    ws.freeze_panes = f'A{first_row}'
    ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
    return ws

def rows(ws, first_row, ncols, input_cols, formula_cols=()):
    """Formatta N_ROWS righe: bordo, zebra, font blu nelle colonne da compilare."""
    for r in range(first_row, first_row + N_ROWS):
        for i in range(ncols):
            col = chr(65 + i); c = ws[f'{col}{r}']
            c.border = Border(bottom=thin)
            c.alignment = Alignment(vertical='center', wrap_text=True)
            if col in input_cols:
                c.font = IN
                if (r - first_row) % 2: c.fill = FILL_ALT
            else:
                c.font = FX
        ws.row_dimensions[r].height = 20

def example(ws, r, values, note='Esempio: cancella questa riga e scrivi i tuoi dati'):
    for i, v in enumerate(values):
        if v is not None:
            ws[f'{chr(65+i)}{r}'] = v
    last = chr(65 + len(values) - 1)
    ws[f'{last}{r}'] = note; ws[f'{last}{r}'].font = Font(name=F, italic=True, size=9, color=MUTED)

def dates(ws, col, first_row):
    for r in range(first_row, first_row + N_ROWS):
        ws[f'{col}{r}'].number_format = 'DD/MM/YYYY'

def listval(ws, col, first_row, options):
    dv = DataValidation(type='list', formula1='"' + ','.join(options) + '"', allow_blank=True)
    ws.add_data_validation(dv)
    for r in range(first_row, first_row + N_ROWS):
        dv.add(ws[f'{col}{r}'])

def stato_rule(ws, rng, col_days):
    """Colora la colonna Stato: rosso scaduto, arancio entro 30 giorni."""
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'AND(ISNUMBER({col_days}5),{col_days}5<0)'], fill=PatternFill('solid', fgColor='F8D7DA'), font=Font(name=F, color='8A2430', bold=True)))
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'AND(ISNUMBER({col_days}5),{col_days}5>=0,{col_days}5<=30)'], fill=PatternFill('solid', fgColor='FFF0C2'), font=Font(name=F, color='7A5A00', bold=True)))

oggi = datetime.date.today()

# ---------- Famiglia ----------
ws = sheet('Famiglia', 'La tua famiglia', 'Una riga per persona. L\'età si calcola da sola dalla data di nascita.',
           ['Nome', 'Ruolo', 'Data di nascita', 'Età', 'Pediatra o medico', 'Allergie note', 'Terapie in corso', 'Note'],
           [18, 14, 16, 8, 24, 24, 24, 30])
rows(ws, 5, 8, 'ABCEFGH'); dates(ws, 'C', 5)
listval(ws, 'B', 5, ['Mamma', 'Papà', 'Bambino/a', 'Nonno/a', 'Altro'])
for r in range(5, 5 + N_ROWS):
    ws[f'D{r}'] = f'=IF(C{r}="","",IF(DATEDIF(C{r},TODAY(),"y")=0,DATEDIF(C{r},TODAY(),"m")&" mesi",DATEDIF(C{r},TODAY(),"y")&" anni"))'
example(ws, 5, ['Sofia', 'Bambino/a', datetime.date(oggi.year - 2, 3, 14), None, 'Dott.ssa Rossi · 010 000000', 'Nessuna nota', '—', None])

# ---------- Documenti (la cartellina) ----------
ws = sheet('Documenti', 'La cartellina di famiglia', 'Dove sta ogni documento e quando scade. "Giorni" e "Stato" si calcolano da soli.',
           ['Documento', 'Di chi', 'Dove si trova', 'Scadenza', 'Giorni', 'Stato', 'Note'],
           [30, 16, 26, 14, 9, 14, 30])
rows(ws, 5, 7, 'ABCDG'); dates(ws, 'D', 5)
listval(ws, 'A', 5, ['Tessera sanitaria', 'Carta d\'identità', 'Passaporto', 'Libretto vaccinale', 'Referto', 'Lettera di dimissione', 'Certificato', 'Altro'])
for r in range(5, 5 + N_ROWS):
    ws[f'E{r}'] = f'=IF(D{r}="","",D{r}-TODAY())'
    ws[f'F{r}'] = f'=IF(D{r}="","",IF(E{r}<0,"Scaduto",IF(E{r}<=30,"In scadenza","Ok")))'
stato_rule(ws, f'F5:F{4+N_ROWS}', 'E')
example(ws, 5, ['Tessera sanitaria', 'Sofia', 'Cartellina blu, primo scomparto', datetime.date(oggi.year + 1, 6, 30), None, None, None])
example(ws, 6, ['Libretto vaccinale', 'Sofia', 'Cartellina blu, primo scomparto', None, None, None, None], note='Senza scadenza: lascia vuota la data')

# ---------- Scadenze ----------
ws = sheet('Scadenze', 'Vaccini, visite e scadenze', 'Tutto ciò che ha una data: richiami, controlli, rinnovi, iscrizioni. Spunta "Fatto" quando è chiuso.',
           ['Cosa', 'Chi', 'Data', 'Giorni', 'Stato', 'Fatto', 'Chi se ne occupa', 'Note'],
           [32, 14, 14, 9, 14, 9, 18, 30])
rows(ws, 5, 8, 'ABCFGH'); dates(ws, 'C', 5)
listval(ws, 'F', 5, ['☐', '☑'])
for r in range(5, 5 + N_ROWS):
    ws[f'D{r}'] = f'=IF(OR(C{r}="",F{r}="☑"),"",C{r}-TODAY())'
    ws[f'E{r}'] = f'=IF(F{r}="☑","Fatto",IF(C{r}="","",IF(D{r}<0,"Scaduto",IF(D{r}<=30,"Entro 30 giorni","Ok"))))'
    ws[f'F{r}'].alignment = Alignment(horizontal='center', vertical='center')
stato_rule(ws, f'E5:E{4+N_ROWS}', 'D')
example(ws, 5, ['Richiamo vaccino (chiedere al pediatra quale)', 'Sofia', oggi + datetime.timedelta(days=21), None, None, '☐', 'Mamma', None])
example(ws, 6, ['Iscrizione al nido', 'Sofia', oggi - datetime.timedelta(days=10), None, None, '☑', 'Papà', None], note='Fatto: sparisce dai promemoria')

# ---------- Visite ----------
ws = sheet('Visite', 'Prima e dopo la visita', 'Dieci minuti prima: scrivi le domande e cosa hai notato. Durante: le risposte. Prima di uscire: cosa fare e quando richiamare.',
           ['Data', 'Chi', 'Medico', 'Domanda 1 (la più importante)', 'Domanda 2', 'Domanda 3', 'Cosa ho notato', 'Risposte', 'Cosa facciamo', 'Richiamare se / quando'],
           [12, 12, 18, 26, 22, 22, 26, 30, 26, 22])
rows(ws, 5, 10, 'ABCDEFGHIJ'); dates(ws, 'A', 5)
for r in range(5, 5 + N_ROWS): ws.row_dimensions[r].height = 36
example(ws, 5, [oggi + datetime.timedelta(days=7), 'Sofia', 'Dott.ssa Rossi', 'Si sveglia 3 volte a notte: è normale a questa età?', 'Mangia poco a cena', 'Quando il prossimo richiamo?', 'Da due settimane, soprattutto dopo giornate al nido', '', '', ''])

# ---------- Settimana ----------
ws = wb.create_sheet('Settimana')
ws.sheet_view.showGridLines = False
ws['A1'] = 'La settimana di tutta la famiglia'; ws['A1'].font = TITLE
ws['A2'] = 'Cosa succede e chi se ne occupa. Cambia i nomi nelle intestazioni con quelli di casa tua.'; ws['A2'].font = SUB
giorni = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
fasce = ['Mattina', 'Pomeriggio', 'Sera', 'Chi se ne occupa']
ws.column_dimensions['A'].width = 18
for i, g in enumerate(giorni):
    col = chr(66 + i); ws.column_dimensions[col].width = 20
    c = ws[f'{col}4']; c.value = g; c.font = H; c.fill = FILL_H; c.alignment = Alignment(horizontal='center')
for j, f in enumerate(fasce):
    r = 5 + j; ws[f'A{r}'] = f; ws[f'A{r}'].font = Font(name=F, bold=True, color=MALVA); ws.row_dimensions[r].height = 48
    for i in range(7):
        c = ws[f'{chr(66+i)}{r}']; c.font = IN; c.border = Border(bottom=thin, right=thin); c.alignment = Alignment(wrap_text=True, vertical='top')
        if j % 2: c.fill = FILL_ALT
ws['B5'] = 'Nido 8:30'; ws['B7'] = 'Bagnetto, storia, nanna 20:30'; ws['B8'] = 'Mamma mattina · Papà sera'
ws['A10'] = 'Esempio nella colonna Lunedì: cancellalo e scrivi la tua settimana.'; ws['A10'].font = Font(name=F, italic=True, size=9, color=MUTED)
ws.freeze_panes = 'B5'; ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1

# ---------- Contatti ----------
ws = sheet('Contatti', 'Contatti utili', 'Tutti i numeri che servono, in un posto solo. Stampalo e mettilo nella cartellina.',
           ['Chi', 'Nome', 'Telefono', 'Orari / quando chiamare', 'Note'], [22, 26, 18, 28, 30])
rows(ws, 5, 5, 'ABCDE')
listval(ws, 'A', 5, ['Pediatra', 'Medico di famiglia', 'Guardia medica', 'ASL', 'Pronto soccorso', 'Nido / scuola', 'Nonni', 'Babysitter', 'Farmacia', 'Altro'])
example(ws, 5, ['Pediatra', 'Dott.ssa Rossi', '010 000000', 'Lun-ven 9-12, telefonate 13-14', None])
example(ws, 6, ['Guardia medica', '', '116117', 'Notte, weekend e festivi', 'Numero unico in molte regioni: verifica nella tua'], note='Verifica il numero della tua regione')

# ---------- Prime volte ----------
ws = sheet('Prime volte', 'Le prime volte e i ricordi', 'La prima parola, i primi passi, il primo giorno di nido. Due righe oggi valgono più di una memoria tra dieci anni.',
           ['Data', 'Chi', 'Cosa è successo', 'Come è andata, con parole tue', 'Dove sta la foto o il video'], [12, 12, 28, 44, 26])
rows(ws, 5, 5, 'ABCDE'); dates(ws, 'A', 5)
for r in range(5, 5 + N_ROWS): ws.row_dimensions[r].height = 32
example(ws, 5, [oggi - datetime.timedelta(days=3), 'Sofia', 'Prima parola: "pappa"', 'A cena, indicando il piatto. Abbiamo riso tutti e lei l\'ha ripetuta dieci volte.', 'Telefono di mamma, album "Sofia"'])

# ---------- Inizia da qui (prima scheda) ----------
ws = wb.active; ws.title = 'Inizia da qui'
ws.sheet_view.showGridLines = False
ws.column_dimensions['A'].width = 34; ws.column_dimensions['B'].width = 14; ws.column_dimensions['C'].width = 60
ws['A1'] = 'Il gestionale di famiglia'; ws['A1'].font = Font(name='Georgia', bold=True, size=20, color=INK)
ws['A2'] = 'di serenainmente.it · cinque minuti per metterlo in piedi, poi si aggiorna da solo'; ws['A2'].font = SUB
ws['A4'] = 'Oggi'; ws['A4'].font = Font(name=F, bold=True, color=MALVA)
ws['B4'] = '=TODAY()'; ws['B4'].number_format = 'DD/MM/YYYY'; ws['B4'].font = FX
ws['A6'] = 'Da tenere d\'occhio'; ws['A6'].font = Font(name=F, bold=True, size=12, color=INK)
items = [
    ('Scadenze nei prossimi 30 giorni', f"=COUNTIFS(Scadenze!D5:D{4+N_ROWS},\">=0\",Scadenze!D5:D{4+N_ROWS},\"<=30\")", 'Scheda Scadenze: richiami, visite, rinnovi non ancora fatti'),
    ('Scadenze già passate (non fatte)', f"=COUNTIF(Scadenze!D5:D{4+N_ROWS},\"<0\")", 'Vale la pena controllarle oggi'),
    ('Documenti scaduti o in scadenza', f"=COUNTIF(Documenti!F5:F{4+N_ROWS},\"Scaduto\")+COUNTIF(Documenti!F5:F{4+N_ROWS},\"In scadenza\")", 'Scheda Documenti: la cartellina di famiglia'),
    ('Prossima scadenza tra (giorni)', f"=IFERROR(MINIFS_PLACEHOLDER,\"\")", ''),
]
# MINIFS non è garantito ovunque: usiamo SUMPRODUCT/MIN con IF in array-safe via AGGREGATE? Più semplice: MIN sui soli positivi con SUMPRODUCT.
items[3] = ('Prossima scadenza tra (giorni)', f"=IF(COUNTIF(Scadenze!D5:D{4+N_ROWS},\">=0\")=0,\"—\",SUMPRODUCT(MIN(IF(Scadenze!D5:D{4+N_ROWS}>=0,Scadenze!D5:D{4+N_ROWS}))))", 'La più vicina tra quelle ancora da fare')
for i, (lab, f, note) in enumerate(items):
    r = 7 + i
    ws[f'A{r}'] = lab; ws[f'A{r}'].font = Font(name=F, color=INK)
    ws[f'B{r}'] = f; ws[f'B{r}'].font = Font(name=F, bold=True, size=13, color=MALVA); ws[f'B{r}'].alignment = Alignment(horizontal='center')
    ws[f'C{r}'] = note; ws[f'C{r}'].font = Font(name=F, size=9, color=MUTED)
    for col in 'ABC': ws[f'{col}{r}'].border = Border(bottom=thin)
ws.conditional_formatting.add('B7:B9', FormulaRule(formula=['B7>0'], fill=PatternFill('solid', fgColor='FFF0C2')))

ws['A13'] = 'Come si usa'; ws['A13'].font = Font(name=F, bold=True, size=12, color=INK)
guida = [
    ('Famiglia', 'Una riga per persona. L\'età si calcola da sola.'),
    ('Documenti', 'La cartellina: dove sta ogni documento e quando scade. Lo stato si colora da solo.'),
    ('Scadenze', 'Vaccini, visite, rinnovi, iscrizioni. Spunta "Fatto" e sparisce dai promemoria.'),
    ('Visite', 'Prima della visita scrivi le domande, la più importante per prima. Dopo, cosa fare e quando richiamare.'),
    ('Settimana', 'La settimana di tutti, con chi se ne occupa: così non ricorda tutto una persona sola.'),
    ('Contatti', 'Pediatra, guardia medica, nido, nonni. Stampalo e mettilo nella cartellina.'),
    ('Prime volte', 'I ricordi che non vuoi perdere, scritti il giorno stesso.'),
]
for i, (k, v) in enumerate(guida):
    r = 14 + i
    ws[f'A{r}'] = k; ws[f'A{r}'].font = Font(name=F, bold=True, color=MALVA)
    ws[f'C{r}'] = v; ws[f'C{r}'].font = Font(name=F, color=INK); ws[f'C{r}'].alignment = Alignment(wrap_text=True)
    ws.merge_cells(f'A{r}:B{r}')
r = 22
ws[f'A{r}'] = 'Legenda'; ws[f'A{r}'].font = Font(name=F, bold=True, size=12, color=INK)
ws[f'A{r+1}'] = 'Testo blu su righe alternate'; ws[f'A{r+1}'].font = IN; ws[f'C{r+1}'] = 'Celle da compilare'; ws[f'C{r+1}'].font = Font(name=F, color=INK)
ws[f'A{r+2}'] = 'Testo nero'; ws[f'A{r+2}'].font = FX; ws[f'C{r+2}'] = 'Si calcola da solo: non scriverci sopra'; ws[f'C{r+2}'].font = Font(name=F, color=INK)
ws[f'A{r+3}'] = 'Ogni scheda ha una riga di esempio in grigio: cancellala e scrivi i tuoi dati.'; ws[f'A{r+3}'].font = Font(name=F, italic=True, size=9, color=MUTED); ws.merge_cells(f'A{r+3}:C{r+3}')
ws[f'A{r+5}'] = 'Questo file resta sul tuo computer o telefono: nessun dato viene inviato a nessuno. Non sostituisce il pediatra o il medico: per vaccini e terapie il riferimento resta loro.'
ws[f'A{r+5}'].font = Font(name=F, size=9, color=MUTED); ws[f'A{r+5}'].alignment = Alignment(wrap_text=True); ws.merge_cells(f'A{r+5}:C{r+5}'); ws.row_dimensions[r+5].height = 30
ws[f'A{r+6}'] = 'serenainmente.it/guide'; ws[f'A{r+6}'].font = Font(name=F, size=9, color=MALVA, underline='single'); ws[f'A{r+6}'].hyperlink = 'https://serenainmente.it/guide/'

wb.properties.title = 'Il gestionale di famiglia · serenainmente.it'
wb.properties.creator = 'Serena'
os.makedirs(os.path.dirname(OUT), exist_ok=True)
wb.save(OUT)
print(OUT)
