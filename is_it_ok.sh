#!/usr/bin/env bash

# pouziti:   is_it_ok.sh xlogin01-XYZ.zip testdir
#  
#   - POZOR: obsah adresare zadaneho druhym parametrem bude po dotazu VYMAZAN!
#   - rozbali archiv studenta xlogin01-XYZ.zip do adresare testdir a overi formalni pozadavky pro odevzdani projektu IPP
#   - nasledne vyzkousi spusteni
#   - detaily prubehu jsou logovany do souboru is_it_ok.log v adresari testdir

# Autor: Zbynek Krivka
# Verze: 1.5 (2018-03-05)
#  2012-04-03  Zverejnena prvni verze
#  2012-04-09  Pridana kontrola tretiho radku (prispel Vilem Jenis) a maximalni velikosti archivu
#  2012-04-26  Oprava povolenych pripon archivu, aby to odpovidalo pozadavkum v terminu ve WIS
#  2014-02-14  Pridana moznost koncovky tbz u archivu; Podpora koncovky .php; Kontrola zkratek rozsireni
#  2014-02-25  Pridani parametru -d open_basedir="" interpretu php
#  2015-03-12  Pridana chybejici zavorka v popisu chyby tretiho paramatru
#  2015-03-22  Pridana kontrola tretiho radku i v dalsich skriptech (prispela Michaela Lukasova), kontrola neexistence __MACOSX
#  2016-03-08  Pridana kontrola ulohy CLS a odebrana uloha CST (upozornil Michal Ormoš)
#  2017-02-06  Zrusen pozadavek na metainformace na tretim radku skriptu, zakomentovan kontrolni kod
#  2017-03-04  Aktualizace prikazu pro PHP 5.6 a Python 3.6 na Merlinovi (upozornil ¼uboš Hlipala)
#  2018-03-05  Zruseno deleni projektu na ulohy, nyni 1. a 2. uloha

LOG="is_it_ok.log"
MAX_ARCHIVE_SIZE=1100000
COURSE="IPP"
PARSESCRIPT="parse.php"
INTERPRETSCRIPT="interpret.py"
TESTSCRIPT="test.php"

# Test validity of argument number
if [[ $# -ne 2 ]]; then
  echo "ERROR: Missing arguments or too much arguments!"
  echo "Usage: $0  ARCHIVE  TESTDIR"
  echo "       This script checks formal requirements for archive with solution of $COURSE project."
  echo "         ARCHIVE - the filename of archive to check"
  echo "         TESTDIR - temporary directory that can be deleted/removed during testing!"
  exit 2
fi

# extrakce archivu
function unpack_archive () {
  local ext=`echo $1 | cut -d . -f 2,3`
  echo -n "Archive extraction: "
  RETCODE=100  
	if [[ "$ext" = "zip" ]]; then
		unzip -o $1 >> $LOG 2>&1
    RETCODE=$?
	elif [[ "$ext" = "tgz" ]]; then
		tar xfz $1 >> $LOG 2>&1
    RETCODE=$? 
	elif [[ "$ext" = "tbz" || "$ext" = "tbz2" ]]; then
		tar xfj $1 >> $LOG 2>&1
    RETCODE=$? 
	fi
  if [[ $RETCODE -eq 0 ]]; then
    echo "OK"
  elif [[ $RETCODE -eq 100 ]]; then
    echo "ERROR (unsupported extension)"
    exit 1
  else
    echo "ERROR (code $RETCODE)"
    exit 1
  fi
} 

#   Priprava testdir
if [[ -d $2 ]]; then
  read -p "Do you want to delete $2 directory? (y/n)" RESP
  if [[ $RESP = "y" ]]; then
    rm -rf $2 2>/dev/null
  else
    echo "ERROR: User cancelled rewriting of existing directory."
    exit 1
  fi
fi
mkdir $2 2>/dev/null
cp $1 $2 2>/dev/null


#   Overeni serveru (ala Eva neni Merlin)
echo -n "Testing on Merlin: "
HN=`hostname`
if [[ $HN = "merlin.fit.vutbr.cz" ]]; then
  echo "Yes"
else
  echo "No"
fi

#   Kontrola jmena archivu
cd $2
touch $LOG
ARCHIVE=`basename $1`
NAME=`echo $ARCHIVE | cut -d . -f 1 | egrep "^x[a-z]{5}[0-9][0-9a-z]$"`
echo -n "Archive name ($ARCHIVE): "
if [[ -n $NAME ]]; then
  echo "OK"
else
  echo "ERROR (the name $NAME does not correspond to a login)"
fi

#   Kontrola velikosti archivu
echo -n "Checking size of $ARCHIVE: "
ARCHIVE_SIZE=`du --bytes $ARCHIVE | cut -f 1`
if [[ ${ARCHIVE_SIZE} -ge ${MAX_ARCHIVE_SIZE} ]]; then 
  echo "Too big (${ARCHIVE_SIZE} bytes > ${MAX_ARCHIVE_SIZE} bytes)"; 
else 
  echo "OK"; 
fi

#   Extrahovat do testdir
unpack_archive ${ARCHIVE}


#   Dokumentace
echo -n "Searching for doc.pdf: "
if [[ -f "doc.pdf" ]]; then
  echo "OK"
else
  echo "ERROR (not found; required for 2nd task only!)"
fi  

echo "Scripts execution test (--help): "
#   Spusteni skriptu 
for SCRIPT in $PARSESCRIPT $INTERPRETSCRIPT $TESTSCRIPT; do
  if [[ -f $SCRIPT ]]; then
    EXT=`echo $SCRIPT | cut -d . -f 2`
    if [[ "$EXT" = "php" ]]; then
      php5.6 $SCRIPT --help >> $LOG 2>&1
      RETCODE=$?
	  elif [[ "$EXT" = "py" ]]; then
      python3 $SCRIPT --help >> $LOG 2>&1
      RETCODE=$?		 
	  else
      echo "INTERNAL ERROR: Unknown script extension."
      exit 3
	  fi
    if [[ $RETCODE -eq 0 ]]; then
      echo "  $SCRIPT: OK"
    else
      echo "  $SCRIPT: ERROR (returns code $RETCODE)"
      exit 1
    fi    
  else
    if [[ "$SCRIPT" = "$PARSESCRIPT" ]]; then
      echo "  $SCRIPT: ERROR (not found; required for 1st task only!)" 
    else
      echo "  $SCRIPT: ERROR (not found; required for 2nd task only!)"
    fi  
  fi
done

#   Kontrola rozsireni
echo -n "Presence of file rozsireni (optional): "
if [[ -f rozsireni ]]; then
  echo "Yes"
  echo -n "Unix end of lines in rozsireni: "
  dos2unix -n rozsireni rozsireni.lf >> $LOG 2>&1
  diff rozsireni rozsireni.lf >> $LOG 2>&1
  RETCODE=$?
  if [[ $RETCODE = "0" ]]; then
    UNKNOWN=`cat rozsireni | grep -v -E -e "^(STATP|FLOAT|STACK|STATI|FILES)$" | wc -l`
    if [[ $UNKNOWN = "0" ]]; then
      echo "OK"
    else
      echo "ERROR (Unknown bonus identifier or redundant empty line)"
    fi
  else
    echo "ERROR (CRLFs)"
  fi
else
  echo "No"
fi 

#   Kontrola adresare __MACOSX
if [[ -d __MACOSX ]]; then
  echo "Archive ($ARCHIVE) should not contain __MACOSX directory!"
fi

echo "ALL CHECKS COMPLETED!"
