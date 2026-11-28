from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from lmm.inputs import load_inputs
from lmm.model import simulate, drift
from lmm.valuation import estimate
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.graphics.shapes import Drawing, String, Line, Rect, PolyLine, Circle

data = load_inputs()
s = simulate(data)
r, cf, pv, cp, pp = estimate(s)
W = 477
NAVY = colors.HexColor('#18374B')
TEAL = colors.HexColor('#087D70')
BLUE = colors.HexColor('#255F89')
INK = colors.HexColor('#263A46')
MUTED = colors.HexColor('#546B78')
PALE = colors.HexColor('#EAF4F2')
LIGHT = colors.HexColor('#EDF3F8')
RUST = colors.HexColor('#A34B32')
RULE = colors.HexColor('#D9E4E6')
WHITE = colors.white
for name, file in [('Body','DejaVuSans'),('Bold','DejaVuSans-Bold'),('Serif','DejaVuSerif')]:
    pdfmetrics.registerFont(TTFont(name, f'/usr/share/fonts/truetype/dejavu/{file}.ttf'))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='Bold')

def style(name, font='Body', size=10.8, leading=16.4, color=INK, after=8, **kw):
    return ParagraphStyle(name, fontName=font,fontSize=size,leading=leading,textColor=color,spaceAfter=after,**kw)

styles = {
    'body':style('body'),
    'title':style('title','Serif',24,29,NAVY,13),
    'tag':style('tag','Bold',9,12,TEAL,8),
    'h':style('h','Bold',12,16,TEAL,6,spaceBefore=8),
    'small':style('small',size=9.1,leading=13,color=MUTED,after=6),
    'formula':style('formula','Body',11.2,20,NAVY,16,backColor=LIGHT,borderPadding=8,leftIndent=9,rightIndent=9,spaceBefore=9),
    'call':style('call','Body',10.5,15,TEAL,12,backColor=PALE,borderPadding=8,leftIndent=9,rightIndent=9,spaceBefore=8),
    'cell':style('cell',size=9.2,leading=13,after=0),
    'th':style('th','Bold',8.7,11.5,NAVY,0),
}
story=[]
chapter=0
def p(t, kind='body'):
    story.append(Paragraph(t,styles[kind]))
def h(t): p(t,'h')
def eq(t): p(t,'formula')
def note(t): p(t,'call')
def start(tag,title):
    global chapter
    if story: story.append(PageBreak())
    chapter+=1
    p(f'{chapter:02d}  /  {tag}','tag')
    p(title,'title')
