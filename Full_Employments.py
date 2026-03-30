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
        
        
    # --- Check whether there is a matching db --- #
    if base.sum() == 0:
        base_value = 0
        db['flag_sem_rais'] = True
    else:
        base_value = db.loc[base, 'estoque_empregos_rais'].iloc[0]
        db['flag_sem_rais'] = False

    # ------------------------ #
    # --- Flag Adjustments --- #
    # ------------------------ #
    
    db['estoque_empregos'] = None
    
    # --- Before --- #
    db.loc[before, 'estoque_empregos'] = base_value - db.loc[before, 'saldo_empregos_caged'][::-1].cumsum()[::-1].shift(-1)

    
    # --- Base --- #
    db.loc[base, 'estoque_empregos'] = base_value
    
    # --- After --- #
    db.loc[after, 'estoque_empregos'] = base_value + db.loc[after, 'saldo_empregos_caged'].cumsum()
    
    return db
