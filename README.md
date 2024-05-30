  <!-- /\* Font Definitions \*/ @font-face {font-family:"Cambria Math"; panose-1:2 4 5 3 5 4 6 3 2 4;} @font-face {font-family:Calibri; panose-1:2 15 5 2 2 2 4 3 2 4;} @font-face {font-family:"Segoe UI"; panose-1:2 11 5 2 4 2 4 2 2 3;} @font-face {font-family:Consolas; panose-1:2 11 6 9 2 2 4 3 2 4;} /\* Style Definitions \*/ p.MsoNormal, li.MsoNormal, div.MsoNormal {margin-top:0cm; margin-right:0cm; margin-bottom:8.0pt; margin-left:0cm; line-height:107%; font-size:11.0pt; font-family:"Calibri",sans-serif;} .MsoPapDefault {margin-bottom:8.0pt; line-height:107%;} @page WordSection1 {size:595.3pt 841.9pt; margin:70.85pt 70.85pt 70.85pt 70.85pt;} div.WordSection1 {page:WordSection1;} /\* List Definitions \*/ ol {margin-bottom:0cm;} ul {margin-bottom:0cm;} -->

Decapod was a project that had some genpdf that should be able to reconstruct a font into a PDF. I thought to bring it back alive once more to cherry-pick some code. I was able to.

Mind the pickyness on the slashes of this program. Every file or directory should be exhaustively surrounded by them, for example -p ./out.pdf and -d ./out/ for the output directory.

While google killed the open source repos it hosted some documentation is still available on https://fluidproject.atlassian.net/wiki/spaces/fluid/pages/11626669/Decapod+script+command+line+options

On git are some repo's that appeared to contain the old versions, so I forked them to keep track of the source. During the development of Decapod until the end of 2012 some project called ocropy was used and killed before the end of decapod. The source of ocropy that matches these commits that were used during the making of the unittests are also still available. The unittests weren't maintained until the end of decapod, but based on a version of decapod-genpdf that relied on ocropy, for example with the ocropus-binarize script, which is still available in the history of https://github.com/ocropus-archive/DUP-ocropy

```


Compiling:
On Ubuntu 20.04:
first compile iulib:
git clone https://github.com/rmast/iulib.git
cd iulib
sudo bash ubuntu-packages
scons
sudo scons install
sudo ldconfig

then compile ocropus 0.44+:
git clone https://github.com/rmast/ocropus-git.git
cd ocropus-git
sudo bash ubuntu-packages
scons
sudo scons install
sudo ldconfig

then compile this repo:
git clone https://github.com/rmast/genpdf.git
cd genpdf
scons
sudo scons install
conda env create -f decapod.yml
conda activate decapod
pip install requirements.txt
pip install -e .
```
Using decapod-gendpdf.py

\# with list of files

decapod-genpdf.py -t 1 \-d path/to/temp/dir -p path/to/pdf /path/to/image1.jpg /path/to/imageN.jpg

#with book

decapod-genpdf.py -t 1 \-d path/to/temp/dir -p path/to/pdf -b /path/to/multipage.tiff

Mandatory Arguments

**Flag**

**Description**

\-d, --dir

Ocropus Directory to be converted

\-p, --pdf

PDF File that will be generated

\-t, --type

type of the PDF to be generates:

1.  image only \[default\]
2.  recognized text overlaid with image
3.  tokenized
4.  reconstructed font

Optional Arguments

**Flag**

**Description**

\-h, --help

print this help

\-b --book

name of multipage tiff file

\-v, --verbose

verbose level \[0,1,2,3\]

\-W, --width

width of the PDF page \[in cm\] \[default = 21.0\]

\-H, --height

height of the PDF page \[in cm\] \[default = 29.7\]

\-r, --resolution

resolution of the images in the PDF \[default = 200dpi\]

\-R --remerge

remerge token clusters \[default = false\]

\-S, --seg2bbox

suppresses generating files necessary to generate PDF

\-C, --enforceCSEG

characters can only match if there CSEG labels are equal

\-e, --eps

matching threshold \[default=7\]

\-s, --reps

matching threshold \[default=.07\]

\-B, --bit

Bit depth of the output image (1, 8, 24))"

**Test 1: Display the help text**

*   Procedure

1.  From the command line run:

decapod-genpdf.py -h

*   Results

*   The help documentation should be displayed. It should contain a list of the command line arguments and a description for each

**Test 2: Generate a pdf from a single file**

*   Procedure

1.  From the command line run:

\# replace "typeNumber" with a number from \[1-4\]

\# replace "~/path/to/image/file" with the correct path

