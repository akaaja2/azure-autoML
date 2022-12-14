# This file has been autogenerated by version 1.44.0 of the Azure Automated Machine Learning SDK.


import numpy
import numpy as np
import pandas as pd
import pickle
import argparse


def setup_instrumentation():
    import logging
    import sys

    from azureml.core import Run
    from azureml.telemetry import INSTRUMENTATION_KEY, get_telemetry_log_handler
    from azureml.telemetry._telemetry_formatter import ExceptionFormatter

    logger = logging.getLogger("azureml.training.tabular")

    try:
        logger.setLevel(logging.INFO)

        # Add logging to STDOUT
        stdout_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(stdout_handler)

        # Add telemetry logging with formatter to strip identifying info
        telemetry_handler = get_telemetry_log_handler(
            instrumentation_key=INSTRUMENTATION_KEY, component_name="azureml.training.tabular"
        )
        telemetry_handler.setFormatter(ExceptionFormatter())
        logger.addHandler(telemetry_handler)

        # Attach run IDs to logging info for correlation if running inside AzureML
        try:
            run = Run.get_context()
            parent_run = run.parent
            return logging.LoggerAdapter(logger, extra={
                "properties": {
                    "codegen_run_id": run.id,
                    "parent_run_id": parent_run.id
                }
            })
        except Exception:
            pass
    except Exception:
        pass

    return logger


logger = setup_instrumentation()


def split_dataset(X, y, weights, split_ratio, should_stratify):
    from sklearn.model_selection import train_test_split

    random_state = 42
    if should_stratify:
        stratify = y
    else:
        stratify = None

    if weights is not None:
        X_train, X_test, y_train, y_test, weights_train, weights_test = train_test_split(
            X, y, weights, stratify=stratify, test_size=split_ratio, random_state=random_state
        )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, stratify=stratify, test_size=split_ratio, random_state=random_state
        )
        weights_train, weights_test = None, None

    return (X_train, y_train, weights_train), (X_test, y_test, weights_test)


def get_training_dataset(dataset_id):
    from azureml.core.dataset import Dataset
    from azureml.core.run import Run
    
    logger.info("Running get_training_dataset")
    ws = Run.get_context().experiment.workspace
    dataset = Dataset.get_by_id(workspace=ws, id=dataset_id)
    return dataset.to_pandas_dataframe()


def prepare_data(dataframe):
    from azureml.training.tabular.preprocessing import data_cleaning
    
    logger.info("Running prepare_data")
    label_column_name = 'rentals'
    
    # extract the features, target and sample weight arrays
    y = dataframe[label_column_name].values
    X = dataframe.drop([label_column_name], axis=1)
    sample_weights = None
    X, y, sample_weights = data_cleaning._remove_nan_rows_in_X_y(X, y, sample_weights,
     is_timeseries=False, target_column=label_column_name)
    
    return X, y, sample_weights


def get_mapper_49c852(column_names):
    from azureml.training.tabular.featurization.text.stringcast_transformer import StringCastTransformer
    from azureml.training.tabular.featurization.utilities import wrap_in_list
    from numpy import uint8
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn_pandas.dataframe_mapper import DataFrameMapper
    from sklearn_pandas.features_generator import gen_features
    
    definition = gen_features(
        columns=column_names,
        classes=[
            {
                'class': StringCastTransformer,
            },
            {
                'class': CountVectorizer,
                'analyzer': 'word',
                'binary': True,
                'decode_error': 'strict',
                'dtype': numpy.uint8,
                'encoding': 'utf-8',
                'input': 'content',
                'lowercase': True,
                'max_df': 1.0,
                'max_features': None,
                'min_df': 1,
                'ngram_range': (1, 1),
                'preprocessor': None,
                'stop_words': None,
                'strip_accents': None,
                'token_pattern': '(?u)\\b\\w\\w+\\b',
                'tokenizer': wrap_in_list,
                'vocabulary': None,
            },
        ]
    )
    mapper = DataFrameMapper(features=definition, input_df=True, sparse=True)
    
    return mapper
    
    
def get_mapper_9133f9(column_names):
    from azureml.training.tabular.featurization.categorical.cat_imputer import CatImputer
    from azureml.training.tabular.featurization.categorical.labelencoder_transformer import LabelEncoderTransformer
    from azureml.training.tabular.featurization.text.stringcast_transformer import StringCastTransformer
    from sklearn_pandas.dataframe_mapper import DataFrameMapper
    from sklearn_pandas.features_generator import gen_features
    
    definition = gen_features(
        columns=column_names,
        classes=[
            {
                'class': CatImputer,
                'copy': True,
            },
            {
                'class': StringCastTransformer,
            },
            {
                'class': LabelEncoderTransformer,
                'hashing_seed_val': 314489979,
            },
        ]
    )
    mapper = DataFrameMapper(features=definition, input_df=True, sparse=True)
    
    return mapper
    
    
