"""Memoria docente. Las tablas y figuras leen la misma simulación que el Excel."""
from functools import partial
from pathlib import Path

import numpy as np
from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from lmm.valuation import estimate

ROOT = Path(__file__).resolve().parents[1]
NAVY = colors.HexColor('#072146')
TEAL = colors.HexColor('#004481')
MUTED = colors.HexColor('#516674')
PALE = colors.HexColor('#EAF4FA')
AQUA = colors.HexColor('#2DCCCD')
WIDTH = 485


def num(x, places=2):
    return f'{x:.{places}f}'.replace('.', ',').replace('-', '−')


def bars(labels, counts, subtitle):
    """Barras horizontales de recuentos con denominador y valor legibles."""
    h = 27 + 20 * len(labels)
    d = Drawing(WIDTH, h)
    d.add(String(0,h-12,subtitle,fontName='BodyBold',fontSize=10,fillColor=NAVY))
    for i, (label, n) in enumerate(zip(labels, counts)):
        y = h-34-20*i
        d.add(String(0,y,label,fontName='Body',fontSize=9,fillColor=NAVY))
        length = 252 * n / max(counts)
        d.add(Rect(120,y-1,length,9,fillColor=TEAL,strokeColor=None))
        d.add(String(127+length,y,str(n),fontName='BodyBold',fontSize=9,fillColor=NAVY))
    return d


def timeline():
    d = Drawing(WIDTH, 54)
    positions = [8, 236, 471]
    d.add(Line(8, 30, 471, 30, strokeColor=AQUA, strokeWidth=2))
    for x, label, anchor in zip(positions, ['Fijamos el Euribor', 'Devengan intereses', 'Pagamos y revisamos el objetivo'],
                               ['start', 'middle', 'end']):
        d.add(Rect(x-2, 27, 5, 6, fillColor=NAVY, strokeColor=None))
        d.add(String(x, 11, label, textAnchor=anchor, fontName='Body', fontSize=9, fillColor=NAVY))
    return d


