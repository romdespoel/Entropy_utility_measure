import pandas as pd

import sys
from random import randrange
import sklearn.model_selection
import sklearn.datasets
import sklearn.metrics

import autosklearn.classification


def auto_tune(file="anon_data/ring_mondrian/k2_minmaxed.csv", y_name="class"):
    print("Loading anonymized training data...")
    data = pd.read_csv(file)

    print("Loading testing data...")
    orig_data = pd.read_csv("anon_data/ring_mondrian/k1_minmaxed.csv")

    print("Preparing train and test split...")
    train_set = data.sample(frac=0.8, random_state=1)
    test_set = orig_data.drop(train_set.index)

    y_train = y = train_set[y_name]
    X_train = train_set.drop(columns=[y_name, "Unnamed: 0"], axis=1)

    y_test = y = test_set[y_name]
    X_test = test_set.drop(columns=[y_name, "Unnamed: 0"], axis=1)

    print(f"X shapes: {X_test.shape, X_train.shape}")
    print(f"y shapes: {y_test.shape, y_train.shape}")
    print(f"Starting training on {file}...\n")
    automl = autosklearn.classification.AutoSklearnClassifier(
        time_left_for_this_task=12*60*60,
        per_run_time_limit=60*60,
        tmp_folder=f"/vol/bitbucket/rd2016/autosklearn_tmp{randrange(100)}",
        output_folder=f"/vol/bitbucket/rd2016/autosklearn_out{randrange(100)}",
        disable_evaluator_output=False,
        n_jobs=4,
        ensemble_memory_limit=2048,
        delete_output_folder_after_terminate=True,
        delete_tmp_folder_after_terminate=True,
    )
    automl.fit(X_train, y_train, dataset_name=f"ringnorm")

    print("############ Done ! ################\n")
    predictions = automl.predict(X_test)
    print("Accuracy score", sklearn.metrics.accuracy_score(y_test, predictions))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print(f"Tuning {sys.argv[1]}")
        auto_tune(sys.argv[1], sys.argv[2])
    else:
        auto_tune()
