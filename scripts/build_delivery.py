"""Excel nuevo con fórmulas y cachés reconciliadas; memoria PDF, sin alterar XLSM."""
import json
from datetime import datetime
from pathlib import Path
import sys
from functools import partial
from datetime import timedelta
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import numpy as np
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell as cell
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from lmm.inputs import load_inputs
from lmm.model import simulate, drift
from lmm.valuation import estimate
from lmm.payoff import SPREADS
from reportlab.pdfgen.canvas import Canvas


def excel(data,s,payload,cf):
    dest=ROOT/'entrega/Snowblade_LMM.xlsx'
    w=xlsxwriter.Workbook(dest)
    w.set_properties({'title':'Snowblade LMM - AFI','author':'Proyecto LMM',
                      'comments':'Libro nuevo sin VBA; fuentes originales intactas.',
                      'created':datetime(2026,11,14)})
    w.set_calc_mode('auto')
    hdr=w.add_format({'bg_color':'#143C60','font_color':'white','bold':True,'text_wrap':True,'valign':'vcenter'})
    num=w.add_format({'num_format':'0.000000'})
    pct=w.add_format({'num_format':'0.0000%'})
    datefmt=w.add_format({'num_format':'dd/mm/yyyy'})
    money=w.add_format({'num_format':'0.0000'})
    title=w.add_format({'bold':True,'font_size':16,'font_color':'#143C60'})
    text=w.add_format({'text_wrap':True,'valign':'top'})
    def sheet(name,head,width=18):
        sh=w.add_worksheet(name);sh.freeze_panes(1,2);sh.set_row(0,32);sh.write_row(0,0,head,hdr)
        sh.set_column(0,len(head)-1,width);sh.autofilter(0,0,1,len(head)-1)
        return sh
    notes=w.add_worksheet('Guia');notes.set_column('A:A',28);notes.set_column('B:B',100)
    notes.write('A1','SNOWBLADE · LMM',title)
    lines=[('Estado','Valoración reproducible con 200 paths. Precisión MC limitada; convenciones residuales explícitas.'),
           ('Fuente contractual','PDF AFI más aclaraciones del profesor aportadas por el usuario; ver docs/ACLARACIONES_PROFESOR.md.'),
           ('Contrato confirmado','Tasas anualizadas ACT/365; no floor; memoria del cupón negativo; objetivo de intereses efectivos netos del 4%.'),
           ('Convenciones restantes','Fixing advance; pago completo en autocall; sin ajuste hábil; terminal 26/07/2032; sigma constante hasta reset.'),
           ('Lectura','Resumen -> Parametros/Calendario -> Aleatorios/PCA/Covarianza -> Estados -> Flujos -> Paths.'),
           ('Fórmulas','Estados implementa log-Euler terminal con drift dependiente de forwards. Flujos calcula cupones, objetivo y bono terminal. Paths y Resumen agregan.'),
           ('Cachés y recálculo','Cada fórmula incluye resultado cacheado de Python. Reconciliación con referencia escalar independiente. No se ha ejecutado recálculo en Microsoft Excel/LibreOffice.'),
           ('Limitación de cambios','Las fórmulas del caso base son editables. Calendario y nodos de interpolación están fijados para este caso; al cambiar fechas, dimensiones o escenarios, regenerar desde Python.'),
           ('Moneda y medida','Valor por 100 de nominal; probabilidades y vida media bajo medida del bono terminal, no previsiones físicas.'),
           ('Originales','Libro nuevo XLSX sin macros; no contiene VBA ni afirma conservarlo. Los originales siguen en data/original/.'),
           ('Reproducción','python scripts/value_snowblade.py; python scripts/validate_solution.py; python scripts/build_delivery.py'),
           ('Excel original SHA-256',data.hashes['2026_Datos.xlsm']),('PDF original SHA-256',data.hashes['2026_Ejercicio.pdf'])]
    for r,(a,b) in enumerate(lines,2):notes.write(r,0,a);notes.write(r,1,b,text);notes.set_row(r,42)
    params=sheet('Parametros',['Parametro','Valor'],30)
    for r,entry in enumerate([('Nominal',100.),('Shift',data.shift),('Objetivo efectivo neto',.04),('P(0,T*)',s.initial_terminal),('Paths',200),('Cupones iniciales anualizados',.01)],1):params.write_row(r,0,entry)
    curve=sheet('Curva',['Dias desde origen','Fecha','Descuento'],22)
    for r,(d,df) in enumerate(zip(data.days,data.discounts),1):
        curve.write_number(r,0,d);curve.write_datetime(r,1,data.start+timedelta(days=int(d)),datefmt);curve.write_number(r,2,df,num)
    cal=sheet('Calendario',['i','Fecha','Dias','ACT365','P0','Forward inicial','Sigma','Carga 1','Carga 2','Carga 3','Spread cupón'],19)
    for i in range(22):
        r=i+1;cal.write_number(r,0,i);cal.write_datetime(r,1,s.dates[i],datefmt);cal.write_number(r,2,int(s.days[i]))
        d=int(s.days[i]);k=min(max(np.searchsorted(data.days,d,side='left')-1,0),len(data.days)-2)
        ca=k+2;cb=k+3
        formula=f'=EXP(LN(Curva!C{ca})+(LN(Curva!C{cb})-LN(Curva!C{ca}))*(C{r+1}-Curva!A{ca})/(Curva!A{cb}-Curva!A{ca}))'
        cal.write_formula(r,4,formula,num,s.p0[i])
        if i<21:
            cal.write_formula(r,3,f'=(C{r+2}-C{r+1})/365',num,s.delta[i])
            cal.write_formula(r,5,f'=(E{r+1}/E{r+2}-1)/D{r+1}',pct,s.f0[i])
            cal.write_number(r,6,data.vols[i],pct)
            cal.write_row(r,7,[0.,0.,0.] if i==0 else data.loadings[i-1],num)
            if i<20:cal.write_number(r,10,float(SPREADS[i]),pct)
    # Link terminal factor instead of a copied parameter.
    params.write_formula('B5','=Calendario!E23',num,s.initial_terminal)
    pca=sheet('PCA',['Forward i','A1','A2','A3','Origen'],22)
    for i in range(20):pca.write_row(i+1,0,[i+1,*data.loadings[i],f'Correlaciones!G{117+i}:I{117+i}'])
    cov=sheet('Covarianza',['Forward i']+[str(i) for i in range(21)],13)
    covariance=s.diffusion@s.diffusion.T
    for i in range(21):
        cov.write_number(i+1,0,i)
        for j in range(21):
            ri=i+2;rj=j+2
            formula=f'=Calendario!G{ri}*Calendario!G{rj}*SUMPRODUCT(Calendario!H{ri}:J{ri},Calendario!H{rj}:J{rj})'
            cov.write_formula(i+1,j+1,formula,num,covariance[i,j])
    rnd=sheet('Aleatorios',['Factor','Paso','Path','Z original'],18)
    for k in range(3):
        for n in range(20):
            for p in range(200):rnd.write_row(1+k*4000+n*200+p,0,[k+1,n+1,p+1,data.normals[k,n,p]])
    st=sheet('Estados',['Path','Paso','Fecha','h ACT365','Z1','Z2','Z3']+[f'F{i}' for i in range(21)]+[f'mu{i}' for i in range(21)],15)
    for p in range(200):
        for n in range(21):
            r=1+p*21+n;st.write_number(r,0,p+1);st.write_number(r,1,n);st.write_datetime(r,2,s.dates[n],datefmt)
            st.write_number(r,3,s.delta[n-1] if n else 0,num)
            if n:
                for k in range(3):st.write_formula(r,4+k,f'=Aleatorios!D{2+k*4000+(n-1)*200+p}',num,data.normals[k,n-1,p])
            previous=r-1
            mu=np.zeros(21)
            if n:mu[n:]=drift(s.states[n-1,p:p+1,n:],s.delta[n:],s.diffusion[n:],data.shift)[0]
            for i in range(21):
                fcol=7+i;mcol=28+i;ri=i+2
                if not n:
                    st.write_formula(r,fcol,f'=Calendario!F{ri}',num,s.f0[i]);st.write_number(r,mcol,0)
                elif i<n:
                    st.write_formula(r,fcol,'='+cell(previous,fcol),num,s.states[n,p,i]);st.write_number(r,mcol,0)
                else:
                    terms=[]
                    for j in range(i+1,21):
                        fj=cell(previous,7+j);dj=f'Calendario!D{j+2}';cv='Covarianza!'+cell(i+1,j+1)
                        terms.append(f'{dj}*({fj}+Parametros!$B$3)/(1+{dj}*{fj})*{cv}')
                    st.write_formula(r,mcol,'=-('+ '+'.join(terms)+')' if terms else '=0',num,mu[i])
                    var='Covarianza!'+cell(i+1,i+1)
                    shock=f'Calendario!G{ri}*(Calendario!H{ri}*E{r+1}+Calendario!I{ri}*F{r+1}+Calendario!J{ri}*G{r+1})'
                    form=f'=({cell(previous,fcol)}+Parametros!$B$3)*EXP(({cell(r,mcol)}-0.5*{var})*D{r+1}+SQRT(D{r+1})*{shock})-Parametros!$B$3'
                    st.write_formula(r,fcol,form,num,s.states[n,p,i])
    flows=sheet('Flujos',['Path','Periodo','Pago','Fixing advance','Tasa anual cupón','ACT365','Vivo antes','Cupón pagado','Acumulado / nominal','Autocall','Principal','P(t,T*)','PV cupon','PV principal','PV total'],20)
    for p in range(200):
        for j in range(20):
            r=1+p*20+j;rr=r+1
            state_reset=1+p*21+j;state_payment=state_reset+1
            flows.write_row(r,0,[p+1,j+1]);flows.write_datetime(r,2,s.dates[j+1],datefmt)
            flows.write_formula(r,3,'=Estados!'+cell(state_reset,7+j),pct,s.fixings[p,j])
            flows.write_formula(r,6,'=1' if j==0 else f'=IF(K{rr-1}>0,0,G{rr-1})',None,int(cf.alive_before[p,j]))
            rate='Parametros!$B$7' if j<2 else f'E{rr-1}+Calendario!K{j+2}-D{rr}'
            flows.write_formula(r,4,f'=IF(G{rr}=1,{rate},0)',pct,cf.rates[p,j])
            flows.write_formula(r,5,f'=Calendario!D{j+2}',num,s.delta[j])
            flows.write_formula(r,7,f'=Parametros!$B$2*E{rr}*F{rr}',money,cf.paid_coupon[p,j])
            flows.write_formula(r,8,f'={"0" if j==0 else f"I{rr-1}"}+H{rr}/Parametros!$B$2',pct,cf.cumulative_paid_fraction[p,j])
            flows.write_formula(r,9,f'=IF(AND(G{rr}=1,I{rr}>=Parametros!$B$4),1,0)',None,int(cf.call_event[p,j]))
            flows.write_formula(r,10,f'=IF(OR(J{rr}=1,AND(B{rr}=20,G{rr}=1)),Parametros!$B$2,0)',money,cf.paid_principal[p,j])
            factors=[f'(1+Calendario!D{i+2}*Estados!{cell(state_payment,7+i)})' for i in range(j+1,21)]
            flows.write_formula(r,11,'=1/PRODUCT('+','.join(factors)+')',num,s.terminal_bonds[p,j])
            cv=cf.paid_coupon[p,j]*s.initial_terminal/s.terminal_bonds[p,j]
            pr=cf.paid_principal[p,j]*s.initial_terminal/s.terminal_bonds[p,j]
            flows.write_formula(r,12,f'=H{rr}*Parametros!$B$5/L{rr}',money,cv)
            flows.write_formula(r,13,f'=K{rr}*Parametros!$B$5/L{rr}',money,pr)
            flows.write_formula(r,14,f'=M{rr}+N{rr}',money,cv+pr)
    paths=sheet('Paths',['Path','PV cupones','PV principal','PV total','Periodo amortizacion','Vida años Q*','Autocall'],23)
    report,_,pv,cp,pp=estimate(s)
    for p in range(200):
        r=p+1;first=p*20+2;last=first+19
        paths.write_number(r,0,p+1)
        for col,source,val in [(1,'M',cp[p]),(2,'N',pp[p]),(3,'O',pv[p])]:paths.write_formula(r,col,f'=SUM(Flujos!{source}{first}:{source}{last})',money,val)
        paths.write_formula(r,4,f'=SUMPRODUCT(Flujos!B{first}:B{last},Flujos!K{first}:K{last})/Parametros!$B$2',num,int(cf.redemption_period[p]))
        paths.write_formula(r,5,f'=INDEX(Calendario!C2:C23,E{r+1}+1)/365',num,s.days[cf.redemption_period[p]]/365)
        paths.write_formula(r,6,f'=SUM(Flujos!J{first}:J{last})',None,int(cf.call_event[p].any()))
    summary=sheet('Resumen',['Metrica','Valor'],36)
    for r,(label,formula,value) in enumerate([
        ('Precio por 100','=AVERAGE(Paths!D2:D201)',report['price']),
        ('PV cupones','=AVERAGE(Paths!B2:B201)',report['coupon_pv']),
        ('PV principal','=AVERAGE(Paths!C2:C201)',report['principal_pv']),
        ('Error estandar','=STDEV(Paths!D2:D201)/SQRT(200)',report['standard_error']),
        ('IC 95% aprox inferior','=B2-TINV(0.05,199)*B5',report['ci95_student'][0]),
        ('IC 95% aprox superior','=B2+TINV(0.05,199)*B5',report['ci95_student'][1]),
        ('Vida media años Q*','=AVERAGE(Paths!F2:F201)',report['expected_life_years_Q_terminal']),
        ('Supervivencia sin autocall Q*','=1-AVERAGE(Paths!G2:G201)',report['maturity_no_call_probability_Q_terminal'])],1):
        summary.write(r,0,label);summary.write_formula(r,1,formula,money,value)
    summary.write(11,0,'IC aproximado: solo error MC; no incluye PCA, malla o convenciones.',text)
    summary.set_row(11,48)
    summary.write_row(13,0,['Periodo','Probabilidad Q*','Recuento'],hdr)
    for j,count in enumerate(report['autocall_counts'],14):summary.write_row(j,0,[j-13,count/200,count])
    scenarios=sheet('Sensibilidades',['Escenario','Precio','Diferencia base','SE diferencia pareada'],35)
    for r,(name,rep) in enumerate(payload['sensitivities'].items(),1):scenarios.write_row(r,0,[name,rep['price'],rep['paired_difference_to_base'],rep['paired_difference_se']])
    for sh in w.worksheets():
        sh.set_landscape();sh.fit_to_pages(1,0);sh.repeat_rows(0)
    w.close()
    return dest