def n(v,dec=4): return f'{v:.{dec}f}'.replace('.',',').replace('-','−')
def pct(v,dec=4): return n(v*100,dec)+'%'
def tab(rows,widths,highlight=(),numeric=False):
    cells = [[Paragraph(str(v),styles['th' if i==0 else 'cell']) for v in row] for i,row in enumerate(rows)]
    t=Table(cells,colWidths=widths,hAlign='LEFT')
    cmds=[('BACKGROUND',(0,0),(-1,0),LIGHT),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
          ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
          ('LINEBELOW',(0,0),(-1,0),0.7,RULE),('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE,colors.HexColor('#F6F8F9')])]
    for row in highlight: cmds.append(('BACKGROUND',(0,row),(-1,row),PALE))
    t.setStyle(TableStyle(cmds))
    story.extend([t,Spacer(1,9)])

start('EL PROBLEMA','De 100 de nominal a un valor de 98,27')
p('Imagina que compras un instrumento con nominal 100. El emisor te devuelve esos 100 al terminar el contrato. Mientras tanto, paga cupones cada seis meses. El importe de esos cupones y la duración de la inversión van a depender del Euribor.')
p('El ejercicio pide calcular cuánto vale hoy ese derecho a recibir y, en algunos escenarios, pagar dinero. La fecha de valoración es el 26 de enero de 2022, según los datos de la plantilla.')
h('El contrato en una línea temporal')
d=Drawing(W,110)
d.add(Line(22,62,450,62,strokeColor=RULE,strokeWidth=2))
for x,top,bottom in [(22,'Hoy','26/01/22'),(126,'Sem. 1','Cupón fijo'),(230,'Sem. 2','Cupón fijo'),(334,'Sem. 3','Cupón variable'),(450,'Sem. 20','Vencimiento')]:
    d.add(Circle(x,62,4,fillColor=TEAL,strokeColor=None))
    anchor='start' if x==22 else 'end' if x==450 else 'middle'
    d.add(String(x,80,top,fontName='Bold',fontSize=9,textAnchor=anchor,fillColor=NAVY))
    d.add(String(x,43,bottom,fontName='Body',fontSize=8.2,textAnchor=anchor,fillColor=MUTED))
d.add(String(232,14,'Esquema no a escala · Si alcanza el objetivo del 4%, termina antes.',fontName='Body',fontSize=9,textAnchor='middle',fillColor=TEAL))
story.append(d)
h('¿Qué tenemos que calcular?')
p('Para cada historia posible de los tipos, identificamos los cupones y cuándo se devuelve el principal. Después valoramos los flujos de esa historia y hacemos una media. El LMM (LIBOR Market Model) nos sirve para generar historias conjuntas de tipos forward.')
tab([['Recorrido','Páginas'],['Entender contrato y curva','2–3'],['Simular curvas mediante LMM','4–8'],['Reconstruir una valoración y entender el precio','9–10'],['Repaso para defender el ejercicio','11']],[365,112])
note('<b>Pregunta que guía toda la lectura.</b> ¿Cómo pasar de conocer una curva de tipos hoy a valorar un contrato cuyos pagos y fecha final aún desconocemos?')

start('EL CONTRATO','Los dos primeros pagos y la memoria')
p('Durante el primer año la tasa anual es fija: 1%. Un 1% sobre 100 representa una unidad al año. Para saber qué corresponde a cada semestre usamos los días efectivos divididos por 365 (ACT/365).')
tab([['Pago','Días','Tasa anual','Importe','Acumulado'],['26/07/22','181','1%','0,4959','0,4959'],['26/01/23','184','1%','0,5041','1,0000']],[113,55,100,101,108],highlight=(2,))
h('El tercer semestre cambia la regla')
p('A partir de entonces el cupón anual cⱼ se obtiene de la tasa anterior, del incremento previsto bⱼ y del Euribor 6M rⱼ fijado al comienzo del semestre. δⱼ₋₁ es la fracción ACT/365 de dicho semestre.')
eq('c<sub>j</sub> = c<sub>j−1</sub> + b<sub>j</sub> − r<sub>j</sub><br/>Cupón efectivo = 100 × c<sub>j</sub> × δ<sub>j−1</sub>')
tab([['Semestre j','3–4','5–8','9–12','13–16','17–20'],['Incremento b','0%','1%','1,25%','1,50%','2%']],[112,73,73,73,73,73])
p('En una trayectoria del ejercicio, el Euribor del tercer semestre es −0,5951%. Antes de hacer la cuenta, ¿sube o baja el cupón? Sube: 1% − (−0,5951%) = 1,5951%. Multiplicamos por 100 y por 181/365: cobramos 0,7910.')
h('¿Qué ocurre cuando acumulamos cuatro unidades?')
p('La estructura devuelve 100 y paga el cupón íntegro del semestre que hace cruzar el objetivo. Los cupones negativos cuentan como pagos del inversor, restan del acumulado y su tasa se conserva para el semestre siguiente. Si sigue viva, amortiza en el semestre 20.')
note('<b>Memoria:</b> conocer solo el Euribor actual resulta insuficiente. El cupón depende de la tasa anterior, y la supervivencia depende de todo el acumulado.')

start('LA CURVA INICIAL','¿Por qué no basta con conocer el Euribor de hoy?')
p('Cuando contratamos el Snowblade conocemos el Euribor del primer semestre y una curva de precios de mercado. Lo que no conocemos es el Euribor que se observará dentro de seis meses, un año o cinco años.')
h('Construir un forward a partir de dos bonos')
p('P(0,t) es el precio hoy de un bono que paga 1 en la fecha t. Por ejemplo, para invertir desde t₁ hasta t₂, podemos usar el cociente de dos precios de bonos. Ese cociente determina la capitalización implícita entre las dos fechas.')
eq('1 + δ<sub>i</sub> F<sub>i</sub>(0) = P(0,t<sub>i</sub>) / P(0,t<sub>i+1</sub>)<br/>F<sub>i</sub>(0) = [P(0,t<sub>i</sub>)/P(0,t<sub>i+1</sub>) − 1] / δ<sub>i</sub>')
tab([['Fecha','Tiempo','P(0,t)'],['26/01/22','t₀',n(s.p0[0],8)],['26/07/22','t₁',n(s.p0[1],8)],['26/01/23','t₂',n(s.p0[2],8)]],[170,90,217])
p(f'Con δ₁ = 184/365 obtenemos F₁(0) = ({n(s.p0[1],8)} / {n(s.p0[2],8)} − 1) / (184/365) = <b>{pct(s.f0[1])}</b>. Es la tasa forward inicial del semestre que empezará en julio de 2022.')
h('Forward de hoy frente al fixing futuro')
p('F₁(0) se conoce hoy. F₁(t₁) será el Euribor observado al comenzar ese semestre. En la trayectoria 1 resulta −0,8638%. Los dos valores pueden diferir porque entre ambas fechas cambia el mercado.')
note('<b>Decisión monocurva.</b> Usamos la misma curva para proyectar forwards y representar bonos de descuento. La plantilla trae 70 nodos; interpolamos logaritmos de factores de descuento entre ellos. Los descuentos superiores a 1 son compatibles con tipos negativos.')

start('QUÉ SIMULAMOS','Una película de curvas, no un único tipo')
p('El LMM modeliza los tipos forward de todos los periodos futuros de forma conjunta. Un paso de simulación hace avanzar seis meses el reloj. Al final de ese paso se observa el forward que empieza en esa fecha y se guarda su fixing.')
h('Una esquina de la trayectoria 1')
rows=[['Fecha','F₀: sem. 1','F₁: sem. 2','F₂: sem. 3','F₃: sem. 4','F₄: sem. 5']]
for k in range(5):
    rows.append([f't{k}']+[pct(s.states[k,0,i],3) if i>=k else 'Fijado' for i in range(5)])
cells=[[Paragraph(str(v),styles['th' if i==0 else 'cell']) for v in row] for i,row in enumerate(rows)]
t=Table(cells,colWidths=[58,83,84,84,84,84])
cmd=[('BACKGROUND',(0,0),(-1,0),LIGHT),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),11),('BOTTOMPADDING',(0,0),(-1,-1),11),('LINEBELOW',(0,0),(-1,0),.6,RULE)]
for k in range(5):
    cmd.append(('BACKGROUND',(k+1,k+1),(k+1,k+1),colors.HexColor('#C5E6DF')))
    if k: cmd.append(('BACKGROUND',(1,k+1),(k,k+1),colors.HexColor('#F1F4F5')))
