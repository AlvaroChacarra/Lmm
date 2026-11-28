"""Excel nuevo con fórmulas y cachés reconciliadas; memoria PDF, sin alterar XLSM."""
import json
from datetime import datetime
from pathlib import Path
import sys
from datetime import timedelta
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import numpy as np
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell as cell
from academic_report import pdf
from lmm.inputs import load_inputs
from lmm.model import simulate, drift
from lmm.valuation import estimate
from lmm.payoff import SPREADS


def excel(data,s,payload,cf):
    dest=ROOT/'entrega/Snowblade_LMM.xlsx'
    w=xlsxwriter.Workbook(dest)
    w.set_properties({'title':'Snowblade LMM - AFI','author':'Proyecto LMM',
                      'comments':'Libro nuevo sin VBA; fuentes originales intactas.',
                      'created':datetime(2026,11,14)})
    w.set_calc_mode('auto')
    hdr=w.add_format({'bg_color':'#072146','font_color':'white','bold':True,'text_wrap':True,'valign':'vcenter'})
    num=w.add_format({'num_format':'0.000000'})
    pct=w.add_format({'num_format':'0.0000%'})
    datefmt=w.add_format({'num_format':'dd/mm/yyyy'})
    money=w.add_format({'num_format':'0.0000'})
    title=w.add_format({'bold':True,'font_size':16,'font_color':'#072146'})
    text=w.add_format({'text_wrap':True,'valign':'top'})
    order=['Resumen','Ejemplo','Paths','Flujos','Estados','Parametros','Calendario',
           'Covarianza','Curva','Volatilidades','PCA','Aleatorios']
    sheets={name:w.add_worksheet(name) for name in order}
    def sheet(name,head,width=18):
        sh=sheets[name];sh.freeze_panes(1,2);sh.set_row(0,32);sh.write_row(0,0,head,hdr)
        sh.set_column(0,len(head)-1,width)
        return sh
    summary=sheet('Resumen',['Snowblade · valoración','Resultado'],28)
    nav=w.add_format({'font_color':'#004481','underline':1})
    example=sheets['Ejemplo']
    for sh in sheets.values():
        sh.set_tab_color('#CAD7E2')
    summary.set_tab_color('#004481')
    example.set_tab_color('#2DCCCD')
    summary.set_column('A:A',33)
    summary.set_column('B:B',18)
    summary.set_column('C:C',13)
    summary.set_column('D:D',4)
    summary.set_column('E:E',38)
    summary.freeze_panes(0,0)
    highlight=w.add_format({'num_format':'0.00','font_size':16,'bold':True,'font_color':'#004481'})
    frequency=w.add_format({'num_format':'0.0%'})
    amount=w.add_format({'num_format':'0.00'})
    input_pct=w.add_format({'font_color':'#1973B8','num_format':'0.00%'})
    params=sheet('Parametros',['Parámetro','Valor'],30)
    for r,entry in enumerate([('Nominal',100.),('Shift',data.shift),('Objetivo efectivo neto',.04),('P(0,T*)',s.initial_terminal),('Paths',200),('Cupones iniciales anualizados',.01),('Paso de difusión (años)',data.dt_template)],1):params.write_row(r,0,entry)
    curve=sheet('Curva',['Días desde origen','Fecha','Descuento'],22)
    for r,(d,df) in enumerate(zip(data.days,data.discounts),1):
        curve.write_number(r,0,d);curve.write_datetime(r,1,data.start+timedelta(days=int(d)),datefmt);curve.write_number(r,2,df,num)
    volsheet=sheet('Volatilidades',['Periodo original','Sigma original','Uso en malla','Celda fuente'],24)
    for k,vol in enumerate(data.vols):
        volsheet.write_row(k+1,0,[k+1,vol,f'F{k+1}' if k<20 else 'Extra; fuera de malla',f'Curva y volas!F{k+9}'])
    cal=sheet('Calendario',['i','Fecha','Días','ACT/365','P0','Spot i=0 / Forward i>=1','Sigma','Carga 1','Carga 2','Carga 3','Spread cupón'],19)
    for i in range(22):
        r=i+1;cal.write_number(r,0,i);cal.write_datetime(r,1,s.dates[i],datefmt);cal.write_number(r,2,int(s.days[i]))
        d=int(s.days[i]);k=min(max(np.searchsorted(data.days,d,side='left')-1,0),len(data.days)-2)
        ca=k+2;cb=k+3
        formula=f'=EXP(LN(Curva!C{ca})+(LN(Curva!C{cb})-LN(Curva!C{ca}))*(C{r+1}-Curva!A{ca})/(Curva!A{cb}-Curva!A{ca}))'
        cal.write_formula(r,4,formula,num,s.p0[i])
        if i<21:
            cal.write_formula(r,3,f'=(C{r+2}-C{r+1})/365',num,s.delta[i])
            cal.write_formula(r,5,f'=(E{r+1}/E{r+2}-1)/D{r+1}',pct,s.f0[i])
            if i==0:
                cal.write_number(r,6,0,pct)  # Spot conocido, no consume sigma.
            else:
                cal.write_formula(r,6,f'=Volatilidades!B{i+1}',pct,data.vols[i-1])
            if i==0:
                cal.write_row(r,7,[0.,0.,0.],num)
            else:
                for k, loading in enumerate(data.loadings[i-1]):
                    cal.write_formula(r,7+k,'=PCA!'+cell(i,k+1),num,loading)
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
    rnd=sheet('Aleatorios',['Factor','Paso','Path','Normal original'],18)
    for k in range(3):
        for n in range(20):
            for p in range(200):rnd.write_row(1+k*4000+n*200+p,0,[k+1,n+1,p+1,data.normals[k,n,p]])
    st=sheet('Estados',['Path','Paso','Fecha','Paso de difusión (años)','Z1','Z2','Z3']+[f'F{i}' for i in range(21)]+[f'mu{i}' for i in range(21)],15)
    for p in range(200):
        for n in range(21):
            r=1+p*21+n;st.write_number(r,0,p+1);st.write_number(r,1,n);st.write_datetime(r,2,s.dates[n],datefmt)
            if n:
                st.write_formula(r,3,'=Parametros!$B$8',num,data.dt_template)
            else:
                st.write_number(r,3,0,num)
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
    flows=sheet('Flujos',['Path','Periodo','Pago','Euribor fijado al inicio','Tasa anual cupón','ACT365','Vivo antes','Cupón pagado','Acumulado / nominal','Autocall','Principal','P(t,T*)','PV cupón','PV principal','PV total'],20)
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
    paths=sheet('Paths',['Path','PV cupones','PV principal','PV total','Semestre de amortización','Vida bajo Q* (años)','Autocall'],23)
    report,_,pv,cp,pp=estimate(s)
    for p in range(200):
        r=p+1;first=p*20+2;last=first+19
        paths.write_number(r,0,p+1)
        for col,source,val in [(1,'M',cp[p]),(2,'N',pp[p]),(3,'O',pv[p])]:paths.write_formula(r,col,f'=SUM(Flujos!{source}{first}:{source}{last})',money,val)
        paths.write_formula(r,4,f'=SUMPRODUCT(Flujos!B{first}:B{last},Flujos!K{first}:K{last})/Parametros!$B$2',num,int(cf.redemption_period[p]))
        paths.write_formula(r,5,f'=INDEX(Calendario!C2:C23,E{r+1}+1)/365',num,s.days[cf.redemption_period[p]]/365)
        paths.write_formula(r,6,f'=SUM(Flujos!J{first}:J{last})',None,int(cf.call_event[p].any()))
    for r,(label,formula,value) in enumerate([
        ('PV del nominal introducido','=AVERAGE(Paths!D2:D201)',report['price']),
        ('PV cupones','=AVERAGE(Paths!B2:B201)',report['coupon_pv']),
        ('PV principal','=AVERAGE(Paths!C2:C201)',report['principal_pv']),
        ('Error estándar','=STDEV(Paths!D2:D201)/SQRT(COUNT(Paths!D2:D201))',report['standard_error']),
        ('IC 95% · límite inferior','=B2-TINV(0.05,199)*B5',report['ci95_student'][0]),
        ('IC 95% · límite superior','=B2+TINV(0.05,199)*B5',report['ci95_student'][1]),
        ('Vida media bajo Q* (años)','=AVERAGE(Paths!F2:F201)',report['expected_life_years_Q_terminal']),
        ('Supervivencia sin autocall Q*','=1-AVERAGE(Paths!G2:G201)',report['maturity_no_call_probability_Q_terminal'])],1):
        summary.write(r,0,label);summary.write_formula(r,1,formula,highlight if r==1 else frequency if r==8 else amount,value)
    paths.write_row('I1', ['Semestre','Frecuencia de autocancelación Q*','Recuento'], hdr)
    paths.set_column('I:K',20)
    for period, count in enumerate(report['autocall_counts'], 1):
        row = period
        address = row + 1
        paths.write_number(row, 8, period)
        paths.write_formula(row, 10,
                              f'=COUNTIFS($E$2:$E$201,I{address},$G$2:$G$201,1)',
                              None, count)
        paths.write_formula(row, 9, f'=K{address}/COUNT($A$2:$A$201)',
                              frequency, count / len(pv))
    summary.set_row(1,34)
    summary.merge_range('E1:F1','¿Cómo llegamos al precio?',hdr)
    summary.merge_range('E2:F2','Calculamos el valor de cada trayectoria y hacemos la media de las 200.',text)
    summary.write('E4','Nominal usado en la valoración')
    summary.write_formula('F4','=Parametros!B2',amount,100)
    summary.set_column('F:F',15)
    summary.merge_range('E6:F6','El intervalo nos dice con qué precisión estimamos el precio con esta muestra.',text)
    summary.set_row(5,30)
    summary.merge_range('E8:F9','Calculamos estas frecuencias bajo Q*, la medida del bono que usamos para valorar los pagos.',text)
    summary.write_url('E11',"internal:'Ejemplo'!A1",nav,string='Seguir los pagos de la trayectoria 1')
    summary.write_url('E12',"internal:'Paths'!A1",nav,string='Consultar las 200 valoraciones')
    summary.write_url('E13',"internal:'Parametros'!A1",nav,string='Ver los supuestos de cálculo')
    summary.merge_range('A11:C11','Amortización en la muestra',hdr)
    summary.write('A12','Alcanzan el objetivo')
    summary.write_formula('B12','=SUM(Paths!G2:G201)',None,sum(report['autocall_counts']))
    summary.write('A13','Llegan al final sin alcanzarlo')
    summary.write_formula('B13','=COUNT(Paths!G2:G201)-B12',None,report['maturity_no_call_count'])
    for row in [2,3,4,6,9,10,11,12]: summary.set_row(row,21)
    summary.print_area('A1:F13')
    summary.set_paper(9)
    example.set_column('A:A',10)
    example.set_column('B:H',13)
    example.set_column('I:I',14)
    example.merge_range('A1:I1','Trayectoria 1 · del Euribor al valor presente',title)
    example.set_row(0,26)
    example.merge_range('A2:I2','Leemos una fila por semestre. El cupón es lo que cobramos o pagamos. El acumulado indica qué porcentaje del nominal llevamos cobrado en neto.',text)
    example.set_row(1,34)
    headers=['Semestre','Euribor fijado','Tasa anual','ACT/365','Cupón pagado','Acumulado','Principal','Bono terminal','PV del flujo']
    example.write_row('A4',headers,hdr)
    example.set_row(3,32)
    for j in range(20):
        values=[j+1,s.fixings[0,j],cf.rates[0,j],s.delta[j],cf.paid_coupon[0,j],
                cf.cumulative_paid_fraction[0,j],cf.paid_principal[0,j],s.terminal_bonds[0,j],
                (cf.paid_coupon[0,j]+cf.paid_principal[0,j])*s.initial_terminal/s.terminal_bonds[0,j]]
        for k,(col,fmt,val) in enumerate(zip('BDEFHIKLO',
                                       [None,pct,pct,num,money,pct,money,num,money],values)):
            example.write_formula(4+j,k,f'=Flujos!{col}{j+2}',fmt,val)
    example.merge_range('A26:G26','¿Cuánto valen hoy todos los pagos de esta trayectoria?',text)
    example.write('H26','PV total',hdr)
    example_total=w.add_format({'num_format':'0.0000','font_size':14,'bold':True,'font_color':'#004481'})
    example.write_formula('I26','=SUM(I5:I24)',example_total,pv[0])
    example.set_row(25,25)
    example.conditional_format('A5:I24',{'type':'formula','criteria':'=$G5>0',
                               'format':w.add_format({'bold':True,'bg_color':'#D9F5F4'})})
    example.conditional_format('A5:I24',{'type':'formula','criteria':'=SUM($G$5:$G5)>$G5',
                               'format':w.add_format({'font_color':'#657783','bg_color':'#F4F4F4'})})
    example.write_url('A28',"internal:'Flujos'!A2",nav,string='Ver flujos')
    example.write_url('E28',"internal:'Paths'!D2",nav,string='Ver trayectoria en Paths')
    example.freeze_panes(4,1)
    example.print_area('A1:I28')
    for sh, last, cols in [(st,4200,49),(flows,4000,15),(paths,200,7),(rnd,12000,4)]:
        sh.autofilter(0,0,last,cols-1)
    volsheet.set_column('B:B',21,input_pct)
    params.write('B3',data.shift,input_pct)
    params.write('B4',0.04,input_pct)
    params.write('B7',0.01,input_pct)
    params.write('C1','Uso',hdr)
    params.set_column('C:C',55)
    params.write('C6','Dimensión fija de la muestra suministrada')
    params.write('C8','Paso de simulación. El pago usa el ACT/365 de Calendario.')
    paths.set_column('E:E',26)
    paths.set_column('A:A',12)
    example.set_column('B:C',15)
    for sh in w.worksheets():
        sh.hide_gridlines(2);sh.set_landscape();sh.fit_to_pages(1,0);sh.repeat_rows(0)
    for sh in (summary,example):
        sh.set_paper(9);sh.fit_to_pages(1,1);sh.center_horizontally()
    w.close()
    return dest


if __name__=='__main__':
    data=load_inputs();s=simulate(data);_,cf,_,_,_=estimate(s)
    payload=json.loads((ROOT/'outputs/resultados.json').read_text())
    current=estimate(s)[0]
    if payload['base'] != current or payload['source_hashes'] != data.hashes:
        raise ValueError('Resultados desactualizados: ejecutar value_snowblade.py antes de generar entrega')
    (ROOT/'entrega').mkdir(exist_ok=True)
    print(excel(data,s,payload,cf));print(pdf(data,s,payload))
