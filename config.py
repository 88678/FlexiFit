#用於連接資料庫?
import os

class Config: 
    # 範例1：用 SQL Server 帳密登入（最常見）
    SQLALCHEMY_DATABASE_URI = "mssql+pyodbc://sa:jonsoncC7@localhost/FlexiFitDB?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '期末作業隨便打'
        