t.setStyle(TableStyle(cmd));story.extend([t,Spacer(1,8)])
p('Verde: fixing que se utiliza ese día. Gris: tipos cuyo periodo ya ha empezado. Los tipos de la derecha todavía cambian. t₀ es hoy, t₁ es julio de 2022 y así sucesivamente.','small')
p('Para el tercer cupón necesitamos F₂(t₂): aparece en la diagonal, con valor −0,5951%. La tasa del cupón se obtiene restándole este fixing a la tasa anterior, tal como hicimos en la página 2.')
h('¿Por qué importa mover toda la curva?')
p('La estructura depende de las relaciones entre tipos de distintos plazos. Además, al valorar un pago futuro necesitaremos saber cuánto vale en ese momento el bono terminal. Ese bono depende de los forwards aún vivos.')
note('<b>Control de índices.</b> F₀ es el spot inicial, conocido, y carece de volatilidad. F₁…F₂₀ son los forwards futuros. Solo F₀…F₁₉ pueden fijar cupones: F₂₀ se utiliza para llegar hasta el bono terminal de 10,5 años.')

start('LOS MOVIMIENTOS DE MERCADO','¿Cómo hacemos que los forwards se muevan juntos?')
p('Si simuláramos cada tipo de forma independiente, destruiríamos parte de la dependencia entre plazos. La plantilla nos da tres factores comunes de ruido y una combinación de esos factores para cada forward.')
eq('λ<sub>i</sub> = σ<sub>i</sub> a<sub>i</sub> &nbsp;&nbsp; | &nbsp;&nbsp; shock = λ<sub>i</sub> · Z<br/>Z = (Z₁, Z₂, Z₃), normales estándar independientes')
p('aᵢ contiene las tres cargas PCA del forward i. σᵢ es su volatilidad. Al compartir Z, dos forwards tienen covarianza instantánea λᵢ · λⱼ. Si sus cargas se parecen, reaccionan de forma parecida.')
h('El primer movimiento, con datos del ejercicio')
z=data.normals[:,0,0]; a=data.loadings[0]; lam=s.diffusion[1]
tab([['F₁ / paso 1 / trayectoria 1','Factor 1','Factor 2','Factor 3'],['Cargas a₁',*[n(v) for v in a]],['Normales Z',*[n(v) for v in z]],['Producto carga × normal',*[n(v) for v in a*z]]],[207,90,90,90])
p(f'Sumamos los tres productos: a₁ · Z = {n(a@z)}. Con σ₁ = 21%, λ₁ · Z = {n(lam@z)}. Al avanzar medio año, √0,5 × λ₁ · Z = {n(np.sqrt(.5)*(lam@z),6)}. Este valor es una contribución al cambio logarítmico, no un cambio en puntos porcentuales de Euribor.')
h('Por qué el modelo desplaza los tipos')
p('Los datos iniciales contienen forwards negativos. El modelo lognormal ordinario requiere una variable positiva. Definimos Xᵢ = Fᵢ + s, con s = 3 puntos porcentuales. F₁(0) = −0,4125% se convierte en X₁(0) = 2,5875%. Modelizamos X y recuperamos F restando el shift.')
note('<b>Qué significa la reducción PCA.</b> Usamos las cargas ya suministradas, con norma unitaria por fila, y las mismas covarianzas en difusión y deriva. En total hay 3 × 20 × 200 = 12.000 normales. La aproximación a tres factores conserva parte de la estructura de dependencia.')