decapod-genpdf.py -t typeNumber -d ~/Desktop/bookDir -p ~/Desktop/test.pdf -l ~/path/to/image/file

*   Type 1 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a 200 DPI, 24-bit colour image of the image file passed in
*   The pdf should have a width of 21cm and a height of 29.7cm

*   Type 2 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a 200 DPI, 24-bit colour image of the image file passed in and have the ocr'd text underplayed
*   The pdf should have a width of 21cm and a height of 29.7cm

*   Type 3 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a computer traced representation of the image file passed in, all the text should be selectable
*   The pdf should have a width of 21cm and a height of 29.7cm

*   Type 4 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf files should be generated
*   test.pdf should contain selectable text in a matching font to the image file passed in
*   The pdf should have a width of 21cm and a height of 29.7cm

*   Stop Test

*   Delete the generated files and directories

**Test 3: Generate a pdf from multiple files**

*   Procedure

1.  From the command line run:

\# replace "typeNumber" with a number from \[1-4\]

\# replace "~/path/to/image/file" and etc. with the correct paths

decapod-genpdf.py -t typeNumber -d ~/Desktop/bookDir -p ~/Desktop/test.pdf -l ~/path/to/image/file ~/path/to/image/file2 ...

*   Type 1 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a 200 DPI, 24-bit colour images of the image files passed in
*   The pdf should have a width of 21cm and a height of 29.7cm

*   Type 2 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a 200 DPI, 24-bit colour image of the image files passed in and have the ocr'd text underplayed
*   The pdf should have a width of 21cm and a height of 29.7cm

*   Type 3 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a computer traced representation of the image files passed in, all the text should be selectable
*   The pdf should have a width of 21cm and a height of 29.7cm

*   Type 4 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf files should be generated
*   test.pdf should contain selectable text in a matching font to the image files passed in
*   The pdf should have a width of 21cm and a height of 29.7cm

*   Stop Test

*   Delete the generated files and directories

**Test 4: Generate a pdf with output width specified**

*   Procedure

1.  From the command line run:

\# replace "typeNumber" with a number from \[1-4\]

\# replace "width" with a size in centimetres

\# replace "~/path/to/image/file" with the correct path

decapod-genpdf.py -t typeNumber -d ~/Desktop/bookDir -p ~/Desktop/test.pdf -w width -l ~/path/to/image/file

*   Type 1 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a 200 DPI, 24-bit colour image of the image file passed in
*   The pdf should have a width equal to the value specified for the -w flag and a height of 29.7cm

*   Type 2 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a 200 DPI, 24-bit colour image of the image file passed in and have the ocr'd text underplayed
*   The pdf should have a width equal to the value specified for the -w flag and a height of 29.7cm

*   Type 3 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a computer traced representation of the image file passed in, all the text should be selectable
*   The pdf should have a width equal to the value specified for the -w flag and a height of 29.7cm

*   Type 4 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf files should be generated
*   test.pdf should contain selectable text in a matching font to the image file passed in
*   The pdf should have a width equal to the value specified for the -w flag and a height of 29.7cm

*   Stop Test

*   Delete the generated files and directories

**Test 5: Generate a pdf with output height specified**

*   Procedure

1.  From the command line run:

\# replace "typeNumber" with a number from \[1-4\]

\# replace "height" with a size in centimetres

\# replace "~/path/to/image/file" with the correct path

decapod-genpdf.py -t typeNumber -d ~/Desktop/bookDir -p ~/Desktop/test.pdf -h height -l ~/path/to/image/file

*   Type 1 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a 200 DPI, 24-bit colour image of the image file passed in
*   The pdf should have a width of 21cm and a height equal to the value specified for the -h flag

*   Type 2 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a 200 DPI, 24-bit colour image of the image file passed in and have the ocr'd text underplayed
*   The pdf should have a width of 21cm and a height equal to the value specified for the -h flag

*   Type 3 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a computer traced representation of the image file passed in, all the text should be selectable
*   The pdf should have a width of 21cm and a height equal to the value specified for the -h flag

*   Type 4 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf files should be generated
*   test.pdf should contain selectable text in a matching font to the image file passed in
*   The pdf should have a width of 21cm and a height equal to the value specified for the -h flag

*   Stop Test

*   Delete the generated files and directories

**Test 6: Generate a pdf with output width and height specified**

*   Procedure

1.  From the command line run:

\# replace "typeNumber" with a number from \[1-4\]

\# replace "width" with a size in centimetres

\# replace "height" with a size in centimetres

\# replace "~/path/to/image/file" with the correct path

decapod-genpdf.py -t typeNumber -d ~/Desktop/bookDir -p ~/Desktop/test.pdf -w width -h height -l ~/path/to/image/file

