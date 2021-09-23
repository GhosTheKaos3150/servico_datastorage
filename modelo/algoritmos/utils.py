import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy import stats

def predict(model, dados):

    def gen_latencia_data(row: dict):
        list_dict = []
        row['t3_end'] = np.int64(row['t3_end'])
        row['t_target'] = 0
        for t in np.arange(1, row['t3_end']):
            new_row = row.copy()
            new_row['t_target'] = t
            list_dict.append(new_row)
        return list_dict

    list_dicts = list(dados.apply(lambda row: gen_latencia_data(dict(row)), axis=1))

    df_to_predict = pd.DataFrame()
    for dict_list in list_dicts:
        df = pd.DataFrame(dict_list)
        df_to_predict = pd.concat([df_to_predict, df])

    df_to_predict.reset_index(inplace=True, drop=True)
    predicted_points = model.predict(df_to_predict)
    df_predito = pd.DataFrame(predicted_points, columns = ['x_predito','y_predito','z_predito'])
    return df_predito


def validation(df_test: pd.DataFrame, df_predito: pd.DataFrame):
    x_real = df_test['x2']
    x_previsto = df_predito['x2']
    rmse_x = mean_squared_error(x_real, x_previsto) ** 1 / 2
    _, _, r_value, _, _ = stats.linregress(x_real, x_previsto)
    r2_x = r_value*r_value
    mae_x = mean_absolute_error(x_real, x_previsto)
    mse_x = mean_squared_error(x_real, x_previsto)

    y_real = df_test['y2']
    y_previsto = df_predito['y2']
    rmse_y = mean_squared_error(y_real, y_previsto) ** 1 / 2
    _, _, r_value, _, _ = stats.linregress(y_real, y_previsto)
    r2_y = r_value*r_value
    mae_y = mean_absolute_error(y_real, y_previsto)
    mse_y = mean_squared_error(y_real, y_previsto)

    return (r2_x, r2_y), (rmse_x, rmse_y), (mae_x, mae_y), (mse_x, mse_y)


def splitData(df: pd.DataFrame, p_train: float, window_size = 3):
    x_start_train = []
    y_start_train = []
    time_start_train = []
    x_end_train = []
    y_end_train = []
    time_end_train = []

    x_target_train = []
    y_target_train = []
    time_target_train = []

    x_start_test = []
    y_start_test = []
    time_start_test = []
    x_end_test = []
    y_end_test = []
    time_end_test = []

    x_real_test = []
    y_real_test = []
    time_real_test = []

    feat_train_data = {}
    feat_test_data = {}
    target_train_data = {}
    real_data = {}
    
    jump = window_size - 1
    for i in range(0, len(df) - jump):
        if (i + jump) <= (len(df) * p_train) - 1:
            for k in range(1, jump):
                x_start_train.append(df.loc[i, "x"])
                y_start_train.append(df.loc[i, "y"])
                time_start_train.append(0)

                x_target_train.append(df.loc[i + k, "x"])
                y_target_train.append(df.loc[i + k, "y"])
                time_target_train.append(k)

                x_end_train.append(df.loc[i + jump, "x"])
                y_end_train.append(df.loc[i + jump, "y"])
                time_end_train.append(jump)
                
        elif i >= len(df) - (len(df) * (1-p_train)):
            for j in reversed(range(2, window_size)):
                for k in range(1, jump):
                    x_start_test.append(df.loc[i, "x"])
                    y_start_test.append(df.loc[i, "y"])
                    time_start_test.append(0)

                    x_real_test.append(df.loc[i + k, "x"])
                    y_real_test.append(df.loc[i + k, "y"])
                    time_real_test.append(k)

                    x_end_test.append(df.loc[i + jump, "x"])
                    y_end_test.append(df.loc[i + jump, "y"])
                    time_end_test.append(jump)

    feat_train_data['x1'] = x_start_train
    feat_train_data['y1'] = y_start_train
    feat_train_data['x3'] = x_end_train
    feat_train_data['y3'] = y_end_train
    feat_train_data['t3'] = time_end_train
    feat_train_data['t2'] = time_target_train

    target_train_data['x2'] = x_target_train
    target_train_data['y2'] = y_target_train

    df_feat_train = pd.DataFrame(data=feat_train_data)
    
    df_target_train = pd.DataFrame(data=target_train_data)

    feat_test_data['x1'] = x_start_test
    feat_test_data['y1'] = y_start_test
    feat_test_data['x3'] = x_end_test
    feat_test_data['y3'] = y_end_test
    feat_test_data['t3'] = time_end_test
    feat_test_data['t2'] = time_real_test

    real_data['x2'] = x_real_test
    real_data['y2'] = y_real_test
    
    df_feat_test = pd.DataFrame(data=feat_test_data)
    
    df_real = pd.DataFrame(data=real_data)
    
    return df_feat_train, df_target_train, df_feat_test, df_real