start('EL NUMERARIO','Un bono como unidad de medida')
p('Supón que en una fecha futura recibimos 102,2411. Si ese día una participación de un activo cuesta 1,010283, el pago equivale a 102,2411 / 1,010283 participaciones. Ese cambio de unidad no altera su valor en ese instante.')
h('¿Qué activo elegimos en el ejercicio?')
p('Elegimos el bono cupón cero que paga una unidad el 26/07/2032, seis meses después del último pago posible. Denotamos su precio B(t) = P(t,t₂₁). No es un bono ligado al Euribor: abona una unidad fija en su vencimiento.')
d=Drawing(W,117)
for x,tt,txt,col in [(0,'Pago futuro','102,2411',BLUE),(169,'Unidades de bono','101,2005',TEAL),(338,'Contribución hoy','98,5533',TEAL)]:
    d.add(Rect(x,28,139,66,fillColor=LIGHT if x==0 else PALE,strokeColor=None))
    d.add(String(x+69.5,75,tt,fontName='Bold',fontSize=8.8,fillColor=NAVY,textAnchor='middle'))
    value=101.200522 if x==169 else 0
    shown= n((cf.paid_coupon[0,4]+100)/s.terminal_bonds[0,4],4) if x==169 else txt
    d.add(String(x+69.5,46,shown,fontName='Bold',fontSize=17,fillColor=col,textAnchor='middle'))