def get_mapper_ab1045(column_names):
    from sklearn.impute import SimpleImputer
    from sklearn_pandas.dataframe_mapper import DataFrameMapper
    from sklearn_pandas.features_generator import gen_features
    
    definition = gen_features(
        columns=column_names,
        classes=[
            {
                'class': SimpleImputer,
                'add_indicator': False,
                'copy': True,
                'fill_value': None,
                'missing_values': numpy.nan,
                'strategy': 'mean',
                'verbose': 0,
            },
        ]
    )
    mapper = DataFrameMapper(features=definition, input_df=True, sparse=True)
    
    return mapper
    
    
def generate_data_transformation_config():
    from sklearn.pipeline import FeatureUnion
    
    column_group_1 = [['temp'], ['atemp'], ['hum'], ['windspeed']]
    
    column_group_2 = ['year', 'holiday', 'workingday']
    
    column_group_3 = ['day', 'mnth', 'season', 'weekday', 'weathersit']
    
    feature_union = FeatureUnion([
        ('mapper_49c852', get_mapper_49c852(column_group_3)),
        ('mapper_9133f9', get_mapper_9133f9(column_group_2)),
        ('mapper_ab1045', get_mapper_ab1045(column_group_1)),
    ])
    return feature_union
    
    
def generate_preprocessor_config_0():
    from sklearn.preprocessing import MaxAbsScaler
    
    preproc = MaxAbsScaler(
        copy=True
    )
    
    return preproc
    
    
def generate_algorithm_config_0():
    from xgboost.sklearn import XGBRegressor
    
    algorithm = XGBRegressor(
        base_score=0.5,
        booster='gbtree',
        colsample_bylevel=1,
        colsample_bynode=1,
        colsample_bytree=1,
        gamma=0,
        gpu_id=-1,
        importance_type='gain',
        interaction_constraints='',
        learning_rate=0.300000012,
        max_delta_step=0,
        max_depth=6,
        min_child_weight=1,
        missing=numpy.nan,
        monotone_constraints='()',
        n_estimators=100,
        n_jobs=0,
        num_parallel_tree=1,
        objective='reg:squarederror',
        random_state=0,
        reg_alpha=0,
        reg_lambda=1,
        scale_pos_weight=1,
        subsample=1,
        tree_method='auto',
        validate_parameters=1,
        verbose=-10,
        verbosity=0
    )
    
    return algorithm
    
    
def generate_preprocessor_config_1():
    from sklearn.preprocessing import MaxAbsScaler
    
    preproc = MaxAbsScaler(
        copy=True
    )
    
    return preproc
    
    
def generate_algorithm_config_1():
    from lightgbm.sklearn import LGBMRegressor
    
    algorithm = LGBMRegressor(
        boosting_type='gbdt',
        class_weight=None,
        colsample_bytree=1.0,
        importance_type='split',
        learning_rate=0.1,
        max_depth=-1,
        min_child_samples=20,
        min_child_weight=0.001,
        min_split_gain=0.0,
        n_estimators=100,
        n_jobs=-1,
        num_leaves=31,
        objective=None,
        random_state=None,
        reg_alpha=0.0,
        reg_lambda=0.0,
        silent=True,
        subsample=1.0,
        subsample_for_bin=200000,
        subsample_freq=0,
        verbose=-1
    )
    
    return algorithm
    
    
def generate_preprocessor_config_2():
    from sklearn.preprocessing import MaxAbsScaler
    
    preproc = MaxAbsScaler(
        copy=True
    )
    
    return preproc
    
    
def generate_algorithm_config_2():
    from sklearn.ensemble import RandomForestRegressor
    
    algorithm = RandomForestRegressor(
        bootstrap=False,
        ccp_alpha=0.0,
        criterion='mse',
        max_depth=None,
        max_features=0.4,
        max_leaf_nodes=None,
        max_samples=None,
        min_impurity_decrease=0.0,
        min_impurity_split=None,
        min_samples_leaf=0.006151578686713196,
        min_samples_split=0.012814223889440833,
        min_weight_fraction_leaf=0.0,
        n_estimators=200,
        n_jobs=-1,
        oob_score=False,
        random_state=None,
        verbose=0,
        warm_start=False
    )
    
    return algorithm
    
    
def generate_preprocessor_config_3():
    from sklearn.preprocessing import StandardScaler
    
    preproc = StandardScaler(
        copy=True,
        with_mean=False,
        with_std=True
    )
    
    return preproc
    
    
