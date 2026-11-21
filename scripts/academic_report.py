"""Memoria docente. Las tablas y figuras leen la misma simulación que el Excel."""
from functools import partial
from pathlib import Path

import numpy as np
from reportlab.graphics.shapes import Drawing, Line, PolyLine, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from lmm.valuation import estimate

ROOT = Path(__file__).resolve().parents[1]
NAVY = colors.HexColor('#18354B')
TEAL = colors.HexColor('#08796D')
MUTED = colors.HexColor('#516674')
PALE = colors.HexColor('#E8F2F0')
RUST = colors.HexColor('#A34A2C')
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


def rate_plot(s, cf):
    d = Drawing(WIDTH,132)
    for k, p in enumerate([0,70]):
        n = int(cf.redemption_period[p])
        left = 35+244*k
        w = 174
        series = [100*s.fixings[p,:n],100*cf.rates[p,:n]]
        lo,hi = (-2,5) if p==0 else (-100,15)
        def y(v): return 25 + 66*(v-lo)/(hi-lo)
        d.add(String(left,111,f'Trayectoria {p+1}',fontName='BodyBold',fontSize=10,fillColor=NAVY))
        for v in [lo,0,hi]:
            d.add(Line(left,y(v),left+w,y(v),strokeColor=colors.HexColor('#D6DDDF'),strokeWidth=.6))
            d.add(String(left-4,y(v)-3,str(v)+'%',textAnchor='end',fontName='Body',fontSize=7,fillColor=MUTED))
        for vals,c in zip(series,[NAVY,RUST]):
            points=[a for j,v in enumerate(vals) for a in (left+j*w/(n-1),y(v))]
            d.add(PolyLine(points,strokeColor=c,strokeWidth=1.8))
        d.add(String(left,10,'Sem. 1',fontName='Body',fontSize=8,fillColor=MUTED))
        d.add(String(left+w,10,f'Sem. {n}',textAnchor='end',fontName='Body',fontSize=8,fillColor=MUTED))
    return d