for x in [139,308]:
    d.add(Line(x+3,61,x+27,61,strokeColor=MUTED,strokeWidth=1.2))
    d.add(Line(x+22,65,x+27,61,strokeColor=MUTED));d.add(Line(x+22,57,x+27,61,strokeColor=MUTED))
d.add(String(154,15,'÷ B(t₅)',fontName='Body',fontSize=8,fillColor=MUTED,textAnchor='middle'))
d.add(String(323,15,'× B(0)',fontName='Body',fontSize=8,fillColor=MUTED,textAnchor='middle'))
story.append(d)
p('El dibujo usa el quinto pago de la trayectoria 1. B(0) = 0,9738425 y B(t₅) = 1,010283. El precio futuro de ese bono cambia con la curva simulada.')
h('La idea de valoración')
p('Si elegimos B como numerario, existe una medida de valoración asociada Q* bajo la cual los precios de activos sin pagos intermedios, expresados en unidades de B, son martingalas. Esto significa que su valor futuro esperado, condicionado a la información de hoy y medido en bonos, coincide con su valor actual. Así podemos valorar cada pago futuro por separado y sumar.')
eq('V(0) = B(0) E<super>Q*</super>[ Σ<sub>m=1</sub><super>20</super> CF<sub>m</sub> / B(t<sub>m</sub>) ]')
p('CFₘ incluye cupón y principal cuando corresponda, con cero después de cancelar. El cálculo de una sola trayectoria es una contribución aleatoria al estimador. El precio aparece al promediar todas ellas.')
note('<b>Consecuencia crucial.</b> La medida Q* determina tanto la dinámica de los forwards como la forma de valorar los pagos. Cambiar el numerario obliga a cambiar ambos de manera coherente.')

start('LA DERIVA TERMINAL','¿De dónde sale la suma de la deriva?')
p('Esta página contiene la demostración matemática. El punto de partida es que los precios de bonos divididos por el numerario deben ser martingalas bajo Q*. Trabajamos antes del fixing de Fᵢ.')
h('1. Relacionar el forward con dos bonos')
p('Sea Rᵢ(t) = P(t,tᵢ)/B(t). Por la relación de la página 3, tenemos Rᵢ = (1 + δᵢFᵢ)Rᵢ₊₁. Repetimos la identidad desde el siguiente forward hasta el último, dado que R₂₁ = 1.')
eq('R<sub>i+1</sub> = ∏<sub>j=i+1</sub><super>20</super> (1 + δ<sub>j</sub>F<sub>j</sub>)')
h('2. Obtener la parte aleatoria del producto')
p('Proponemos dFᵢ = (Fᵢ+s)(μᵢ du + λᵢ·dW*), donde W* es un browniano de tres factores bajo Q*. La difusión relativa del término 1+δⱼFⱼ es wⱼλⱼ, con wⱼ = δⱼ(Fⱼ+s)/(1+δⱼFⱼ). Por la regla del producto, la difusión relativa de Rᵢ₊₁ es la suma βᵢ₊₁ = Σⱼ&gt;ᵢ wⱼλⱼ.')
h('3. Imponer deriva cero al cociente de bonos')
p('Aplicamos Itô a Rᵢ = (1+δᵢFᵢ)Rᵢ₊₁:')
eq('dR<sub>i</sub> = (1+δ<sub>i</sub>F<sub>i</sub>)dR<sub>i+1</sub> + δ<sub>i</sub>R<sub>i+1</sub>dF<sub>i</sub> + δ<sub>i</sub>dF<sub>i</sub>dR<sub>i+1</sub>')
p('El primer término tiene deriva cero. El segundo aporta la deriva μᵢ y el tercero aporta covarianza, ya que dW* dW*ᵀ = I du. Sumamos las dos contribuciones restantes e imponemos que la deriva total sea cero.')
eq('0 = δ<sub>i</sub>(F<sub>i</sub>+s)R<sub>i+1</sub> [μ<sub>i</sub> + λ<sub>i</sub>·β<sub>i+1</sub>]<br/>μ<sub>i</sub> = −Σ<sub>j=i+1</sub><super>20</super> [δ<sub>j</sub>(F<sub>j</sub>+s)/(1+δ<sub>j</sub>F<sub>j</sub>)] (λ<sub>i</sub>·λ<sub>j</sub>)')
p('Dividimos por δᵢ(Fᵢ+s)Rᵢ₊₁, que es positivo en nuestro modelo. El ajuste depende de las covarianzas con forwards posteriores: el numerador usa la variable desplazada y el denominador el tipo sin desplazar de la identidad del bono.')
note('<b>Chequeo:</b> el último forward tiene suma vacía y μ₂₀ = 0. Su propia medida de pago coincide con la terminal. La deriva relativa de cada forward anterior se ajusta para que los cocientes de bonos sean martingalas.')