def pdf(data,s,payload):
    for name,file in [('Body','DejaVuSans'),('BodyBold','DejaVuSans-Bold'),('Serif','DejaVuSerif')]:
        pdfmetrics.registerFont(TTFont(name,f'/usr/share/fonts/truetype/dejavu/{file}.ttf'))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold')
    def sty(name,font,size,leading,color=NAVY,after=8,**extra):
        return ParagraphStyle(name,fontName=font,fontSize=size,leading=leading,textColor=color,spaceAfter=after,**extra)
    styles = dict(body=sty('body','Body',11.7,17.6), title=sty('title','BodyBold',23,29,after=13),
                  section=sty('section','BodyBold',12,17,TEAL,6,spaceBefore=9),
                  tag=sty('tag','BodyBold',9,13,TEAL,9), small=sty('small','Body',9,13,MUTED,6),
                  eq=sty('eq','Body',11.3,19,NAVY,17,backColor=PALE,borderPadding=6,
                         leftIndent=9,rightIndent=9,spaceBefore=15),
                  price=sty('price','BodyBold',40,49,TEAL,3))
    story=[]
    def p(line,style='body'): story.append(Paragraph(line,styles[style]))
    def start(topic,heading):
        if story: story.append(PageBreak())
        p(topic,'tag'); p(heading,'title')
    def table(rows,widths,numeric=False):
        t=Table(rows,colWidths=widths,hAlign='LEFT',repeatRows=1)
        cmds=[('FONTNAME',(0,0),(-1,-1),'Body'),('FONTNAME',(0,0),(-1,0),'BodyBold'),
              ('FONTSIZE',(0,0),(-1,-1),9),('TEXTCOLOR',(0,0),(-1,-1),NAVY),
              ('BACKGROUND',(0,0),(-1,0),PALE),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F6F8F8')]),
              ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
              ('VALIGN',(0,0),(-1,-1),'MIDDLE')]
        if numeric: cmds.append(('ALIGN',(1,0),(-1,-1),'RIGHT'))
        t.setStyle(TableStyle(cmds));story.extend([t,Spacer(1,9)])
    r,cf,pv,cp,pp=estimate(s)
    start('MODELOS DE TIPOS DE INTERÉS   /   VALORACIÓN AL 26.01.2022','¿Cuánto vale hoy el Snowblade?')
    p(num(r['price']),'price')
    p('Valor estimado por cada 100 de nominal','small')
    p('Imaginemos que compramos el derecho a recibir los pagos de esta nota. Conocemos los dos primeros cupones. A partir del tercero, el Euribor modifica el cupón anterior. La evolución de los tipos decide cuánto cobramos y cuándo recuperamos los 100 de principal.')
    p('Cómo llegamos al precio','section')
    p('Partimos de la curva de tipos del día de valoración. Simulamos 200 evoluciones posibles con el modelo de mercado de tipos a plazo (LMM). En cada una aplicamos el contrato semestre a semestre, llevamos los pagos a valor presente y, al final, promediamos los 200 valores.')
    table([['Por cada 100 de nominal','Valor presente medio'],
           ['Devolución del principal',num(r['principal_pv'])],
           ['Cupones netos',num(r['coupon_pv'])],['Total',num(r['price'])]],[322,163],True)
    p('Qué nos dice la descomposición','section')
    p('Con tipos iniciales negativos y muchas devoluciones tempranas, el principal vale en promedio algo más de 100. Los cupones netos restan valor. Para entender por qué, hay que seguir qué ocurre cuando un cupón negativo se arrastra al siguiente semestre.')
    p(f'El intervalo aproximado al 95% va de {num(r["ci95_student"][0])} a {num(r["ci95_student"][1])}. Incluye 100, así que la simulación deja abierta la posibilidad de un valor a la par.','eq')

    start('CONTRATO   /   DEL EURIBOR AL COBRO','¿Qué cobramos cada semestre?')
    p('Al comienzo del semestre fijamos el Euribor 6M. Al cierre pagamos el cupón por los días transcurridos y comprobamos si se ha alcanzado el objetivo. El contrato dura como máximo 20 semestres.')
    story.append(timeline())
    p('Primero calculamos una tasa anual','section')
    p('Los dos primeros semestres pagan un 1% anual. Desde el tercero se conserva la tasa del cupón anterior y se aplica esta regla.')
    p('Tasa nueva = tasa anterior + incremento del semestre − Euribor fijado','eq')
    table([['Semestre','3–4','5–8','9–12','13–16','17–20'],
           ['Incremento','0%','1%','1,25%','1,50%','2%']],[120,71,71,74,75,74])
    p('Después convertimos esa tasa en dinero','section')
    p('Multiplicamos el nominal por la tasa anual y por la fracción de año ACT/365. Para los primeros 181 días cobramos 100 × 1% × 181/365 = 0,4959. El semestre siguiente aporta 0,5041. Tras un año hemos recibido 1 por cada 100.')
    p('El acumulado determina la fecha de devolución','section')
    p('Los cupones negativos reducen el acumulado y su tasa pasa al semestre siguiente. En el primer cierre con al menos 4 por cada 100, cobramos el <b>cupón íntegro</b> más el principal. Si el acumulado pasa de 3,80 a 4,40, ese día recibimos 100,60. Si nunca alcanza 4, recuperamos el principal junto al cupón del semestre 20.')
    p('Fuente: Anexo I y aclaraciones del profesor sobre fijación, devengo, memoria y amortización.','small')

    start('MODELO   /   DE LOS DATOS A LOS ESCENARIOS','¿Cómo simulamos y descontamos?')
    p('1. Leemos los tipos que el mercado implica hoy','section')
    p('Un factor P(0,t) es el precio hoy de una unidad pagadera en t. Interpolamos su logaritmo entre los nodos de la plantilla. La capitalización entre dos fechas da el tipo a plazo: F = [P(0,inicio)/P(0,fin) − 1] / δ, con δ = días/365. Usamos la misma curva para proyectar y descontar.')
    p(f'El primer tipo ya está fijado en {num(100*s.f0[0],4)}%. El siguiente parte de {num(100*s.f0[1],4)}% y usa la primera volatilidad de la plantilla.','small')
    p('2. Movemos juntos los tipos aún pendientes','section')
    p('En cada paso, cada forward combina los mismos tres shocks normales con sus cargas de componentes principales (PCA). Así, dos plazos con cargas similares tienden a moverse juntos. Cada volatilidad escala el movimiento. Simulamos F + 3% como cantidad positiva, lo que permite que F tome valores negativos.')
    p('Aplicamos log-Euler con h=0,5 años y volatilidad constante por forward hasta su fijación. La deriva bajo el bono terminal corrige el movimiento por la covarianza con los forwards posteriores. Para el último forward es cero.')
    p('μᵢ = − Σ<sub>j&gt;i</sub> [δⱼ (Fⱼ + 3%) / (1 + δⱼ Fⱼ)] (λᵢ · λⱼ)','eq')
    p('λᵢ contiene las tres cargas del forward i multiplicadas por su volatilidad. Usamos los shocks y cargas originales, y aniversarios semestrales sin ajuste hábil ni desfase.','small')
    p('3. Expresamos todos los pagos en la misma unidad','section')
    p('Tomamos como unidad el bono B que paga 1 el 26/07/2032, un semestre después del último cupón. En cada fecha reconstruimos B(t) con los forwards vivos. Dividir un pago por B(t) lo expresa en bonos. Multiplicar su media por B(0) devuelve el precio de hoy en dinero.')
    p('Valor por trayectoria = B(0) × suma de [pago(t) / B(t)]','eq')

    start('EJEMPLO   /   TRAYECTORIA 1','Cinco pagos bastan para amortizar')
    p('Seguimos uno de los 200 escenarios con nominal 100. Las dos primeras filas pagan el cupón fijo. Desde la tercera se ve cómo un Euribor negativo eleva la tasa del cupón y adelanta la devolución del principal.')
    n=int(cf.redemption_period[0])
    rows=[['Sem.','Euribor','Tasa cupón','Días','Cupón','Acumulado','Principal']]
    for j in range(n):
        rows.append([str(j+1),num(100*s.fixings[0,j],4)+'%',num(100*cf.rates[0,j],4)+'%',
                     str(int(round(s.delta[j]*365))),num(cf.paid_coupon[0,j],4),
                     num(100*cf.cumulative_paid_fraction[0,j],4),num(cf.paid_principal[0,j],0)])
    table(rows,[40,77,84,39,67,95,83],True)
    p('Semestre 3 · la memoria entra en juego','section')
    p('Partimos del 1% anterior. El incremento es cero y restamos un Euribor de −0,5951%. La nueva tasa es 1,5951%. En 181 días, eso supone 100 × 1,5951% × 181/365 = 0,7910. El acumulado sube de 1,0000 a 1,7910.')
    p('Semestre 5 · el cupón cruza el objetivo','section')
    p('El acumulado sube de 2,9557 a 5,1968. Ese día cobramos 2,2411 de cupón y 100 de principal. El bono terminal vale 1,010283 en la fecha de pago y 0,9738425 hoy. Este flujo aporta 102,2411 × 0,9738425 / 1,010283 = 98,5533 al valor de la trayectoria.')
    p('Sumamos los cinco pagos a valor de hoy','section')
    p(f'{num(cp[0],4)} de cupones + {num(pp[0],4)} de principal = <b>{num(pv[0],4)}</b>','eq')
    p('Los otros quince semestres aportan cero. El total puede reproducirse en Ejemplo!I26. Esta trayectoria cuenta tanto como cada una de las otras 199.','small')

    start('RESULTADOS   /   PRECISIÓN Y LÍMITES','¿Por qué la media queda bajo 100?')
    p(f'La mediana es {num(r["median_path_pv"])} por 100. La media baja a {num(r["price"])} porque unas pocas trayectorias acumulan pérdidas grandes. Alcanzar el objetivo de intereses termina el contrato. En cambio, un cupón negativo puede seguir afectando a los pagos durante años.')
    hist=np.histogram(pv,bins=[-np.inf,0,90,100,110,np.inf])[0]
    story.append(bars(['Menos de 0','De 0 a <90','De 90 a <100','De 100 a <110','110 o más'],hist,
                      'Valor presente por 100 de nominal · número de trayectorias'))
    counts=r['autocall_counts']
    p(f'En {sum(counts[:6])} escenarios ya se ha amortizado al cierre del tercer año. En total, {sum(counts)} alcanzan el objetivo y {r["maturity_no_call_count"]} llegan al vencimiento sin alcanzarlo. En la trayectoria 71 el Euribor sostiene una secuencia de cupones negativos que lleva el valor presente a {num(pv[70])}.')
    p('Qué precisión tienen los 200 escenarios','section')
    p(f'La dispersión entre los valores de las trayectorias da un error estándar de {num(r["standard_error"],4)}. Para el precio de {num(r["price"],4)}, el intervalo t aproximado al 95% es [{num(r["ci95_student"][0],4)}, {num(r["ci95_student"][1],4)}]. Las pérdidas concentradas en pocos escenarios limitan la precisión de esta aproximación.')
    p('Las frecuencias corresponden a la medida de valoración del bono terminal. El intervalo cuantifica el error de muestreo bajo ese modelo. El uso de tres factores y de pasos semestrales también condiciona el resultado.')
    p('Cómo comprobamos el cálculo','section')
    p(f'Al poner la volatilidad a cero, las 200 trayectorias coinciden: amortizan en el semestre 5 y valen {num(payload["sensitivities"]["zero_volatility"]["price"],4)}, igual que al descontar directamente con la curva inicial. Al duplicar el nominal se duplica el precio. Contrastamos en LibreOffice las fórmulas del libro con los resultados de Python.')
    def frame(canvas, doc):
        canvas.setStrokeColor(AQUA); canvas.setLineWidth(1.25); canvas.line(49,793,546,793)
        canvas.setFont('Body',8); canvas.setFillColor(MUTED)
        canvas.drawString(49,29,'AFI   /   Modelos de tipos de interés')
        canvas.drawRightString(546,29,f'Snowblade     {doc.page}')
    dest=ROOT/'entrega/Memoria_Snowblade.pdf'
    SimpleDocTemplate(str(dest),pagesize=A4,leftMargin=49,rightMargin=49,topMargin=60,bottomMargin=49,
                      title='Valoración del Snowblade',author='Ejercicio AFI').build(
        story,onFirstPage=frame,onLaterPages=frame,canvasmaker=partial(Canvas,invariant=1))
    return dest