def generate_algorithm_config_3():
    from lightgbm.sklearn import LGBMRegressor
    
    algorithm = LGBMRegressor(
        boosting_type='gbdt',
        class_weight=None,
        colsample_bytree=0.6,
        importance_type='split',
        learning_rate=0.16842263157894738,
        max_bin=1023,
        max_depth=9,
        min_child_samples=3,
        min_child_weight=0.001,
        min_split_gain=0.7368421052631579,
        n_estimators=100,
        n_jobs=-1,
        num_leaves=255,
        objective=None,
        random_state=None,
        reg_alpha=0,
        reg_lambda=0.75,
        silent=True,
        subsample=0.9,
        subsample_for_bin=200000,
        subsample_freq=6,
        verbose=-1
    )
    
    return algorithm
    
    
def generate_preprocessor_config_4():
    from sklearn.preprocessing import StandardScaler
    
    preproc = StandardScaler(
        copy=True,
        with_mean=False,
        with_std=False
    )
    
    return preproc
    
    
def generate_algorithm_config_4():
    from xgboost.sklearn import XGBRegressor
    
    algorithm = XGBRegressor(
        base_score=0.5,
        booster='gbtree',
        colsample_bylevel=1,
        colsample_bynode=1,
        colsample_bytree=0.9,
        eta=0.5,
        gamma=0.01,
        gpu_id=-1,
        importance_type='gain',
        interaction_constraints='',
        learning_rate=0.5,
        max_delta_step=0,
        max_depth=8,
        max_leaves=0,
        min_child_weight=1,
        missing=numpy.nan,
        monotone_constraints='()',
        n_estimators=50,
        n_jobs=0,
        num_parallel_tree=1,
        objective='reg:squarederror',
        random_state=0,
        reg_alpha=1.3541666666666667,
        reg_lambda=1.6666666666666667,
        scale_pos_weight=1,
        subsample=1,
        tree_method='auto',
        validate_parameters=1,
        verbose=-10,
        verbosity=0
    )
    
    return algorithm
    
    
def generate_preprocessor_config_5():
    from sklearn.preprocessing import MaxAbsScaler
    
    preproc = MaxAbsScaler(
        copy=True
    )
    
    return preproc
    
    
def generate_algorithm_config_5():
    from sklearn.ensemble import ExtraTreesRegressor
    
    algorithm = ExtraTreesRegressor(
        bootstrap=False,
        ccp_alpha=0.0,
        criterion='mse',
        max_depth=None,
        max_features=0.8,
        max_leaf_nodes=None,
        max_samples=None,
        min_impurity_decrease=0.0,
        min_impurity_split=None,
        min_samples_leaf=0.0023646822772690063,
        min_samples_split=0.005285388593079247,
        min_weight_fraction_leaf=0.0,
        n_estimators=10,
        n_jobs=-1,
        oob_score=False,
        random_state=None,
        verbose=0,
        warm_start=False
    )
    
    return algorithm
    
    
def generate_preprocessor_config_6():
    from sklearn.preprocessing import Normalizer
    
    preproc = Normalizer(
        copy=True,
        norm='l2'
    )
    
    return preproc
    
    
def generate_algorithm_config_6():
    from xgboost.sklearn import XGBRegressor
    
    algorithm = XGBRegressor(
        base_score=0.5,
        booster='gbtree',
        colsample_bylevel=1,
        colsample_bynode=1,
        colsample_bytree=0.7,
        eta=0.5,
        gamma=0,
        gpu_id=-1,
        grow_policy='lossguide',
        importance_type='gain',
        interaction_constraints='',
        learning_rate=0.5,
        max_bin=255,
        max_delta_step=0,
        max_depth=2,
        max_leaves=3,
        min_child_weight=1,
        missing=numpy.nan,
        monotone_constraints='()',
        n_estimators=25,
        n_jobs=0,
        num_parallel_tree=1,
        objective='reg:squarederror',
        random_state=0,
        reg_alpha=2.1875,
        reg_lambda=0.8333333333333334,
        scale_pos_weight=1,
        subsample=0.8,
        tree_method='hist',
        validate_parameters=1,
        verbose=-10,
        verbosity=0
    )
    
    return algorithm
    
    
def generate_preprocessor_config_7():
    from sklearn.preprocessing import MaxAbsScaler
    
    preproc = MaxAbsScaler(
        copy=True
    )
    
    return preproc
    
    
def generate_algorithm_config_7():
    from sklearn.linear_model import ElasticNet
    
    algorithm = ElasticNet(
        alpha=0.001,
        copy_X=True,
        fit_intercept=True,
        l1_ratio=0.6873684210526316,
        max_iter=1000,
        normalize=False,
        positive=False,
        precompute=False,
        random_state=None,
        selection='cyclic',
        tol=0.0001,
        warm_start=False
    )
    
    return algorithm
    
    