start('DE LA ECUACIÓN AL NÚMERO','Simular un paso con log-Euler')
p('Ya tenemos una dinámica para Xᵢ=Fᵢ+s. Aplicando Itô a ln(Xᵢ), obtenemos el cambio logarítmico con la corrección de varianza.')
eq('d ln X<sub>i</sub> = (μ<sub>i</sub> − ½ ‖λ<sub>i</sub>‖²)du + λ<sub>i</sub>·dW*<br/>X<sub>i</sub>(u+h) ≈ X<sub>i</sub>(u) exp[(μ<sub>i</sub> − ½‖λ<sub>i</sub>‖²)h + √h λ<sub>i</sub>·Z]')
p('Como la deriva depende de toda la curva, la evaluamos al comienzo del paso (log-Euler). Las volatilidades se mantienen constantes hasta que cada forward se fija. Todos los forwards vivos se actualizan usando el mismo estado anterior.')
mu=drift(s.states[0,0:1,1:],s.delta[1:],s.diffusion[1:],data.shift)[0,0]
var=lam@lam; hstep=.5; shock=np.sqrt(hstep)*(lam@z); det=(mu-.5*var)*hstep
h('Reconstrucción del primer forward de la trayectoria 1')
tab([['Magnitud','Cálculo / valor'],['X₁ inicial',pct(s.f0[1]+data.shift,6)],['Deriva relativa μ₁',n(mu,8)],['Varianza instantánea ‖λ₁‖²',n(var,6)],['Parte determinista del exponente',n(det,8)],['Parte aleatoria (pág. 5)',n(shock,8)],['Exponente total',n(det+shock,8)]],[274,203],highlight=(6,))
eq(f'F₁(t₁) ≈ {pct(s.f0[1]+data.shift,6)} × exp({n(det+shock,8)}) − 3%<br/>= <b>{pct(s.states[1,0,1],6)}</b>')
p('Repetimos el proceso para los forwards pendientes. Veamos F₂, que necesitamos para el tercer cupón. Tras el primer paso vale −0,907277%. En el segundo, su exponente determinista es −0,0163623 y su shock vale +0,1554209.')
eq('F₂(t₂) ≈ (−0,907277% + 3%) × exp(0,1390586) − 3%<br/>= <b>−0,5951%</b>')
note('<b>Dos relojes.</b> h=0,5 es el paso de difusión según la convención indicada por el profesor. δᵢ = días/365 corresponde a contratos y bonos. Con σ=0 desaparecen la corrección de varianza, el shock y la deriva, y la curva forward se mantiene determinista.')

start('JUNTAMOS TODAS LAS PIEZAS','Cinco pagos, un solo valor presente')
p('Una vez simuladas las curvas, calculamos la regla contractual en los veinte semestres, hasta la amortización. En la trayectoria 1 ocurre en el quinto semestre. Todos los importes son por 100 de nominal.')
rows=[['Sem.','Euribor','Tasa anual','Cupón','Acum.','Principal']]
for j in range(5):
    rows.append([str(j+1),pct(s.fixings[0,j],3),pct(cf.rates[0,j],3),n(cf.paid_coupon[0,j]),n(100*cf.cumulative_paid_fraction[0,j]),n(cf.paid_principal[0,j],0)])
