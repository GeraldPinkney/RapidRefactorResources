import datetime
import fnmatch
import shutil
import zipfile
import logging
import os
import pathlib
import re


def replace_text(filename, frm, to):
    logging.info('starting string replace')
    with open(filename, 'r') as in_file:
        filedata = in_file.read()

    # replace string in file
    newdata = filedata.replace(frm, to)

    # replace string in filename
    newname = filename.replace(frm, to)

    with open(newname, 'w') as out_file:
        out_file.write(newdata)
    #if filename contains the string you don't like you'll need to delete it
    #if fnmatch.fnmatch(filename, '*'+frm+'*'):
    #    logging.info(f'removing old file: {filename} as it contains {frm}')
    #    os.remove(filename)
    logging.info('string replace complete')


def is_unzippable(filename):
    if re.findall('\\.rpk$|\\.wwb$|\\.alt$', filename):
        return True
    else:
        return False


def process_directory(dirname, extension, frm, to):

    logging.info(f'started directory processor')
    from_text = frm
    to_text = to

    # create listing of stuff in directory
    working_dir = dirname
    file_list = []
    for thing in os.listdir(working_dir):
        if os.path.isfile(os.path.join(working_dir, thing)):
            file_list.append(thing)
    # for each file in DIR
    for file in file_list:
        full_name = working_dir + '\\' + file
        logging.info('full filename: ' + full_name)
        # if its an archive, and therefore needs recursive processing
        if zipfile.is_zipfile(full_name):

            extract_dir = re.split('\\.', full_name)[0]
            extract_dir = extract_dir.replace(frm, to)
            ext = '.' + re.split('\\.', full_name)[1]
            # print zip contents
            with zipfile.ZipFile(full_name, mode="r") as archive:
                for info in archive.infolist():
                    logging.info(f"Filename: {info.filename}")
                    logging.info(f"Modified: {datetime.datetime(*info.date_time)}")
                    logging.info(f"Normal size: {info.file_size} bytes")
                    logging.info(f"Compressed size: {info.compress_size} bytes")
                    logging.info("-" * 20)
            # unzip contents of file
            with zipfile.ZipFile(full_name, mode="r") as archive:

                archive.extractall(path=extract_dir+"\\")
            # call process dir on contents
            process_directory(extract_dir, ext, frm, to)
            # remove directory
            try:
                shutil.rmtree(extract_dir)
            except OSError as e:
                print(f'Error: {extract_dir} : {e.strerror}')
        else:
            replace_text(full_name, from_text, to_text)


    # zip up directory
    directory = pathlib.Path(working_dir)
    zip_name = working_dir + extension

    with zipfile.ZipFile(zip_name, 'w') as archive:
        for file_path in directory.iterdir():
            archive.write(file_path, arcname=file_path.name)



if __name__ == '__main__':
    logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    process_directory('C:\\Users\\gpinkney\\PycharmProjects\\RapidRefactorResources\\RapidRefactorResources\\data_dir', '.rpk',
                   '[EU]', '[MEA]')

