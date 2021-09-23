import pandas as pd

def run(df, col_x1, col_y1, col_z1, col_x3, col_y3, col_z3, col_t3, col_target):

    def get_proporcional_interpolation(row):

        x_diff = row[col_x3] - row[col_x1]
        y_diff = row[col_y3] - row[col_y1]
        z_diff = row[col_z3] - row[col_z1]

        perc_total = (row[col_target]) / row[col_t3]

        x = row[col_x1] + x_diff * perc_total
        y = row[col_y1] + y_diff * perc_total
        z = row[col_z1] + z_diff * perc_total
        return {"x2": x, "y2": y, "z2": z}

    list_dicts = list(df.apply(lambda row: get_proporcional_interpolation(dict(row)), axis=1))
    df_interpoled = pd.DataFrame(list_dicts)

    df_interpoled.columns = ["x2", "y2", "z2"]
    return df_interpoled