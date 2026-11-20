"""Recálculo real en copias temporales con LibreOffice: centinelas, sigma cero y nominal doble.
Nunca abre el XLSM original con una aplicación ni sobrescribe los entregables.
Requiere soffice en PATH (o --soffice /ruta/soffice).
"""
import argparse
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import posixpath
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import numpy as np
import openpyxl
from lmm.inputs import load_inputs,verify_originals
from lmm.model import Config,simulate
from lmm.valuation import estimate

NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
SENTINEL=123456.789

def make_copy(source,dest,zero=False,nominal=None):
    count=0
    with zipfile.ZipFile(source) as src,zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as out:
        sheets=ET.fromstring(src.read('xl/workbook.xml')).findall('m:sheets/m:sheet',NS)
        relationships=ET.fromstring(src.read('xl/_rels/workbook.xml.rels'))
        targets={e.attrib['Id']:posixpath.normpath(posixpath.join('xl',e.attrib['Target'])) for e in relationships}
        sheet_paths = {sheet.attrib['name']: targets[sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
                       for sheet in sheets}
        for item in src.infolist():
            data=src.read(item.filename)
            if item.filename.startswith('xl/worksheets/sheet') and item.filename.endswith('.xml'):
                xml=ET.fromstring(data)
                for c in xml.findall('.//m:c',NS):
                    if c.find('m:f',NS) is not None:
                        v=c.find('m:v',NS)
                        if v is None:v=ET.SubElement(c,'{'+NS['m']+'}v')
                        v.text=str(SENTINEL);count+=1
                    if nominal is not None and item.filename == sheet_paths['Parametros'] and c.attrib['r'] == 'B2':
                        c.find('m:v', NS).text = str(nominal)
                    if zero and item.filename==sheet_paths['Volatilidades']:
                        address=c.attrib['r']
                        if address.startswith('B') and address[1:].isdigit() and 2<=int(address[1:])<=22:
                            c.find('m:v',NS).text='0'
                data=ET.tostring(xml,encoding='utf-8',xml_declaration=True)
            out.writestr(item,data)
    return count


def recalc(executable,source,out,profile,mode):
    out.mkdir();(profile/'user').mkdir(parents=True)
    (profile/'user/registrymodifications.xcu').write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry"><item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="OOXMLRecalcMode" oor:op="fuse"><value>{mode}</value></prop></item></oor:items>''')
    command=[executable,f'-env:UserInstallation={profile.as_uri()}','--headless','--convert-to','xlsx','--outdir',str(out),str(source)]
    process=subprocess.run(command,capture_output=True,text=True,timeout=180)
    result=out/source.name
    if process.returncode or not result.exists():
        raise RuntimeError(f'Falló LibreOffice: {process.stdout} {process.stderr}')
    return result


def audit(executable):
    source=ROOT/'entrega/Snowblade_LMM.xlsx'
    before=sha256(source.read_bytes()).hexdigest()
    originals=verify_originals()
    version=subprocess.run([executable,'--version'],capture_output=True,text=True,check=True).stdout.strip()
    original=openpyxl.load_workbook(source,read_only=True,data_only=True)
    formulas=openpyxl.load_workbook(source,read_only=True,data_only=False)
    original_values={sh.title:{c.coordinate:c.value for row in sh for c in row if hasattr(c,'coordinate')} for sh in original}
    expected={}
    for sh in formulas:
        expected[sh.title]=[(c.coordinate,original_values[sh.title][c.coordinate]) for row in sh for c in row if c.data_type=='f']
    formulas.close();original.close()
    with tempfile.TemporaryDirectory(prefix='lmm-calc-') as folder:
        temp=Path(folder)
        forged=temp/'sentinel.xlsx';count=make_copy(source,forged)
        negative=recalc(executable,forged,temp/'negative',temp/'profile_never',1)
        # Guardar sin recalcular es el control negativo: no se considera validación.
        w=openpyxl.load_workbook(negative,read_only=True,data_only=True)
        preserved=sum(c.value==SENTINEL for sh in w for row in sh for c in row)
        w.close()
        if preserved!=count:raise AssertionError('Control negativo no conservó todos los centinelas')
        forced=recalc(executable,forged,temp/'forced',temp/'profile_always',0)
        w=openpyxl.load_workbook(forced,read_only=True,data_only=True)
        values={sh.title:{c.coordinate:c.value for row in sh for c in row if hasattr(c,'coordinate')} for sh in w}
        errors=[(sh.title,c.coordinate) for sh in w for row in sh for c in row if c.data_type=='e'];w.close()
        residual=0.;remaining=0
        for sheet,entries in expected.items():
            for address,value in entries:
                got=values[sheet][address]
                remaining+=got==SENTINEL
                residual=max(residual,abs(float(got)-float(value)))
        assert not errors and remaining==0 and residual<1e-9,(errors,remaining,residual)
        inputs=load_inputs();zero=simulate(inputs,replace(Config(),vol_scale=0))
        zr,zcf,zpv,zcp,zpp=estimate(zero)
        zero_copy=temp/'zero_vol.xlsx';make_copy(source,zero_copy,zero=True)
        zero_book=recalc(executable,zero_copy,temp/'zero',temp/'profile_zero',0)
        w=openpyxl.load_workbook(zero_book,read_only=True,data_only=True)
        np.testing.assert_allclose(w['Resumen']['B2'].value,zr['price'],rtol=0,atol=1e-10)
        distribution = list(w['Resumen'].iter_rows(min_row=15, max_row=34, max_col=3, values_only=True))
        expected_counts = zr['autocall_counts']
        np.testing.assert_array_equal(distribution, [
            (period, count / len(zpv), count) for period, count in enumerate(expected_counts, 1)
        ])
        states=np.array([[c.value for c in row[7:28]] for row in w['Estados'].iter_rows(min_row=2)],float)
        expected_states=zero.states.transpose(1,0,2).reshape(-1,21)
        np.testing.assert_allclose(states,expected_states,rtol=0,atol=1e-12)
        paths=np.array([[c.value for c in row[1:5]] for row in w['Paths'].iter_rows(min_row=2)],float)
        expected_paths=np.stack([zcp,zpp,zpv,zcf.redemption_period],axis=1)
        np.testing.assert_allclose(paths,expected_paths,rtol=0,atol=1e-10)
        zero_errors=[(sh.title,c.coordinate) for sh in w for row in sh for c in row if c.data_type=='e'];w.close()
        assert not zero_errors
        double_copy = temp / 'nominal_200.xlsx'
        make_copy(source, double_copy, nominal=200)
        double_book = recalc(executable, double_copy, temp/'double', temp/'profile_double', 0)
        w = openpyxl.load_workbook(double_book, read_only=True, data_only=True)
        label, double_pv = next(w['Resumen'].iter_rows(min_row=2, max_row=2, max_col=2, values_only=True))
        w.close()
        assert label == 'PV del nominal introducido'
        np.testing.assert_allclose(double_pv, 2 * values['Resumen']['B2'], rtol=0, atol=1e-10)
    assert sha256(source.read_bytes()).hexdigest()==before
    assert verify_originals()==originals
    record={'engine':version,'source_xlsx_sha256':before,'base_config':estimate(simulate(inputs))[0]['config'],
            'formula_count':count,'negative_control_preserved_sentinels':preserved,
            'forced_remaining_sentinels':remaining,'forced_error_cells':errors,
            'max_formula_cache_difference':residual,'base_price_recalculated':values['Resumen']['B2'],
            'zero_volatility_price':zr['price'],'zero_volatility_state_max_error':float(np.max(abs(states-expected_states))),
            'zero_volatility_paths_max_error':float(np.max(abs(paths-expected_paths))),
            'zero_volatility_autocall_counts':[row[2] for row in distribution],
            'nominal_200_pv_recalculated':double_pv,
            'zero_volatility_error_cells':zero_errors,'original_sha256':originals,'microsoft_excel_tested':False}
    (ROOT/'outputs/recalculo_validacion.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(record,ensure_ascii=False,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--soffice',default=shutil.which('soffice'))
    args=p.parse_args()
    if not args.soffice:p.error('No hay soffice: indicar --soffice /ruta/soffice')
    audit(args.soffice)
