import os
from glob import glob
from PIL import Image

INPUT_PATH = 'GRBs'

def combine_pngs_to_pdf(png_files, output_path):
    pages = [Image.open(png_path) for png_path in png_files]
    pages[0].save(output_path, "PDF", optimize=False, 
                  save_all=True, append_images=pages[1:], 
                  dpi=(300, 300), compression=None, quality=100)

if __name__ == '__main__':
    for grb in os.listdir(INPUT_PATH):
        if os.path.isdir(os.path.join(INPUT_PATH, grb)):
            if grb == 'reports':
                continue

            output_path = f'{INPUT_PATH}/reports/{grb}.pdf'
            print(output_path)
            png_files = glob(os.path.join(INPUT_PATH, grb,'*.png'))
            print(png_files)
            combine_pngs_to_pdf(png_files, output_path)
