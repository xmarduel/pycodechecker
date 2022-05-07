#
# arguments:
# ---------
#  1- db
#  2- sql script file
#
SQLITE=/opt/local/bin/sqlite3 
#
(echo BEGIN TRANSACTION\;; cat $2; echo END TRANSACTION\;) | $SQLITE $1

