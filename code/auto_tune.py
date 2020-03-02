import pandas as pd

import sys

import sklearn.model_selection
import sklearn.datasets
import sklearn.metrics

import autosklearn.classification


def auto_tune(file="anon_data/ring_mondrian/k2_minmaxed.csv", y_name="class"):
    data = pd.read_csv(file)
    y = data[y_name]
    print(data)
    X = data.drop(columns=[y_name, "Unnamed: 0"], axis=1)

    print(X)
    print(y)
    #feature_types = ['Categorical']*len(X.columns)

    X_train, X_test, y_train, y_test = \
        sklearn.model_selection.train_test_split(X, y, random_state=1)
    print(X_test.shape, X_train.shape)
    automl = autosklearn.classification.AutoSklearnClassifier(
        time_left_for_this_task=2*60*60,
        per_run_time_limit=60*60,
        tmp_folder=None,
        output_folder=None,
        disable_evaluator_output=False,
        n_jobs=4,
        seed=1,
        delete_output_folder_after_terminate=True,
        delete_tmp_folder_after_terminate=True,
    )
    automl.fit(X_train, y_train, dataset_name=f"adult")
    print("\n\n\n\n\n######################################")
    # Print the final ensemble constructed by auto-sklearn.
    print(automl.show_models())
    predictions = automl.predict(X_test)

    print("\n\n\n\n\n######################################")
    # Print the final ensemble constructed by auto-sklearn.
    # Print statistics about the auto-sklearn run such as number of
    # iterations, number of models failed with a time out.
    print(automl.sprint_statistics())
    print("Accuracy score", sklearn.metrics.accuracy_score(y_test, predictions))


    print("\n\n\n\n\n######################################")
    print(automl.get_params())

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print(f"Tuning {sys.argv[1]}")
        auto_tune(sys.argv[1], sys.argv[2])
    else:
        auto_tune()
