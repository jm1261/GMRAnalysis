import os
import matplotlib.pyplot as plt
import GMR.InputOutput as io
import GMR.DataPreparation as dp
import GMR.DataAnalysis.RIndex as ri

root = io.config_dir_path()

process_dict = {
    'Default' : 0,
    'Normalise' : 1,
    'Data Cube' : 2,
    'Free Spectral Range' : 3,
}
process_choice = io.user_in(choiceDict=process_dict)
normalise, datacube, fsr = io.process_choice(choice=process_choice)

norm_save_dict = {
    'Default settings' : 0,
    'All raw/normalised image save' : 1,
    'Save only result' : 2,
}
norm_choice = io.user_in(choiceDict=norm_save_dict)
raw_save, norm_save, pwr_save = io.norm_choice(choice=norm_choice)

exp_settings = io.exp_in(root)
print(f'Experiment Settings:\n{exp_settings}\n')

dp.processing_parameters(main_dir=root,
                         exp_settings=exp_settings,
                         image_save=norm_save)

for hs_img in exp_settings['hs_imgs']:
    img_dir = os.path.join(root, hs_img)
    corrected_img_dir = os.path.join(img_dir, 'corrected_imgs')
    if not os.path.isdir(img_dir):
        continue

    step, wl, f, power, norm_power = io.get_pwr_spectrum(dir_name=img_dir,
                                                         plot_show=False,
                                                         plot_save=pwr_save)

    io.create_all_dirs(dir_name=img_dir)

    if normalise:
        data_files = io.extract_files(dir_name=img_dir,
                                      file_string='img_')

        print('\nNormalising csvs...')
        for index, file in enumerate(data_files):
            file_path = os.path.join(img_dir, file)
            img, file_name = io.csv_in(file_path=file_path)

            _, img_no = file_name.split('_')
            if raw_save:
                io.png_out(image_data=img,
                           file_name=file_name,
                           dir_name=img_dir,
                           image_title=f'Image: {img_no}',
                           out_name=f'{file_name}.png',
                           plot_show=False)

            norm_img = dp.pwr_norm(image_data=img,
                                   file_name=file_name,
                                   norm_power=norm_power,
                                   dir_name=img_dir)

            if norm_save:
                io.png_out(image_data=norm_img,
                           file_name=file_name,
                           dir_name=img_dir,
                           image_title=f'Normalised image: {img_no}',
                           out_name=f'corrected_{file_name}.png',
                           plot_show=False)

            io.array_out(array_name=norm_img,
                         file_name=f'corrected_{file_name}',
                         dir_name=os.path.join(img_dir, 'corrected_imgs'))

            io.update_progress(index / len(data_files))

    if datacube:
        data_files = io.extract_files(dir_name=corrected_img_dir,
                                      file_string='corrected_img_')

        data_cube = []
        print(f'\nBuilding data cube for {hs_img}...')
        for index, file in enumerate(data_files):
            file_path = os.path.join(corrected_img_dir, file)

            corrected_img, file_name = io.array_in(file_path, mode='r')
            data_cube.append(corrected_img)

            io.update_progress(index / len(data_files))

        print('\nSaving data cube...approximately 1min per 100 images')
        io.array_out(array_name=data_cube,
                     file_name=f'{hs_img}_datacube',
                     dir_name=root)

    if fsr:
        rows, cols = dp.find_img_size(dir_name=corrected_img_dir,
                                      file_string='corrected_img_')

        data_cube = os.path.join(root, f'{hs_img}_datacube.npy')
        data_cube, file_name = io.array_in(file_path=data_cube,
                                           mode='r')

        spectra = dp.reshape_to_spec_lists(hs_data_cube=data_cube,
                                           img_width=rows,
                                           img_height=cols)
        for index, spectrum in enumerate(spectra):
            wavs = dp.wav_space(exp_settings=exp_settings)
            freqs, freq_intensity = ri.interp_spectrum(wavelength=wavs,
                                                       intensity=spectrum)


            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=[10,7])
            ax1.plot(wavs, spectrum, 'r', lw=2)
            ax2.plot(freqs, freq_intensity, 'b', lw=2)
            ax1.grid(True)
            ax2.grid(True)
            plt.show()
            fig.clf()
            plt.close(fig)
