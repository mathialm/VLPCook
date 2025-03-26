#/etc/bin/bash
CUDA_VISIBLE_DEVICES=0 python -m bootstrap.run -o bootstrap/options/vlpcook_clip_finetune.yaml \
--dataset.batch_size 100 \
--model.network.path_vocab data_dir/recipe1m/text/vocab_all.txt \
--model.network.path_ingrs data_dir/recipe1m/text/vocab.pkl \
--dataset.aux_kw_path.train data_dir/recipe1m/context_annotation/layer1_train_titles_kw.json \
--dataset.aux_kw_path.test data_dir/recipe1m/context_annotation/layer1_test_titles_kw.json \
--dataset.aux_kw_path.val data_dir/recipe1m/context_annotation/layer1_val_titles_kw.json \
--model.network.bert_config ~/vlpcook/recipe1m/models/networks/recipe_networks/config_bert_albef.json \
--dataset.randkw_p 0.3 \
--dataset.kw_path.train data_dir/recipe1m/context_annotation/layer1_train_ingr_kw.json \
--dataset.kw_path.test data_dir/recipe1m/context_annotation/layer1_test_ingr_kw.json \
--dataset.kw_path.val data_dir/recipe1m/context_annotation/layer1_val_ingr_kw.json \
--dataset.randkw_p_aux 0.5 \
--dataset.eval_split test \
--dataset.train_split \
--exp.resume best_eval_epoch.metric.recall_at_1_im2recipe_mean \
--model.metric.nb_bags 10 \
--model.metric.nb_matchs_per_bag 1000 \
--model.metric.trijoint true
