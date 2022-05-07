echo off

rem
rem arguments:
rem ---------
rem  1- db
rem  2- sql script file
rem

set SQLITE=C:\Programme\Sqliteman\sqlite3.exe 

(echo BEGIN TRANSACTION; & cat %2 & echo END TRANSACTION;) | %SQLITE% %1  

