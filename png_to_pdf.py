import os
from glob import glob
from PIL import Image

INPUT_PATH = 'GRBs'

def combine_pngs_to_pdf(png_files, output_path):
    pages = [Image.open(png_path) for png_path in png_files]
    for i in range(len(pages)):
        pages[i].resize((1600, int(1600/pages[i].width * pages[i].height)))
    pages[0].save(output_path, "PDF", optimize=False, 
                  save_all=True, append_images=pages[1:], 
                  dpi=(300, 300), compression=None, quality=100)

def make_pdf_files():
    for grb in os.listdir(INPUT_PATH):
        if os.path.isdir(os.path.join(INPUT_PATH, grb)):
            if grb == 'reports':
                continue

            output_path = f'{INPUT_PATH}/reports/{grb}.pdf'
            png_files = glob(os.path.join(INPUT_PATH, grb,'*.png'))
            combine_pngs_to_pdf(png_files, output_path)

if __name__ == '__main__':
    make_pdf_files()