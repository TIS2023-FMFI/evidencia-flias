% Gardener's LaTeX template
% https://github.com/gardenerik/latex
\newcommand{\templversion}{v2023.2}

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{zah}

\LoadClass[12pt]{article}

% nastavenie papiera
\RequirePackage[
    paper                   = a4paper,
    left                    = 25mm,
    right                   = 25mm,
    top                     = 25mm,
    bottom                  = 25mm,
    headsep                 = 16pt,     % priestor medzi hlavickou a textom
    footskip                = 32pt,     % priestor medzi footerom a textom
    includeheadfoot,                    % chcem header a footer
]{geometry}

\RequirePackage[utf8]{inputenc} % encoding UTF-8
\RequirePackage{savesym}
\RequirePackage{graphicx}       % obrazky
\RequirePackage{titlesec}       % custom nadpisy sekcii
\RequirePackage{booktabs}       % pekne tabulky - \midrule, \toprule...
\RequirePackage{multirow}       % viacriadkove bunky v tabulkach
\RequirePackage{siunitx}        % fyzikalne jednotky
\RequirePackage{bm}             % bold math
\RequirePackage{amsfonts}       % nejake maticke fonty, primarne asi \mathbb{R}
\RequirePackage{amsmath}        % vacsina matickych symbolov
\RequirePackage{titling}
\RequirePackage{longtable}
\RequirePackage{MnSymbol}
\savesymbol{mathdollar}
%\DeclareMathAlphabet\mathbb{U}{msb}{m}{n}

\RequirePackage{fancyhdr}       % header a footer
\pagestyle{fancy}               % chcem fancy stranku - zo vsetkym, co sa da

\setlength{\parindent}{0cm}     % nechcem odsadenie prveho riadku v odseku
\setlength{\parskip}{6pt}       % medzera medzi odsekmi

% obsah headeru
\fancyhead{}
\fancyhead[L]{\scshape\@title}

% obsah footeru
\fancyfoot{}
\fancyfoot[L]{\small\@author}
\fancyfoot[R]{\small\thepage}

% chceme ciary pri footeri a headeri
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}

% na miesto "Figure 1" chceme "Obrázok 1"
\renewcommand{\figurename}{Obrázok}

% nechcem ciaru nad poznamkami pod ciarou (ake ironicke, ze)
\def\footnoterule{}

% toto je na podporu slovenskych uvodzoviek (napises "aa" a vykresli sa tak, ako je u nas zvykom ,,aa'')
\RequirePackage[slovak]{babel}
\RequirePackage{csquotes}
\DeclareQuoteAlias{german}{slovak}
\MakeOuterQuote{"}

% nastavime si riadkovanie na 1.2
\renewcommand{\baselinestretch}{1.2}

% nechcem cislovane sekcie
% \titleformat{\section}{\bfseries\Large}{}{0em}{}

% subsekcie chcem cislovat len ich cislom (t.j. nie 1.1. ale len 1.)
% \renewcommand{\thesubsection}{\arabic{subsection}}
% \titleformat{\subsection}{\bfseries\large}{\thesubsection.}{1em}{}

% nastavenie odkazov
\RequirePackage[unicode]{hyperref}  % links
\RequirePackage{xcolor}             % colors
\RequirePackage{xurl}               % rozdelenie dlhych linkov na viac riadkov

\definecolor{default-linkcolor}{HTML}{A50000}
\definecolor{default-filecolor}{HTML}{A50000}
\definecolor{default-citecolor}{HTML}{4077C0}
\definecolor{default-urlcolor}{HTML}{4077C0}

\hypersetup{
  hidelinks,
  colorlinks=true,
  linkcolor=default-linkcolor,                  % internal links
  filecolor=default-filecolor,  % local files
  citecolor=default-citecolor,  % citation links
  urlcolor=default-urlcolor,    % url links
  pdfcreator={Gardener's LaTeX template \templversion}
}
\urlstyle{same} % disable monospaced font for URLs

\RequirePackage{footnotebackref} % add backlinks to footnote references, cf. https://tex.stackexchange.com/questions/302266/make-footnote-clickable-both-ways

% defaultne nech je figure tam, kde sa nachadza v tex zdrojaku
\RequirePackage{float}
\floatplacement{figure}{H}

% code highlighting
% \RequirePackage{minted}
% \usemintedstyle{tango}

% source sans a source code fonty
\RequirePackage[default]{sourcesanspro}
\RequirePackage{sourcecodepro}

% lepsie figure captions
\RequirePackage[skip=4mm, labelfont=bf, singlelinecheck=false, justification=raggedright]{caption}

% highlight
\newcommand{\highlight}[1]{\colorbox{yellow}{$\displaystyle #1$}}
\newcommand{\bhighlight}[1]{\colorbox{yellow}{$\bm{\displaystyle #1}$}}

\setlength{\emergencystretch}{3em}  % prevent overfull lines

\renewcommand{\maketitlehooka}{\thispagestyle{empty}\vspace{2cm}\hrulefill}
\pretitle{\begin{center}\bfseries\Huge}
\posttitle{\end{center}}

\preauthor{\vspace{-0.75cm}\begin{center}\large}
\postauthor{\end{center}}

\predate{\vspace{-1cm}\begin{center}\small}
\postdate{\end{center}}
\renewcommand{\maketitlehookd}{\hrulefill\clearpage}

\let\oldmaketitle\maketitle
\renewcommand{\maketitle}{\oldmaketitle\cleardoublepage\thispagestyle{fancy}\setcounter{page}{1}}

% tightlist
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

% href in footnote
\DeclareOption{hreffootnote}{\DeclareRobustCommand{\href}[2]{#2\footnote{\url{#1}}}}
\DeclareOption{twoside}{\geometry{inner=35mm}}

\ProcessOptions\relax
