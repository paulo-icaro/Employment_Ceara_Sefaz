# ======================== #
# === FULL EMPLOYMENTS === #
# ======================== #

# --- Script by: Paulo Icaro --- #


# ================================= #
# === Full Employments Function === #
# ================================= #
def full_employments(db, base_period):
    db = db.sort_values('periodo').reset_index(drop= True)
    
    # ------------- #
    # --- Flags --- #
    # ------------- #
    before = db['periodo'] <= base_period
    base = db['periodo'] == base_period
    after = db['periodo'] > base_period       
        
        
    # --- Check where there is a matching db --- #
    if base.sum() == 0:
        base_value_empregos = 0
        db['flag_sem_rais'] = True
    else:
        base_value_empregos = db.loc[base, 'estoque_empregos_rais_vinc'].iloc[0]
        base_value_massa_salarial = db.loc[base, 'massa_salarial_rais_vinc'].iloc[0]
        db['flag_sem_rais'] = False

    # ------------------------ #
    # --- Flag Adjustments --- #
    # ------------------------ #
    
    #db['estoque_empregos'] = None
    
    # --- Before --- #
    db.loc[before, 'estoque_empregos'] = base_value_empregos - db.loc[before, 'saldo_empregos_caged'][::-1].cumsum()[::-1].shift(-1)
    db.loc[before, 'massa_salarial'] = base_value_massa_salarial - db.loc[before, 'massa_salarial_caged'][::-1].cumsum()[::-1].shift(-1)
    
    # --- Base --- #
    db.loc[base, 'estoque_empregos'] = base_value_empregos
    db.loc[base, 'massa_salarial'] = base_value_massa_salarial
    
    # --- After --- #
    db.loc[after, 'estoque_empregos'] = base_value_empregos + db.loc[after, 'saldo_empregos_caged'].cumsum()
    db.loc[after, 'massa_salarial'] = base_value_massa_salarial + db.loc[after, 'massa_salarial_caged'].cumsum()
    
    db['salario_medio'] = db['massa_salarial']/db['estoque_empregos']
    
    return db
