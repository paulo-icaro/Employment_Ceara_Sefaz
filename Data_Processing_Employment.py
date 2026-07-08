# ==================================== #
# === DATA PROCESSING - EMPLOYMENT === #
# ==================================== #

# --- Script by: Paulo Icaro --- #


# ================= #
# === Libraries === #
# ================= #
import pandas as pd           # For database manipulations
import os                     # For list folders files
import time                   # For time functions

from Full_Employments import full_employments


# ========================== #
# === Defining Data Kind === #
# ========================== #
while True:
    data_kind = input('Selecione o nivel de detalhamento desejado. Insira: \n(m) para Macro \n(r) para Região \n(c) para CNAE e \n(rc) para Região e Cnae \n').strip().lower()
    if data_kind in {'m', 'r', 'c', 'rc', 'cr'}:
        print('Realizando agregação das informações ...')
        time.sleep(1.5)
        break
    print('Opção inválida ! Tente novamente.')


# ===================== #
# === Key Variables === #
# ===================== #
if data_kind == 'm':
    keys = ['periodo']
elif data_kind == 'r':
    keys = ['periodo', 'regiao']
elif data_kind == 'c':
    keys = ['periodo', 'subclasse']
else:
    keys = ['periodo', 'regiao', 'subclasse']



# ===================== #
# === File Handling === #
# ===================== #

# --- Common Parts --- #
c = 0
path = 'Databases/Inputs/'
folder_files = os.listdir(path)


# --- Auxiliary Databases --- #
state_municipalities = pd.read_excel(io = path + 'Lista_Municipios_Brasil.xlsx',
                                     usecols = 'B, E', header = 0, sheet_name = 'Ceara',
                                     names = ['municipio', 'regiao'],
                                     dtype = {'municipio':str, 'regiao':str})
state_municipalities = state_municipalities.set_index('municipio')

cnae_list = pd.read_excel(io = path + 'Lista_Cnaes.xlsx',
                          usecols = 'A:K', header = 0, sheet_name = 'Lista - Cnaes',
                          names = ['setor', 'secao', 'desc_secao', 'divisao', 'desc_divisao', 'grupo', 'desc_grupo', 'classe', 'desc_classe', 'subclasse', 'desc_subclasse'],
                          dtype = {'divisao':str, 'grupo':str, 'classe':str, 'subclasse':str})
cnae_list = cnae_list.set_index('subclasse')


# --- Old Caged Files --- #
data_files_old_caged = [f for f in folder_files if f.endswith('.csv')]


# --- New Caged Files --- #
data_files_new_caged = [f for f in folder_files if f.endswith('.txt')]
caged_file_kind = ['EXC', 'FOR', 'MOV']


# --- Rais Files --- #
data_files_rais = [f for f in folder_files if f.endswith('.COMT')]





# ======================= #
# === Data Processing === #
# ======================= #

# -------------------------- #
# --- Results Dataframes --- #
# -------------------------- #
dataframe_old_caged = df_old_caged = dataframe_new_caged = dataframe_rais_estab = dataframe_rais_vinc = rais_vinc = pd.DataFrame()        # Empty dataframes


# ------------------------- #
# --- Caged Old Version --- #
# ------------------------- #

# --- Data Processing --- #
for file in data_files_old_caged:
    df = pd.read_csv(filepath_or_buffer = path + file,
                     sep = ',',
                     header = 0,
                     names = ['ano', 'mes', 'municipio', 'saldo_empregos_caged', 'subclasse', 'massa_salarial_caged'],
                     dtype = {'ano':str, 'mes':str, 'municipio':str, 'subclasse':str, 'saldo_empregos_caged':int, 'massa_salarial_caged':float}
                     )
    
    df['mes'] = df['mes'].str.zfill(2)
    df = df.assign(periodo = df['ano'].astype('str') + '/' + df['mes'].astype('str'))
    df = df.merge(right = state_municipalities['regiao'], how = 'left', on = 'municipio')
    df_old_caged = pd.concat([df_old_caged, df], ignore_index = True)
    
# --- Grouping Results --- #
dataframe_old_caged = df_old_caged.groupby(by = keys, as_index = False).agg({'saldo_empregos_caged':'sum', 'massa_salarial_caged':'sum'})



# ------------------------- #
# --- Caged New Version --- #
# ------------------------- #