def generate_algorithm_config():
    from azureml.training.tabular.models.forecasting_pipeline_wrapper import PreFittedSoftVotingRegressor
    from sklearn.pipeline import Pipeline
    
    pipeline_0 = Pipeline(steps=[('preproc', generate_preprocessor_config_0()), ('model', generate_algorithm_config_0())])
    pipeline_1 = Pipeline(steps=[('preproc', generate_preprocessor_config_1()), ('model', generate_algorithm_config_1())])
    pipeline_2 = Pipeline(steps=[('preproc', generate_preprocessor_config_2()), ('model', generate_algorithm_config_2())])
    pipeline_3 = Pipeline(steps=[('preproc', generate_preprocessor_config_3()), ('model', generate_algorithm_config_3())])
    pipeline_4 = Pipeline(steps=[('preproc', generate_preprocessor_config_4()), ('model', generate_algorithm_config_4())])
    pipeline_5 = Pipeline(steps=[('preproc', generate_preprocessor_config_5()), ('model', generate_algorithm_config_5())])
    pipeline_6 = Pipeline(steps=[('preproc', generate_preprocessor_config_6()), ('model', generate_algorithm_config_6())])
    pipeline_7 = Pipeline(steps=[('preproc', generate_preprocessor_config_7()), ('model', generate_algorithm_config_7())])
    algorithm = PreFittedSoftVotingRegressor(
        estimators=[
            ('model_0', pipeline_0),
            ('model_1', pipeline_1),
            ('model_2', pipeline_2),
            ('model_3', pipeline_3),
            ('model_4', pipeline_4),
            ('model_5', pipeline_5),
            ('model_6', pipeline_6),
            ('model_7', pipeline_7),
        ],
        weights=[0.3333333333333333, 0.2, 0.06666666666666667, 0.06666666666666667, 0.13333333333333333, 0.06666666666666667, 0.06666666666666667, 0.06666666666666667]
    )
    
    return algorithm
    
    
def build_model_pipeline():
    from sklearn.pipeline import Pipeline
    
    logger.info("Running build_model_pipeline")
    pipeline = Pipeline(
        steps=[
            ('featurization', generate_data_transformation_config()),
            ('ensemble', generate_algorithm_config()),
        ]
    )
    
    return pipeline


def train_model(X, y, sample_weights=None, transformer=None):
    logger.info("Running train_model")
    model_pipeline = build_model_pipeline()
    
    model = model_pipeline.fit(X, y)
    return model


def calculate_metrics(model, X, y, sample_weights, X_test, y_test, cv_splits=None):
    from azureml.training.tabular.preprocessing.binning import make_dataset_bins
    from azureml.training.tabular.score.scoring import score_regression
    
    y_pred = model.predict(X_test)
    y_min = np.min(y)
    y_max = np.max(y)
    y_std = np.std(y)
    
    bin_info = make_dataset_bins(X_test.shape[0], y_test)
    metrics = score_regression(
        y_test, y_pred, get_metrics_names(), y_max, y_min, y_std, sample_weights, bin_info)
    return metrics
def get_metrics_names():
    metrics_names = [
        'mean_absolute_percentage_error',
        'normalized_median_absolute_error',
        'normalized_root_mean_squared_error',
        'predicted_true',
        'r2_score',
        'spearman_correlation',
        'residuals',
        'root_mean_squared_log_error',
        'median_absolute_error',
        'normalized_mean_absolute_error',
        'explained_variance',
        'root_mean_squared_error',
        'normalized_root_mean_squared_log_error',
        'mean_absolute_error',
    ]
    return metrics_names


def main(training_dataset_id=None):
    from azureml.core.run import Run
    
    # The following code is for when running this code as part of an AzureML script run.
    run = Run.get_context()
    
    df = get_training_dataset(training_dataset_id)
    X, y, sample_weights = prepare_data(df)
    split_ratio = 0.25
    (X_train, y_train, sample_weights_train), (X_valid, y_valid, sample_weights_valid) = split_dataset(X, y, sample_weights, split_ratio, should_stratify=False)
    model = train_model(X_train, y_train, sample_weights_train)
    
    metrics = calculate_metrics(model, X, y, sample_weights, X_test=X_valid, y_test=y_valid)
    
    print(metrics)
    for metric in metrics:
        run.log(metric, metrics[metric])
    
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)
    run.upload_file('outputs/model.pkl', 'model.pkl')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--training_dataset_id', type=str, default='c40daae3-2c7d-4e22-a231-4c2706efe0df', help='Default training dataset id is populated from the parent run')
    args = parser.parse_args()
    
    main(args.training_dataset_id)