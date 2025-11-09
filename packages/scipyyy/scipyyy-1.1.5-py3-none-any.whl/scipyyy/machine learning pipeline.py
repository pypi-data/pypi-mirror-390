#Implementing a machine learning pipeline for automated feature engineering and model 
selection. 
from pycaret.utils import version 
from pycaret.datasets import get_data 
from pycaret.classification import setup, compare_models, finalize_model, predict_model 
from pycaret.regression import * 
from pycaret.utils.generic import check_metric 
 
data = get_data('diamond') 
data.shape 
data.info() 
 
dataset = data.sample(frac=0.95, random_state=786) 
data_unseen = data.drop(dataset.index) 
dataset.reset_index(drop=True, inplace=True) 
data_unseen.reset_index(drop=True, inplace=True) 
 
s = setup(data=dataset, target='Price', session_id=120) 
best = compare_models() 
final_model = create_model('xgboost') 
print(final_model) 
 
plot_model(final_model, plot='error') 
predict_model(final_model, data=data_unseen) 
 
production_model = finalize_model(final_model) 
unseen_preds = predict_model(production_model, data=data_unseen) 
unseen_preds 
 
check_metric(unseen_preds.Price, unseen_preds.prediction_label, metric='R2') 
save_model('production_model', 'Production_model_complete_version') 
saved_model_retrieve = load_model('/content/Production_model_complete_version')