tab(rows,[47,85,88,85,87,85],highlight=(5,))
h('Construir el bono a partir de la curva simulada')
p('Al pagar en tₘ queda una curva de tipos vivos desde tₘ hasta t₂₁. Invertimos el producto de factores de capitalización para obtener el bono que vence en t₂₁.')
eq('B(t<sub>m</sub>) = [ ∏<sub>j=m</sub><super>20</super> (1+δ<sub>j</sub>F<sub>j</sub>(t<sub>m</sub>)) ]<super>−1</super>')
rows=[['Sem.','Flujo total','B(tₘ)','B(0) / B(tₘ)','Contribución PV']]
for j in range(5):
    flow=cf.paid_coupon[0,j]+cf.paid_principal[0,j]
    wt=s.initial_terminal/s.terminal_bonds[0,j]
    rows.append([str(j+1),n(flow),n(s.terminal_bonds[0,j],6),n(wt,6),n(flow*wt)])
rows.append(['Total','','','',n(pv[0])])
tab(rows,[48,108,100,110,111],highlight=(5,6))
p('El semestre 5 paga 102,2411 porque el acumulado alcanza 5,1968. Las otras quince filas aportan cero. Sumamos los cinco valores presentes: 5,0428 de cupones y 96,3931 de principal.')
note('<b>Resultado de una historia:</b> 101,4358. Existe una contribución de este tipo para cada una de las 200 trayectorias.')

start('RESULTADOS','¿Por qué la mayoría parece favorable y el precio es 98,27?')
p('Los cupones con memoria pueden volverse muy negativos si el Euribor permanece alto. En las trayectorias con tipos bajos, el producto suele terminar pronto. En las desfavorables, puede seguir vivo y acumular pérdidas.')
d=Drawing(W,155)
for k,j in enumerate([0,70]):
    length=int(cf.redemption_period[j]); left=34+240*k; width=174; lo,hi=(-2,5) if k==0 else (-100,15)
    def yy(v): return 29+88*(v-lo)/(hi-lo)
    d.add(String(left,139,f'Trayectoria {j+1} · {length} semestres',fontName='Bold',fontSize=9,fillColor=NAVY))
    for v in [lo,0,hi]:
        d.add(Line(left,yy(v),left+width,yy(v),strokeColor=RULE,strokeWidth=.6))
        d.add(String(left-3,yy(v)-2,f'{v}%',textAnchor='end',fontName='Body',fontSize=7.5,fillColor=MUTED))
    for series,c in [(s.fixings[j,:length],BLUE),(cf.rates[j,:length],RUST)]:
        d.add(PolyLine([v for u,val in enumerate(series) for v in (left+u*width/(length-1),yy(100*val))],strokeColor=c,strokeWidth=2))
    d.add(String(left,12,'1',fontName='Body',fontSize=8,fillColor=MUTED))
    d.add(String(left+width,12,str(length),fontName='Body',fontSize=8,fillColor=MUTED,textAnchor='end'))
story.append(d)
p('Azul: Euribor. Terracota: tasa anual de cupón. Cada gráfico utiliza su propia escala vertical. En la trayectoria 71 el principal se devuelve al final, pero el PV neto es −310,62.','small')
h('La distribución de valores presentes')
bins=[-np.inf,0,90,100,110,np.inf]; counts=np.histogram(pv,bins)[0]
d=Drawing(W,114)
for i,(label,cnt) in enumerate(zip(['PV &lt; 0','0 a &lt;90','90 a &lt;100','100 a &lt;110','110 o más'],counts)):
    y=97-i*20
    d.add(String(0,y,label.replace('&lt;','<'),fontName='Body',fontSize=9,fillColor=NAVY))
    w=292*cnt/max(counts)
    d.add(Rect(122,y-2,w,10,fillColor=RUST if i==0 else TEAL,strokeColor=None))
    d.add(String(129+w,y,str(cnt),fontName='Bold',fontSize=9,fillColor=NAVY))