def pdf(data,s,payload):
    for name,file in [('Body','DejaVuSans'),('BodyBold','DejaVuSans-Bold'),('Serif','DejaVuSerif')]:
        pdfmetrics.registerFont(TTFont(name,f'/usr/share/fonts/truetype/dejavu/{file}.ttf'))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold')
    def sty(name,font,size,leading,color=NAVY,after=8,**extra):
        return ParagraphStyle(name,fontName=font,fontSize=size,leading=leading,textColor=color,spaceAfter=after,**extra)
    styles = dict(body=sty('body','Body',11,16.5), title=sty('title','Serif',25,31,after=13),
                  section=sty('section','BodyBold',12,17,TEAL,6,spaceBefore=9),
                  tag=sty('tag','BodyBold',9,13,TEAL,9), small=sty('small','Body',9,13,MUTED,6),
                  eq=sty('eq','Body',11.3,19,NAVY,17,backColor=PALE,borderPadding=6,
                         leftIndent=9,rightIndent=9,spaceBefore=15),
                  price=sty('price','Serif',38,47,TEAL,3))
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
    start('VALORACIÓN DE TIPOS DE INTERÉS  /  AFI','¿Cuánto vale hoy el Snowblade?')
    p(num(r['price']),'price')
    p('por 100 de nominal · valoración a 26 de enero de 2022','small')
    p('El Snowblade devuelve 100 al amortizar y paga cupones semestrales ligados al Euribor. Cada cupón conserva la memoria del anterior. El contrato termina cuando los intereses efectivos acumulados alcanzan el 4% del nominal, con un plazo máximo de diez años.')
    p('De dónde sale el precio','section')
    table([['Componente','PV por 100'],['Devolución del principal',num(r['principal_pv'])],
           ['Cupones netos',num(r['coupon_pv'])],['Valor total',num(r['price'])]],[340,145],True)
    p('Los tipos cortos iniciales son negativos y muchos principales se devuelven pronto. En esta muestra, su valor presente medio supera 100. En algunas trayectorias largas el Euribor sube y se encadenan cupones negativos. Su coste lleva el precio estimado a 98,27.')
    p('Qué precisión aporta la muestra','section')
    p(f'El error estándar es {num(r["standard_error"])} por 100. El intervalo Monte Carlo aproximado al 95% va de {num(r["ci95_student"][0])} a {num(r["ci95_student"][1])} e incluye la par. Con estos 200 escenarios, la distancia estimada a 100 queda dentro de la incertidumbre de muestreo.')
    p('Para seguir el cálculo','section')
    p('Las páginas 2–4 construyen el contrato y el modelo. La página 5 sigue cinco pagos de una trayectoria hasta su valor actual. Las páginas 6–7 interpretan los 200 resultados y comprueban la valoración.')
    p('En Excel · Resumen!B2 muestra el precio para el nominal de Resumen!F4. La segunda pestaña, Ejemplo, desarrolla la trayectoria 1.','small')

    start('01  /  CONTRATO','¿Qué se paga cada semestre?')
    p('Al inicio de cada semestre se observa el Euribor 6M. Al final se liquida el cupón correspondiente. El primer y el segundo cupón tienen una tasa anual fija del 1%. A partir del tercero intervienen la tasa anterior, el incremento contractual y el Euribor fijado.')
    p('Tasa del cupón j = tasa anterior + incremento del semestre − Euribor 6M','eq')
    table([['Semestre','1–2','3–4','5–8','9–12','13–16','17–20'],
           ['Regla','Fijo 1%','+0%','+1%','+1,25%','+1,50%','+2%']],[85,63,60,58,72,74,73])
    p('Del tipo anual al dinero','section')
    p('Para un nominal H y una tasa anual c, el pago es H × c × días/365. El primer semestre tiene 181 días. Por cada 100 de nominal, el primer cobro asciende a 100 × 1% × 181/365 = 0,4959. El semestre siguiente aporta 0,5041. Al cabo del primer año se ha acumulado 1,00 por 100.')
    p('Cuándo se termina el contrato','section')
    p('Sumamos los cupones efectivos desde el origen, incluyendo los importes negativos. Al primer cierre con un acumulado de al menos 4 por 100, se paga el cupón completo junto al principal. Si el acumulado pasa de 3,80 a 4,40 con un cupón de 0,60, la liquidación de ese día es 100,60. A partir de entonces todos los flujos son cero.')
    p('Si el acumulado sigue por debajo del objetivo, el contrato continúa. Una tasa negativa genera un pago a cargo del inversor y se conserva como base del semestre siguiente. Si la estructura sigue viva en el periodo 20, devuelve el principal con el último cupón.')
    p('Fuente contractual · Anexo I del enunciado y aclaraciones del profesor sobre fijación al inicio, ACT/365, memoria negativa, objetivo neto y cupón íntegro. En Excel, Flujos recoge cada evento.','small')

    start('02  /  DATOS DE MERCADO','¿Cómo arrancan los forwards?')
    p('La plantilla aporta una curva de descuento, volatilidades y tres componentes principales. En el esquema monocurva usamos la misma curva para extraer los tipos iniciales y para construir los bonos que intervienen en el descuento.')
    p('Un semestre visto desde hoy','section')
    p('P(0,t) es el precio hoy de una unidad pagadera en t. Entre los 70 nodos suministrados interpolamos el logaritmo del factor de descuento, como en el modo 0 de CInterPol. Dividir dos factores consecutivos da la capitalización implícita del semestre.')
    p('F<sub>i</sub>(0) = [P(0,t<sub>i</sub>)/P(0,t<sub>i+1</sub>) − 1] / δ<sub>i</sub>      ·      δ<sub>i</sub> = días del semestre / 365','eq')
    p(f'En el primer semestre P(0,t₀) = 1 y P(0,t₁) = {num(s.p0[1],7)}. La división anterior da {num(s.f0[0]*100,4)}% anual. Ese tipo ya está fijado. El primer forward futuro parte de {num(s.f0[1]*100,4)}% y recibe la primera volatilidad, {num(data.vols[0]*100,0)}%.')
    p('Cómo se mueve toda la curva con tres shocks','section')
    p('En cada paso de cada trayectoria se leen tres normales de la plantilla. Cada forward combina esas mismas normales con sus tres cargas. Dos forwards con cargas parecidas responden de forma parecida al mismo shock. La volatilidad de cada plazo determina la amplitud del movimiento.')
    a=data.loadings[0]; z=data.normals[:,0,0]
    table([['Primer paso, trayectoria 1','Factor 1','Factor 2','Factor 3'],
           ['Cargas del primer forward',*[num(x,4) for x in a]],
           ['Normales suministradas',*[num(x,4) for x in z]]],[227,86,86,86],True)
    p(f'El producto escalar de ambas filas da {num(a@z,4)}. Al multiplicarlo por la volatilidad y por √0,5 se obtiene la contribución aleatoria al cambio logarítmico. Se emplean los 12.000 datos originales: tres factores en veinte pasos para cada una de las 200 trayectorias.')
    p('En Excel · Curva y Calendario producen los forwards iniciales. PCA contiene las cargas de Correlaciones!G117:I136. Volatilidades identifica las filas F9:F28 de la plantilla.','small')

    start('03  /  SIMULACIÓN Y DESCUENTO','¿Cómo llevamos un flujo a hoy?')
    p('Elegimos como unidad de cuenta el bono que paga 1 el 26/07/2032, seis meses después del último cupón. Si el bono vale B(t) en una fecha de pago, un flujo de 100 equivale entonces a 100/B(t) bonos. Bajo la medida asociada a ese bono podemos promediar esas cantidades y convertirlas a valor de hoy con B(0).')
    p('Simular en la medida de ese bono','section')
    p('El desplazamiento s = 3% permite que el forward F sea negativo mientras X = F + s evoluciona como variable positiva. Para el plazo i, el vector λᵢ es su volatilidad por sus tres cargas. El cambio desde la medida propia de ese forward hasta la medida terminal introduce la deriva μᵢ.')
    p('dXᵢ / Xᵢ = μᵢ du + λᵢ · dW*<br/>μᵢ = − Σ<sub>j=i+1</sub><super>20</super> [δⱼ (Fⱼ + s) / (1 + δⱼ Fⱼ)] (λᵢ · λⱼ)','eq')
    p('W* es el movimiento browniano de tres factores bajo la medida terminal. La suma recoge la covarianza con los forwards posteriores. Para el último forward la suma está vacía y la deriva vale cero. El denominador usa Fⱼ porque procede de la capitalización del bono.')
    p('Actualizar solo los forwards pendientes de fijación','section')
    p('Xᵢ(u+h) = Xᵢ(u) exp[(μᵢ − ½ ‖λᵢ‖²)h + √h (λᵢ · Z)]','eq')
    p('En cada paso log-Euler calculamos las derivas con la curva al inicio del paso. Avanzamos h=0,5 años de simulación y congelamos el tipo al fijarse. El devengo del cupón usa los días reales de su semestre.')
    p('Valorar los pagos de cada trayectoria','section')
    p('B(tₘ) = ∏<sub>j=m</sub><super>20</super> (1 + δⱼ Fⱼ(tₘ))<super>−1</super><br/>PV de la trayectoria = B(0) × Σ<sub>m=1</sub><super>20</super> [flujo(tₘ) / B(tₘ)]','eq')
    p(f'B(0) = {num(s.initial_terminal,7)}. En el último pago todavía queda un semestre hasta que vence el bono. El precio inicial es la media de los 200 PV. En Excel, Estados genera los forwards y Flujos!L:O aplica el descuento.','small')

    start('04  /  EJEMPLO NUMÉRICO','Una trayectoria de principio a fin')
    p('Seguimos la trayectoria 1 con nominal 100. Cada fila corresponde a un pago mientras el instrumento está vivo. Las tasas son anuales. Los cupones y el acumulado se muestran en unidades monetarias por 100 de nominal.')
    n=int(cf.redemption_period[0])
    rows=[['Sem.','Euribor','Tasa cupón','Días','Cupón','Acumulado','Principal']]
    for j in range(n):
        rows.append([str(j+1),num(100*s.fixings[0,j],3)+'%',num(100*cf.rates[0,j],3)+'%',
                     str(int(round(s.delta[j]*365))),num(cf.paid_coupon[0,j],4),
                     num(100*cf.cumulative_paid_fraction[0,j],4),num(cf.paid_principal[0,j],0)])
    table(rows,[39,67,81,38,78,93,89],True)
    p('Semestre 3 · aparece la memoria','section')
    p('La tasa anterior era 1% y el incremento contractual es cero. Restar un Euribor de −0,5951% lleva la tasa a 1,5951%. El pago resulta 100 × 1,5951% × 181/365 = 0,7910. Así pasa el acumulado de 1,0000 a 1,7910.')
    p('Semestre 5 · se cruza el objetivo','section')
    p('El acumulado pasa de 2,9557 a 5,1968. El flujo del día es 102,2411, suma de 100 de principal y 2,2411 de cupón. El bono terminal vale 1,010283. La aportación de este pago al estimador es 102,2411 × 0,9738425 / 1,010283 = 98,5533.')
    p('Sumar los cinco flujos valorados','section')
    p(f'{num(cp[0],4)} de cupones + {num(pp[0],4)} de principal = <b>{num(pv[0],4)}</b>','eq')
    p('Este valor aporta una observación a la media Monte Carlo. Los quince semestres restantes tienen pago cero. Puede verificarse fila a fila en Ejemplo!A5:I9 y contrastarse el total de Ejemplo!I26 con Paths!D2.','small')

    start('05  /  RESULTADOS','¿Por qué la media queda bajo la par?')
    p(f'La mediana de los PV es {num(r["median_path_pv"])} y la media, {num(r["price"])}. El producto cancela pronto cuando el acumulado sube. Cuando el Euribor supera de forma sostenida los incrementos, la memoria puede encadenar pagos negativos y prolongar la vida del contrato.')
    story.append(rate_plot(s,cf))
    p('Euribor 6M en azul y tasa anual de cupón en terracota. Cada panel termina en la amortización y usa su propia escala vertical.','small')
    counts=r['autocall_counts']
    story.append(bars(['Semestres 1–4','Semestre 5','Semestre 6','Semestres 7–20','Sin autocancelar'],
                      [sum(counts[:4]),counts[4],counts[5],sum(counts[6:]),r['maturity_no_call_count']],
                      'Momento de cancelación · trayectorias de un total de 200'))
    boundaries=[-np.inf,0,90,100,110,np.inf]
    hist=np.histogram(pv,bins=boundaries)[0]
    story.append(bars(['PV < 0','0 ≤ PV < 90','90 ≤ PV < 100','100 ≤ PV < 110','PV ≥ 110'],hist,
                      'Distribución del valor presente · unidades por 100 de nominal'))
    p(f'La trayectoria 71 llega a vencimiento. Sus cupones valen {num(cp[70])} y su principal {num(pp[70])}, lo que da un PV de {num(pv[70])}. En total, {r["negative_coupon_paths"]} trayectorias pagan algún cupón negativo y {r["negative_pv_paths"]} tienen PV negativo. Las 200 contribuyen al precio.')
    p(f'Al terminar el tercer año han cancelado {sum(counts[:6])} de 200 trayectorias. La vida media es {num(r["expected_life_years_Q_terminal"])} años. Ambas cifras se estiman bajo la medida del bono terminal.','small')

    start('06  /  DECISIONES Y VALIDACIÓN','¿Qué respalda el resultado?')
    p('Condiciones recibidas y decisiones propias','section')
    p('<b>Enunciado y plantilla.</b> Valoramos por Monte Carlo con LMM monocurva desplazado, el bono terminal y las componentes y normales originales.')
    p('<b>Aclaraciones del profesor.</b> El Euribor se fija al inicio. Los cupones negativos reducen el acumulado y se trasladan al siguiente semestre. En la cancelación se paga el cupón íntegro. El devengo es ACT/365 y el reloj de difusión avanza de 0,5 en 0,5.')
    p('<b>Elecciones de implementación.</b> Usamos aniversarios semestrales sin ajuste hábil ni desfase, volatilidad constante de cada forward hasta fijación y log-Euler. El bono terminal a 10,5 años es una elección admitida. El semestre auxiliar sirve para construir ese bono.')
    p('Tres comprobaciones con significado económico','section')
    p(f'<b>1. Apagar la volatilidad.</b> Todas las trayectorias pasan a ser idénticas, cancelan en el semestre 5 y valen {num(payload["sensitivities"]["zero_volatility"]["price"],4)}. El descuento directo con la curva inicial reproduce ese valor.')
    p('<b>2. Contrastar el cambio de medida.</b> Los 230 contrastes de bonos tienen |z| máximo de 2,03. En 60 caplets valorados también con shifted-Black, el máximo es 1,83. La comparación se expresa en errores estándar Monte Carlo.')
    p('<b>3. Reconciliar el camino completo.</b> Una implementación escalar independiente del cálculo vectorizado reproduce los 200 PV con diferencia máxima inferior a 3 × 10⁻¹³. El recálculo externo del Excel comprueba también los casos de volatilidad cero y nominal doble.')
    p('Alcance de la cifra','section')
    p(f'Con 200 trayectorias, el error estándar es la desviación muestral de los 200 PV dividida por √200. El intervalo usa un cuantil t con 199 grados de libertad. La concentración de pérdidas en pocas trayectorias limita esa aproximación. La reducción a tres factores, la malla semestral y las convenciones añaden incertidumbre de modelo.')
    p(f'Conciliación por 100 · precio {num(r["price"],4)} · error estándar {num(r["standard_error"],4)} · IC aproximado [{num(r["ci95_student"][0],4)}; {num(r["ci95_student"][1],4)}].','small')
    def frame(canvas, doc):
        canvas.setStrokeColor(TEAL); canvas.setLineWidth(1.25); canvas.line(49,793,546,793)
        canvas.setFont('Body',8); canvas.setFillColor(MUTED)
        canvas.drawString(49,29,'AFI   /   Modelos de tipos de interés')
        canvas.drawRightString(546,29,f'Snowblade     {doc.page}')
    dest=ROOT/'entrega/Memoria_Snowblade.pdf'
    SimpleDocTemplate(str(dest),pagesize=A4,leftMargin=49,rightMargin=49,topMargin=60,bottomMargin=49,
                      title='Valoración del Snowblade',author='Ejercicio AFI').build(
        story,onFirstPage=frame,onLaterPages=frame,canvasmaker=partial(Canvas,invariant=1))
    return dest
