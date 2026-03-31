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
state_municipalities = pd.read_excel(io = path + 'Lista_Municipios_Brasil.xlsx',
                                     usecols = 'B, E',
                                     header = 0,
                                     names = ['municipio', 'regiao'],
                                     sheet_name = 'Ceara',
                                     dtype = {'municipio':str, 'regiao':str})
state_municipalities = state_municipalities.set_index('municipio')

# --- Old Caged --- #
folder_files_caged = os.listdir(path)
data_files_old_caged = [f for f in folder_files_caged if f.endswith('.csv')]
dataframes_old_caged = df_old_caged = pd.DataFrame()        # Empty dataframe

# --- New Caged --- #
data_files_new_caged = [f for f in folder_files_caged if f.endswith('.txt')]
caged_file_kind = ['EXC', 'FOR', 'MOV']
dataframes_new_caged = pd.DataFrame()                       # Empty dataframe

# --- Rais --- #
data_files_rais = [f for f in folder_files_caged if f.endswith('.COMT')]




# ======================= #
# === Data Processing === #
# ======================= #

# ------------------------- #
# --- Caged Old Version --- #
# ------------------------- #

# --- Data Processing Loop --- #
for file in data_files_old_caged:
    df = pd.read_csv(filepath_or_buffer = path + file,
                     sep = ',',
                     header = 1,
                     names = ['ano', 'mes', 'municipio', 'saldo_empregos_caged', 'subclasse'],
                     dtype = {'ano':str, 'mes':str, 'municipio':str, 'subclasse':str, 'saldo_empregos_caged':int}
                     )
    
    df['mes'] = df['mes'].str.zfill(2)
    df = df.assign(periodo = df['ano'].astype('str') + '/' + df['mes'].astype('str'))
    df = df.merge(right = state_municipalities['regiao'], how = 'left', on = 'municipio')
    #df = df.set_index(['municipio', 'subclasse'])
    df_old_caged = pd.concat([df_old_caged, df], ignore_index = True)
    
    
# --- Grouping Results --- #
dataframes_old_caged = df_old_caged.groupby(by = keys, as_index = False)['saldo_empregos_caged'].sum()




# ------------------------- #
# --- Caged New Version --- #
# ------------------------- #

# --- Data Processing Loop --- #
for kind in caged_file_kind:
    caged_files = [f for f in data_files_new_caged if kind in f]
    df_new_caged = pd.DataFrame()   # Empty dataframe

    for file in caged_files:
        df = pd.read_csv(filepath_or_buffer = path + file,
                         sep = ';',
                         header = 1,
                         usecols = [0, 2, 3, 5, 6],
                         names = ['periodo', 'uf', 'municipio', 'subclasse', 'saldo_movimentacao'],
                         dtype = {'periodo':str, 'uf':str, 'municipio':str, 'subclasse':str, 'saldo_movimentacao':int})
        df = df[df.uf == '23']
        df = df.loc[:, ['periodo', 'municipio', 'subclasse', 'saldo_movimentacao']]
        df = df.merge(right = state_municipalities['regiao'], how = 'left', on = 'municipio')
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
df_summary_mov = df_summary_mov.groupby(keys, as_index=False)['saldo_movimentacao'].sum()
df_summary_for = df_summary_for.groupby(keys, as_index=False)['saldo_movimentacao'].sum()
df_summary_exc = df_summary_exc.groupby(keys, as_index=False)['saldo_movimentacao'].sum()
df_summary_exc['saldo_movimentacao'] = (-1)*df_summary_exc['saldo_movimentacao']

# --- Renaming Columns --- #
df_summary_mov = df_summary_mov.rename(columns={'saldo_movimentacao': 'saldo_mov'})
df_summary_for = df_summary_for.rename(columns={'saldo_movimentacao': 'saldo_for'})
df_summary_exc = df_summary_exc.rename(columns={'saldo_movimentacao': 'saldo_exc'})

# --- Final Summary --- #
dataframes_new_caged = df_summary_mov.merge(right = df_summary_for, how = 'left', on = keys).merge(right = df_summary_exc, how = 'left', on = keys)
dataframes_new_caged['saldo_empregos_caged'] = dataframes_new_caged.loc[:, ['saldo_mov', 'saldo_for', 'saldo_exc']].sum(axis = 1)