# --- Data Processing --- #
for kind in caged_file_kind:
    caged_files = [f for f in data_files_new_caged if kind in f]
    df_new_caged = pd.DataFrame()   # Empty dataframe

    for file in caged_files:
        df = pd.read_csv(filepath_or_buffer = path + file,
                         sep = ';',
                         header = 0,
                         usecols = [0, 2, 3, 5, 6, 20],
                         names = ['periodo', 'uf', 'municipio', 'subclasse', 'saldo_movimentacao', 'salario'],
                         dtype = {'periodo':str, 'uf':str, 'municipio':str, 'subclasse':str, 'saldo_movimentacao':int, 'salario':str})
        df = df[df.uf == '23']
        df['salario'] = df['salario'].str.replace(',', '.').astype('float')
        df = df.loc[:, ['periodo', 'municipio', 'subclasse', 'saldo_movimentacao', 'salario']]
        df = df.merge(right = state_municipalities['regiao'], how = 'left', on = 'municipio')
        #df = df.merge(right = cnae_list['setor'], how = 'left', on = 'subclasse')
        df['subclasse'] = df['subclasse'].str.zfill(7)
        
        
        # --- Storing Dataframes --- #
        df_new_caged = pd.concat([df_new_caged, df], ignore_index = True)
        
        
    # --- Defining Databases According to Aggregation Type --- #
    if kind == 'EXC':
        df_summary_exc = df_new_caged
    elif kind == 'FOR':
        df_summary_for = df_new_caged
    else:
        df_summary_mov = df_new_caged


# --- Setting Keys --- #
df_summary_mov = df_summary_mov.set_index(keys)
df_summary_for = df_summary_for.set_index(keys)
df_summary_exc = df_summary_exc.set_index(keys)

# --- Grouping Results --- #
df_summary_mov = df_summary_mov.groupby(keys, as_index=False).agg({'saldo_movimentacao':'sum', 'salario':'sum'})
df_summary_for = df_summary_for.groupby(keys, as_index=False).agg({'saldo_movimentacao':'sum', 'salario':'sum'})
df_summary_exc = df_summary_exc.groupby(keys, as_index=False).agg({'saldo_movimentacao':'sum', 'salario':'sum'})
df_summary_exc['saldo_movimentacao'] = (-1)*df_summary_exc['saldo_movimentacao']
df_summary_exc['salario'] = (-1)*df_summary_exc['salario']

# --- Renaming Columns --- #
df_summary_mov = df_summary_mov.rename(columns={'saldo_movimentacao': 'saldo_mov', 'salario':'massa_salarial_mov'})
df_summary_for = df_summary_for.rename(columns={'saldo_movimentacao': 'saldo_for', 'salario':'massa_salarial_for'})
df_summary_exc = df_summary_exc.rename(columns={'saldo_movimentacao': 'saldo_exc', 'salario':'massa_salarial_exc'})

# --- Final Summary --- #
dataframe_new_caged = df_summary_mov.merge(right = df_summary_for, how = 'left', on = keys).merge(right = df_summary_exc, how = 'left', on = keys)
dataframe_new_caged['saldo_empregos_caged'] = dataframe_new_caged.loc[:, ['saldo_mov', 'saldo_for', 'saldo_exc']].sum(axis = 1)
dataframe_new_caged['massa_salarial_caged'] = dataframe_new_caged.loc[:, ['massa_salarial_mov', 'massa_salarial_for', 'massa_salarial_exc']].sum(axis = 1)

# --- Few Adjustments --- #
dataframe_new_caged['periodo'] = dataframe_new_caged['periodo'].str.slice(0,4) + '/' + dataframe_new_caged['periodo'].str.slice(4,6)



# ----------------------------- #
# --- Rais Estabelecimentos --- #
# ----------------------------- #
for file in data_files_rais:
    rais_estab = pd.read_csv(filepath_or_buffer = path + file,
                                usecols = [7, 9, 14, 17], 
                                header = 0,
                                names = ['estoque_empregos_rais_estab', 'ind_atividade_ano', 'municipio', 'subclasse'],
                                encoding = 'latin-1',
                                sep = ',',
                                dtype = {'estoque_empregos_rais_estab':int, 'ind_atividade_ano':str, 'municipio':str, 'subclasse':str})

    rais_estab = rais_estab[
        (rais_estab['municipio'].str.slice(0,2) == '23') &
        (rais_estab['ind_atividade_ano'] == '1')]
    
    rais_estab['subclasse'] = rais_estab['subclasse'].str.zfill(7)


    rais_estab = rais_estab.merge(right = state_municipalities['regiao'], how = 'left', on = 'municipio')
    rais_estab['periodo'] = file[22:26] + '/12'
    dataframe_rais_estab = rais_estab.groupby(keys, as_index = False)['estoque_empregos_rais_estab'].sum()



# --------------------- #
# --- Rais Vinculos --- #
# --------------------- #
with pd.read_csv('Databases/RAIS_VINC_PUB_NORDESTE.COMT',
                   sep = ',', encoding = 'latin-1', header = 0, chunksize = 50000,
                   usecols = [7, 11, 25, 32, 33, 34, 35, 36, 44],
                   names = ['cbo', 'ind_vinc', 'municipio', 'rem_dez_nom', 'rem_dez_sm', 'rem_media_nom', 'rem_media_sm', 'subclasse', 'tp_vinculo'],
                   dtype = {'municipio':str, 'subclasse':str}) as reader:
    #print(reader)
    for chunk in reader:
        rais_vinc_chunk = chunk[
            (chunk['municipio'].str.slice(0,2) == '23') &
            (chunk['ind_vinc'] == 1) &
            (~chunk['tp_vinculo'].isin([40, 50, 55, -1]))]
        rais_vinc = pd.concat([rais_vinc, rais_vinc_chunk], ignore_index = True)

