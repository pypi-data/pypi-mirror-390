# Configuração instalação:
pip3 install -r requirements.txt


# Uso dividir páginas de um arquivo PDF:
    >>> from soup_files import File, Directory
    >>> from pdflib import PdfStream

    # instâncie o caminho do arquivo PDF e o diretório para exportar os dados.
    file_pdf = File('path/to/file.pdf')
    output_dir = Directory('path/to/save')

    pdf_stream = PdfStream()
    pdf_stream.add_file_pdf(file_pdf)
    pdf_stream.to_files_pdf(output_dir) # isso irá converter cada página em um arquivo PDF

# Uso para unir vários arquivos PDF.
    >>> from soup_files import File, Directory
    >>> from pdflib import PdfStream

    # instâncie o caminho dos arquivos PDF que deseja unir.
    f = File('path/to/file.pdf')
    f2 = File('path/to/file2.pdf)
    ...
    ... # Adicione quantos arquivos desejar.
    
    pdf_stream = PdfStream()
    pdf_stream.add_file_pdf(f)
    pdf_stream.add_file_pdf(f2)
    pdf_stream.to_file_pdf(File('path/to/new_file.pdf'))
