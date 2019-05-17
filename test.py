import os
import GMR.InputOutput as io
import GMR.DataPreparation as dp

main_dir = io.config_dir_path()

exp_settings = io.exp_in(main_dir)
print('Experiment Settings:\n' + f'{exp_settings}' + '\n')

system_settings = io.system_settings()

#analysis_file = io.analysis_in_json(main_dir)

#dp.processing_parameters(main_dir=main_dir,
#                         exp_settings=exp_settings,
#                         image_save=False)