story.append(d)
p(f'Media: <b>{n(r["price"],2)}</b>. Mediana: {n(r["median_path_pv"],2)}. La cola negativa reduce la media: 29 trayectorias pagan algún cupón negativo y 5 tienen PV neto negativo. Por ejemplo, en la trayectoria 71 la tasa del semestre 4 es 0,348%. En el 5 pasa a 0,348% + 1% − 2,211% = −0,863%. La memoria lleva ese valor al semestre 6.')
note('<b>Precio = 100,52 − 2,25 ≈ 98,27.</b> No hemos eliminado ningún extremo. Bajo Q*, 160/200 trayectorias cancelan hasta el año 3 y la vida media es 3,38 años. Esas frecuencias son de valoración, no previsiones físicas.')

start('DEFENSA Y REPASO','Las cinco preguntas que debes poder responder')
tab([['Pregunta','Respuesta que debes saber construir'],
     ['¿Qué compramos?','Un contrato con nominal, cupones con memoria y devolución condicionada a un objetivo efectivo del 4%. (Págs. 1–2)'],
     ['¿Qué simulamos?','Curvas de forwards futuras correlacionadas por tres factores. Usamos la diagonal de fijaciones. (Págs. 3–5)'],
     ['¿Por qué un bono terminal?','Permite valorar en una unidad común. La medida Q* exige ajustar las derivas. (Págs. 6–7)'],
     ['¿Cómo calculamos el precio?','Log-Euler, flujos según contrato, descuento bajo el bono y media de 200 PV. (Págs. 8–9)'],
     ['¿Qué explica el 98,27?','La cola negativa de trayectorias largas reduce la media. (Pág. 10)']],[145,332])
h('Qué podemos afirmar con 200 escenarios')
p('El error estándar de la media es la desviación típica muestral de los PV dividida por √200: 2,7454. El intervalo t aproximado al 95% es [92,8555; 103,6829]. Incluye 100; no podemos concluir con esa precisión que el verdadero valor esté por debajo de la par. El intervalo refleja ruido Monte Carlo, no incertidumbre total del modelo.')
h('Validaciones y decisiones que conviene recordar')
p('Con σ=0 se obtiene 105,3566 por descuento directo. La solución conserva los 200 escenarios, reproduce los PV con una referencia escalar y contrasta bonos y caplets. Las aclaraciones del profesor fijan ACT/365, memoria negativa, fixing al inicio, h=0,5 y cupón íntegro. La volatilidad constante hasta reset, log-Euler y calendario sin ajuste son elecciones de implementación.')
p('Fuente: ejercicio AFI 2026, plantilla de datos y aclaraciones del profesor. Cifras reproducidas de la solución Snowblade LMM, memoria académica y simulación original de 200 trayectorias. Repositorio: <link href="https://github.com/AlvaroChacarra/Lmm/tree/42db65d3726e5d465340533a409aafed024b29b6" color="#255F89">AlvaroChacarra/Lmm, revisión 42db65d</link>.','small')
note('<b>Siguiente paso:</b> empezar por el tercer cupón, dibujar la diagonal de fijaciones, explicar la deriva y reconstruir 101,4358. Finalmente, explicar por qué el promedio es 98,27.')

def frame(canvas,doc):
    canvas.setStrokeColor(TEAL);canvas.setLineWidth(1.2);canvas.line(53,799,542,799)
    canvas.setFont('Body',8);canvas.setFillColor(MUTED)
    canvas.drawString(53,28,'AFI  /  Guía de estudio · Snowblade y LMM')
    canvas.drawRightString(542,28,f'{doc.page:02d} / 11')

output=ROOT/'docs/Guia_pedagogica_Snowblade_LMM.pdf'
SimpleDocTemplate(str(output),pagesize=A4,leftMargin=53,rightMargin=53,topMargin=58,bottomMargin=49,
                  title='Snowblade y LMM: guía de estudio',author='AFI').build(story,onFirstPage=frame,onLaterPages=frame)
print(output)