rais_vinc['subclasse'] = rais_vinc['subclasse'].str.zfill(7)

rais_vinc = rais_vinc[['rem_dez_nom', 'municipio', 'subclasse']]
rais_vinc = rais_vinc.merge(right = state_municipalities['regiao'], how = 'left', on = 'municipio')

rais_vinc['periodo'] = '2024/12'
dataframe_rais_vinc = rais_vinc.groupby(keys, as_index = False).agg(estoque_empregos_rais_vinc = ('municipio', 'count'), massa_salarial_rais_vinc = ('rem_dez_nom', 'sum'))




# ============================== #
# === Employment Full Series === #
# ============================== #

# --- Time Dataframe --- #
k = 0
time_interval = pd.DataFrame(columns = ['periodo'])
for ano in range(2015,2026):
    for mes in range(1,13):
        time_interval.loc[k, 'periodo'] = f'{ano}/{mes:02d}'
        k += 1


# --- Assembling all dataframes --- #
employment_dataframe = pd.concat([dataframe_old_caged, dataframe_new_caged[keys + ['saldo_empregos_caged', 'massa_salarial_caged']]], ignore_index = True)
employment_dataframe = employment_dataframe.merge(right = dataframe_rais_estab[keys + ['estoque_empregos_rais_estab']], how = 'outer', on = keys)
employment_dataframe = employment_dataframe.merge(right = dataframe_rais_vinc[keys + ['estoque_empregos_rais_vinc', 'massa_salarial_rais_vinc']], how = 'outer', on = keys)


# --- Final Dataframe --- #
if data_kind == 'm':
    employment_dataframe_full = time_interval
elif data_kind == 'r':
    employment_dataframe_full = time_interval.merge(right = pd.DataFrame(employment_dataframe['regiao'].unique(), columns = ['regiao']), how = 'left')
elif data_kind == 'c':
    employment_dataframe_full = time_interval.merge(right = pd.DataFrame(employment_dataframe['subclasse'].unique(), columns = ['subclasse']), how = 'left')
else:
    employment_dataframe_full = time_interval.merge(right = pd.DataFrame(employment_dataframe['regiao'].unique(), columns = ['regiao']), how = 'left').merge(right = pd.DataFrame(employment_dataframe['subclasse'].unique(), columns = ['subclasse']), how = 'cross')
    
employment_dataframe_full = employment_dataframe_full.merge(right = employment_dataframe, how = 'left', on = keys)
employment_dataframe_full = employment_dataframe_full.fillna(0)


# --- Final Employees Amount and Wage Approach --- #
group_cols = [k for k in keys if k != 'periodo']
base_period = file[22:26] + '/12'

if len(group_cols) == 0:
    employment_dataframe_full = full_employments(employment_dataframe_full, base_period)
else:
    employment_dataframe_full = pd.concat(
        [full_employments(g, base_period) for _, g in employment_dataframe_full.groupby(group_cols)],
        ignore_index=True)




# ======================= #
# === Storing Results === #
# ======================= #
if data_kind == 'm':       
    with pd.ExcelWriter(path = 'Databases/Outputs/empregos_ceara_macro.xlsx', engine='xlsxwriter') as writer:
        employment_dataframe_full.to_excel(excel_writer = writer, sheet_name = 'empregos', index = False)
        
elif data_kind == 'r':       
    with pd.ExcelWriter(path = 'Databases/Outputs/empregos_ceara_regiao.xlsx', engine='xlsxwriter') as writer:
        employment_dataframe_full.to_excel(excel_writer = writer, sheet_name = 'empregos', index = False)
        
elif data_kind == 'c':       
    with pd.ExcelWriter(path = 'Databases/Outputs/empregos_ceara_cnae.xlsx', engine='xlsxwriter') as writer:
        employment_dataframe_full.to_excel(excel_writer = writer, sheet_name = 'empregos', index = False)
        
else:
    with pd.ExcelWriter(path = 'Databases/Outputs/empregos_ceara_regiao_cnae.xlsx', engine='xlsxwriter') as writer:
        employment_dataframe_full.to_excel(excel_writer = writer, sheet_name = 'empregos', index = False)




# ===================== #
# === Full Cleasing === #
# ===================== #
#[f for f in dir() if f.startswith(pattern)]         # List of variables
for pattern in {'df', 'data', 'caged', 'rais'}:
    for var in list(globals().keys()):
        if var.startswith(pattern):
            del globals()[var]
    
del (ano, mes, base_period, c, k, file, folder_files,
     reader, group_cols, keys, kind, path, pattern,
     cnae_list, state_municipalities, time_interval,
     chunk, employment_dataframe, var, writer)