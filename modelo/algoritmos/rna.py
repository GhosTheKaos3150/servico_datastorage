import os
import matplotlib.pyplot as plt
import pandas as pd
import tensorflow as tf
from tensorflow.keras import models, layers, optimizers
from modelo import modelagem_utils as utils


def run(dados: pd.DataFrame, ambiente: str, latencia: int, use_gpu=False, store_metrics=False):
    global path
    global min_x
    global max_x
    global min_y
    global max_y
    global min_t
    global max_t
    global w

    path = f"../modelagem/{ambiente}/rna"
    if not os.path.exists(f"../modelagem/{ambiente}"):
        os.mkdir(f"../modelagem/{ambiente}")
        os.mkdir(f"../modelagem/{ambiente}/rna")

    dados['time'] = [i for i in range(len(dados))]

    min_x = dados.x.min()
    max_x = dados.x.max()
    min_y = dados.y.min()
    max_y = dados.y.max()
    min_t = 0
    max_t = dados.time.max()

    if not use_gpu:
        os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    if tf.test.gpu_device_name():
        print('GPU found')
    else:
        print("No GPU found")

    percentage_train = 0.8
    percentage_test = 0.2
    epochs=500
    
    callbacks = [tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=10, verbose=1, min_delta=1e-4, mode='min')]
    callbacks.append(tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=15, verbose=0, restore_best_weights=True))

    dados_norm = dados.apply(lambda row: normalize(row), axis=1)
    dados_norm = pd.DataFrame(dados_norm.tolist())

    print("Separando o dado...")
    df_feat_train_full, df_target_train_full, df_feat_val, df_target_val = utils.splitData(dados_norm, percentage_train, window_size=w) #DEFINE HOW TO GET W

    size_test = int(len(df_feat_train_full) * percentage_test)
    df_feat_test = df_feat_train_full.iloc[-size_test:]
    df_target_test = df_target_train_full.iloc[-size_test:]

    df_feat_train = df_feat_train_full.iloc[:-size_test]
    df_target_train = df_target_train_full.iloc[:-size_test]

    print("modelando...")
    model = create_model()
    history = model.fit(df_feat_train, df_target_train, validation_data=(df_feat_val, df_target_val), epochs=epochs, callbacks=callbacks)

    model.save(f'{path}/rna/model_d{w-2}')

    if store_metrics:
        store(model, history, df_feat_test, df_target_test)


def create_model():
    model = models.Sequential()
    model.add(layers.Input(shape=(6,)))
    model.add(layers.Dense(2000, activation='relu'))
    model.add(layers.Dense(500, activation='relu'))
    model.add(layers.Dense(20, activation='relu'))
    model.add(layers.Dense(2, activation='tanh'))
    
    optimizer = optimizers.Adam(learning_rate=0.0001)
    
    model.summary()
    model.compile(loss="mse", optimizer=optimizer)
    return model


def normalize(row):
    if row['x'] >= 0:
        norm_x = row['x'] / max_x
    else:
        norm_x = row['x'] / -min_x

    if row['y'] >= 0:
        norm_y = row['y'] / max_y
    else:
        norm_y = row['y'] / -min_y

    return {'x': norm_x, 'y': norm_y}


def desnormalize(row):
    
    if row['x'] >= 0:
        desnorm_x = row['x'] * max_x
    else:
        desnorm_x = row['x'] * -min_x

    if row['y'] >= 0:
        desnorm_y = row['y'] * max_y
    else:
        desnorm_y = row['y'] * -min_y

    return {'x': desnorm_x, 'y': desnorm_y}


def store(model, history, df_feat_test: pd.DataFrame, df_target_test: pd.DataFrame):
    df_target_test.columns = ['x', 'y']
    df_target_test = df_target_test.apply(lambda row: desnormalize(row), axis=1)
    df_target_test = pd.DataFrame(df_target_test.tolist())
    df_target_test.columns = ['x2', 'y2']

    predicted_points = model.predict(df_feat_test)
        
    df_predito = pd.DataFrame(predicted_points, columns = ['x','y'])
    
    df_predito = df_predito.apply(lambda row: desnormalize(row), axis=1)
    df_predito = pd.DataFrame(df_predito.tolist())
    df_predito.columns = ['x2', 'y2']

    model_indicators = utils.validation(df_target_test, df_predito)
    
    (r2_x, r2_y), (rmse_x, rmse_y), (mae_x, mae_y), (mse_x, mse_y) = model_indicators
    print(f"R2: x={r2_x}, y={r2_y}")
    print(f"RMSE: x={rmse_x}, y={rmse_y}")
    print(f"MAE: x={mae_x}, y={mae_y}")
    print(f"MSE: x={mse_x}, y={mse_y}")
    
    r2_exec = [{'x': r2_x, 'y': r2_y}]    
    mse_exec = [{'x': mse_x, 'y': mse_y}]
    rmse_exec = [{'x': rmse_x, 'y': rmse_y}]
    mae_exec = [{'x': mae_x, 'y': mae_y}]
    
    pd.DataFrame(history.history).plot(figsize=(12, 8))
    plt.grid(True)
    plt.savefig(f"{path}/learning_curve.png")
    plt.close()
    
    pd.DataFrame(r2_exec).to_csv(f"{path}/r2.csv")
    pd.DataFrame(mse_exec).to_csv(f"{path}/mse.csv")
    pd.DataFrame(rmse_exec).to_csv(f"{path}/rmse.csv")
    pd.DataFrame(mae_exec).to_csv(f"{path}/mae.csv")