# --- Few Adjustments --- #
dataframes_new_caged['periodo'] = dataframes_new_caged['periodo'].str.slice(0,4) + '/' + dataframes_new_caged['periodo'].str.slice(4,6)




# ------------ #
# --- Rais --- #
# ------------ #
for file in data_files_rais:
    rais_database = pd.read_csv(filepath_or_buffer = path + file,
                                usecols = [7, 9, 14, 17], 
                                header = 1,
                                names = ['estoque_empregos_rais', 'ind_atividade_ano', 'municipio', 'subclasse'],
                                encoding = 'latin-1',
                                sep = ',',
                                dtype = {'estoque_empregos_caged':int, 'ind_atividade_ano':str, 'municipio':str, 'subclasse':str})

    rais_database = rais_database[
        (rais_database['municipio'].str.slice(0,2) == '23') &
        (rais_database['ind_atividade_ano'] == '1')]
    
    rais_database['subclasse'] = rais_database['subclasse'].str.zfill(7)

    #rais_database = rais_database.set_index('municipio')

    rais_database = rais_database.merge(right = state_municipalities['regiao'], how = 'left', on = 'municipio')
    rais_database['periodo'] = file[22:26] + '/12'
    rais_database = rais_database.groupby(keys, as_index = False)['estoque_empregos_rais'].sum()
    rais_database = rais_database.set_index(keys)

base_period = file[22:26] + '/12'




# ============================== #
# === Employment Full Series === #
# ============================== #
employment_dataframe = pd.concat([dataframes_old_caged, dataframes_new_caged[keys + ['saldo_empregos_caged']]], ignore_index = True)
employment_dataframe = employment_dataframe.merge(right = rais_database['estoque_empregos_rais'], how = 'outer', on = keys)
employment_dataframe = employment_dataframe.groupby(keys, as_index = False).agg({'saldo_empregos_caged':'sum', 'estoque_empregos_rais':'sum'})


group_cols = [k for k in keys if k != 'periodo']


if len(group_cols) == 0:
    employment_dataframe = full_employments(employment_dataframe, base_period)
else:
    employment_dataframe = pd.concat(
        [full_employments(g, base_period) for _, g in employment_dataframe.groupby(group_cols)],
        ignore_index=True
    )




# ======================= #
# === Storing Results === #
# ======================= #
if data_kind == 'm':       
    
    # --- Storing --- #
    with pd.ExcelWriter(path = 'Databases/Outputs/empregos_ceara_macro.xlsx', engine='xlsxwriter') as writer:
        employment_dataframe.to_excel(excel_writer = writer, sheet_name = 'empregos', index = False)
        
elif data_kind == 'r':       
    
    # --- Storing --- #
    with pd.ExcelWriter(path = 'Databases/Outputs/empregos_ceara_regiao.xlsx', engine='xlsxwriter') as writer:
        employment_dataframe.to_excel(excel_writer = writer, sheet_name = 'empregos', index = False)
        
elif data_kind == 'c':       
    
    # --- Storing --- #
    with pd.ExcelWriter(path = 'Databases/Outputs/empregos_ceara_cnae.xlsx', engine='xlsxwriter') as writer:
        employment_dataframe.to_excel(excel_writer = writer, sheet_name = 'empregos', index = False)
        
else:
    
    # --- Storing --- #
    with pd.ExcelWriter(path = 'Databases/Outputs/empregos_ceara_regiao_cnae.xlsx', engine='xlsxwriter') as writer:
        employment_dataframe.to_excel(excel_writer = writer, sheet_name = 'empregos', index = False)




# ===================== #
# === Full Cleasing === #
# ===================== #

#[f for f in dir() if f.startswith(pattern)]         # List of variables

for pattern in {'df', 'data', 'caged'}:
    for var in list(globals().keys()):
        if var.startswith(pattern):
            del globals()[var]
    
del base_period, c, file, folder_files_caged, group_cols, keys, kind, path, pattern, rais_database, state_municipalities, var, writer