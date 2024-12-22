# Organizador de Comprovantes de Bancos

O `receipt-sweeper` é um script criado para organizar automaticamente aquels comprovantes de bancos gerados ao fazer uma
transferência Pix, TED ou pagar uma fatura de cartão de crédito.

Ele identifica o banco ao qual o comprovante pertence, lê as principais informações, renomeia o arquivo para facilitar 
a busca e os move para pastas organizadas.

Atualmente, o `receipt-sweeper` é capaz de lidar com as seguintes instituições:
1. Nubank
2. Mercado Pago
3. C6 Bank
4. Banco Inter
5. Claro Pay (apenas comprovantes de recarga)
6. Genial Investimentos

No entanto, por se tratar de um software em desenvolvimento, as funcionalidades podem variar de banco para banco.

Além disso, o `receipt-sweeper` possui as seguintes funcionalidades:
* Otimizar o tamanho das imagens JPG e PNG usando o `oxipng` e `jpegoptim`.
* Remover a senha de faturas de cartões de crédito automaticamente (desde que a senha seja numérica).

O `receipt-sweeper` foi testado apenas no Linux e, por enquanto, não existem planos de oferecer suporte para execução no
Windows.

### Dependências
* Módulos:
  * Estes módulos devem ser instalados pelo `pip`: 
    * [Pillow](https://pypi.org/project/pillow/)
    * [pdf2image](https://pypi.org/project/pdf2image/)
    * [pypdf](https://pypi.org/project/pypdf/)
    * [pytesseract](https://pypi.org/project/pytesseract/)
* Software:
  * Estes softwares devem ser instalados na máquina que executará o script:
    * [tesseract-ocr](https://tesseract-ocr.github.io/tessdoc/Installation.html)
      * O `tesseract-ocr` é obrigatório, pois é usado na extração do texto das imagens e dos PDFs que não possuem camada de texto.
    * [oxipng](https://github.com/shssoichiro/oxipng)
      * O `oxipng` é opcional e seu uso pode ser desativado no arquivo `config.py`.
    * [jpgoptim](https://github.com/tjko/jpegoptim)
      * O `jpgoptim` é opcional e seu uso pode ser desativado no arquivo `config.py`.

### Utilização

Altere as opções de uso no arquivo `config.py`, informando a pasta de origem dos dados, ou seja, onde o script procurará
por novos comprovantes, e a pasta de saída, para onde o script copiará os arquivos finais renomeados.