*   Type 1 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a 200 DPI, 24-bit colour image of the image file passed in
*   The pdf should have a width and height equal to the values specified for the -w and -h flags respectively

*   Type 2 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a 200 DPI, 24-bit colour image of the image file passed in and have the ocr'd text underplayed
*   The pdf should have a width and height equal to the values specified for the -w and -h flags respectively

*   Type 3 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a computer traced representation of the image file passed in, all the text should be selectable
*   The pdf should have a width and height equal to the values specified for the -w and -h flags respectively

*   Type 4 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf files should be generated
*   test.pdf should contain selectable text in a matching font to the image file passed in
*   The pdf should have a width and height equal to the values specified for the -w and -h flags respectively

*   Stop Test

*   Delete the generated files and directories

**Test 7: Generate a pdf with dpi specified**

*   Procedure

1.  From the command line run:

\# replace "typeNumber" with a number from \[1-4\]

\# replace "dpiNumber" with an integer greater than 0

\# replace "~/path/to/image/file" with the correct path

decapod-genpdf.py -t typeNumber -d ~/Desktop/bookDir -p ~/Desktop/test.pdf -dpi dpiNumber -l ~/path/to/image/file

*   Type 1 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a 24-bit colour image of the image file passed in
*   The pdf should have a width of 21cm and a height of 29.7cm
*   The pdf should have the specified dpi

*   Type 2 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a 24-bit colour image of the image file passed in and have the ocr'd text underplayed
*   The pdf should have a width of 21cm and a height of 29.7cm
*   The pdf should have the specified dpi

*   Type 3 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a computer traced representation of the image file passed in, all the text should be selectable
*   The pdf should have a width of 21cm and a height of 29.7cm

*   Type 4 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf files should be generated
*   test.pdf should contain selectable text in a matching font to the image file passed in
*   The pdf should have a width of 21cm and a height of 29.7cm

*   Stop Test

*   Delete the generated files and directories

**Test 8: Generate a pdf with the colour flag specified**

*   Procedure

1.  From the command line run:

\# replace "typeNumber" with a number from \[1-4\]

\# replace "imageColour" with one of the following \[color, colour, grey, gray\]

\# replace "~/path/to/image/file" with the correct path

decapod-genpdf.py -t typeNumber -d ~/Desktop/bookDir -p ~/Desktop/test.pdf -c imageColour -l ~/path/to/image/file

*   Type 1 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a 200 DPI image of the image file passed in
*   The colour of the image should match the passed in value
*   The pdf should have a width of 21cm and a height of 29.7cm

*   Type 2 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a 200 DPI image of the image file passed in and have the ocr'd text underplayed
*   The colour of the image should match the passed in value
*   The pdf should have a width of 21cm and a height of 29.7cm

*   Type 3 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a computer traced representation of the image file passed in, all the text should be selectable
*   The pdf should have a width of 21cm and a height of 29.7cm

*   Type 4 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf files should be generated
*   test.pdf should contain selectable text in a matching font to the image file passed in
*   The pdf should have a width of 21cm and a height of 29.7cm

*   Stop Test

*   Delete the generated files and directories

**Test 9: Generate a pdf with a specified bit depth**

*   Procedure

1.  From the command line run:

\# replace "typeNumber" with a number from \[1-4\]

\# replace "bitDepth" with a number from \[24, 16, 8, 1\]

\# replace "~/path/to/image/file" with the correct path

decapod-genpdf.py -t typeNumber -d ~/Desktop/bookDir -p ~/Desktop/test.pdf -bit bitDepth -l ~/path/to/image/file

*   Type 1 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a 200 DPI image of the image file passed in
*   The bit depth of the image should match the value passed in
*   The image should be colour, unless a bit depth of 1 is passed in
*   The pdf should have a width of 21cm and a height of 29.7cm

*   Type 2 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a 200 DPI image of the image file passed in
*   The bit depth of the image should match the value passed in
*   The image should be colour, unless a bit depth of 1 is passed in
*   The pdf should have a width of 21cm and a height of 29.7cm

*   Type 3 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf file should be generated
*   test.pdf should contain a computer traced representation of the image file passed in, all the text should be selectable
*   The pdf should have a width of 21cm and a height of 29.7cm

*   Type 4 Results

*   The test.json file should be created and updated with the progress as the export is generated
*   The bookDir directory should be created containing the working files
*   After the export has finished the test.pdf files should be generated
*   test.pdf should contain selectable text in a matching font to the image file passed in
*   The pdf should have a width of 21cm and a height of 29.7cm

*   Stop Test

*   Delete the generated files and directories