def pdf(data,s,payload):
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    pdfmetrics.registerFont(TTFont('DV',font));pdfmetrics.registerFont(TTFont('DV-Bold',bold))
    styles=getSampleStyleSheet()
    for name in ['Normal','BodyText','Heading1','Heading2','Title']:
        styles[name].fontName='DV';styles[name].leading=14
    styles['Normal'].fontSize=9;styles['BodyText'].fontSize=9
    styles['Title'].fontSize=23;styles['Title'].leading=29;styles['Title'].textColor=colors.HexColor('#143C60')
    styles['Heading1'].fontSize=16;styles['Heading1'].leading=21
    styles['Heading2'].fontSize=11;styles['Heading2'].leading=16
    story=[]
    def p(t,style='BodyText'):story.append(Paragraph(t,styles[style]));story.append(Spacer(1,7))
    def table(rows,widths=None):
        t=Table([[Paragraph(str(x),styles['Normal']) for x in row] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E4EDF5')),('FONTNAME',(0,0),(-1,0),'DV-Bold'),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#143C60')),('LINEBELOW',(0,1),(-1,-1),.25,colors.lightgrey)]))
        story.append(t);story.append(Spacer(1,12))
    r=payload['base'];f=lambda x:f'{x:,.4f}'.replace(',','X').replace('.',',').replace('X','.')
    p('Snowblade bajo LMM','Title');p('Valoración Monte Carlo · 200 trayectorias originales · AFI','Heading2')
    p('Resultado reproducible con las aclaraciones del profesor. Estado: ÁMBAR por precisión estadística limitada y convenciones residuales.')
    table([['Magnitud por 100 de nominal','Resultado'],['Precio',f(r['price'])],['PV de cupones',f(r['coupon_pv'])],['PV del principal',f(r['principal_pv'])],['Error estándar Monte Carlo',f(r['standard_error'])],['IC 95% aproximado (Student, 199 g.l.)',f(r['ci95_student'][0])+' a '+f(r['ci95_student'][1])],['Vida media bajo Q terminal',f(r['expected_life_years_Q_terminal'])+' años'],['Llegada a vencimiento sin autocall','15 / 200 = 7,5%']],[300,180])
    p('Qué explica el resultado','Heading2')
    p('La curva inicial contiene tipos negativos. Muchas trayectorias autocancelan pronto con cupones positivos. Otras permanecen vivas y, al subir Euribor, acumulan cupones negativos: el inversor debe pagarlos. Esas pérdidas forman parte del contrato confirmado, no son errores que puedan eliminarse.')
    p('Hay 29 trayectorias con algún cupón negativo y 4 con PV neto negativo. La trayectoria 71 vale −292,7628 por 100 de nominal. El intervalo estadístico es orientativo: la muestra es pequeña y asimétrica; no engloba riesgo de PCA, discretización o convenciones.')
    p('Recomendación','Heading2');p('Presentar 98,52 como estimación del caso documentado, acompañada de error estándar e hipótesis. Mantener los 200 paths exigidos y no recentrar ni sustituir los shocks. No expresar céntimos como precisión estadística.')
    story.append(PageBreak())
    p('1. Contrato y convenciones','Heading1')
    p('El profesor confirma, mediante respuestas transmitidas por el usuario en esta sesión (correo sin fecha): (i) no hay suelo cero, el inversor paga los cupones negativos y la recursión conserva ese valor; (ii) el objetivo del 4% suma intereses reales acumulados; (iii) el 1% inicial es anualizado y se devenga con ACT/365.')
    table([['Periodo j','Tasa anual c<sub>j</sub>'],['1–2','1%'],['3–4','c<sub>j−1</sub> − r<sub>j</sub>'],['5–8','c<sub>j−1</sub> + 1% − r<sub>j</sub>'],['9–12','c<sub>j−1</sub> + 1,25% − r<sub>j</sub>'],['13–16','c<sub>j−1</sub> + 1,50% − r<sub>j</sub>'],['17–20','c<sub>j−1</sub> + 2% − r<sub>j</sub>']],[100,380])
    p('Pago del cupón: H δ<sub>j−1</sub> c<sub>j</sub>. Acumulado: S<sub>m</sub> = Σ<sub>j≤m</sub> δ<sub>j−1</sub> c<sub>j</sub>. Primer cruce S<sub>m</sub> ≥ 0,04: cupón completo y devolución de H; se suprimen todos los pagos posteriores. Si no cruza, H se devuelve en el periodo 20. Los intereses negativos reducen el acumulado.')
    p('El cupón completo en la fecha de cruce, sin recortar el exceso al 4%, sigue siendo una convención razonada: no fue confirmado expresamente en la respuesta del profesor. Recortarlo reduce esta muestra en 1,1919 puntos; se presenta como sensibilidad, no como contrato base.')
    p('Calendario adoptado','Heading2')
    p('Origen 26/01/2022; pagos cada seis meses calendario, sin ajuste hábil, hasta 26/01/2032. Primer devengo 181/365; segundo 184/365. Fixing advance al inicio de cada periodo. Bono terminal auxiliar a 26/07/2032. Este semestre extra no añade un cupón: completa el numerario y permite mapear 21 sigmas a F₀…F₂₀, con F₀ ya fijo y 20 tipos estocásticos.')
    p('P(0,t₂₀)=0,9796669786; P(0,t₂₁)=0,9738424984. Esta correspondencia temporal y el mapa de volatilidades no han sido confirmados por el profesor. Las sensibilidades están en la sección 4.')
    story.append(PageBreak())
    p('2. Datos, dinámica y descuento','Heading1')
    p('Curva: 70 factores de descuento originales, interpolación log-lineal equivalente al modo 0 de CInterPol. Forwards: F<sub>i</sub>(0) = [P(0,t<sub>i</sub>)/P(0,t<sub>i+1</sub>) − 1]/δ<sub>i</sub>, con δ<sub>i</sub>=días(t<sub>i+1</sub>−t<sub>i</sub>)/365.')
    p('Se conservan las cargas A de Correlaciones!G117:I136 y los 12.000 números de Aleatorios. El tensor Z tiene dimensiones factor × paso × path = 3×20×200. No hay nuevas semillas, antitéticas, recentrado ni PCA recalculada en el caso base.')
    p('Modelo bajo Q terminal','Heading2')
    p('X<sub>i</sub> = F<sub>i</sub> + s, con s=0,03; λ<sub>i</sub>=σ<sub>i</sub>a<sub>i</sub>. Se adopta σ<sub>i</sub> constante hasta reset; para i=1…20 se usa Curva y volas!F(9+i). La fila F9 corresponde al forward F₀ fijo en origen.')
    p('dX<sub>i</sub>/X<sub>i</sub> = μ<sub>i</sub>dt + λ<sub>i</sub>·dW<sup>21</sup>')
    p('μ<sub>i</sub> = −Σ<sub>j=i+1…20</sub> {δ<sub>j</sub>(F<sub>j</sub>+s)/(1+δ<sub>j</sub>F<sub>j</sub>)} (λ<sub>i</sub>·λ<sub>j</sub>)')
    p('El numerador contiene F+s y el denominador F sin desplazar. La suma del último forward es vacía: μ₂₀=0. Drift y difusión emplean la misma covarianza efectiva A Aᵀ. Las cargas finales ya son unitarias por fila: no se multiplican de nuevo por raíces de autovalores.')
    p('Paso log-Euler: X<sub>i</sub>(t+h) = X<sub>i</sub>(t) exp[(μ<sub>i</sub> − ||λ<sub>i</sub>||²/2)h + √h λ<sub>i</sub>·Z]. Solo evolucionan tipos vivos; todos los drifts se calculan con el mismo estado anterior. h se mide en ACT/365. Se comprueba X&gt;0 y 1+δF&gt;0 sin clipping.')
    p('Descuento por numerario','Heading2')
    p('B(t<sub>m</sub>) = P(t<sub>m</sub>,t₂₁) = ∏<sub>j=m…20</sub>(1+δ<sub>j</sub>F<sub>j</sub>(t<sub>m</sub>))<sup>−1</sup>')
    p('PV<sub>p</sub> = P(0,t₂₁) Σ<sub>m=1…20</sub> CF<sub>p,m</sub>/B<sub>p</sub>(t<sub>m</sub>); precio = media de los 200 PV<sub>p</sub>.')
    p('En el último pago queda el factor F₂₀; el producto no es vacío. El bono terminal vale 1 solo en t₂₁. No se sustituye el descuento estocástico por la curva inicial. El error estándar se calcula sobre trayectorias completas, no sobre los 4.000 registros de pago.')
    story.append(PageBreak())
    p('3. Resultados y riesgo de cola','Heading1')
    rows=[['Periodo de autocall','Recuento / 200','Probabilidad Q terminal']]
    for j,c in enumerate(r['autocall_counts'],1):
        if c:rows.append([str(j),str(c),str(round(c/2,2))+'%'])
    rows.append(['Vencimiento sin autocall','15','7,5%'])
    table(rows,[160,140,180])
    p('El 61,5% cancela hasta el periodo 5 y el 78,5% hasta el periodo 6. Las frecuencias se estiman bajo la medida del bono terminal; no son probabilidades físicas de inversión. La vida media de 3,3826 años se interpreta bajo esa misma medida.')
    p('La mediana de los PV es 103,5984, superior a la media 98,5198 por la cola negativa. Quitar solo el path 71 subiría la media a 100,4861: es un diagnóstico de influencia y no una estimación alternativa admisible. La muestra original se conserva completa.')
    p('La protección del principal significa devolución de 100 en la fecha de amortización, no protección del conjunto de pagos de cupones. Sin floor ni límite de responsabilidad indicado, los pagos negativos pueden superar el nominal. Eso explica los PV netos negativos.')
    p('El caso sin volatilidad vale 105,3566 y cancela en el periodo 5. Sirve para verificar algebraicamente los flujos y el descuento; no reemplaza al precio estocástico.')
    story.append(PageBreak())
    p('4. Validación, sensibilidades y reproducción','Heading1')
    p('17 tests superados: integridad y rechazo de corrupción, interpolación, forwards, drift/shift, último forward, congelación al reset, caso σ=0, memoria negativa, objetivo, amortización única y referencia escalar de todos los paths. Máxima diferencia de PV frente a esa referencia: 2,28×10⁻¹³; σ=0 frente a descuento directo: 7,11×10⁻¹⁴.')
    p('230 diagnósticos de martingalas de cocientes de bonos quedan dentro de cinco errores estándar; máximo |z|=2,029. Son controles con tolerancia MC, no una demostración de ausencia de sesgo de discretización ni de convergencia.')
    names={'predictor_corrector':'Predictor-corrector','diffusion_dt_05':'Difusión h=0,5','terminal_10_years':'Bono terminal a 10 años','vol_mapping_first_row':'Sigma desde primera fila','zero_volatility':'Sin volatilidad','coupon_capped_at_target_not_base':'Cupón recortado al objetivo'}
    table([['Escenario','Precio','Δ base','SE pareado']]+[[names[n],f(a['price']),f(a['paired_difference_to_base']),f(a['paired_difference_se'])] for n,a in payload['sensitivities'].items()],[210,90,90,90])
    p('Predictor-corrector comparte los mismos shocks: detecta sensibilidad del drift, no refina el Browniano ni acredita convergencia temporal. La variante h=0,5 cambia solo el reloj de difusión, conservando calendario y devengo ACT/365. Cambiar el bono terminal cambia también medida y dimensión; la diferencia con ruido común es orientativa.')
    p('La PCA suministrada es aproximada: error máximo de R frente a A Aᵀ de 0,1535. Se conserva por exigencia del ejercicio. Su riesgo no forma parte del intervalo estadístico. Falta confirmación explícita de fechas/terminal, mapa sigma y tratamiento del exceso del objetivo.')
    p('Reproducción y entregables','Heading2')
    for command in ['python scripts/value_snowblade.py','PYTHONPATH=src python -m unittest discover -s tests -v','python scripts/validate_solution.py','python scripts/build_delivery.py']:
        p(command)
    p('El XLSX es un libro nuevo sin VBA, con fórmulas y resultados cacheados reconciliados con Python. No se ha ejecutado recálculo en una aplicación Excel. Los dos originales conservan sus SHA-256; ver outputs/resultados.json y outputs/validacion.json. Código, decisiones y trazabilidad completa en el repositorio.')
    dest=ROOT/'entrega/Memoria_Snowblade.pdf'
    def footer(canvas,doc):
        canvas.setFont('DV',8);canvas.setFillColor(colors.grey)
        canvas.drawString(42,25,'Snowblade · LMM terminal · 200 paths originales')
        canvas.drawRightString(A4[0]-42,25,str(doc.page))
    SimpleDocTemplate(str(dest),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=40,bottomMargin=42,title='Snowblade LMM - Memoria de valoración',author='Proyecto LMM').build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=partial(Canvas,invariant=1))
    return dest

if __name__=='__main__':
    data=load_inputs();s=simulate(data);_,cf,_,_,_=estimate(s)
    payload=json.loads((ROOT/'outputs/resultados.json').read_text())
    current=estimate(s)[0]
    if payload['base'] != current or payload['source_hashes'] != data.hashes:
        raise ValueError('Resultados desactualizados: ejecutar value_snowblade.py antes de generar entrega')
    (ROOT/'entrega').mkdir(exist_ok=True)
    print(excel(data,s,payload,cf));print(pdf(data,s,payload))
