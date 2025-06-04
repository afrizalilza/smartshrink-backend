import pikepdf
import sys
import os
import shutil
import subprocess
import tempfile

def compress_pdf(input_path, output_path):
    import shutil
    import subprocess
    import tempfile
    import os
    gs_path = shutil.which('gswin64c') or shutil.which('gswin32c') or shutil.which('gs')
    if not gs_path:
        raise RuntimeError('Ghostscript (gs) not found in PATH')
    tmp_fd, tmp_path = tempfile.mkstemp(suffix='.pdf')
    os.close(tmp_fd)
    cmd = [
        gs_path,
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.4',
        '-dPDFSETTINGS=/ebook',
        '-dNOPAUSE',
        '-dQUIET',
        '-dBATCH',
        f'-sOutputFile={tmp_path}',
        input_path
    ]
    try:
        subprocess.run(cmd, check=True)
        if os.path.exists(tmp_path):
            shutil.move(tmp_path, output_path)
            return "gs"
        else:
            raise RuntimeError('Ghostscript did not produce output')
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise RuntimeError(f'Ghostscript PDF compression failed: {e}')


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python pdf_optimize.py input.pdf output.pdf")
        sys.exit(1)
    compress_pdf(sys.argv[1], sys.argv[2])
