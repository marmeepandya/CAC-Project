
# DEBUG: check index alignment
print("\nDEBUG - extracted_df index sample:", extracted_df.index[:5].tolist())
print("DEBUG - eval_df df1_idx sample:", eval_df["df1_idx"][:5].tolist())
print("DEBUG - do they overlap?", set(eval_df["df1_idx"]) & set(extracted_df.index))
