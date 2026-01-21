# preprints/monograph/.latexmkrc
# Monograph wrapper: deterministic build; enforce biblatex+biber.

$pdflatex = 'pdflatex -interaction=nonstopmode -file-line-error -halt-on-error -recorder %O %S';

$recorder = 1;
$halt_on_error = 1;
$silent = 0;

# Force biber (NOT bibtex)
$bibtex = 'biber %O %B';

# Prefer biber route (latexmk variants differ; harmless if ignored)
$bibtex_use = 2;

1;
